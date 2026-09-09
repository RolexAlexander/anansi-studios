"""The studio's agent crew, wired as one ADK pipeline.

Every agent uses include_contents="none" and pulls its inputs from explicit
session-state keys (templated as {key} in the instruction) rather than the
full conversation history. This keeps each call cheap -- important on a
tight token budget -- and makes the data flow between agents explicit and
easy to follow top to bottom.

Pipeline order:
    ScriptLoop (Writer <-> Critic, capped at 2 passes)
    -> Style agent            (picks one fixed theme)
    -> Extractor agent        (characters + scenes as JSON)
    -> Composer agent         (Imagen panel generation, character-consistent)
    -> Producer agent         (Parallel trend signal -> greenlight decision)
"""

from google.adk.agents import Agent, LoopAgent, SequentialAgent

from studio.config import TEXT_MODEL, THEMES
from studio.tools import approve_script, combine_comic_page, generate_panel_image, parallel_trend_search

_THEME_MENU = "\n".join(f"- {t['name']}: {t['mood']}" for t in THEMES)

writer_agent = Agent(
    name="writer",
    model=TEXT_MODEL,
    include_contents="none",
    instruction=(
        "You are the staff writer for a Caribbean folklore comic studio. "
        "Write a short comic script (4-6 panels) based on this seed: "
        "{genre_seed}\n\n"
        "Ground it in real, specific Caribbean folklore (e.g. Anansi, La "
        "Diablesse, Soucouyant, or another genuine figure/tradition that "
        "fits the seed) -- not a generic tropical reskin of a Western story. "
        "Use authentic voice and texture where it fits naturally.\n\n"
        "Editor feedback from the last review (may say 'none yet' on your "
        "first draft): {critic_feedback}\n"
        "If there is real feedback above, revise to address it directly.\n\n"
        "Output ONLY the script: a title, then each panel numbered with a "
        "one-line scene description and any dialogue/caption."
    ),
    output_key="script",
)

critic_agent = Agent(
    name="critic",
    model=TEXT_MODEL,
    include_contents="none",
    instruction=(
        "You are a sharp, honest virality critic for short comics. Review "
        "this script:\n\n{script}\n\n"
        "A script PASSES if it has: a clear hook in panel 1, a twist/reveal "
        "or turn, a genuine emotional beat, and a specific (not generic) "
        "Caribbean cultural anchor.\n\n"
        "If it PASSES: call the approve_script tool, then respond with one "
        "sentence confirming why it passes.\n"
        "If it FAILS: do NOT call the tool. Respond with specific, "
        "actionable feedback the writer can act on -- name exactly what's "
        "missing or weak."
    ),
    tools=[approve_script],
    output_key="critic_feedback",
)

script_loop = LoopAgent(
    name="script_loop",
    sub_agents=[writer_agent, critic_agent],
    max_iterations=2,
)

style_agent = Agent(
    name="style_agent",
    model=TEXT_MODEL,
    include_contents="none",
    instruction=(
        "Given this comic script:\n\n{script}\n\n"
        f"Pick exactly ONE visual theme from this fixed menu that best fits "
        f"the story's tone:\n{_THEME_MENU}\n\n"
        "Respond with ONLY the theme name on the first line, then one "
        "sentence explaining why it fits this specific story."
    ),
    output_key="theme_choice",
)

extractor_agent = Agent(
    name="extractor_agent",
    model=TEXT_MODEL,
    include_contents="none",
    instruction=(
        "Given this comic script:\n\n{script}\n\n"
        "Extract structured data as STRICT JSON only, no markdown fences, "
        "matching exactly this shape:\n"
        '{{"characters": [{{"name": "...", "appearance": "detailed visual '
        'description for consistent art generation -- hair, build, clothing, '
        'distinguishing features"}}], "panels": [{{"panel_number": 1, '
        '"characters_present": ["..."], "action": "what happens in this '
        'panel", "caption_or_dialogue": "..."}}]}}\n\n'
        "Include every panel from the script. Output nothing but the JSON."
    ),
    output_key="characters_and_scenes",
)

composer_agent = Agent(
    name="composer_agent",
    model=TEXT_MODEL,
    include_contents="none",
    instruction=(
        "You are the studio's art composer. You have:\n"
        "Characters and panels (JSON): {characters_and_scenes}\n"
        "Chosen visual theme: {theme_choice}\n\n"
        "For EVERY panel in the JSON, call generate_panel_image once, in "
        "panel order. Build each prompt by combining: the panel's action, "
        "the FULL appearance description (verbatim) of every character "
        "present in that panel so they stay visually consistent across "
        "panels, and the chosen theme's mood/palette -- do NOT ask the "
        "image itself to render dialogue text. Separately, pass that "
        "panel's caption_or_dialogue text as the `caption` argument so it "
        "can be baked on afterward when text mode is enabled. Use "
        "panel_number as the panel_number argument.\n\n"
        "After all panel calls succeed, call combine_comic_page ONCE with "
        "the ordered list of panel image paths returned by those calls, to "
        "produce a single combined comic page.\n\n"
        "Finally, respond with a JSON object summarizing everything: "
        '{{"panels": [{{"panel_number": 1, "path": "...", "prompt_used": '
        '"..."}}, ...], "comic_page_path": "..."}} using the exact paths '
        "returned by the tools."
    ),
    tools=[generate_panel_image, combine_comic_page],
    output_key="panels_manifest",
)

producer_agent = Agent(
    name="producer_agent",
    model=TEXT_MODEL,
    include_contents="none",
    instruction=(
        "You are the studio's producer. The comic below has just been "
        "finished and 'launched':\n\n{script}\n\n"
        "Call parallel_trend_search with 1-3 concise keyword queries about "
        "the specific folklore figure/genre/theme this story uses, and an "
        "objective describing that you're checking real current audience "
        "interest. Use the REAL results it returns -- do not invent data.\n\n"
        "Then make a greenlight decision: should this be produced as a "
        "3-5 minute short film? Respond with:\n"
        "VERDICT: GREENLIGHT or HOLD\n"
        "SIGNAL: one paragraph citing the specific real evidence the search "
        "returned (or stating plainly that no real signal was available, if "
        "the tool returned mock/empty data)\n"
        "RATIONALE: one paragraph tying the signal to the decision."
    ),
    tools=[parallel_trend_search],
    output_key="greenlight_decision",
)

root_agent = SequentialAgent(
    name="anansi_studio_pipeline",
    sub_agents=[
        script_loop,
        style_agent,
        extractor_agent,
        composer_agent,
        producer_agent,
    ],
)

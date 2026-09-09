# Anansi Studios

**An autonomous multi-agent production company, in a box — built for the [Agentic Cinema hackathon](https://agentic-cinema.devpost.com/), Parallel track.**

**Live on Google Cloud (Cloud Run):** https://anansi-studios-538522341838.us-central1.run.app — deployed via `adk deploy cloud_run`, running the real ADK agent server (verify with `curl .../list-apps` → `["studio"]`).

Anansi Studios takes a story seed, writes and critiques a short comic script, generates a comic in an authentic Caribbean folklore voice, "launches" it, and then — using [Parallel](https://parallel.ai)'s live web search — grounds its greenlight-to-movie decision in a *real* trend signal instead of a manually entered popularity number. This repo is the first working slice of a much larger vision: an AI-native studio that discovers, tests, and greenlights Caribbean-rooted IP before a single dollar of real production budget is spent on it.

Built end-to-end in a single ~3-hour session against a hard hackathon deadline. See [`docs/scope.md`](docs/scope.md) and [`process-notes.md`](process-notes.md) for the full, unedited planning trail — including the scope cuts made under time pressure.

## Why Caribbean folklore

Real folklore figures — Anansi the trickster spider, La Diablesse, the Soucouyant — are, in the words of one write-up on Caribbean comics, "visual gold for adaptation," and a real (if small) ecosystem of Caribbean animation/comics studios already exists (Listen Mi Caribbean, CARIALITY Studios, Animae Caribe). That audience and cultural material is real; what's missing is a fast, cheap way to test which stories would actually land before a studio commits real production resources to them. This project is explicitly designed to be **authentically Caribbean**, not a tropical reskin of Western comic conventions.

## Architecture

```
seed (e.g. "Anansi tricks the wind spirit into a race, comedic")
    |
    v
+------------------+       +--------------------+
|  Writer agent     | <--> |  Critic agent       |   script_loop (LoopAgent, max 2 passes)
|  drafts script    |      |  virality gate      |
+------------------+       +--------------------+
    |
    v
+------------------+
|  Style agent      |  picks one fixed visual theme
+------------------+
    |
    v
+------------------+
|  Extractor agent  |  script -> {characters[], panels[]} JSON
+------------------+
    |
    v
+------------------+
|  Composer agent   |  --tool--> generate_panel_image (Gemini/Imagen 3)
|  (character-      |            one call per panel, character appearance
|   consistent art) |            repeated verbatim for visual consistency
+------------------+
    |
    v
+------------------+
|  Producer agent   |  --tool--> parallel_trend_search (Parallel Search API)
|  greenlight gate  |            REAL trend/interest signal, not a guess
+------------------+
    |
    v
GREENLIGHT or HOLD, with cited real-world evidence
```

Every agent is a Google ADK `Agent` (Gemini-backed), wired into one `SequentialAgent` pipeline (`studio/agents.py`). Agents talk to each other through explicit ADK session state (`{key}` templating), not shared conversation history — this keeps each model call cheap and the data flow auditable top to bottom.

**The two integration points that matter for judging:**
- `generate_panel_image` (`studio/tools.py`) — real runtime call to Gemini/Imagen 3, not a name-drop.
- `parallel_trend_search` (`studio/tools.py`) — real runtime call to Parallel's Search API (`POST /v1/search`), whose result is what the Producer agent's greenlight decision is actually grounded in.

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in GOOGLE_API_KEY and PARALLEL_API_KEY
python main.py "Anansi tricks the wind spirit into a race, comedic"
```

Generated comic panels land in `output/`, plus a combined `output/comic_page.png` stitching all panels into one page. Set `STUDIO_MOCK=1` in `.env` to run the tool layer in placeholder mode (useful for structural testing without spending API budget — the ADK agents themselves still require a real `GOOGLE_API_KEY` to run at all, since ADK calls Gemini directly). Set `STUDIO_WITH_TEXT=1` to bake each panel's dialogue/caption onto the image as a comic caption box (off by default -- clean, text-free panel art).

### Testing without spending anything

```bash
python -m unittest tests.test_tools -v
```

These tests mock the network/SDK layer entirely and verify both integration points against the actual documented Parallel response schema and the Imagen SDK call shape — every assertion here was checked for free before a single real API call was made.

## What's built vs. what's roadmap

This is a deliberately honest accounting, not a sales pitch — cut under a real ~3-hour deadline, not because the ideas were weak.

**Built and running today:**
- Full write -> critique -> theme -> extract -> compose -> greenlight pipeline, one real end-to-end pass
- Real Imagen 3 panel generation with character-consistency prompting
- Real Parallel-grounded greenlight decision

**Explicitly cut, designed but not implemented — the actual long-term differentiator:**
- **Movie/short-film stage.** Turning a greenlit comic into a 3-5 minute video via image-per-N-seconds generation and video extension.
- **Durable per-agent memory.** Each agent (writer, critic, director, producer) keeping its own persistent memory across runs — the studio *remembering* what worked, not starting cold every time.
- **Cron-scheduled agent "workdays."** Agents that wake up, work, and go home on a schedule rather than running once end-to-end on demand — the "studio that runs itself" framing from the original concept.
- **A board agent evaluating the director/CEO agent.** Governance layer modeled on how a real studio's board oversees leadership.
- **Multi-theme generation (5 options, selected).** Today the style agent picks from 3 fixed themes rather than generating 5 novel ones.
- **An evolving virality-test rubric.** Today the critic runs one fixed rubric; the vision is a rubric that updates based on which past greenlights actually succeeded.
- **Real publishing to a third-party platform.** "Launch" today means writing artifacts to `output/`; the vision is publishing to an actual open-source comics site or similar.

## License

MIT — see [`LICENSE`](LICENSE).

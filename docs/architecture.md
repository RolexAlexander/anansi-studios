# Architecture

Technical detail behind the top-level [README.md](../README.md) diagram --
this doc covers what's actually running, file by file.

## Repo layout

```
Spark/ (repo root, published as anansi-studios on GitHub)
├── main.py                  CLI entrypoint: creates an ADK session, runs
│                            the pipeline once, prints results, saves output/
├── studio/
│   ├── __init__.py          re-exports root_agent -- required for ADK's
│   │                        CLI tooling (adk run / adk web / adk deploy)
│   │                        to discover this package as an agent
│   ├── agent.py             all agent + pipeline definitions (see below)
│   ├── config.py            env loading, model names, theme list, flags
│   └── tools.py             the two graded integrations + comic-page compositor
├── tests/
│   └── test_tools.py        zero-cost mocked tests for both integrations
├── docs/                    this folder -- planning trail + submission docs
├── output/                  generated artifacts (gitignored)
├── requirements.txt
├── .env.example             template; real .env is gitignored, never committed
└── LICENSE                  MIT
```

## Agent pipeline (`studio/agent.py`)

One `SequentialAgent` (`root_agent`, name `anansi_studio_pipeline`) runs
five stages in order:

1. **`script_loop`** -- an ADK `LoopAgent` wrapping `writer` and `critic`,
   capped at 2 iterations. `writer` drafts/revises the script into session
   state key `script`. `critic` reviews it against a fixed virality rubric
   (hook, twist, emotional beat, specific cultural anchor) and either calls
   the `approve_script` tool -- which sets `tool_context.actions.escalate =
   True` to end the loop immediately -- or writes feedback into
   `critic_feedback`, which the next `writer` pass reads back via `{critic_feedback}`
   templating.
2. **`style_agent`** -- picks one theme from the fixed list in
   `config.THEMES` (see "Why fixed themes" below), writes `theme_choice`.
3. **`extractor_agent`** -- turns the finished script into strict JSON
   (`characters[]`, `panels[]`) in `characters_and_scenes`. Character
   `appearance` fields are deliberately verbose/specific -- they get
   repeated verbatim in every panel prompt to keep art style consistent
   panel to panel.
4. **`composer_agent`** -- for every panel, calls `generate_panel_image`
   (one Gemini image-gen call per panel), then calls `combine_comic_page`
   once with all resulting paths. Writes `panels_manifest`.
5. **`producer_agent`** -- calls `parallel_trend_search` with a real query
   about the story's folklore figure/genre, then writes a
   GREENLIGHT/HOLD verdict into `greenlight_decision`, citing the actual
   search results returned (not invented data -- the instruction explicitly
   forbids that).

### Why every agent uses `include_contents="none"`

By default, ADK `LlmAgent`s see the full conversation history on every
call. With five-plus sequential stages, that history grows every step,
meaning later agents would resend everything earlier agents said --
quadratic token cost for no benefit, since each agent only actually needs
specific upstream outputs. Every agent here instead pulls exactly what it
needs via explicit `{state_key}` templating and ignores the rest. This was
a deliberate design choice given the hackathon's real, small token budget.

`genre_seed` and `critic_feedback` are pre-seeded into session state
*before* the run starts (in `main.py`), rather than relying on ADK's
optional-key template syntax, so the very first `writer` call always has
both keys available regardless of `include_contents` settings.

## The two graded integrations (`studio/tools.py`)

**`generate_panel_image(panel_number, prompt, caption="")`** -- calls
`google.genai.Client.models.generate_content` with `IMAGE_MODEL`
(`gemini-2.5-flash-image`). Note this is deliberately *not* Imagen's
`generate_images` endpoint -- that requires Vertex AI project-based auth
and 404s on a plain Developer API key (confirmed via a live
`client.models.list()` call during the build; see git history for the
exact fix commit). When `STUDIO_WITH_TEXT=1`, the prompt is extended with
explicit bubble/narration-box rendering instructions (via
`_with_bubble_instructions`) rather than compositing text on top of the
image afterward -- the model's own lettering looks like an actual comic
page rather than a caption bar glued on top. Off by default.

**`parallel_trend_search(search_queries, objective)`** -- a direct REST
call to Parallel's `POST https://api.parallel.ai/v1/search` (see
`docs/devpost-submission.md` for why the SDK wasn't used: the PyPI package
named `parallel` is an unrelated, abandoned Python 2-era library, not
Parallel Web Systems' SDK). Response parsing was verified against the
*actual* documented response schema via a mocked unit test before any real
API budget was spent -- see `tests/test_tools.py::test_real_response_schema_is_parsed_correctly`.

Both functions degrade to clearly-labeled mock output (`{"mock": True, ...}`)
when `STUDIO_MOCK=1` or a key is missing, rather than crashing -- this is
what allowed the whole pipeline's structure to be verified for free before
spending real API budget.

## Why fixed themes, not generated ones

The original design generated 5 novel visual themes per story and picked
one. Under the real time budget this was cut to picking from 3 fixed,
pre-written themes (`config.THEMES`) -- one fewer LLM call, and a
guaranteed-coherent set of options rather than gambling on 5 freshly
generated ones being usable. See [roadmap.md](roadmap.md) Phase 5 for
restoring the original generated-themes design.

## Deployment

`adk deploy cloud_run --project=<project> --region=us-central1
--service_name=anansi-studios --app_name=studio studio` builds a container
from the `studio/` package (ADK generates the Dockerfile) and deploys the
ADK API server -- not the ADK dev web UI (`--with_ui` was intentionally
omitted to save build/deploy time) -- to Cloud Run with
`--allow-unauthenticated`. Real credentials are passed via
`--env-vars-file` pointing at a YAML file outside the repo, never inline on
the command line and never committed. See the live endpoint list at
`/openapi.json` on the deployed service, or `/list-apps` for a fast
liveness check (`["studio"]` confirms the agent is discovered and serving).

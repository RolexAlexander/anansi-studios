# Full Vision & Roadmap

This is the complete original vision, in full — not just the vertical slice
built for the hackathon deadline. Everything here was designed during
`/scope` and deliberately cut for time, not because it was weak. This
document exists so the repo reads as a real product roadmap, not a
hackathon throwaway.

## The core premise

Anansi Studios is a **production company in a box**: a Caribbean equivalent
of a fully autonomous studio, where AI agents play every role a real
studio's staff would — writer, critic, art director, producer, director,
even a board — and the studio runs continuously, discovering and testing
IP before a single dollar of real production budget is spent.

## Phase 0 — Built today (the hackathon slice)

One live pipeline, run on demand: seed -> script (writer/critic loop) ->
theme -> character/scene extraction -> comic panel art (with optional
native model-rendered speech bubbles) -> combined comic page -> a
Parallel-grounded greenlight decision. See [architecture.md](architecture.md)
for the technical detail. This phase proves the mechanism end to end; every
later phase extends it rather than replacing it.

## Phase 1 — The virality loop, closed for real

Today the critic runs a **single fixed rubric** once per script (hook,
twist, emotional beat, cultural anchor), with one revision pass. The
original design was a loop that actually *learns*:

- After a comic is greenlit (or held) and the Parallel-grounded decision is
  made, **record the outcome** — the seed, the script, the theme, the
  critic's original verdict, and the real signal Parallel returned —
  as a structured record, not just printed output.
- Periodically (or after every N runs), a **rubric-update agent** reviews
  the accumulated outcomes and proposes a revision to the critic's actual
  rubric: which story beats correlated with a real greenlight signal,
  which didn't. The critic's instruction text becomes a living document
  the studio edits about itself, not a hardcoded string in `agent.py`.
- This is the mechanism that was originally described as "an update loop
  that updates the virality test based on success" — the critic gets
  measurably better at predicting what will actually land, using real
  outcomes instead of a static heuristic.

**Engineering note:** this only requires two additions to the current
architecture — a small persistence layer for outcome records (a single
JSON-lines file is enough to start; see Phase 3 for why markdown/OKF is the
better long-term choice), and one new agent stage that runs on its own
schedule rather than inside the per-comic pipeline.

## Phase 2 — The movie / short-film stage

A greenlit comic doesn't stop at the page. This phase turns it into a real
3-5 minute short film, using the **same underlying process** as the comic
(script -> critique -> theme -> extraction -> generation -> launch ->
signal -> feedback) but with a different generation step:

- Instead of one static image per panel, generate a new frame **every 3-10
  seconds** along the story's timeline, prompted from the same
  character/scene data the comic used — so a scene that was one comic
  panel becomes several frames of continuous coverage.
- Use video-extension/interpolation models to turn those generated frames
  into continuous motion rather than a slideshow of stills.
- Add voice: Gemini TTS for dialogue, with each character's voice
  established once (from the character sheet the extractor already
  produces) and reused consistently across every scene they appear in.
- Add a score: generative music (e.g. Lyria) scored to the film's mood and
  beat structure — using the same theme/mood metadata the comic's style
  agent already picks, not a separate creative decision from scratch.
- The finished short goes through the **exact same launch-and-signal loop**
  as the comic did: it "launches," a producer agent researches real
  audience reaction via Parallel, and that signal feeds back into the
  studio's outcome record from Phase 1 — did the movie actually perform
  the way the comic's greenlight predicted it would? That comparison is
  itself valuable data the rubric-update agent in Phase 1 can use.

**Engineering note:** this is a new terminal stage appended after today's
`producer_agent`, gated on `greenlight_decision` == GREENLIGHT. It reuses
`characters_and_scenes` and `theme_choice` from session state directly —
no new upstream agents needed, only a new generation + compositing stage
and a second, movie-specific launch/signal pass.

## Phase 3 — Durable studio memory (Google Cloud's Open Knowledge Format)

Today's pipeline starts cold on every run — it has no memory of past
scripts, past critiques, or what actually got greenlit. Google Cloud
announced the **Open Knowledge Format (OKF)** on June 12, 2026: an open,
vendor-neutral spec for storing knowledge as a directory of markdown files
with YAML frontmatter — one required field (`type`), a handful of optional
metadata fields, and a free-form markdown body. No SDK, no central
registry: if you can `git clone` it, an agent can read it. This is exactly
the "markdown memory standard" this project was designed around, and it's
a natural fit precisely because it's just files — durable, human-readable,
diffable in git, and directly editable by a real person if needed.

Each agent gets its own OKF-formatted memory directory:

- The **writer** remembers which folklore figures, jokes, and structures
  it has already used, so the studio doesn't repeat itself across runs.
- The **critic** remembers past verdicts *and* their real outcomes (from
  Phase 1's outcome records) — this is the actual substrate the
  rubric-update agent reads from.
- The **producer** remembers past Parallel research, building a running
  picture of what's trending in Caribbean folklore/animation over time
  instead of researching cold on every single run.
- The **director** (Phase 4) reads across all of the above to set overall
  studio strategy.

**Engineering note:** this is additive, not a rewrite — each agent's OKF
memory directory is read into session state as extra context before that
agent runs (a `before_agent_callback` reading the relevant markdown files),
and written back after. No change to the pipeline's control flow.

## Phase 4 — The studio "runs itself"

The most differentiated part of the original vision: agents modeled less
like stateless functions and more like actual staff with a working day.

- **Scheduled workdays.** Agents wake up on a cron schedule, do a day's
  work, and "go home" — rather than only running end-to-end on demand.
- **A daily reset ritual.** At the end of a scheduled workday, each agent
  is given an explicit wind-down prompt — family, rest, a good night's
  sleep — before the next day's context begins. This isn't decoration: it
  is the mechanism by which each agent's persistent voice/persona (stored
  in its Phase 3 OKF memory) evolves gradually across many days rather than
  being reset to a blank slate or drifting unboundedly within one
  ever-growing context window.
- **Manager/team tooling.** The director agent gets real project-management
  primitives — a task board across the studio's in-flight scripts/comics/
  films, status tracking per subagent, and a simple way to hold a "meeting"
  (a structured status-summary generation) when a project completes, before
  publishing.
- **A director/CEO agent** that sets overall studio direction — which
  genres to pursue, which folklore traditions to prioritize — based on
  greenlight history (Phase 1) and Parallel research (Phase 3's producer
  memory), rather than a human providing a fresh seed every time.
- **A board agent** that periodically evaluates the director/CEO agent's
  performance — greenlight hit rate, resource use, strategic direction —
  the governance layer a real studio's board provides. This is a distinct
  agent role from the director, deliberately: it reviews the director's
  OKF memory and outcome history rather than participating in production.

## Phase 5 — Real distribution

Today, "launch" means writing files to `output/`. Phase 5 makes it real:
- Publish finished comics (and, later, films) to an actual platform — a
  real open-source comics site, or a purpose-built one — instead of a
  local folder.
- Replace the manually-observed/simulated engagement signal with real
  first-party engagement data from that platform, used *alongside*
  Parallel's external signal for a fuller picture, feeding the same
  outcome-record substrate from Phase 1.
- Multi-theme generation: instead of picking from 3 fixed themes, generate
  5 novel visual directions per story and have a style-critic agent (or a
  human) select the best fit — closer to the original "5 themes, pick one"
  design cut for time in the hackathon build.

## How we progress from here

The phases above are ordered by dependency, not just ambition — each one
is buildable directly on top of the current, working codebase without
re-architecting the pipeline that already runs:

1. **Start with Phase 1 (virality loop).** It needs nothing new
   architecturally — just an outcome-record file and one new agent that
   runs outside the per-comic pipeline. It also produces the data every
   later phase (3, 4) depends on, so it's the correct starting point even
   though it's not the most visible feature.
2. **Phase 2 (movie stage) next**, since it's a pure extension — a new
   terminal stage on the existing `SequentialAgent`, reusing state that
   already exists. It's also the single most demo-able addition: "comic
   that becomes a short film" is the clearest, most literal fulfillment of
   the original pitch.
3. **Phase 3 (OKF memory) once outcome data exists.** Building durable
   memory before Phase 1 produces anything worth remembering would mean
   memory of nothing. Once Phase 1 is running, wiring OKF-formatted memory
   directories into each agent is additive and low-risk.
4. **Phase 4 (scheduled, self-directed studio) last of the agent work**,
   because it depends on every agent already having real memory (Phase 3)
   and a real feedback signal (Phase 1) to act on — a director agent
   setting strategy with no memory or outcome data to draw on would just be
   guessing with extra steps.
5. **Phase 5 (real distribution) can start in parallel with any of the
   above** whenever there's a real platform to publish to — it's the one
   phase that's gated by an external dependency (having somewhere real to
   publish) rather than by this codebase's own architecture.

None of this requires discarding what exists today. Every phase is
something layered on top of the same `SequentialAgent` pipeline, the same
session-state conventions, and the same two graded integrations
(Gemini generation, Parallel research) that are already proven working.

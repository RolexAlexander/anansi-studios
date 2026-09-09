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

## Phase 1 — Built today (the hackathon slice)

One live pipeline, run on demand: seed -> script (writer/critic loop) ->
theme -> character/scene extraction -> comic panel art (with optional
native model-rendered speech bubbles) -> combined comic page -> a
Parallel-grounded greenlight decision. See [architecture.md](architecture.md)
for the technical detail.

## Phase 2 — The movie stage

A greenlit comic doesn't stop at the page. The next phase turns it into a
3-5 minute short film:
- Generate a new image every 3-10 seconds along the story's timeline
  (rather than one static image per panel), prompted from the same
  character/scene data the comic used, so visual continuity carries over.
- Use video-extension models to interpolate/extend between those
  generated frames into continuous motion rather than a slideshow.
- Add voice: Gemini TTS for dialogue, matched to each character's voice
  profile (established once, reused across the character's appearances).
- Add a score: generative music (e.g. Lyria) scored to the film's mood/beat
  structure, not just a generic loop.

## Phase 3 — Durable studio memory

Today's pipeline starts cold on every run — it has no memory of past
scripts, past critiques, or what actually got greenlit. Phase 3 gives every
agent its own persistent memory, stored as markdown (durable, human-
readable, and directly inspectable/editable by a real person if needed):
- The **writer** remembers which folklore figures, jokes, and structures it
  has already used, so the studio doesn't repeat itself.
- The **critic** remembers past verdicts and their real outcomes (did a
  greenlit story actually perform well?), so its rubric improves over time
  instead of staying static — this closes the loop that Phase 0's design
  called an "evolving virality-test rubric."
- The **producer** remembers past Parallel research, building a running
  picture of what's trending in Caribbean folklore/animation over time
  rather than researching cold on every single run.

## Phase 4 — The studio "runs itself"

The most differentiated part of the original vision: agents modeled less
like stateless functions and more like actual staff.
- **Scheduled workdays.** Agents wake up on a cron schedule, do a day's
  work, and "go home" -- rather than only running end-to-end on demand.
- **A sense of self.** Each agent's memory isn't just task history -- it
  can include a lightweight persona/voice that persists and evolves,
  the way a real staff writer's voice develops over a career.
- **A director/CEO agent** that sets overall studio direction (which
  genres to pursue, which folklore traditions to prioritize) based on
  greenlight history and Parallel research, rather than a human providing
  a fresh seed every time.
- **A board agent** that periodically evaluates the director/CEO agent's
  performance -- greenlight hit rate, resource use, strategic
  direction -- the governance layer a real studio's board provides.

## Phase 5 — Real distribution

Today, "launch" means writing files to `output/`. Phase 5 makes it real:
- Publish finished comics to an actual platform (a real open-source comics
  site, or a purpose-built one) instead of a local folder.
- Replace the manually-observed/simulated engagement signal with real
  first-party engagement data from that platform, used alongside Parallel's
  external signal for a fuller picture.
- Multi-theme generation: instead of picking from 3 fixed themes, generate
  5 novel visual directions per story and have a style-critic agent (or a
  human) select the best fit, closer to the original "5 themes, pick one"
  design.

## Why this order

Each phase is a superset of real value on its own -- Phase 2 makes a
better single deliverable, Phase 3 makes the studio smarter over runs,
Phase 4 makes it autonomous, Phase 5 makes it a real product with real
users. None of them require re-architecting Phase 1's agent pipeline --
they extend it.

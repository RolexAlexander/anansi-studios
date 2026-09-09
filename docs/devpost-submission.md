# Devpost Submission — Copy/Paste Blocks

**Project name:** Anansi Studios

**Tagline (one line):**
An autonomous multi-agent production company that writes, illustrates, and
greenlights Caribbean folklore comics — grounding the greenlight decision in
a real trend signal from Parallel instead of a guess.

**Partner track:** Parallel

---

## Inspiration

Caribbean folklore — Anansi the trickster spider, La Diablesse, the
Soucouyant — is genuinely rich material with a real, if under-served,
audience: small studios like Listen Mi Caribbean, CARIALITY Studios, and
Animae Caribe already prove that. What's missing is a fast, cheap way for a
studio to test which specific stories would actually land with an audience
before committing real production budget to full illustration or animation.
We set out to build the smallest real version of an AI-native studio that
does exactly that.

## What it does

Anansi Studios takes a story seed and runs it through a full production
pipeline: a writer agent drafts a short comic script rooted in real
Caribbean folklore; a critic agent runs a virality check and sends it back
for revision if it doesn't land; a style agent picks a visual theme; an
extractor pulls out characters and scene beats; a composer agent generates
character-consistent comic panel art; and finally a producer agent calls
Parallel's live search API to find real-world evidence of audience interest
in that story's folklore figure or theme — and uses that real evidence,
not a manually entered number, to decide whether the comic should be
greenlit for a future short-film adaptation.

## How we built it

Built on Google ADK, with every pipeline stage as a Gemini-backed agent
communicating through explicit session state rather than shared
conversation history (kept token cost down on a tight budget). The
writer/critic stage is an ADK `LoopAgent` that exits early via a tool call
the moment the critic approves. Comic panels are generated with Gemini's
native image model, with each panel's prompt repeating every present
character's full appearance description verbatim to keep them visually
consistent across panels. The producer agent's greenlight decision is
built entirely on a real `POST /v1/search` call to Parallel — the response
is what the agent's final verdict actually cites.

Deployed as a real Google Cloud service via `adk deploy cloud_run`.

## Challenges we ran into

Under a genuinely hard time constraint (built in one session against a
same-day deadline), we had to cut hard: the original vision was a full
"studio that runs itself" — durable per-agent memory, cron-scheduled agent
workdays, a board agent evaluating the director, and a full comic-to-movie
pipeline. All of that is real, designed, and documented in the README as
roadmap — but we made the deliberate call to ship one complete, honest,
working vertical slice rather than a half-built version of everything.
We also hit a real integration snag: Imagen's `generate_images` endpoint
requires Vertex AI project auth and 404s on a plain Gemini Developer API
key — caught via a live model-list call, fixed by switching to Gemini's
native `generateContent`-based image model instead.

## Accomplishments we're proud of

The Parallel-grounded greenlight decision is real, not simulated — in
testing, the producer agent cited actual specific evidence (real view
counts on an existing Anansi animated short, a real recent book release)
to justify its verdict. That's the whole point of the project working
exactly as intended.

## What we learned

That an honest, working narrow slice beats an ambitious, broken wide one —
and that verifying integration schemas (Parallel's API, the image-gen SDK
call shape) against real documentation *before* spending API budget, via
mocked unit tests, catches real bugs for free.

## What's next for Anansi Studios

The full original vision: turning greenlit comics into 3-5 minute short
films via image-per-N-seconds generation and video extension; durable
per-agent memory so the studio actually improves over time instead of
starting cold on every run; cron-scheduled agent "workdays"; and a board
agent that evaluates the director/CEO agent's performance over time. See
the README's "What's built vs. what's roadmap" section for the full,
honest breakdown.

---

## Built With
google-adk, google-genai, gemini, parallel, google-cloud-run, python

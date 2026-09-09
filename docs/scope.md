<!-- Compressed under extreme time pressure: /scope, /prd, and /spec were collapsed into
     this single document. Written at T-minus ~2h40m to the Agentic Cinema deadline
     (2026-09-09, 5:00 PM Guyana time / 2:00 PM PDT). -->

# Anansi Studios (working title)

## Idea
An autonomous multi-agent "production company in a box," built on Google ADK + Gemini, that takes a genre/idea seed, writes and critiques a short comic script, generates a themed comic, "launches" it, and uses **Parallel** to pull a real-world trend/interest signal that the agent uses to decide — for real, not a coin flip — whether the story is a hit worth greenlighting further. Long-term vision: hits get promoted into 3-5 minute short films; the studio runs continuously with durable per-agent memory, scheduled "workdays," and a board agent evaluating the director/CEO agent. Today's build is the vertical slice that proves the core loop end-to-end.

## Who It's For
Independent Caribbean creators, small animation/comics studios (e.g. the real ecosystem around Listen Mi Caribbean, CARIALITY Studios, Animae Caribe), and — longer-term — a real content studio that wants an AI-native pipeline for discovering and validating Caribbean-rooted IP before spending real production budget on it. The unmet need: authentic Caribbean folklore-based content (Anansi, La Diablesse, Soucouyant, etc.) is culturally rich but under-produced relative to demand, and studios have no fast, cheap way to test which stories/themes would actually land before committing full production resources.

## Inspiration & References
- Real Caribbean folklore figures as seed material: Anansi (trickster spider), La Diablesse, Soucouyant — via https://river-stories.com/caribbean-folklore-folktales-fables-ananse/ and https://en.wikipedia.org/wiki/Caribbean_folklore
- Real comparable studios (proof of real audience/market): Listen Mi Caribbean (https://medium.com/@animationjamaica/caribbean-comics-37dd31e9a55), CARIALITY Studios (https://carialitystudios.com/), Animae Caribe (https://www.animaecaribe.com/)
- Architectural comparable (proof of concept feasibility, not a template to copy): MetaGPT-style role-based multi-agent org simulation
- Aesthetic direction: explicitly NOT a generic "tropical" reskin. Authentic Caribbean visual and narrative texture — real folklore figures, real Creolese narrative voice where appropriate, not Westernized comic conventions with palm trees added.

## Goals
Rolex's stated goal (from onboarding): this should be a **real product** — a credible seed for a business or open-source project, not throwaway hackathon scaffolding. Under today's time constraint, that goal is served by: (1) a working core loop that actually runs, (2) an honest, well-documented architecture for the full vision so the repo reads as "real roadmap," not vaporware, (3) clean enough code/licensing to actually reopen and continue after the hackathon.

## What "Done" Looks Like (submission-ready, ~90 min build budget)
One live, runnable pipeline (CLI or minimal hosted UI — whichever is faster to stand up):
1. Input: a genre/seed (e.g. "Anansi trickster story, comedic").
2. **Writer agent** drafts a short comic script (Gemini).
3. **Critic agent** runs one virality-check pass against the script; on fail, one revision loop (not an evolving/updating rubric — that's cut).
4. **Style agent** picks one visual theme (from a small fixed set, not 5 generated).
5. **Extraction step** pulls characters + scene beats from the script.
6. **Composer agent** generates comic panel images (Gemini/Imagen) using the extracted characters/scenes for consistency.
7. "Launch" step: the studio publishes/logs the finished comic.
8. **Producer agent calls Parallel** to research real trend/interest signal relevant to the theme/genre.
9. **Decision step**: agent uses that real signal to output a greenlight/no-greenlight verdict for "movie production" — this is the payoff moment for the demo and the required authentic Parallel integration.
10. Runs on Google ADK, deployed/callable via Google Cloud (Agent Builder / Vertex AI) to satisfy the mandatory platform requirement.

Output artifacts needed for submission: hosted project URL, public GitHub repo with OSS license visible in About section, 3-minute demo video (screen recording of one full run, English), Devpost form with Parallel selected as track.

## What's Explicitly Cut (documented as roadmap, not built today)
- **Movie/short-film generation stage** (image-per-N-seconds + video extension). No time. Described in README as Phase 2.
- **Durable per-agent memory wiki, cron-scheduled agent "workdays," agents "going home to family."** This is the studio-personhood layer — genuinely the most differentiated "Quality of Idea" material, but zero chance of running reliably live in the time remaining. Documented in README as the core long-term differentiator.
- **Board agent evaluating the director/CEO agent.** Roadmap only.
- **Multiple theme generation (5 options) + selection UI.** Collapsed to one fixed theme for today.
- **Continuous/evolving virality-test rubric with an update loop.** Collapsed to a single static critic pass today.
- **Real publishing to an actual open-source comics site.** "Launch" today just means writing/logging the finished artifact somewhere visible (repo output folder or a minimal hosted page) — not a live third-party platform integration.

## Loose Implementation Notes (non-binding, refined live during build)
- Stack: Python + Google ADK for agent orchestration; Gemini for text (script/critic/decision reasoning) and image generation for comic panels; Parallel's API called directly from the Producer agent's tool set (real runtime call, not a stub).
- Given the time budget, prioritize a CLI/script entrypoint that produces visible artifacts (script text, panel images, a final verdict) over a polished web UI — a working terminal run recorded cleanly is a legitimate demo video.
- Build order locked from /scope conversation: (1) walking skeleton of the full loop with placeholder content, (2) real Gemini generation wired in, (3) real Parallel call wired into the decision step, (4) record demo + write README/roadmap + license + push repo + hosted URL + Devpost form.
- Deadline-driven note: if the hosted-URL requirement becomes a time sink, prefer the simplest possible hosting (e.g., a static output page or a minimal Cloud Run deploy of the same script) over building a real frontend.

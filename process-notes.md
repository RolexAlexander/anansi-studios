# Process Notes

## /onboard
- Severe time crunch: onboarding started 10:01 AM Guyana time, deadline 5:00 PM Guyana time (2:00 PM PDT) — ~7 hours total budget. Compressed the standard onboarding conversation (bundled questions instead of one-at-a-time) to preserve build time.
- Experienced multi-agent builder (CrewAI, Google ADK, full-stack). No beginner framing needed anywhere downstream.
- Wants a real product (business or open-source), not throwaway hackathon scaffolding — hold this bar even under time pressure.
- Wants authentic Caribbean creative voice, explicitly rejecting generic/tropical-reskin aesthetics.
- Decision: given the time budget, skipping the literal `/clear` between commands for this session — proceeding directly into `/scope` to avoid losing conversational context that would otherwise need to be re-derived from docs. Docs are still being written at each stage as the source of truth.

## /scope
- CRITICAL CORRECTION: initial time estimate (10:01 AM local) was read from a stale directory timestamp, not the real clock. Actual check mid-conversation: 2:13 PM local (UTC-4, confirmed matches Guyana offset), deadline 5:00 PM local (2:00 PM PDT) — true remaining budget was ~2h47m at correction time, not 6-7h. Flagged transparently to learner; lesson for future sessions — always verify wall-clock time directly (`date`), never infer "now" from a file mtime.
- Learner pushed back hard on an early "build small, cut most of the vision" framing — insisted ADK + agentic coding makes the full vision buildable, wanted end goal of finishing everything for submission. Resolution: kept the ambition, changed the sequencing instead (walking skeleton → real Gemini gen → real Parallel integration → polish), so a demo-able core always exists first regardless of how far the stretch goals get.
- Partner track locked: Parallel. Integration point: a Producer/board agent calls Parallel for real trend/interest signal to power the greenlight-to-movie decision — directly matches the learner's own "agent decides" framing rather than being bolted on.
- Given the corrected ~2h47m budget (now less, post-scope-writing), collapsed /prd and /spec into the scope doc itself and skipped straight to /build. Did not run those commands as separate conversations — full curriculum chain is not survivable in this window.
- Research that resonated: real Caribbean folklore figures (Anansi, La Diablesse, Soucouyant) as concrete, non-generic seed material; real small Caribbean animation/comics studios as proof of actual audience.
- Final scope: one live pipeline run (script → critic pass → theme → extraction → comic panels → launch → Parallel signal → greenlight decision). Movie stage, durable memory/cron "agent lives," board-evaluates-CEO loop, multi-theme generation, and evolving virality rubric all cut to documented roadmap, not built today.

# 3-Minute Demo Video Script

Record this as one continuous screen capture. Don't over-produce it — the
requirement is "showing your project/agent functioning as built," not a
trailer. A clean terminal run + a look at the panels is a legitimate,
strong demo.

## 0:00-0:20 — The hook (talk to camera or voiceover, no screen yet)
"Caribbean folklore — Anansi, La Diablesse, the Soucouyant — has a real
audience and almost no fast way to test which stories will actually land
before a studio spends real production money on them. Anansi Studios is an
autonomous multi-agent production company that writes, critiques, illustrates,
and greenlights Caribbean folklore comics — using a real trend signal from
Parallel to make that greenlight decision, not a guess."

## 0:20-0:40 — Architecture, fast
Screen: `README.md` architecture diagram. Point at it while saying:
"Built on Google ADK and Gemini. A writer and critic agent loop on the
script, a style agent picks the visual theme, an extractor pulls characters
and scenes, a composer generates character-consistent comic panels, and a
producer agent calls Parallel's live search API to ground the final
greenlight decision in real evidence."

## 0:40-2:10 — The real run
Screen: terminal, run `python main.py "Anansi tricks the wind spirit into a
race, comedic"` (or your best take from testing). Let it play, but feel
free to cut/speed up the quiet stretches between agent outputs — keep the
following moments un-cut and clearly readable:
- The writer's script appearing (proves authentic Caribbean voice, not
  generic).
- The critic's pass/fail response (proves the loop is real).
- Cut to `output/panel_01.png` through `panel_05.png` — show the actual
  generated images, ideally full-screen for a beat each.
- The producer agent's final output — **read the SIGNAL line out loud**.
  This is the moment that matters most for judging: it's citing specific,
  real search results (e.g. actual view counts, actual book releases),
  not invented numbers. Make sure this is visible on screen long enough
  to read.

## 2:10-2:40 — Proof it's really on Google Cloud
Screen: hit the deployed Cloud Run URL (browser or curl) and show it
responding. One sentence: "This runs as a real Google Cloud Agent Builder
service, not just on my laptop."

## 2:40-3:00 — Honest close
"This is the vertical slice — one full pass through the pipeline, working
end to end today. The full vision — turning greenlit comics into short
films, giving every agent durable memory, a scheduled studio 'workday,' and
a board agent that evaluates the director — is documented in the README as
the actual roadmap. Thanks for watching."

## Reminders before you record
- Upload to YouTube or Vimeo, set **public**, English audio (or add subtitles).
- Keep it at or under 3 minutes — judges may not watch past the cutoff.
- Don't narrate this as a cinematic trailer — it should read as "here is my
  project running," per the hackathon's own submission requirements.

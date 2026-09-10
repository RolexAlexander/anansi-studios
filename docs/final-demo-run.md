# Final Demo Run

This is the last real pipeline run produced during the hackathon build,
generated the same evening the project was submitted (moments before a
power outage cost the submission its final few minutes -- see
[process-notes.md](../process-notes.md) for the full account). The images
are committed at [assets/sample-output/](../assets/sample-output/) as
concrete proof of what the pipeline actually produces, independent of
whether a hosted URL is live.

## Seed used

```
La Diablesse walks the midnight road in a beautiful gown, hiding her one
cloven hoof, and lures a lone traveler who ignores every warning sign,
genuinely eerie horror tone
```

Run with text mode enabled:

```bash
STUDIO_WITH_TEXT=1 python main.py "La Diablesse walks the midnight road in a beautiful gown, hiding her one cloven hoof, and lures a lone traveler who ignores every warning sign, genuinely eerie horror tone"
```

## What this run demonstrates

- The writer/critic loop producing a genre outside the earlier
  Anansi-comedy examples -- a straight horror folk tale built on La
  Diablesse, a different real Caribbean folklore figure, proving the
  pipeline isn't hard-coded to one character or tone.
- `STUDIO_WITH_TEXT=1` -- native model-rendered speech bubbles/narration,
  not a PIL overlay -- carried through end to end on a full 5-panel run.
- The comic-page compositor (`combine_comic_page`) stitching all five
  panels into a single page, `comic_page.png`.

## Result

| File | Description |
|---|---|
| [panel_01.png](../assets/sample-output/panel_01.png) | Opening panel -- La Diablesse on the midnight road |
| [panel_02.png](../assets/sample-output/panel_02.png) | The traveler encounters her, warning signs begin |
| [panel_03.png](../assets/sample-output/panel_03.png) | Escalation |
| [panel_04.png](../assets/sample-output/panel_04.png) | The turn/reveal |
| [panel_05.png](../assets/sample-output/panel_05.png) | Final beat |
| [comic_page.png](../assets/sample-output/comic_page.png) | All five panels combined into one page |

## Honest gap in this record

The full text transcript for this specific run (the writer's script draft,
the critic's verdict, and the producer agent's Parallel-grounded greenlight
decision) was not captured -- it printed to a terminal window that closed
with the blackout before it could be saved. The image artifacts above are
real and survived (written to disk as each panel completed, before the
outage), but the accompanying text output for *this exact run* is not
available. For a fully documented run with the complete text output --
script, critic verdict, and the real cited Parallel evidence behind the
greenlight decision -- see the Anansi/Bra Breeze wind-race example
reproduced in full in [README.md](../README.md) and
[devpost-submission.md](devpost-submission.md), captured earlier in the
same session under identical code.

"""Tool functions called by agents. Each doubles as the real hackathon-graded
integration points: generate_panel_image (Gemini/Imagen) and
parallel_trend_search (Parallel -- the required partner integration).

Both respect STUDIO_MOCK / missing keys and degrade to clearly-labeled
placeholder output instead of crashing, so the pipeline's *structure* can be
verified for free before spending real API budget.
"""

import requests
from google import genai
from google.adk.tools import ToolContext

from studio.config import GOOGLE_API_KEY, IMAGE_MODEL, MOCK, OUTPUT_DIR, PARALLEL_API_KEY


def parallel_trend_search(search_queries: list[str], objective: str) -> dict:
    """Search the live web for real-world trend and audience-interest signal.

    Use this to ground a greenlight decision in real evidence -- is this
    genre/folklore figure/theme actually resonating right now -- instead of a
    guess or a manually-entered fake popularity number.

    Args:
        search_queries: 1-4 concise keyword queries, 3-6 words each.
        objective: One sentence describing what you're trying to find out.

    Returns:
        A dict with "results" (list of {url, title, excerpts}) and a
        "signal_summary" string, or {"error": ...} on failure.
    """
    if MOCK or not PARALLEL_API_KEY:
        return {
            "mock": True,
            "results": [],
            "signal_summary": (
                "MOCK MODE: no PARALLEL_API_KEY set / STUDIO_MOCK=1. "
                "No real trend signal was fetched -- this run cannot support "
                "a real greenlight decision."
            ),
        }

    try:
        response = requests.post(
            "https://api.parallel.ai/v1/search",
            headers={"x-api-key": PARALLEL_API_KEY, "Content-Type": "application/json"},
            json={
                "objective": objective,
                "search_queries": search_queries[:4],
                "mode": "fast",
                "max_chars_total": 4000,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        summary = "; ".join(
            f"{r.get('title', 'untitled')}: {' '.join(r.get('excerpts', []))[:200]}"
            for r in results[:5]
        )
        return {"results": results, "signal_summary": summary or "No results found."}
    except Exception as exc:  # noqa: BLE001 - surface any failure to the agent, not a crash
        return {"error": str(exc)}


def generate_panel_image(panel_number: int, prompt: str) -> dict:
    """Generate one comic panel image and save it to disk.

    Args:
        panel_number: 1-based panel index, used for the filename.
        prompt: Full visual description of this panel. Repeat each character's
            appearance details verbatim from the character sheet so the same
            character stays visually consistent across panels. Include the
            scene's action, setting, and the chosen style/mood.

    Returns:
        A dict with "path" (saved image file path) or "error".
    """
    path = OUTPUT_DIR / f"panel_{panel_number:02d}.png"

    if MOCK or not GOOGLE_API_KEY:
        path.write_text(f"MOCK PLACEHOLDER -- prompt was:\n{prompt}", encoding="utf-8")
        return {"path": str(path), "mock": True}

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        result = client.models.generate_images(
            model=IMAGE_MODEL,
            prompt=prompt,
            config={"number_of_images": 1},
        )
        image = result.generated_images[0].image
        image.save(str(path))
        return {"path": str(path)}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def approve_script(tool_context: ToolContext) -> dict:
    """Call this ONLY when the script clearly passes the virality check --
    it has a hook, a twist or reveal, and a clear emotional beat suitable for
    a short comic. Calling this ends the write/critique loop immediately.
    """
    tool_context.actions.escalate = True
    return {"status": "approved"}

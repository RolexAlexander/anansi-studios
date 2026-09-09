"""Tool functions called by agents. Each doubles as the real hackathon-graded
integration points: generate_panel_image (Gemini/Imagen) and
parallel_trend_search (Parallel -- the required partner integration).

Both respect STUDIO_MOCK / missing keys and degrade to clearly-labeled
placeholder output instead of crashing, so the pipeline's *structure* can be
verified for free before spending real API budget.
"""

import math
import textwrap

import requests
from google import genai
from google.adk.tools import ToolContext
from PIL import Image, ImageDraw, ImageFont

from studio.config import GOOGLE_API_KEY, IMAGE_MODEL, MOCK, OUTPUT_DIR, PARALLEL_API_KEY, WITH_TEXT


def _load_font(size: int) -> ImageFont.ImageFont:
    for candidate in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:  # noqa: BLE001 - font not found, try next
            continue
    return ImageFont.load_default()


def _overlay_caption(image_path, caption: str) -> None:
    """Bake a comic-style caption box onto the bottom of an image, in place."""
    if not caption:
        return
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    width, height = img.size

    font_size = max(18, width // 28)
    font = _load_font(font_size)
    wrapped = textwrap.fill(caption, width=max(20, width // (font_size // 2)))
    lines = wrapped.split("\n")
    line_height = int(font_size * 1.3)
    bar_height = line_height * len(lines) + 24

    draw.rectangle([0, height - bar_height, width, height], fill=(0, 0, 0, 190))
    y = height - bar_height + 12
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) / 2, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_height

    img.save(image_path)


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


def generate_panel_image(panel_number: int, prompt: str, caption: str = "") -> dict:
    """Generate one comic panel image and save it to disk.

    Args:
        panel_number: 1-based panel index, used for the filename.
        prompt: Full visual description of this panel. Repeat each character's
            appearance details verbatim from the character sheet so the same
            character stays visually consistent across panels. Include the
            scene's action, setting, and the chosen style/mood. Do NOT ask the
            image model to render text/dialogue itself -- pass that separately
            via `caption`, which is baked on afterward as a reliable caption
            box (only when text mode is enabled).
        caption: The panel's dialogue/caption text (from the character/scene
            JSON). Ignored unless text mode (STUDIO_WITH_TEXT=1) is on.

    Returns:
        A dict with "path" (saved image file path) or "error".
    """
    path = OUTPUT_DIR / f"panel_{panel_number:02d}.png"

    if MOCK or not GOOGLE_API_KEY:
        path.write_text(f"MOCK PLACEHOLDER -- prompt was:\n{prompt}", encoding="utf-8")
        return {"path": str(path), "mock": True}

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(model=IMAGE_MODEL, contents=prompt)
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                path.write_bytes(part.inline_data.data)
                if WITH_TEXT:
                    _overlay_caption(path, caption)
                return {"path": str(path)}
        return {"error": "No image data in response (model returned text only)."}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def combine_comic_page(panel_paths: list[str]) -> dict:
    """Stitch the generated panel images into a single comic page, in order.

    Args:
        panel_paths: Ordered list of panel image file paths (as returned by
            generate_panel_image), first panel first.

    Returns:
        A dict with "path" (saved combined comic page) or "error".
    """
    out_path = OUTPUT_DIR / "comic_page.png"
    try:
        images = [Image.open(p).convert("RGB") for p in panel_paths]
        if not images:
            return {"error": "No panel images provided."}

        cols = min(2, len(images)) if len(images) > 1 else 1
        rows = math.ceil(len(images) / cols)
        cell_w, cell_h = 640, 640
        gap = 12

        page = Image.new(
            "RGB",
            (cols * cell_w + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap),
            (20, 20, 20),
        )
        for i, im in enumerate(images):
            im_resized = im.resize((cell_w, cell_h))
            col, row = i % cols, i // cols
            x = gap + col * (cell_w + gap)
            y = gap + row * (cell_h + gap)
            page.paste(im_resized, (x, y))

        page.save(out_path)
        return {"path": str(out_path)}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def approve_script(tool_context: ToolContext) -> dict:
    """Call this ONLY when the script clearly passes the virality check --
    it has a hook, a twist or reveal, and a clear emotional beat suitable for
    a short comic. Calling this ends the write/critique loop immediately.
    """
    tool_context.actions.escalate = True
    return {"status": "approved"}

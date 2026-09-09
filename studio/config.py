import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
PARALLEL_API_KEY = os.environ.get("PARALLEL_API_KEY", "")
MOCK = os.environ.get("STUDIO_MOCK", "0") == "1"

# Off by default -- preserves the clean, text-free panel art. Set
# STUDIO_WITH_TEXT=1 to overlay each panel's caption/dialogue as a comic
# caption box baked into the image.
WITH_TEXT = os.environ.get("STUDIO_WITH_TEXT", "0") == "1"

TEXT_MODEL = "gemini-flash-latest"
# Note: plain Gemini Developer API keys (not Vertex AI project auth) don't have
# access to the separate Imagen `generate_images` endpoint -- confirmed via a
# live model-list call against this project's key. Using Gemini's native
# image-generation model via generateContent instead, which this key does have.
IMAGE_MODEL = "gemini-2.5-flash-image"

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Fixed style palette. /scope cut multi-theme generation+selection for time;
# the style agent picks one of these rather than generating five from scratch.
THEMES = [
    {
        "name": "Backyard Folklore",
        "mood": "warm, sun-bleached comic panels, hand-inked linework, "
        "colors like old zinc-roof houses and mango season",
    },
    {
        "name": "Midnight Moonshine",
        "mood": "moody indigo-and-lantern-gold palette, high-contrast night "
        "scenes, the visual register of a story told on a porch after dark",
    },
    {
        "name": "Carnival Bright",
        "mood": "saturated, kinetic, mas-costume colors and movement lines, "
        "loud and joyful panel composition",
    },
]

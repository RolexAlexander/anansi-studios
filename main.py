"""Anansi Studios -- CLI entrypoint.

Runs one full pass through the studio pipeline: write -> critique loop ->
theme -> extract -> compose (Imagen panels) -> Parallel-grounded greenlight
decision.

Usage:
    python main.py "Anansi tricks the wind spirit into a race, comedic"
"""

import asyncio
import sys

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from studio.agents import root_agent
from studio.config import MOCK, GOOGLE_API_KEY, PARALLEL_API_KEY

APP_NAME = "anansi_studio"
USER_ID = "founder"
SESSION_ID = "run-1"


async def run(genre_seed: str) -> None:
    if not MOCK:
        missing = [
            name
            for name, val in [("GOOGLE_API_KEY", GOOGLE_API_KEY), ("PARALLEL_API_KEY", PARALLEL_API_KEY)]
            if not val
        ]
        if missing:
            print(
                f"[warning] Missing: {', '.join(missing)}. "
                "Those tool calls will fall back to mock output. "
                "Set STUDIO_MOCK=1 to silence this and run a pure structural dry run.\n"
            )

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={
            "genre_seed": genre_seed,
            "critic_feedback": "none yet -- this is the first draft.",
        },
    )

    runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)

    message = types.Content(role="user", parts=[types.Part(text=genre_seed)])

    print(f"\n=== Anansi Studios: producing a comic from seed: {genre_seed!r} ===\n")

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        author = getattr(event, "author", "?")
        if event.is_final_response() and event.content and event.content.parts:
            text = "".join(p.text or "" for p in event.content.parts)
            if text.strip():
                print(f"--- [{author}] ---\n{text.strip()}\n")

    final_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    state = final_session.state

    print("\n=== FINAL STATE SUMMARY ===")
    print(f"Theme chosen: {state.get('theme_choice', 'MISSING')}\n")
    print(f"Panels manifest:\n{state.get('panels_manifest', 'MISSING')}\n")
    print(f"Greenlight decision:\n{state.get('greenlight_decision', 'MISSING')}\n")


if __name__ == "__main__":
    seed = " ".join(sys.argv[1:]) or "Anansi tricks the wind spirit into a race, comedic"
    asyncio.run(run(seed))

#!/usr/bin/env python3
"""
Copilot SDK — one-shot prompt (ILLUSTRATIVE).

The docs (get-started/sdk-quickstart, verified 2026-10-17) describe the flow
    new CopilotClient() -> createSession({model: "auto"}) -> sendAndWait({prompt})
for npm `@github/copilot-sdk`, and name the Python package `github-copilot-sdk` (`from copilot import CopilotClient`).
The exact Python method names and signatures below are UNVERIFIED — check the SDK README before relying on them.
Programmatic hooks (e.g. onPreToolUse returning permissionDecision) exist per the SDK hooks docs.

    pip install github-copilot-sdk
    python sdk_example.py "Summarise README.md in three bullets"
"""
import asyncio
import sys

from copilot import CopilotClient  # package: github-copilot-sdk


async def main(prompt: str) -> None:
    client = CopilotClient()
    # Mirrors createSession({model: "auto"}) / sendAndWait({prompt}); snake_case names are an assumption.
    session = await client.create_session({"model": "auto"})
    reply = await session.send_and_wait({"prompt": prompt})
    print(reply)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "Say hello in one sentence."))

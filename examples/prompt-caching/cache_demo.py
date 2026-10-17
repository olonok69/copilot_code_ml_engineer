#!/usr/bin/env python3
"""
Minimal prompt-caching demo against the Anthropic API.

Makes TWO calls with the same long system prompt (stable, with cache_control) and a different
question (variable, outside the cache). Call 1 WRITES the cache; call 2 READS it.

    pip install anthropic python-dotenv   # dotenv optional
    export ANTHROPIC_API_KEY=sk-ant-...   # or a .env at the course root
    python cache_demo.py

Expected output (indicative numbers):
    Call 1: cache_creation=~2100  cache_read=0      input=12
    Call 2: cache_creation=0      cache_read=~2100  input=11
    -> call 2 processed the prefix at 0.1x the input price.

GitHub Copilot does NOT expose `cache_control` (or any caching setting) in the CLI, VS Code or the cloud
agent. This demo talks to the Anthropic API directly to teach the MECHANISM that runs underneath —
the one the Copilot pricing tables bill as "cached input" and "cache write".
"""
import os
import anthropic

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # optional; exporting ANTHROPIC_API_KEY is enough

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY

# --- STABLE prefix: long instructions (>1024 tokens to be cacheable). ---
# In an agent (Copilot / Cursor / Claude Code) this role is played by system + tools + AGENTS.md etc.
STABLE_SYSTEM = (
    "You are a senior code reviewer on a platform team. Follow these conventions:\n"
    + "\n".join(
        f"{i}. Style rule number {i}: domain {i} modules expose a single facade; importing their "
        f"internals is forbidden; errors propagate typed and logs carry no PII."
        for i in range(1, 61)
    )
)

MODEL = os.environ.get("CACHE_DEMO_MODEL", "claude-sonnet-4-5")  # override with any current model id


def ask(question: str) -> None:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": STABLE_SYSTEM,
                # the breakpoint goes AT THE END of the stable block:
                "cache_control": {"type": "ephemeral"},  # 5 min TTL (use {"ttl": "1h"} for one hour)
            }
        ],
        # the variable part (the question) goes AFTER the breakpoint -> does not invalidate the cache
        messages=[{"role": "user", "content": question}],
    )
    u = resp.usage
    print(
        f"cache_creation={getattr(u, 'cache_creation_input_tokens', 0):>6}  "
        f"cache_read={getattr(u, 'cache_read_input_tokens', 0):>6}  "
        f"input={u.input_tokens:>4}  output={u.output_tokens:>4}"
    )


if __name__ == "__main__":
    print("Call 1 (writes the cache):")
    ask("May a domain-3 module import domain-7 internals? Answer in one sentence.")
    print("Call 2 (reads the cache):")
    ask("May logs carry the user's email? Answer in one sentence.")

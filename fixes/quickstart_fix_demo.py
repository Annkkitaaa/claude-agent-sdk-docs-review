"""Proof for fix 3: the quickstart's result line reports success on a failed run.

Runs with a deliberately invalid ANTHROPIC_API_KEY and prints, side by side:

  docs line  ->  print(f"Done: {message.subtype}")
  fixed line ->  print(f"Done: {'error' if message.is_error else message.subtype}")

It also shows that AssistantMessage.error carries the structured reason, which the
quickstart's hasattr(block, "text") branch renders as if it were Claude's reasoning.

Run:
    python quickstart_fix_demo.py
"""

import asyncio
import os

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    query,
)

os.environ["ANTHROPIC_API_KEY"] = "sk-ant-deliberately-invalid-for-this-demo"


async def main():
    try:
        async for message in query(
            prompt="Reply with exactly: OK",
            options=ClaudeAgentOptions(tools=[], permission_mode="default"),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text") and block.text:
                        # What the quickstart prints: indistinguishable from reasoning.
                        print(f"  [docs  ] {block.text}")
                # The structured signal the quickstart ignores.
                if getattr(message, "error", None):
                    print(f"  [fixed ] AssistantMessage.error={message.error!r}")

            elif isinstance(message, ResultMessage):
                print(f"  [docs  ] Done: {message.subtype}")
                fixed = "error" if message.is_error else message.subtype
                print(f"  [fixed ] Done: {fixed}")
                print(f"  (raw: subtype={message.subtype!r} is_error={message.is_error!r})")
    except Exception as exc:
        print(f"  then raises: {type(exc).__name__}: {exc}")


asyncio.run(main())

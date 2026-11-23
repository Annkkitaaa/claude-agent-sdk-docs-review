import asyncio
import os

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


async def main():
    print(f"env key present: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")
    try:
        async for message in query(
            prompt="Reply with exactly: OK",
            options=ClaudeAgentOptions(tools=[], permission_mode="default"),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        print(f"TEXT: {block.text!r}")
            elif isinstance(message, ResultMessage):
                print(f"RESULT subtype: {message.subtype}")
    except Exception as exc:
        print(f"EXCEPTION {type(exc).__name__}: {exc}")


asyncio.run(main())

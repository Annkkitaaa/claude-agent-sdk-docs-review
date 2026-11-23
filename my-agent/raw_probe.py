import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    try:
        async for message in query(
            prompt="Reply with exactly: OK",
            options=ClaudeAgentOptions(tools=[], permission_mode="default"),
        ):
            print(f"--- {type(message).__name__}")
            print(f"    {message!r}"[:600])
    except Exception as exc:
        print(f"EXCEPTION {type(exc).__name__}: {exc}")


asyncio.run(main())

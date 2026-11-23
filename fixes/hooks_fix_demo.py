"""Proof for fixes 1 and 2: the hooks.md .env example, broken vs fixed.

Both phases run with permission_mode="acceptEdits" and Write pre-approved, so the
permission mode cannot block the write. The hook is the only thing that can. That
isolation is fix 2; without it the demo passes either way.

  phase "broken" -> docs logic, file_path.split("/")[-1]  -> .env IS written
  phase "fixed"  -> os.path.basename(file_path)           -> .env is BLOCKED

Run both:
    python hooks_fix_demo.py broken
    python hooks_fix_demo.py fixed
"""

import asyncio
import os
import sys

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    ResultMessage,
)

PROMPT = "Create a .env file in this directory with DB_HOST=localhost in it."
TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

DENY = {
    "permissionDecision": "deny",
    "permissionDecisionReason": "Cannot modify .env files",
}


def make_hook(mode: str):
    async def protect_env_files(input_data, tool_use_id, context):
        raw = input_data["tool_input"].get("file_path", "")

        if mode == "broken":
            # Verbatim from hooks.md.
            file_name = raw.split("/")[-1]
        else:
            # Fix 1.
            file_name = os.path.basename(raw)

        matched = file_name.lower() == ".env"
        print(f"  hook: file_path={raw!r}")
        print(f"  hook: derived file_name={file_name!r}  matched={matched}")

        if matched:
            print("  hook: -> DENY")
            return {
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    **DENY,
                }
            }

        print("  hook: -> {} (no opinion, write proceeds)")
        return {}

    return protect_env_files


async def run(mode: str):
    if os.path.exists(TARGET):
        os.remove(TARGET)

    options = ClaudeAgentOptions(
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Write|Edit", hooks=[make_hook(mode)])
            ]
        },
        # Fix 2: isolate the hook as the only possible blocker.
        allowed_tools=["Read", "Write", "Edit", "Glob"],
        permission_mode="acceptEdits",
    )

    print(f"=== phase={mode} | .env before: {os.path.exists(TARGET)} ===")
    async with ClaudeSDKClient(options=options) as client:
        await client.query(PROMPT)
        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                print(f"  denials={message.permission_denials!r}")

    written = os.path.exists(TARGET)
    print(f"=== phase={mode} | .env after: {written} ===")
    expected = mode == "broken"
    verdict = "as expected" if written == expected else "UNEXPECTED"
    print(f"=== {verdict}: protection {'failed open' if written else 'held'} ===\n")

    if os.path.exists(TARGET):
        os.remove(TARGET)


asyncio.run(run(sys.argv[1] if len(sys.argv) > 1 else "fixed"))

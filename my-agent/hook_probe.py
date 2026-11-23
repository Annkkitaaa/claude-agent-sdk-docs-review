"""Isolate whether the docs' PreToolUse hook actually fires and denies.

Phase "withhook": docs' hook logic + permission_mode="acceptEdits" so that a
permission-mode denial cannot be confused with a hook denial.
Phase "nohook":   identical options, hook removed. Control.
"""

import asyncio
import os
import sys

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
)

PROMPT = "Create a .env file in this directory with DB_HOST=localhost in it."
TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


async def protect_env_files(input_data, tool_use_id, context):
    # Instrumentation only — the matching logic below is the docs' verbatim logic.
    raw = input_data["tool_input"].get("file_path", "")
    print(f"  [HOOK FIRED] tool={input_data.get('tool_name')!r}")
    print(f"  [HOOK FIRED] raw file_path={raw!r}")

    file_path = raw
    file_name = file_path.split("/")[-1]
    print(f"  [HOOK FIRED] docs split('/')[-1] -> {file_name!r}")
    print(f"  [HOOK FIRED] os.path.basename  -> {os.path.basename(raw)!r}")

    if file_name.lower() == ".env":
        print("  [HOOK FIRED] decision=DENY")
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Cannot modify .env files",
            }
        }

    print("  [HOOK FIRED] decision={} (no opinion)")
    return {}


async def run(phase: str):
    hooks = (
        {"PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])]}
        if phase == "withhook"
        else {}
    )
    options = ClaudeAgentOptions(
        hooks=hooks,
        allowed_tools=["Read", "Write", "Edit", "Glob"],
        permission_mode="acceptEdits",
    )

    if os.path.exists(TARGET):
        os.remove(TARGET)

    print(f"=== phase={phase} | .env before: {os.path.exists(TARGET)} ===")
    async with ClaudeSDKClient(options=options) as client:
        await client.query(PROMPT)
        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                print(f"  subtype={message.subtype!r} is_error={message.is_error!r}")
                print(f"  permission_denials={message.permission_denials!r}")
    print(f"=== phase={phase} | .env after:  {os.path.exists(TARGET)} ===\n")


asyncio.run(run(sys.argv[1]))

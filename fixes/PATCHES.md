# Proposed doc patches, implemented and verified

The three fixes from the [review](../README.md), written as the exact edits I'd make, each
with a runnable proof.

**Why these are patches and not a pull request.** The affected pages live at
`code.claude.com` and are not in any public repository. I checked: no public docs repo
exists (`anthropics/claude-docs`, `claude-code-docs` and similar all 404), the example's
distinctive string `"Cannot modify .env files"` returns **0 results** across the whole
`anthropics` org, and the SDK repo's own examples don't carry the bugs —
`examples/hooks.py` uses a substring check (`if "important" in file_path`) rather than a
basename split, and `examples/quick_start.py` never prints `subtype`. There is no file
upstream that these edits would change, so there is nothing to open a PR against. They are
filed as issues instead:

- [claude-agent-sdk-python#1574](https://github.com/anthropics/claude-agent-sdk-python/issues/1574)
  — fixes 1 and 2
- [claude-agent-sdk-python#1575](https://github.com/anthropics/claude-agent-sdk-python/issues/1575)
  — fix 3

---

## Fix 1 — `hooks.md`: derive the filename with a platform-aware basename

Python tab:

```diff
 async def protect_env_files(input_data, tool_use_id, context):
     file_path = input_data["tool_input"].get("file_path", "")
-    file_name = file_path.split("/")[-1]
+    file_name = os.path.basename(file_path)
```

TypeScript tab, same defect:

```diff
   const filePath = toolInput?.file_path as string;
-  const fileName = filePath?.split("/").pop();
+  const fileName = filePath ? basename(filePath) : undefined;
```

...with `import { basename } from "node:path";` added, and `import os` in the Python tab.

**Verified** — `hooks_fix_demo.py`, identical conditions, only the derivation changed:

```
=== phase=broken | .env before: False ===
  hook: file_path='D:\agent-sdk-doc\fixes\.env'
  hook: derived file_name='D:\agent-sdk-doc\fixes\.env'  matched=False
  hook: -> {} (no opinion, write proceeds)
=== phase=broken | .env after: True ===
=== as expected: protection failed open ===

=== phase=fixed | .env before: False ===
  hook: file_path='D:\agent-sdk-doc\fixes\.env'
  hook: derived file_name='.env'  matched=True
  hook: -> DENY
=== phase=fixed | .env after: False ===
=== as expected: protection held ===
```

In the fixed phase the `Write` denial also shows up in
`ResultMessage.permission_denials`, which it does not in the broken phase.

## Fix 2 — `hooks.md`: isolate the hook in that example

```diff
 async def main():
     options = ClaudeAgentOptions(
         hooks={
             "PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])]
-        }
+        },
+        allowed_tools=["Read", "Write", "Edit", "Glob"],
+        permission_mode="acceptEdits",
     )
```

As published the example sets no `permission_mode`, so it runs in `default`. In a
non-interactive script the `Write` is blocked by the permission mode regardless, `.env`
never appears, and the example looks correct whether or not the hook does anything. That
is what hid fix 1. Both phases above set `acceptEdits` precisely so the hook is the only
possible blocker.

## Fix 3 — `quickstart.md`: don't report success on a failed run

```diff
         elif isinstance(message, ResultMessage):
-            print(f"Done: {message.subtype}")  # Final result
+            print(f"Done: {'error' if message.is_error else message.subtype}")
```

And in Setup step 3, after the `export ANTHROPIC_API_KEY=...` block:

> If Claude Code is installed and logged in, the SDK uses those credentials when
> `ANTHROPIC_API_KEY` is unset. Environments without them, such as CI or Docker, require
> the key.

**Verified** — `quickstart_fix_demo.py` with a deliberately invalid key:

```
  [docs  ] Invalid API key · Fix external API key
  [fixed ] AssistantMessage.error='authentication_failed'
  [docs  ] Done: success
  [fixed ] Done: error
  (raw: subtype='success' is_error=True)
  then raises: ResultError: Claude Code returned an error result: Invalid API key (exit code: 1)
```

`subtype` is `'success'` while `is_error` is `True`, so the published line prints
`Done: success` on an authentication failure. The first line also shows the auth error
arriving as a `TextBlock`, which the quickstart's `hasattr(block, "text")` branch prints as
though it were Claude's reasoning; `AssistantMessage.error` carries the structured reason.

---

## Running these

```powershell
cd fixes
..\my-agent\.venv\Scripts\Activate.ps1
python hooks_fix_demo.py broken     # .env IS written  -> protection failed open
python hooks_fix_demo.py fixed      # .env is blocked  -> protection held
python quickstart_fix_demo.py       # Done: success vs Done: error
```

Fix 1 is Windows-specific; `split("/")` is correct on POSIX paths. Fixes 2 and 3 apply on
every platform.

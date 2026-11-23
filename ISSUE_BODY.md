The lead `PreToolUse` example on the hooks page silently fails to block on Windows, in
both the Python and TypeScript tabs. The hook runs, declines to deny, and the `.env` file
it is supposed to protect gets written. There is no error or warning.

Docs page: https://code.claude.com/docs/en/agent-sdk/hooks (section "How hooks work")

## Cause

Both tabs derive the filename by splitting on a forward slash only:

```python
# Python tab
file_name = file_path.split("/")[-1]
```

```typescript
// TypeScript tab
const fileName = filePath?.split("/").pop();
```

On Windows the hook receives a backslash path, so neither split separates anything and
`file_name` is the entire path. The `== ".env"` comparison is therefore `False`, the hook
returns `{}` ("no decision, normal permissions apply"), and the write proceeds.

## Reproduction

Keeping the docs' matching logic byte-for-byte and adding only print statements, plus
`permission_mode="acceptEdits"` and `allowed_tools` so that a permission-mode denial cannot
be mistaken for a hook denial:

```
=== phase=withhook | .env before: False ===
  [HOOK FIRED] tool='Write'
  [HOOK FIRED] raw file_path='D:\agent-sdk-doc\my-agent\.env'
  [HOOK FIRED] docs split('/')[-1] -> 'D:\agent-sdk-doc\my-agent\.env'
  [HOOK FIRED] os.path.basename  -> '.env'
  [HOOK FIRED] decision={} (no opinion)
  subtype='success' is_error=False
  permission_denials=[]
=== phase=withhook | .env after:  True ===

################ CONTROL (hook removed) ################
=== phase=nohook | .env before: False ===
  subtype='success' is_error=False
  permission_denials=[]
=== phase=nohook | .env after:  True ===
```

The outcome with the hook registered is identical to the control with no hook at all.

Full script and transcripts:
https://github.com/Annkkitaaa/claude-agent-sdk-docs-review

## Why this is easy to miss

Run exactly as published, the example sets no `permission_mode`, so it runs in `default`.
In a non-interactive script the `Write` is blocked by the permission mode regardless, no
`.env` appears, and the example looks like it worked. The deny reason the hook is supposed
to supply (`"Cannot modify .env files"`) never appears in the output, and
`ResultMessage.permission_denials` records that a call was denied but not which hook or
reason denied it — so there is no signal distinguishing "the hook blocked it" from "the
permission mode blocked it".

That matters more than the typo, because the example is presented under "Block dangerous
operations before they execute". Anyone adapting it as a security control on Windows gets a
hook that passes its own demo while enforcing nothing.

## Suggested fix

Use the platform-aware basename in both tabs:

```python
import os
file_name = os.path.basename(file_path)
```

```typescript
import { basename } from "node:path";
const fileName = filePath ? basename(filePath) : undefined;
```

A real `.env` guard probably also wants to match any path *ending* in `.env` rather than an
exact filename, but the basename change alone fixes the reported failure.

Separately, consider setting `permission_mode="acceptEdits"` in that example so the hook is
the only thing that can block the write. As written, the demo passes whether or not the
hook works, which is what hid this.

## Minor, same example

The two tabs use different entry points for identical behaviour — the Python tab uses
`ClaudeSDKClient`, the TypeScript tab uses `query()` — with no note on why. Readers coming
from the quickstart, which uses `query()`, hit the switch without explanation.

## Environment

- Windows 11, PowerShell
- Python 3.12.6
- `claude-agent-sdk` 0.2.187 (`claude_agent_sdk-0.2.187-py3-none-win_amd64.whl`)
- Docs reviewed 23 November 2026

# 4. Hooks — the feature past the quickstart

The quickstart links hooks under *Next steps* but never walks through them. The hooks page
leads with a `PreToolUse` example that blocks writes to `.env` files, presented under
"Block dangerous operations before they execute".

Two things to note before the result. The hooks page silently switches entry point from the
quickstart's `query()` to `ClaudeSDKClient`, with no explanation of why or when that matters.
And its example sets no `allowed_tools` and no `permission_mode`, so it runs in `default`.

## Run 1 — docs example, verbatim

[`../my-agent/hook_env.py`](../my-agent/hook_env.py), copied from the docs unchanged.

Result: no `.env` created. `permission_denials` shows the Write was blocked:

```
permission_denials=[{'tool_name': 'Write',
  'tool_use_id': 'toolu_01Sh4a3N8NnH5QJevwPrYbK3',
  'tool_input': {'file_path': 'D:\\agent-sdk-doc\\my-agent\\.env', ...}}]
```

Looks like a pass. But the deny reason the hook is supposed to supply —
`"Cannot modify .env files"` — appears nowhere in the output, and the model's own summary
attributes the block to permissions, not to the hook:

```
I couldn't create the `.env` file because the write needs your permission and it wasn't
granted. This session can't ask you interactively, so I stopped there rather than trying
another way around it.
```

`permission_denials` records *that* a call was denied, never *which* hook or reason denied
it. So this run cannot distinguish "the hook worked" from "the permission mode blocked it".

Cost of this single run: `total_cost_usd=0.22603079999999998`.

## Run 2 — isolated, with a control

[`../my-agent/hook_probe.py`](../my-agent/hook_probe.py) keeps the docs' matching logic
byte-for-byte, adds prints, and sets `permission_mode="acceptEdits"` plus
`allowed_tools=["Read", "Write", "Edit", "Glob"]` so that a permission-mode denial cannot
be mistaken for a hook denial.

```
=== phase=withhook | .env before: False ===
  [HOOK FIRED] tool='Write'
  [HOOK FIRED] raw file_path='D:\\agent-sdk-doc\\my-agent\\.env'
  [HOOK FIRED] docs split('/')[-1] -> 'D:\\agent-sdk-doc\\my-agent\\.env'
  [HOOK FIRED] os.path.basename  -> '.env'
  [HOOK FIRED] decision={} (no opinion)
  subtype='success' is_error=False
  permission_denials=[]
=== phase=withhook | .env after:  True ===

################ CONTROL ################
=== phase=nohook | .env before: False ===
  subtype='success' is_error=False
  permission_denials=[]
=== phase=nohook | .env after:  True ===
```

## Conclusion

The hook fires. It receives a Windows path with backslashes. The docs'
`file_path.split("/")[-1]` does not split a backslash path, so `file_name` is the whole
path, `file_name.lower() == ".env"` is `False`, the hook returns `{}` — "no opinion" — and
`.env` is written. The outcome is identical to the no-hook control.

It **fails open**: no error, no warning, the protection silently does not apply.
`os.path.basename()` returns `.env` correctly, as the instrumented line shows.

The reason this is easy to miss is Run 1. With the docs' own `permission_mode="default"`
in a non-interactive script, the write is blocked regardless, `.env` never appears, and the
example looks correct. The demo passes whether or not the hook does anything.

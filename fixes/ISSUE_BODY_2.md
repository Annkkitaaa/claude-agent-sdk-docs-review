Two problems in the quickstart's worked example, both visible on a failed run.

Docs page: https://code.claude.com/docs/en/agent-sdk/quickstart

## 1. The example reports `Done: success` when the run failed

`ResultMessage` carries `subtype='success'` alongside `is_error=True` on an authentication
failure. The quickstart's final line reads the first field:

```python
elif isinstance(message, ResultMessage):
    print(f"Done: {message.subtype}")  # Final result
```

Observed with a deliberately invalid `ANTHROPIC_API_KEY`:

```
  [docs  ] Done: success
  [fixed ] Done: error
  (raw: subtype='success' is_error=True)
  then raises: ResultError: Claude Code returned an error result: Invalid API key (exit code: 1)
```

Suggested fix:

```diff
-            print(f"Done: {message.subtype}")  # Final result
+            print(f"Done: {'error' if message.is_error else message.subtype}")
```

Anyone who copies the example as a starting point inherits a success report on failure. If
`subtype` is meant to stay `'success'` here, then `is_error` is the field the example should
be reading.

## 2. The auth error renders as Claude's reasoning

On the same run, the error arrives as a `TextBlock`, so the example's print loop treats it
as model output:

```
  [docs  ] Invalid API key · Fix external API key
```

`AssistantMessage.error` carries the structured reason (`'authentication_failed'`) and the
example doesn't look at it. Worth either checking it in the sample or noting that a terminal
error surfaces as text.

## 3. Setup step 3 doesn't mention the local-credentials fallback

Following the quickstart without ever setting `ANTHROPIC_API_KEY`, the run succeeded and
printed `Done: success`. The bundled binary fell back to `~/.claude/.credentials.json` — the
local Claude Code login. The overview page separately states that Anthropic does not permit
claude.ai login for agents built on the SDK, so the documented default path and the stated
policy point in different directions, and the same script fails in CI or a container where
`~/.claude` doesn't exist.

Suggested addition after the `export ANTHROPIC_API_KEY=...` block in Setup step 3:

> If Claude Code is installed and logged in, the SDK uses those credentials when
> `ANTHROPIC_API_KEY` is unset. Environments without them, such as CI or Docker, require the
> key.

## Reproduction

Runnable proof for all three, with the before/after output quoted above:
https://github.com/Annkkitaaa/claude-agent-sdk-docs-review/blob/main/fixes/PATCHES.md

## Environment

- Windows 11, PowerShell
- Python 3.12.6
- `claude-agent-sdk` 0.2.187 (`claude_agent_sdk-0.2.187-py3-none-win_amd64.whl`)
- Docs reviewed 23 November 2026

Related: #1574 covers two defects in the hooks page example.

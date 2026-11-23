# 3. Auth resolution probe

The quickstart run succeeded with `ANTHROPIC_API_KEY` unset. This establishes why, and
what a genuine auth failure actually looks like in the message stream.

Script: [`../my-agent/auth_probe.py`](../my-agent/auth_probe.py).

## A — no key

```
env key present: False
TEXT: 'OK'
RESULT subtype: success
```

## B — deliberately invalid key

```
⚠ claude.ai connectors are disabled because ANTHROPIC_API_KEY or another auth source is
  set and takes precedence over your claude.ai login · Unset it to load your
  organization's connectors
env key present: True
TEXT: 'Invalid API key · Fix external API key'
RESULT subtype: success
EXCEPTION ResultError: Claude Code returned an error result: Invalid API key · Fix
external API key (exit code: 1)
```

## Where the credential comes from

```
C:\Users\Ankita Singh\.claude\.credentials.json exists: True
claude: C:\Users\Ankita Singh\AppData\Roaming\npm\claude.ps1
ant: not installed
```

So with no env var, the bundled binary used the local Claude Code OAuth login. The
quickstart presents Setup step 3 as a required step; on any machine with Claude Code
installed and logged in, it is optional. The overview page separately states that Anthropic
does not permit claude.ai login for agents built on the SDK — so the default local path and
the stated policy disagree. In CI or a container with no `~/.claude`, the same script fails.

## `subtype='success'` on a failed run

Raw stream from [`../my-agent/raw_probe.py`](../my-agent/raw_probe.py), bogus key:

```
--- SystemMessage
    SystemMessage(subtype='init', data={... 'model': 'claude-opus-5-5',
    'permissionMode': 'default', ...})
--- AssistantMessage
    AssistantMessage(content=[TextBlock(text='Invalid API key · Fix external API key')],
    model='<synthetic>', error='authentication_failed', ...)
--- ResultMessage
    ResultMessage(subtype='success', duration_ms=662, duration_api_ms=0, is_error=True,
    num_turns=1, stop_reason='stop_sequence', total_cost_usd=0, ...)
EXCEPTION ResultError: Claude Code returned an error result: Invalid API key · Fix
external API key (exit code: 1)
```

Two problems for the quickstart's sample code:

- `subtype='success'` while `is_error=True`. The quickstart prints
  `f"Done: {message.subtype}"`, so a failed run reports `Done: success`.
- The auth error arrives as a `TextBlock`. The quickstart's `hasattr(block, "text")` branch
  prints it as if it were Claude's reasoning. The structured discriminator
  (`error='authentication_failed'`) is present and ignored.

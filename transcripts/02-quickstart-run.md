# 2. Quickstart run

`utils.py` and `agent.py` were created verbatim from the quickstart. `utils.py` started as:

```python
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


def get_user_name(user):
    return user["name"].upper()
```

Run deliberately made **without** setting `ANTHROPIC_API_KEY`, to see what a reader who
skims past Setup step 3 actually gets.

```
ANTHROPIC_API_KEY set: False
=== RUN 14:00:49 ===
Tool: Read
Tool: Write
Tool: Bash
I found two crash bugs in `utils.py` and fixed both. I couldn't run a quick test because
the command needed approval, so the fixes haven't been run yet.
...
**A trade-off to decide on:** returning `0` and `""` stops the crashes, but it also hides
bad input. An average of `0` for an empty list could be confused with a real result. If
you'd rather callers hear about bad data, I can change these to raise a clear `ValueError`
instead, or return `None`.
Done: success
=== exit=0  14:01:13 ===
```

24 seconds. `utils.py` afterwards — the fix is correct and matches the docs' claim about
"defensive code handling empty lists and null users":

```python
def calculate_average(numbers):
    if not numbers:
        return 0
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


def get_user_name(user):
    if not user:
        return ""
    name = user.get("name")
    if not name:
        return ""
    return str(name).upper()
```

## Findings

**1. Succeeded with no API key.** See [03-auth-probe.md](03-auth-probe.md).

**2. `allowed_tools` pre-approves, it does not restrict.** `agent.py` passes
`allowed_tools=["Read", "Edit", "Glob"]`. The run called `Write` and `Bash` — neither
listed — and used `Write` rather than the `Edit` the docs predict. The docs do explain
this, in *Key concepts*, below the code sample that already relies on it.

**3. A denied tool call has no programmatic signal in this example.** `Bash` was blocked.
The only evidence in stdout is the model saying so in prose: *"I couldn't run a quick test
because the command needed approval."* `ResultMessage.permission_denials` carries this
structurally, but the quickstart's print loop never looks at it.

**4. The agent is not hermetic.** The init message shows it loaded this machine's personal
Claude Code configuration — slash commands that belong to my local setup, not to the
project:

```
SystemMessage(subtype='init', data={... 'slash_commands': ['deep-research', 'design',
'design-sync', 'dataviz', 'update-config', 'verify', 'debug', 'code-review', 'simplify',
'batch', 'fewer-permission-prompts', 'doctor', 'loop', 'claude-api', 'workflow-authoring',
'run', ...]})
```

That is `setting_sources` behaviour, on by default for `query()`. The hooks page mentions
it in passing; the quickstart never does. It means the same script can behave differently
on two machines.

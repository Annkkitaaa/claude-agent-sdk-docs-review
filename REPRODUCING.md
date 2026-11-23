# Reproducing these findings

Windows 11, PowerShell, Python 3.12.6, `claude-agent-sdk` 0.2.187.

`my-agent/utils.py` in this repo is the agent's **fixed** output from the recorded run, so
reset it to the docs' original before reproducing the quickstart. `utils.buggy.py` is that
original, byte-verbatim from `quickstart.md`.

```powershell
cd my-agent
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install claude-agent-sdk

Copy-Item utils.buggy.py utils.py -Force   # reset the quickstart's input
python agent.py                  # quickstart
python hook_env.py               # hooks example, verbatim from docs
python hook_probe.py withhook    # hook fires, returns {}, .env is written
python hook_probe.py nohook      # control: identical result
```

On macOS or Linux: `python3 -m venv .venv`, `source .venv/bin/activate`, and `cp` instead
of `Copy-Item`.

## Platform scope of each finding

| Finding | Scope |
| - | - |
| Hooks example fails open (`split("/")` on a backslash path) | **Windows only.** `split("/")` is correct on POSIX paths. |
| Hooks example unfalsifiable (`permission_mode="default"` masks it) | Any platform, any non-interactive run. |
| `subtype='success'` with `is_error=True` | Any platform. |
| Auth falls back to `~/.claude/.credentials.json` | Any machine with Claude Code installed and logged in. Fails in CI/containers without it. |
| `allowed_tools` pre-approves rather than restricts | Any platform. |

## A note on the auth finding

The no-API-key success happens **because** Claude Code is installed and logged in on this
machine (`~/.claude/.credentials.json` is present). On a clean machine, Setup step 3 is
genuinely required. The finding is that the docs don't say which situation you're in, not
that the key is never needed.

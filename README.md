# Claude Agent SDK: quickstart + hooks, on Windows

I ran the Agent SDK Python quickstart end to end, then tried hooks — a feature the
quickstart links to but never walks through. Windows 11, Python 3.12.6,
`claude-agent-sdk` 0.2.187. Everything here reproduces from [`my-agent/`](my-agent/);
verbatim terminal output is in [`transcripts/`](transcripts/).

## The quickstart works. Three things it tells you are wrong.

Install to working agent was three commands and about 60 seconds. The agent found both
bugs in `utils.py`, fixed them, and volunteered a trade-off I hadn't asked about:
returning `0` and `""` stops the crashes but hides bad input. That was better than I
expected. One thing nobody warns you about: the wheel is 170.1 MB.

**It ran without an API key.** Setup step 3 says to set `ANTHROPIC_API_KEY`. I didn't,
and still got `Done: success`. The bundled binary silently fell back to
`~/.claude/.credentials.json` — my Claude Code login. The overview page says Anthropic
doesn't permit claude.ai login for SDK apps. So the quickstart's happy path leans on auth
the overview forbids, and the same script dies in CI where `~/.claude` doesn't exist.

**`Done: success` prints on failure.** With a deliberately bogus key I got
`ResultMessage(subtype='success', ..., is_error=True)`. The quickstart's own final line is
`print(f"Done: {message.subtype}")`. It also pushes `Invalid API key · Fix external API key`
through the `hasattr(block, "text")` branch, so an auth error renders as Claude's
reasoning. `AssistantMessage.error='authentication_failed'` is sitting right there, unused.

**`allowed_tools` doesn't restrict anything.** My run listed `Read, Edit, Glob` and then
called `Write` and `Bash`. That behaviour is documented — in Key concepts, underneath the
code that already did it. `Bash` was denied, and the only trace was the model mentioning it
in prose.

## The hooks example is broken on Windows

Copied verbatim from the hooks page: block writes to `.env`. The hook fires, receives
`D:\agent-sdk-doc\my-agent\.env`, runs `file_path.split("/")[-1]`, and gets the entire path
back. The `== ".env"` comparison fails, the hook returns `{}`, and `.env` is written.
Byte-identical outcome to my no-hook control run.

The part that annoyed me is that you can't notice. As written the example uses
`permission_mode="default"`, which in a non-interactive script blocks the write anyway — so
`.env` never appears and the hook looks like it worked. I only caught it by switching to
`acceptEdits` and adding a control.

## Three fixes

1. **`hooks.md`** — replace `file_name = file_path.split("/")[-1]` with
   `file_name = os.path.basename(file_path)`. As written it fails open on every Windows path.
2. **`hooks.md`** — set `permission_mode="acceptEdits"` in that example so the hook is the
   only thing that can block the write. Otherwise the demo passes whether or not the hook
   works.
3. **`quickstart.md`** — make the result line
   `print(f"Done: {'error' if message.is_error else message.subtype}")`, and add to Setup
   step 3: *"If Claude Code is installed and logged in, the SDK uses those credentials when
   `ANTHROPIC_API_KEY` is unset. Environments without them, such as CI or Docker, require
   the key."*

## Reproducing

```bash
cd my-agent
py -m venv .venv && .venv\Scripts\Activate.ps1 && pip install claude-agent-sdk
python agent.py                  # quickstart
python hook_env.py               # hooks example, verbatim from docs
python hook_probe.py withhook    # hook fires, returns {}, .env is written
python hook_probe.py nohook      # control: identical result
```

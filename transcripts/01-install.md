# 1. Install

Windows 11, PowerShell. Python 3.12.6, pip 24.2. Followed the quickstart's
**Python (pip)** + **Windows** tabs verbatim.

```powershell
mkdir my-agent
cd my-agent
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install claude-agent-sdk
```

Start `13:59:05`, pip began `13:59:18`, finished `14:00:17`. Install itself ≈ 59s.

Platform wheel, not a source dist — so the bundled Claude Code binary was present and no
separate Claude Code install was needed:

```
Collecting claude-agent-sdk
  Downloading claude_agent_sdk-0.2.187-py3-none-win_amd64.whl.metadata (14 kB)
...
Downloading claude_agent_sdk-0.2.187-py3-none-win_amd64.whl (170.1 MB)
   ---------------------------------------- 170.1/170.1 MB 8.2 MB/s eta 0:00:00
```

31 packages total:

```
Successfully installed annotated-types-0.8.0 anyio-4.16.0 attrs-26.1.0 cffi-2.1.1
claude-agent-sdk-0.2.187 click-8.5.1 cryptography-50.0.2 h11-0.16.0 httpcore2-2.16.2
httpx2-2.16.2 idna-3.20 jsonschema-4.26.0 jsonschema-specifications-2025.9.1 mcp-2.3.0
mcp-types-2.3.0 opentelemetry-api-1.45.2 pycparser-3.12 pydantic-2.14.4
pydantic-core-2.50.5 pyjwt-2.15.1 python-multipart-0.0.34 pywin32-312 referencing-0.37.0
rpds-py-2026.9.1 sniffio-1.3.1 sse-starlette-3.7.1 starlette-1.10.0 truststore-0.10.5
typing-inspection-0.4.5 typing_extensions-4.16.0 uvicorn-0.54.0
```

**Note.** The 170 MB download is the bundled Claude Code binary. The docs mention the
bundling in a side note, but never the size — worth a line for anyone installing in a
container image or on metered bandwidth.

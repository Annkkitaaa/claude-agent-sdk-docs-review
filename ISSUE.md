# Upstream issue — filed

**[anthropics/claude-agent-sdk-python#1574](https://github.com/anthropics/claude-agent-sdk-python/issues/1574)**
— filed 23 November 2026, open.

> Docs: hooks.md PreToolUse .env example fails open on Windows (Python and TypeScript)

Covers finding 1 from the [review](README.md): the lead `PreToolUse` example on the hooks
page returns "no decision" on Windows because both language tabs split a filesystem path on
`/` only, so the `.env` file the example exists to protect gets written.

The body as submitted is [`ISSUE_BODY.md`](ISSUE_BODY.md). It includes the instrumented
reproduction, a no-hook control run proving the outcomes are identical, the one-line fix for
each language, and the reason the bug survived review — the example's own
`permission_mode="default"` blocks the write anyway, so the demo passes whether or not the
hook works.

Filed against the SDK repo because that is the channel the
[overview page](https://code.claude.com/docs/en/agent-sdk/overview) names for Python SDK
issues; there is no separate public docs repo for `code.claude.com`. A maintainer may
redirect it, which is fine — the report says plainly that it is a docs bug.

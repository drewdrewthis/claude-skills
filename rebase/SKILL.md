---
name: rebase
description: "Rebase current branch on origin/main. Use when the user says 'rebase', 'rebase main', 'update from main', 'sync with main', or before opening a PR."
user-invocable: true
---

# Rebase

Rebase the current branch on `origin/main`. Always fetches first — never rebases on stale local `main`.

```bash
git fetch origin && git rebase origin/main
```

If conflicts occur, report them and stop. Do not auto-resolve.

If rebase succeeds, run the project's build and test commands from CLAUDE.md. Report the result.

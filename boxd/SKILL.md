---
name: boxd
description: Manage Boxd VM lifecycle via ssh boxd.sh — list, stop, start, fork, destroy VMs, or fork from a golden source. Use when the user says "boxd", "list my vms", "stop boxd", "pause boxd", "wake up X", "fork from golden", "destroy vm", or asks about Boxd VM status. Does NOT launch Claude sessions (use /launch-remote for that).
user-invocable: true
argument-hint: "<subcommand> [args]"
---

# Boxd

Lifecycle management for Boxd VMs. The interface is `ssh boxd.sh '<cmd>'` — there's no local CLI or MCP. All commands accept `--json` for parseable output.

## Subcommands

| Command | Purpose |
|---------|---------|
| `list` / `status` | Show all VMs with status; flag failed/stopped |
| `stop <name>` | Pause a VM (reversible, preserves state) — **undocumented but works** |
| `stop-all [--keep <name1,name2>]` | Pause every running VM except keep-list |
| `start <name>` | Wake a stopped VM |
| `fork <source> [--name <new>]` | Copy an existing VM |
| `golden [--name <new>]` | Fork from the user's golden source VM (configured in `~/.config/boxd/golden`) |
| `destroy <name>` | Permanently delete — runs safety checks first |
| `reboot <name>` | Stop then start |
| `proxy <list\|new\|delete\|set-port>` | Manage subdomain proxies |

Pass-through: any other subcommand goes straight to `ssh boxd.sh '<cmd>'`.

## Behavior

### list / status
Run `ssh boxd.sh 'list'`. Format as a table. Call out:
- VMs with status `failed` (need cleanup)
- Count by status (running/stopped/failed)
- VMs that look stale (e.g. `pr<N>` or `issue<N>` where the PR/issue is closed — check via `gh`)

### stop <name>
`ssh boxd.sh 'stop <name>'`. Confirm the resulting status is `stopped`.

### stop-all
1. Run `list --json`, parse running VMs.
2. Subtract `--keep` names (default keep-list: empty).
3. **Show the user the list and ask for confirmation before stopping >1 VM** — bulk actions need an explicit yes.
4. Stop each. Report final state.

### start <name>
`ssh boxd.sh 'start <name>'` (also undocumented but works).

### fork <source> [--name <new>]
`ssh boxd.sh 'fork <source> --name <new>'`. If `--name` omitted, boxd defaults to `<source>-fork`.

### golden [--name <new>]
Convention: the user's "golden image" is whichever VM they keep nicely configured. The source is configured in `~/.config/boxd/golden` (a one-line file containing the VM name). If that file doesn't exist, ask the user which VM to use as their golden and offer to create the file.
1. Read golden source from `~/.config/boxd/golden`.
2. Verify it exists via `list --json`. If not, tell the user and stop.
3. `ssh boxd.sh 'fork <golden> --name <new>'`. If `--name` omitted, suggest a name based on the user's current branch or open issue, and confirm.

### destroy <name>
**Destructive — extra safety required.**
1. Run `ssh boxd.sh 'list --json'` to confirm the VM exists and capture its status.
2. **Heuristic checks** — if the name matches `issue<N>`, `pr<N>`, or contains a number, query `gh issue view <N> -R <owner>/<repo> --json state,title` and `gh pr view <N> -R <owner>/<repo> --json state,title` against the user's current project. If either is OPEN, warn the user.
3. **Always require explicit confirmation** before running `destroy -y`. Show what's being destroyed and any warnings. Wait for the user's "yes" before proceeding.
4. Run `ssh boxd.sh 'destroy <name> -y'`.

### Pass-through
For any subcommand not listed above (`new`, `exec`, `cp`, `connect`, `proxy ...`, `whoami`, `reboot`), forward to `ssh boxd.sh '<args>'` and report the output.

## Examples

- `/boxd list` — table of VMs, highlight failed/stale
- `/boxd stop feature-branch` — pause one VM
- `/boxd stop-all --keep my-main,my-worker` — end-of-day cleanup
- `/boxd start issue123` — wake up to resume work
- `/boxd golden --name issue456` — fork from golden source
- `/boxd destroy pr789` — destroy with safety checks

## Notes

- `stop` and `start` are undocumented in `ssh boxd.sh 'help'` but work. Don't be alarmed if they're missing from help output.
- Failed VMs (`failed` status) usually need `destroy` — they won't recover via `start`.
- Boxd is a private service; no public docs/MCP exist. The SSH shell IS the API.
- For *creating* per-issue Claude sessions, defer to `/launch-remote` — this skill is just lifecycle.

---
name: write-pr
description: "Create a PR with a filled-in template. Use when: 'write pr', 'create pr', 'open pr', 'make a pr', 'ship it', or after implementation is done and user wants to open a PR."
user-invocable: true
argument-hint: "[base-branch]"
---

# Write PR

Create a pull request by analyzing the branch's commits and diffs, filling in the repo's PR template, and opening via `gh pr create`.

## Steps

### 1. Pre-flight

```bash
BASE="${ARGUMENTS:-main}"
```

Check if a PR already exists:
```bash
gh pr view --json url,number --jq '{url, number}' 2>/dev/null
```
If it does, continue — steps 2-5 are the same. In step 6, use `gh pr edit` instead of `gh pr create`.

### 2. Gather context

Run in parallel:
```bash
git log --oneline "$BASE"..HEAD
git diff "$BASE"...HEAD --stat
git diff "$BASE"...HEAD
```

Read the full diff to understand the changes deeply — the PR body must reflect real understanding, not just commit message parroting.

### 3. Read the PR template

Look for `.github/PULL_REQUEST_TEMPLATE.md` in the repo root. If missing, read the bundled template at `docs/PR_TEMPLATE.md` (relative to this skill's directory).

### 4. Fill the template

For each section, follow the HTML comment hints in the template as writing guidance, then strip the comments from output. Key rules:

- **Why** — Link the issue (`Closes #N`). One paragraph on motivation. A reviewer unfamiliar with the issue should understand after reading this.
- **What changed** — Approach and decisions, not a line-by-line diff. Accessible to a non-technical teammate.
- **How it works** — Only include when the mechanism isn't obvious. Omit the section entirely for straightforward changes.
- **Test plan** — Specific scenarios tested. For bug fixes: name the regression test and confirm it fails without the fix.
- **Anything surprising?** — Omit entirely if nothing to flag. Otherwise: limitations, follow-ups, edge cases deliberately skipped.

### 5. Title

Conventional commits format, under 70 characters: `type: description`

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

### 6. Create or update

**New PR:**
```bash
gh pr create --base "$BASE" --title "<title>" --body "$(cat <<'EOF'
<filled template>
EOF
)"
```

**Existing PR:**
```bash
gh pr edit <number> --title "<title>" --body "$(cat <<'EOF'
<filled template>
EOF
)"
```

Print the PR URL.

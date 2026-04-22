---
name: slack-pr-request
description: "Post a PR review request to a team Slack channel. Use when a PR is ready for review, all checks pass, and it needs human eyes."
user-invocable: true
argument-hint: "[PR number or URL]"
---

# Slack PR Review Request

Post a PR review request to your team's Slack channel.

## Arguments

`$ARGUMENTS` — PR number, URL, or omit to detect from current branch.

## Setup

This skill reads a Slack bot token and target channel ID from files. Create them before first use:

```bash
mkdir -p ~/.config/slack-pr-request
echo "xoxb-your-bot-token" > ~/.config/slack-pr-request/token
echo "C01234567" > ~/.config/slack-pr-request/channel
chmod 600 ~/.config/slack-pr-request/*
```

The bot token needs the `chat:write` scope and must be invited to the channel.

## Steps

### Step 0: Track Progress

Before starting, create a task for each step below using TaskCreate. Chain sequential steps with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

### 1. Resolve PR

- If a number or URL is given, extract the PR number
- If omitted, detect from current branch: `gh pr list --head $(git branch --show-current) --json number --jq '.[0].number'`
- Fetch PR details: `gh pr view <N> -R <repo> --json title,url,number,headRefName,body,statusCheckRollup,isDraft`

### 2. Check readiness

- PR must be OPEN (not merged, not closed) — refuse to post for merged/closed PRs
- PR must NOT be a draft
- CI checks should be passing (warn if not, but still post if explicitly requested)

### 3. Generate summary

Read the PR body and generate a 1-2 sentence summary of what the PR does. Focus on the user-facing change, not implementation details.

### 4. Post to Slack

Read the token and channel from config:
```bash
SLACK_TOKEN=$(cat ~/.config/slack-pr-request/token)
SLACK_CHANNEL=$(cat ~/.config/slack-pr-request/channel)
```

Post using Block Kit:
```bash
curl -s -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "'$SLACK_CHANNEL'",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": ":mag: *PR Review Request*\n\n*<PR_URL|PR_TITLE (#N)>*\nBranch: `BRANCH`  |  CI: STATUS\n\nSUMMARY"
        }
      }
    ]
  }'
```

### 5. Confirm

Report success/failure. If Slack returns `ok: false`, show the error.

### Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Rules

- Keep the summary to 1-2 sentences max
- CI status: use checkmark for passing, X for failing, spinner for pending
- Never post draft PRs unless explicitly asked
- Don't include the full PR body — just the summary
- Do not use `<!here>` or `<!channel>` — post without broadcast pings

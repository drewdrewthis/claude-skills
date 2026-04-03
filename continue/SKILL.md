---
name: continue
description: "Find and resume a conversation from any project. Deep-searches session content, not just titles. Gathers context and continues the work."
user-invocable: true
argument-hint: "<what you were working on>"
---

# Continue

Find a prior conversation, gather its context, and continue it here.

## Steps

### 1. Understand what the user wants to continue

The `$ARGUMENTS` could be:
- A topic or description of work ("readme update", "auth refactor", "review plugin")
- A repo or project name ("my-app", "my-api")
- A session UUID or prefix
- Empty — show recent sessions

Extract the **intent**: what were they working on, what do they want to pick back up?

### 2. Deep search across all projects

Run ALL of these searches and merge results. Don't stop at the first method — the right session might only show up in one of them.

#### 2a. Search session indexes (fast, but incomplete)

```bash
python3 << 'PYEOF'
import json, os, glob, sys

search = os.environ.get("SEARCH", "").lower()
results = []

for index_path in glob.glob(os.path.expanduser("~/.claude/projects/*/sessions-index.json")):
    project_dir = os.path.dirname(index_path)
    project_name = os.path.basename(project_dir)
    try:
        data = json.load(open(index_path))
        entries = data.get("entries", data) if isinstance(data, dict) else data
        for entry in entries:
            text = f"{entry.get('summary', '')} {entry.get('firstPrompt', '')} {entry.get('sessionId', '')}".lower()
            if not search or search in text:
                results.append({
                    "sessionId": entry.get("sessionId"),
                    "summary": entry.get("summary", "(no summary)"),
                    "firstPrompt": entry.get("firstPrompt", "")[:120],
                    "modified": entry.get("modified", ""),
                    "messageCount": entry.get("messageCount", 0),
                    "project": project_name,
                })
    except Exception:
        continue

results.sort(key=lambda r: r.get("modified", ""), reverse=True)
for r in results[:10]:
    # Decode project directory path back to a human-readable form
    proj = r["project"].replace("-", "/").lstrip("/")
    print(f"{r['sessionId']}|{r['summary'][:80]}|{r['modified']}|{r['messageCount']}|{proj}")
PYEOF
```

#### 2b. Search project directory names

Project directories encode the working directory path. Search for keywords in directory names to find worktree-based sessions that may lack index entries.

```bash
find ~/.claude/projects/ -maxdepth 1 -type d -iname "*${KEYWORD}*" 2>/dev/null
```

For each matching directory, list its `.jsonl` files and peek at the first user message.

#### 2c. Deep content search (the critical one)

**This is what makes /continue actually work.** Search inside the actual JSONL session files for the user's keywords. Sessions about a topic often don't mention that topic in their summary or first prompt.

```bash
# Search ALL session JSONL files for the keyword
find ~/.claude/projects/ -name "*.jsonl" -not -path "*/subagents/*" \
  -exec grep -l -i "KEYWORD1" {} \; 2>/dev/null | \
  xargs grep -l -i "KEYWORD2" 2>/dev/null | head -20
```

Use multiple keywords from the user's query to narrow results. For each hit, extract context:

```python
# For each matching JSONL, extract: first user message, last few user messages, project name
import json, os, sys

jsonl_path = sys.argv[1]
session_id = os.path.basename(jsonl_path).replace(".jsonl", "")
project = os.path.basename(os.path.dirname(jsonl_path))

user_msgs = []
with open(jsonl_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if obj.get("type") == "user":
                content = obj.get("message", {}).get("content", "")
                text = ""
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            text = c["text"]
                            break
                else:
                    text = str(content)
                # Skip skill/command boilerplate
                if text.startswith("Base directory for this skill:") or text.startswith("<local-command"):
                    continue
                if len(text.strip()) > 10:
                    user_msgs.append(text[:200])
        except:
            pass

proj_short = project.replace("-", "/").lstrip("/")
print(f"Session: {session_id}")
print(f"Project: {proj_short}")
print(f"Messages: {len(user_msgs)}")
if user_msgs:
    print(f"First: {user_msgs[0][:150]}")
if len(user_msgs) > 1:
    print(f"Last:  {user_msgs[-1][:150]}")
```

### 3. Rank and present results

Merge results from all three searches. Deduplicate by session ID. Rank by:
1. **Relevance** — how closely the content matches what the user described
2. **Recency** — more recent sessions first (use file mtime if no modified date)
3. **Depth** — sessions with more messages are more likely to be the one

Present the top 3-5 candidates with enough context for the user to pick:
- Session ID
- What the session was about (from content, not just summary)
- Key topics discussed
- When it was last active
- Which project it belongs to

If one match is clearly the right one, confirm it directly instead of listing.

### 4. Gather context from the chosen session

Before telling the user to resume, **read the session** and extract a working context summary:

```python
# Extract the last ~10 substantive user messages to understand where things left off
import json, sys

jsonl_path = sys.argv[1]
user_msgs = []
assistant_msgs = []

with open(jsonl_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            msg_type = obj.get("type")
            content = obj.get("message", {}).get("content", "")
            text = ""
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        text += c["text"] + " "
            else:
                text = str(content)
            text = text.strip()
            if not text or len(text) < 10:
                continue
            if text.startswith("Base directory for this skill:") or text.startswith("<local-command"):
                continue
            if msg_type == "user":
                user_msgs.append(text[:300])
            elif msg_type == "assistant":
                assistant_msgs.append(text[:300])
        except:
            pass

# Show last 10 user messages for context
print("=== Where things left off ===")
for msg in user_msgs[-10:]:
    print(f"  User: {msg[:200]}")
    print()
```

Summarize for the user:
- What the session was about
- Where it left off (last topic/decision/action)
- What was unfinished

### 5. Move session if needed

If the session is in a different project directory, move it to the current one:

```bash
CURRENT_PROJECT_DIR=$(python3 -c "
import os
cwd = os.getcwd()
encoded = cwd.replace('/', '-')
print(os.path.expanduser(f'~/.claude/projects/{encoded}'))
")

mv "$SOURCE_JSONL" "$CURRENT_PROJECT_DIR/"

# Move subagent dirs too
SESSION_DIR="${SOURCE_JSONL%.jsonl}"
[ -d "$SESSION_DIR" ] && mv "$SESSION_DIR" "$CURRENT_PROJECT_DIR/"
```

Update both source and destination `sessions-index.json` files (remove from source, add to destination).

If the session is already in the current project, skip the move.

### 6. Continue the work

Don't just say "resume with `claude --resume`". Actually continue the work:

- Tell the user what was unfinished
- Ask if they want to pick up where they left off or take it in a new direction
- If the user already stated what they want to do (in their original `/continue` message), start doing it with the gathered context

## Key Principle

The user says `/continue X` because they have context in their head about what X means. Your job is to **match their mental context** — search broadly, read deeply, and find the conversation they're thinking of even if their search term doesn't appear in any title or summary.

"""Extract a structured digest from a Claude session JSONL file.

Pulls out: user requests, corrections, errors, tool failures, redirections,
token-heavy operations, and key decisions. Outputs a condensed text summary.
"""
import json
import sys
import os
from collections import Counter


def extract_text(content):
    """Extract text from message content (string or list of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    parts.append(f"[TOOL_CALL: {block.get('name', '?')}]")
                elif block.get("type") == "tool_result":
                    result_content = block.get("content", "")
                    if isinstance(result_content, list):
                        for rc in result_content:
                            if isinstance(rc, dict) and rc.get("type") == "text":
                                text = rc.get("text", "")
                                if "error" in text.lower() or "Error" in text:
                                    parts.append(f"[TOOL_ERROR: {text[:300]}]")
                    elif isinstance(result_content, str) and (
                        "error" in result_content.lower()
                    ):
                        parts.append(f"[TOOL_ERROR: {result_content[:300]}]")
        return "\n".join(parts)
    return str(content)


def get_tool_calls(content):
    """Extract tool call names and inputs from content."""
    calls = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                name = block.get("name", "?")
                inp = block.get("input", {})
                if name == "Read":
                    calls.append(f"Read({inp.get('file_path', '?')})")
                elif name == "Edit":
                    calls.append(f"Edit({inp.get('file_path', '?')})")
                elif name == "Write":
                    calls.append(f"Write({inp.get('file_path', '?')})")
                elif name == "Bash":
                    cmd = inp.get("command", "?")[:100]
                    calls.append(f"Bash({cmd})")
                elif name == "Grep":
                    calls.append(f"Grep({inp.get('pattern', '?')})")
                elif name == "Glob":
                    calls.append(f"Glob({inp.get('pattern', '?')})")
                elif name == "Agent":
                    desc = inp.get("description", "?")
                    calls.append(f"Agent({desc})")
                elif name == "Skill":
                    calls.append(f"Skill({inp.get('skill', '?')})")
                else:
                    calls.append(f"{name}()")
    return calls


def detect_correction(text):
    """Detect if user message is a correction/redirection."""
    lower = text.lower().strip()
    correction_signals = [
        "no,",
        "no ",
        "not that",
        "don't",
        "stop",
        "wrong",
        "instead",
        "actually",
        "wait",
        "hold on",
        "forget",
        "that's not",
        "nope",
        "ugh",
        "hmm",
        "why did you",
        "i said",
        "i meant",
        "try again",
        "revert",
        "undo",
        "go back",
        "shouldn't",
        "not what i",
    ]
    return any(lower.startswith(s) or s in lower for s in correction_signals)


def detect_frustration(text):
    """Detect frustration signals."""
    lower = text.lower()
    signals = [
        "ugh",
        "sigh",
        "come on",
        "why",
        "again?",
        "still broken",
        "not working",
        "same error",
        "still failing",
        "fuck",
        "shit",
        "wtf",
        "dumb",
        "stupid",
    ]
    return any(s in lower for s in signals)


def process_session(filepath):
    session_id = os.path.basename(filepath).replace(".jsonl", "")

    entries = []
    with open(filepath) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except Exception:
                continue

    user_messages = []
    corrections = []
    frustrations = []
    tool_errors = []
    tool_calls_total = []
    agent_spawns = []
    assistant_messages = []
    interrupts = []

    for entry in entries:
        msg = entry.get("message", {})
        role = msg.get("role", entry.get("type", ""))
        content = msg.get("content", "")
        text = extract_text(content)
        timestamp = entry.get("timestamp", "")

        if role == "user" or entry.get("type") == "user":
            if entry.get("isMeta") or entry.get("type") == "file-history-snapshot":
                continue
            # Check tool results for errors
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        rc = block.get("content", "")
                        if isinstance(rc, list):
                            for item in rc:
                                if isinstance(item, dict) and "error" in str(
                                    item.get("text", "")
                                ).lower():
                                    tool_errors.append(
                                        {
                                            "ts": timestamp,
                                            "text": str(item.get("text", ""))[:300],
                                        }
                                    )
                        elif isinstance(rc, str) and "error" in rc.lower():
                            tool_errors.append({"ts": timestamp, "text": rc[:300]})

            if text.strip() and not text.startswith("[TOOL"):
                clean = text.strip()
                if len(clean) > 5:
                    is_interrupt = "[Request interrupted" in clean
                    if is_interrupt:
                        interrupts.append({"ts": timestamp})
                        continue

                    is_correction = detect_correction(clean)
                    is_frustration = detect_frustration(clean)

                    # Skip noise sources from correction/frustration detection
                    is_task_notification = "<task-notification>" in clean
                    is_command_output = "<local-command-stdout>" in clean

                    is_noise = is_task_notification or is_command_output

                    user_messages.append(
                        {
                            "ts": timestamp,
                            "text": clean[:500],
                            "correction": is_correction and not is_noise,
                            "frustration": is_frustration and not is_noise,
                        }
                    )
                    if is_correction and not is_noise:
                        corrections.append({"ts": timestamp, "text": clean[:500]})
                    if is_frustration and not is_noise:
                        frustrations.append({"ts": timestamp, "text": clean[:500]})

        elif role == "assistant" or entry.get("type") == "assistant":
            tools = get_tool_calls(content)
            tool_calls_total.extend(tools)
            for t in tools:
                if t.startswith("Agent("):
                    agent_spawns.append({"ts": timestamp, "tool": t})

            if text.strip():
                assistant_messages.append(
                    {"ts": timestamp, "length": len(text), "preview": text[:200]}
                )

    # Build digest
    digest = []
    project = os.path.dirname(filepath).split("projects/")[-1].split("/")[0]
    digest.append(f"# Session: {session_id}")
    digest.append(f"Project: {project}")
    digest.append(f"Entries: {len(entries)} | User msgs: {len(user_messages)} | "
                   f"Tool calls: {len(tool_calls_total)} | Agents: {len(agent_spawns)}")
    digest.append(f"Corrections: {len(corrections)} | Frustrations: {len(frustrations)} | "
                   f"Tool errors: {len(tool_errors)} | Interrupts: {len(interrupts)}")
    digest.append("")

    # User messages (condensed — only show corrections, frustrations, and key requests)
    digest.append("## User Messages")
    for m in user_messages:
        markers = ""
        if m["correction"]:
            markers += " [CORRECTION]"
        if m["frustration"]:
            markers += " [FRUSTRATION]"
        # Always show corrections/frustrations, but limit normal messages
        if markers or len(user_messages) <= 30:
            digest.append(f"- [{m['ts'][:16]}]{markers} {m['text'][:300]}")
    digest.append("")

    # Tool frequency
    tool_freq = Counter()
    for t in tool_calls_total:
        name = t.split("(")[0]
        tool_freq[name] += 1
    digest.append("## Tool Frequency: " + ", ".join(
        f"{n}:{c}" for n, c in tool_freq.most_common(10)
    ))

    if agent_spawns:
        digest.append("## Agents: " + " | ".join(
            a["tool"].replace("Agent(", "").rstrip(")") for a in agent_spawns[:15]
        ))

    # Verbosity
    if assistant_messages:
        lengths = [m["length"] for m in assistant_messages]
        digest.append(f"## Verbosity: avg={sum(lengths)//len(lengths)} chars, "
                       f"max={max(lengths)}, total={sum(lengths)}")

    digest.append("")
    return "\n".join(digest)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: extract_session_digest.py <file.jsonl> [file2.jsonl ...]")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        print(process_session(filepath))
        print("---\n")

#!/usr/bin/env python3
"""PostToolUse hook for the Skill tool: logs every invocation and nudges
when a skill crosses a usage threshold since its last review.
"""
import json
import os
import sys
from datetime import datetime, timezone

LOG_PATH = os.environ.get("SKILL_USAGE_LOG", os.path.expanduser("~/.claude/skill-usage.jsonl"))
COUNTS_PATH = os.environ.get("SKILL_USAGE_COUNTS", os.path.expanduser("~/.claude/skill-usage-counts.json"))
THRESHOLD = int(os.environ.get("SKILL_USAGE_THRESHOLD", "10"))


def extract_skill_name(tool_input):
    # Field naming for tool_input drifted across doc sources during research;
    # "skill" is confirmed from the Skill tool's own parameter schema.
    for key in ("skill", "skill_name", "name"):
        value = tool_input.get(key)
        if value:
            return value
    return "unknown"


def append_log_entry(entry):
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_counts():
    if not os.path.exists(COUNTS_PATH):
        return {}
    with open(COUNTS_PATH) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_counts(counts):
    with open(COUNTS_PATH, "w") as f:
        json.dump(counts, f, indent=2)


def update_counts_and_maybe_nudge(counts, skill_name):
    """Increment counts[skill_name], decide whether this invocation crosses
    the nudge threshold, and return a nudge message string if so (else None).

    counts[skill_name] shape: {"count": int, "last_nudge_count": int}
    """
    entry = counts.setdefault(skill_name, {"count": 0, "last_nudge_count": 0})
    entry["count"] += 1

    if entry["count"] - entry["last_nudge_count"] >= THRESHOLD:
        entry["last_nudge_count"] += THRESHOLD
        return (
            f"Skill usage nudge: '{skill_name}' has been invoked "
            f"{entry['count']} times since its last review (threshold: {THRESHOLD}). "
            "Consider running a skill-creator-plus review pass on it."
        )

    return None
    

def main():
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input", {}) or {}
    skill_name = extract_skill_name(tool_input)

    append_log_entry({
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "skill": skill_name,
        "args": tool_input.get("args", ""),
        "session_id": payload.get("session_id", ""),
        "cwd": payload.get("cwd", ""),
    })

    counts = load_counts()
    nudge_message = update_counts_and_maybe_nudge(counts, skill_name)
    save_counts(counts)

    if nudge_message:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": nudge_message,
                "systemMessage": nudge_message,
            }
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()

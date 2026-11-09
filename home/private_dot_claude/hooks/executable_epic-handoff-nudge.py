#!/usr/bin/env python3
"""Reminds the model to offer the change-to-github-epic skill at the
planning-to-build handoff, because a skill description alone is only
best-effort routing.

Two events, one script (the event name comes from the hook input):

- UserPromptSubmit: the prompt starts with /opsx:apply or /speckit.implement.
- PostToolUse (matcher ExitPlanMode): a Claude Code plan was just approved.

It never blocks. It adds context telling the model to offer the skill first,
and stays silent when the skill was already used in this session, so it
nudges once per session rather than on every build step.
"""
import json
import re
import sys

SKILL = "change-to-github-epic"

# Slash commands that start the build phase. Anchored to the start of the prompt
# so a sentence that merely mentions them does not trigger.
BUILD_COMMANDS = re.compile(r"^\s*/(opsx:apply|speckit\.implement)\b")

# Evidence the skill already ran: a Skill tool call, or the /<skill> slash command.
ALREADY_RAN = re.compile(
    r'"name"\s*:\s*"Skill"\s*,\s*"input"\s*:\s*\{\s*"skill"\s*:\s*"' + SKILL + r'"'
    r"|<command-name>/" + SKILL
)


def skill_already_ran(transcript_path):
    if not transcript_path:
        return False
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            return ALREADY_RAN.search(f.read()) is not None
    except OSError:
        return False


def build_message(data):
    event = data.get("hook_event_name")
    if event == "UserPromptSubmit":
        match = BUILD_COMMANDS.match(data.get("prompt", ""))
        if not match:
            return None
        return (
            f"The user is about to start building with /{match.group(1)}. Before running it, "
            f"offer the {SKILL} skill once: it turns the finished plan into a GitHub Epic with "
            "linked sub-issues and a wave roadmap. If the user declines or an epic already "
            "exists for this work, continue with the build."
        )
    if event == "PostToolUse" and data.get("tool_name") == "ExitPlanMode":
        return (
            f"A plan was just approved. Before making the first edit, offer the {SKILL} skill "
            "once to turn it into a GitHub Epic with linked sub-issues. If the user declines, "
            "continue with the build."
        )
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # never break the session over a malformed payload

    message = build_message(data)
    if message is None or skill_already_ran(data.get("transcript_path")):
        return 0

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": data["hook_event_name"],
                "additionalContext": message,
            }
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Enforces the shell-script conventions BEFORE a Write or Edit lands.

PreToolUse counterpart of the lint-shell git hook (home/dot_git-hooks/lint-shell): same
shebang list, same shellcheck call, but it denies the tool call, so a bad script is never
written and the model can retry with a corrected one. The git hook stays as the backstop
for what this cannot see (hand edits, Bash-written files, the executable bit).

Checks, on the content the tool call would produce:
- Only files whose first line is a shell shebang are checked (same rule as lint-shell).
- NEW files: the shebang must be '#!/usr/bin/env bash' (or '#!/bin/sh'), and an
  executable_*.sh name is refused (a command has no extension).
- shellcheck at warning level; only findings the call INTRODUCES block (see
  new_findings), so a legacy script with old warnings can still be edited.
  (lint-shell is stricter: any warning in a staged script blocks the commit.)

Not checked: the plain-versus-executable naming rule, because the file mode does not exist
until after the write. lint-shell checks that at commit time.

Fails open: missing shellcheck, a malformed payload, or an Edit whose old_string is not found
all allow the call (the tool reports its own error).
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter

NEW_FILE_SHEBANGS = ("#!/usr/bin/env bash", "#!/bin/sh")


def is_shell_shebang(line):
    return line in ("#!/bin/sh", "#!/bin/bash", "#!/usr/bin/env bash", "#!/usr/bin/env sh") or line.startswith(
        ("#!/bin/sh ", "#!/bin/bash ")
    )


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def proposed_content(tool, tool_input, current):
    """The full file text after the tool call, or None when it cannot be worked out."""
    if tool == "Write":
        return tool_input.get("content")
    old, new = tool_input.get("old_string"), tool_input.get("new_string")
    if current is None or not old or new is None or old not in current:
        return None
    return current.replace(old, new) if tool_input.get("replace_all") else current.replace(old, new, 1)


def policy_violation(path, shebang):
    """New files only. Returns a one-line reason, or None when fine."""
    if shebang not in NEW_FILE_SHEBANGS:
        return f"shebang is '{shebang}'; use '#!/usr/bin/env bash' (or '#!/bin/sh' for a tiny hook)"
    name = os.path.basename(path)
    if name.startswith("executable_") and name.endswith(".sh"):
        return "a command has no extension; drop the .sh"
    return None


def shellcheck_findings(text):
    """Finding lines (gcc format), or None when shellcheck cannot run."""
    try:
        run = subprocess.run(
            ["shellcheck", "--severity=warning", "--external-sources", "--format=gcc", "-"],
            input=text, capture_output=True, text=True, timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return [line for line in run.stdout.splitlines() if line.strip()]


def location_free(findings):
    """gcc-format findings without the '-:LINE:COL: ' prefix."""
    return [re.sub(r"^[^:]*:\d+:\d+: ", "", line) for line in findings]


def new_findings(before, after):
    """The findings the call introduces; any of them denies it.

    before: findings in the file as it is now (empty for a new file).
    after:  findings in the file the Write or Edit would produce.
    """
    # Only findings the call introduces count, so editing a legacy script is never refused
    # for warnings it already had. Line and column are stripped because an edit shifts them;
    # the Counter lets each old finding cancel exactly one match, so a warning that now
    # appears more often than before still counts.
    remaining = Counter(location_free(before))
    introduced = []
    for line, key in zip(after, location_free(after)):
        if remaining[key] > 0:
            remaining[key] -= 1
        else:
            introduced.append(line)
    return introduced


def deny(reason):
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool, tool_input = data.get("tool_name"), data.get("tool_input") or {}
    path = tool_input.get("file_path")
    if tool not in ("Write", "Edit") or not path:
        return 0

    current = read_text(path)
    after = proposed_content(tool, tool_input, current)
    if after is None:
        return 0
    shebang = after.split("\n", 1)[0].rstrip("\r")
    if not is_shell_shebang(shebang):
        return 0

    problems = []
    if current is None:
        reason = policy_violation(path, shebang)
        if reason:
            problems.append(reason)

    after_findings = shellcheck_findings(after)
    if after_findings is not None:
        before_findings = (shellcheck_findings(current) if current else None) or []
        introduced = new_findings(before_findings, after_findings)
        if introduced:
            problems.append("shellcheck:\n" + "\n".join(introduced))

    if problems:
        deny(f"shell conventions ({path}): " + "\n".join(problems) + "\nSee 'Shell scripts' in the dotfiles README.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

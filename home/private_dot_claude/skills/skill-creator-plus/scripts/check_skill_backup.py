#!/usr/bin/env python3
"""
Check that every skill you authored or uploaded has a git-backed home, i.e. that
nothing exists only on the Claude account or only on this disk.

Usage:
    python3 -m scripts.check_skill_backup             # report only
    python3 -m scripts.check_skill_backup --harvest   # also copy account-only skills to disk

Why this exists: Claude Desktop has no export for skills, so a skill created only
in its UI exists solely on the account. Desktop's cache holds a complete copy of
every account skill, which makes the copy-out possible, but it is only a cache:
run this soon after creating or uploading a skill.

What counts as a "home": a skill folder that the dotfiles manager (chezmoi) tracks
in a git repository, with its changes committed and pushed. A folder that is merely
tracked but has uncommitted or unpushed changes is reported as not yet backed up.

What it checks
  1. Every user skill registered on the account (Desktop manifest, creatorType
     "user") has a home. Anthropic's own skills are skipped: the account provides
     them.
  2. Every skill folder in ~/.claude/skills is tracked. (Claude Code's own `synced/`
     cache is skipped.)

--harvest copies an account-only skill from Desktop's cache into ~/.claude/skills/<name>/
(never overwriting anything) and prints the `chezmoi add` command to run next. It
does not touch the repo itself: chezmoi renames some files in its source tree, so let
it do the adding. Read-only otherwise.

Exit code: 0 if every skill has a pushed home, 1 if anything needs attention,
2 if no Claude Desktop bundle or no chezmoi was found.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from scripts.verify_desktop_registration import CODE_SKILLS, find_bundles, load_manifest


def run(*cmd, cwd=None):
    """(returncode, stdout) of a command; (127, "") if the program is missing."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return r.returncode, r.stdout.strip()
    except FileNotFoundError:
        return 127, ""


def managed_skill_dirs():
    """Names of skill folders in ~/.claude/skills that chezmoi tracks (via SKILL.md)."""
    code, out = run("chezmoi", "managed", "--include=files", "--path-style=absolute")
    if code != 0:
        return None
    root = str(CODE_SKILLS) + "/"
    names = set()
    for line in out.splitlines():
        if line.startswith(root) and line.endswith("/SKILL.md"):
            names.add(line[len(root):].split("/")[0])
    return names


def backup_state(name):
    """'ok' | 'drift' | 'new-files' | 'uncommitted' | 'unpushed' | 'no-repo', for a
    skill chezmoi tracks. Live-folder problems come first: if the folder Claude Code
    reads differs from what the repo holds, the repo is not a backup of it yet."""
    folder = str(CODE_SKILLS / name)
    _, drift = run("chezmoi", "status", folder)
    if drift:
        return "drift"
    _, unmanaged = run("chezmoi", "unmanaged", folder)
    if [l for l in unmanaged.splitlines() if "__pycache__" not in l and ".DS_Store" not in l]:
        return "new-files"
    code, src = run("chezmoi", "source-path", folder)
    if code != 0 or not src:
        return "no-repo"
    code, top = run("git", "rev-parse", "--show-toplevel", cwd=src)
    if code != 0:
        return "no-repo"
    _, dirty = run("git", "status", "--porcelain", "--", src, cwd=top)
    if dirty:
        return "uncommitted"
    # Commits touching this skill that the upstream branch doesn't have yet.
    code, ahead = run("git", "log", "@{u}..HEAD", "--oneline", "--", src, cwd=top)
    if code != 0:
        return "unpushed"  # no upstream configured: nothing is on a remote
    return "unpushed" if ahead else "ok"


def main():
    harvest = "--harvest" in sys.argv[1:]
    if any(a not in ("--harvest",) for a in sys.argv[1:]):
        print(__doc__)
        return 1

    bundles = find_bundles()
    if not bundles:
        print("No Claude Desktop skills bundle found on this machine. Nothing to check.")
        return 2
    tracked = managed_skill_dirs()
    if tracked is None:
        print("chezmoi is not available (or failed), so tracked skills can't be determined.")
        return 2

    problems = 0
    account_user = {}  # name -> Desktop bundle that has its folder
    for bundle in bundles:
        for s in load_manifest(bundle / "manifest.json"):
            if s.get("creatorType") == "user":
                account_user[s["name"]] = bundle

    print("Skills registered on the account by you (creatorType: user):")
    for name in sorted(account_user):
        on_disk = (CODE_SKILLS / name / "SKILL.md").exists()
        if name in tracked:
            state = backup_state(name)
            note = {"ok": "backed up (tracked, committed, pushed)",
                    "drift": "live folder has changes NOT yet pulled into the repo: "
                             f"bin/sync-dotfiles.sh ~/.claude/skills/{name}",
                    "new-files": "live folder has files the repo doesn't track: "
                                 "chezmoi unmanaged ~/.claude/skills/" + name,
                    "uncommitted": "tracked, but has UNCOMMITTED changes: commit and push",
                    "unpushed": "committed, but NOT PUSHED to a remote",
                    "no-repo": "tracked, but not inside a git repository"}[state]
            mark = "✅" if state == "ok" else "⚠️ "
            problems += state != "ok"
            print(f"  {mark} {name}: {note}")
        elif on_disk:
            problems += 1
            print(f"  ❌ {name}: on disk but NOT tracked. Run: chezmoi add ~/.claude/skills/{name}")
        else:
            problems += 1
            print(f"  ❌ {name}: exists ONLY on the account (no home anywhere)")
            src = account_user[name] / "skills" / name
            if harvest and (src / "SKILL.md").exists():
                dest = CODE_SKILLS / name
                shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "*.skill"))
                print(f"       harvested from Desktop's cache to {dest}")
                print(f"       next: chezmoi add ~/.claude/skills/{name}   then commit and push the dotfiles repo")
            elif harvest:
                print("       cannot harvest: no copy in Desktop's cache")
            else:
                print("       run again with --harvest to copy it out of Desktop's cache")

    print("\nSkill folders in ~/.claude/skills that are not on the account:")
    local_only = [p.name for p in sorted(CODE_SKILLS.iterdir())
                  if p.is_dir() and p.name != "synced" and (p / "SKILL.md").exists()
                  and p.name not in account_user]
    if not local_only:
        print("  none")
    for name in local_only:
        if name in tracked:
            state = backup_state(name)
            mark = "✅" if state == "ok" else "⚠️ "
            problems += state != "ok"
            print(f"  {mark} {name}: {'backed up' if state == 'ok' else 'tracked but ' + state}")
        else:
            problems += 1
            print(f"  ❌ {name}: NOT tracked. Run: chezmoi add ~/.claude/skills/{name}")

    print("\nAll skills have a pushed home." if not problems else f"\n{problems} skill(s) need attention.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Check whether skills are registered with Claude Desktop (Chat / Cowork), and
whether they have reached Claude Code's synced mirror. Read-only: it never
writes to Desktop's bundle or to manifest.json.

Usage:
    python -m scripts.verify_desktop_registration <skill-name> [<skill-name> ...]

Why this exists: Desktop only loads skills registered on the user's account; a
folder copied into its skills-plugin bundle is deleted at the next sync
("orphans cleaned"). The only signal that an upload worked is the skill showing
up in the bundle's manifest.json as a user skill, so that's what this checks.

It also compares each copy's content with the personal copy in
~/.claude/skills/<name>/ (the deployment target of the skill's home in the
dotfiles repo). A Desktop copy that differs from the personal copy is stale:
re-zip and re-upload. The synced mirror can differ only because it lags.

Exit code: 0 if every named skill is registered and enabled in Desktop's
manifest and its Desktop copy matches the personal copy, 1 if any is not or
does not, 2 if no Desktop bundle exists on this machine.
The Claude Code mirror and duplicate-copy findings are reported as notes, not
failures: that mirror syncs on Claude Code's own schedule (session start, then
roughly every 10 minutes) so it can lag behind an upload.
"""

import hashlib
import json
import sys
from pathlib import Path

HOME = Path.home()

# macOS path is confirmed. The other two are educated guesses (see
# references/deployment-locations.md) and are only searched, never assumed.
DESKTOP_BASES = [
    HOME / "Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin",
    HOME / "AppData/Roaming/Claude/local-agent-mode-sessions/skills-plugin",
    HOME / ".config/Claude/local-agent-mode-sessions/skills-plugin",
]
CODE_SKILLS = HOME / ".claude/skills"
IGNORED_FILES = {".DS_Store"}


def fingerprint(folder):
    """Short hash of a skill folder's file names and contents, so two copies
    can be compared. Ignores OS junk and Python caches."""
    h = hashlib.sha256()
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.name not in IGNORED_FILES and "__pycache__" not in p.parts:
            h.update(str(p.relative_to(folder)).encode() + b"\0")
            h.update(p.read_bytes() + b"\0")
    return h.hexdigest()[:12]


def load_manifest(path):
    try:
        return json.loads(path.read_text()).get("skills", [])
    except (OSError, ValueError):
        return []


def find_bundles():
    """Every <base>/<account>/<install>/ that has a manifest.json."""
    return sorted(m.parent for base in DESKTOP_BASES if base.is_dir()
                  for m in base.glob("*/*/manifest.json"))


def main():
    names = sys.argv[1:]
    if not names or any(n.startswith("-") for n in names):
        print(__doc__)
        return 1

    bundles = find_bundles()
    if not bundles:
        print("No Claude Desktop skills bundle found on this machine "
              "(Desktop not installed, or agent mode never used). Nothing to verify.")
        return 2

    synced = {}       # skill name -> synced manifest entry, across all synced buckets
    synced_dirs = {}  # skill name -> folder of the synced copy
    for m in (CODE_SKILLS / "synced").glob("*/manifest.json"):
        for s in load_manifest(m):
            synced[s["name"]] = s
            synced_dirs[s["name"]] = m.parent / s["name"]

    all_ok = True
    stale = False
    for bundle in bundles:
        print(f"Desktop bundle: {bundle}")
        entries = {s["name"]: s for s in load_manifest(bundle / "manifest.json")}
        for name in names:
            entry = entries.get(name)
            folder = (bundle / "skills" / name / "SKILL.md").exists()
            if entry and entry.get("enabled") and folder:
                kind = entry.get("creatorType", "?")
                print(f"  ✅ {name}: registered ({kind} skill, enabled, "
                      f"updated {entry.get('updatedAt')}, folder present)")
                personal_dir = CODE_SKILLS / name
                if (personal_dir / "SKILL.md").exists():
                    if fingerprint(bundle / "skills" / name) == fingerprint(personal_dir):
                        print("     content matches the personal copy")
                    else:
                        stale = True
                        print("  ❌ " + name + ": Desktop copy DIFFERS from the personal copy. "
                              "The personal copy is the source (dotfiles repo), so the account "
                              "copy is stale: re-zip and re-upload (package_skill.py --zip).")
            else:
                all_ok = False
                why = ("not in manifest.json" if not entry
                       else "disabled in manifest" if not entry.get("enabled")
                       else "listed in manifest but folder missing")
                print(f"  ❌ {name}: {why}")

    print("\nClaude Code (synced mirror and personal copies):")
    for name in names:
        in_sync = name in synced
        personal = (CODE_SKILLS / name / "SKILL.md").exists()
        print(f"  {name}: synced mirror {'yes' if in_sync else 'not yet'}"
              f"; personal copy {'yes' if personal else 'no'}")
        if in_sync and personal:
            print("    note: duplicate, no collision. /" + name + " runs the personal copy; "
                  "/anthropic-skills:" + name + " runs the synced one (Claude Code docs; "
                  "observed 2026-10-18).")
            mirror = synced_dirs.get(name)
            if mirror and mirror.is_dir():
                if fingerprint(mirror) == fingerprint(CODE_SKILLS / name):
                    print("    synced mirror content matches the personal copy")
                else:
                    print("    note: synced mirror content DIFFERS from the personal copy. "
                          "The mirror can lag an upload by about 10 minutes; if it still "
                          "differs later, the account copy is stale: re-upload.")
        if not in_sync:
            print("    note: Claude Code syncs account skills at session start and "
                  "about every 10 minutes, so this can lag an upload.")

    if not all_ok:
        print("\nNot registered means: upload the zip via Customize > Skills > + > "
              "Create skill > Upload a skill. Do not copy folders into the bundle "
              "or edit manifest.json; Desktop deletes unregistered folders on its next sync.")
    return 0 if (all_ok and not stale) else 1


if __name__ == "__main__":
    sys.exit(main())

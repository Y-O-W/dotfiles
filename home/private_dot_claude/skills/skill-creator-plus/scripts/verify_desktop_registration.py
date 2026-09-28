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

Exit code: 0 if every named skill is registered and enabled in Desktop's
manifest, 1 if any is not, 2 if no Desktop bundle exists on this machine.
The Claude Code mirror and duplicate-copy findings are reported as notes, not
failures: that mirror syncs on Claude Code's own schedule (session start, then
roughly every 10 minutes) so it can lag behind an upload.
"""

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

    synced = {}  # skill name -> synced manifest entry, across all synced buckets
    for m in (CODE_SKILLS / "synced").glob("*/manifest.json"):
        for s in load_manifest(m):
            synced[s["name"]] = s

    all_ok = True
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
            print("    note: duplicate. The account skill and ~/.claude/skills/"
                  f"{name}/ both exist; which one Claude Code loads is unverified.")
        if not in_sync:
            print("    note: Claude Code syncs account skills at session start and "
                  "about every 10 minutes, so this can lag an upload.")

    if not all_ok:
        print("\nNot registered means: upload the zip via Customize > Skills > + > "
              "Create skill > Upload a skill. Do not copy folders into the bundle "
              "or edit manifest.json; Desktop deletes unregistered folders on its next sync.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

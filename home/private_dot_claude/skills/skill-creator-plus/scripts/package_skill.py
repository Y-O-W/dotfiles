#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file (or .zip) of a skill folder

Usage:
    python -m scripts.package_skill <path/to/skill-folder> [output-directory] [--zip]
    python -m scripts.package_skill --all <skills-directory> [output-directory] [--zip]

Example:
    python -m scripts.package_skill skills/public/my-skill
    python -m scripts.package_skill skills/public/my-skill ./dist
    python -m scripts.package_skill --all .claude/skills ~/Downloads/upload --zip

Both extensions are the same zip archive. `.skill` is what a file-delivery tool's
"Save skill" card expects; `--zip` writes `<name>.zip`, the extension Claude
Desktop's Customize > Skills > Upload a skill dialog takes. Both forms are
verified: six hand-built zips (`zip -r`, with directory entries) and this
script's own output (same files, no directory entries) were accepted by the
dialog, the latter as a same-name replacement on 2026-09-28.
`--all` packages every subfolder of <skills-directory> that contains a SKILL.md
and reports a summary; it exits non-zero if any skill failed validation.
"""

import fnmatch
import sys
import zipfile
from pathlib import Path
from scripts.quick_validate import validate_skill

# Patterns to exclude when packaging skills.
EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}
# Directories excluded only at the skill root (not when nested deeper).
ROOT_EXCLUDE_DIRS = {"evals"}


def should_exclude(rel_path: Path) -> bool:
    """Check if a path should be excluded from packaging."""
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    # rel_path is relative to skill_path.parent, so parts[0] is the skill
    # folder name and parts[1] (if present) is the first subdir.
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def package_skill(skill_path, output_dir=None, extension="skill"):
    """
    Package a skill folder into a .skill (or .zip) file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the file (defaults to current directory)
        extension: "skill" (default) or "zip"; the archive format is identical

    Returns:
        Path to the created file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.{extension}"

    # Create the .skill file (zip format)
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory, excluding build artifacts
            for file_path in skill_path.rglob('*'):
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                if should_exclude(arcname):
                    print(f"  Skipped: {arcname}")
                    continue
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

        print(f"\n✅ Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return None


def package_all(skills_dir, output_dir=None, extension="skill"):
    """Package every subfolder of skills_dir that holds a SKILL.md.

    Returns (packaged, failed) as lists of skill folder names. Hidden folders and
    `*-workspace` folders (eval scratch space) are skipped.
    """
    skills_dir = Path(skills_dir).expanduser().resolve()
    if not skills_dir.is_dir():
        print(f"❌ Error: Not a directory: {skills_dir}")
        return [], []

    candidates = sorted(
        d for d in skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
        and not d.name.startswith(".") and not d.name.endswith("-workspace")
    )
    packaged, failed = [], []
    for d in candidates:
        print(f"📦 Packaging skill: {d.name}")
        (packaged if package_skill(d, output_dir, extension) else failed).append(d.name)
        print()
    return packaged, failed


def main():
    args = sys.argv[1:]
    extension = "skill"
    if "--zip" in args:
        args.remove("--zip")
        extension = "zip"
    batch = "--all" in args
    if batch:
        args.remove("--all")

    if not args:
        print("Usage: python -m scripts.package_skill <path/to/skill-folder> [output-directory] [--zip]")
        print("       python -m scripts.package_skill --all <skills-directory> [output-directory] [--zip]")
        print("\nExample:")
        print("  python -m scripts.package_skill skills/public/my-skill")
        print("  python -m scripts.package_skill skills/public/my-skill ./dist")
        print("  python -m scripts.package_skill --all .claude/skills ~/Downloads/upload --zip")
        sys.exit(1)

    target = args[0]
    output_dir = args[1] if len(args) > 1 else None
    if output_dir:
        print(f"   Output directory: {output_dir}\n")

    if batch:
        packaged, failed = package_all(target, output_dir, extension)
        print(f"Packaged {len(packaged)}: {', '.join(packaged) or 'none'}")
        if failed:
            print(f"Failed {len(failed)}: {', '.join(failed)}")
        if not packaged and not failed:
            print("No skill folders (with a SKILL.md) found.")
        sys.exit(0 if packaged and not failed else 1)

    print(f"📦 Packaging skill: {target}\n")
    sys.exit(0 if package_skill(target, output_dir, extension) else 1)


if __name__ == "__main__":
    main()

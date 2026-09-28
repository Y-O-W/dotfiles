#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    # PyYAML is not installed everywhere (macOS system Python has none). Skill
    # frontmatter is flat enough that the line-based fallback below is enough
    # to validate it, so don't make packaging depend on a pip install.
    yaml = None


def _parse_frontmatter_fallback(frontmatter_text):
    """Top-level `key: value` pairs only. Nested blocks (metadata, allowed-tools
    lists) come back as empty strings, which is all the checks below need."""
    data = {}
    for line in frontmatter_text.splitlines():
        m = re.match(r'^([A-Za-z0-9_-]+):\s*(.*)$', line)
        if not m:
            continue  # indented continuation, list item, or comment
        key, value = m.group(1), m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
            value = value[1:-1]
        data[key] = value
    return data


def _description_spans_lines(frontmatter_text):
    """True if `description:` is a block scalar (`>` / `|`) or continues onto an
    indented next line. Claude Code silently drops such skills from discovery."""
    lines = frontmatter_text.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith('description:'):
            continue
        value = line.split(':', 1)[1].strip()
        if re.match(r'^[>|][+-]?\d*$', value):
            return True
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        return bool(nxt.strip()) and nxt[0] in ' \t'
    return False

# Directories whose contents are not packaged as part of the skill, so any
# SKILL.md inside them shouldn't count toward the single-SKILL.md check below.
# Mirrors package_skill.py: __pycache__ and node_modules are excluded at any
# depth, while evals is only excluded at the skill root.
EXCLUDED_DIR_PARTS = {'__pycache__', 'node_modules'}
ROOT_EXCLUDED_DIR_PARTS = {'evals'}


def _counts_as_skill_md(rel_path):
    """True if a SKILL.md at rel_path (relative to the skill root) would be packaged."""
    dir_parts = rel_path.parts[:-1]
    if any(part in EXCLUDED_DIR_PARTS for part in dir_parts):
        return False
    if dir_parts and dir_parts[0] in ROOT_EXCLUDED_DIR_PARTS:
        return False
    return True


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # A skill must contain exactly one SKILL.md, at <folder>/SKILL.md. Extra
    # (nested) SKILL.md files are rejected on upload: the Skills API and claude.ai
    # accept exactly one per skill — only Claude Code's filesystem loads nested
    # ones. package_skill produces an upload-bound .skill, so block here rather
    # than ship an artifact that's guaranteed to fail on upload.
    skill_md_files = [
        p for p in skill_path.rglob('SKILL.md')
        if _counts_as_skill_md(p.relative_to(skill_path))
    ]
    if len(skill_md_files) > 1:
        extras = sorted(
            str(p.relative_to(skill_path)) for p in skill_md_files
            if p.resolve() != skill_md.resolve()
        )
        return False, (
            f"Found {len(skill_md_files)} SKILL.md files, but a skill must contain "
            f"exactly one at <folder>/SKILL.md. The Skills API and claude.ai reject "
            f"multiple on upload (only Claude Code's filesystem loads nested skills). "
            f"Extra: {', '.join(extras)}.\n"
            "  - Separate skills: package each on its own, or build a plugin "
            "(skills/<name>/SKILL.md).\n"
            "  - Supporting docs: rename to non-SKILL.md files (e.g. references/<topic>.md).\n"
            "  - Swept in by mistake: package only the one skill directory."
        )

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Checked on the raw text, before parsing: a real YAML parser happily accepts
    # a block-scalar description, so this only shows up as a skill that quietly
    # never appears in Claude Code.
    if _description_spans_lines(frontmatter_text):
        return False, (
            "The `description` spans multiple lines (block scalar or indented "
            "continuation). Claude Code's discovery silently drops such skills, "
            "with no error anywhere. Put the whole description on one line."
        )

    # Parse YAML frontmatter
    if yaml is None:
        frontmatter = _parse_frontmatter_fallback(frontmatter_text)
    else:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return False, "Frontmatter must be a YAML dictionary"
        except yaml.YAMLError as e:
            return False, f"Invalid YAML in frontmatter: {e}"

    # Define allowed properties
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        hint = ""
        if 'version' in unexpected_keys:
            # `version:` is a common habit but is not in the allowed set; `metadata`
            # takes arbitrary string keys, so the value can be kept there instead.
            hint = " To keep a version, nest it: `metadata:` then an indented `version: \"1.0\"`."
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}.{hint}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (kebab-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        # Check for angle brackets
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"
        # Check description length (max 1024 characters per spec)
        if len(description) > 1024:
            return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    # Validate compatibility field if present (optional)
    compatibility = frontmatter.get('compatibility', '')
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    return True, "Skill is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)

# kepano/obsidian-skills (vendored)

Third-party Agent Skills for Obsidian, vendored as **plain copies** so this repo alone can
restore them: no network, and no dependence on upstream still existing.

| | |
|---|---|
| Source | https://github.com/kepano/obsidian-skills (Steph Ango) |
| Pinned commit | `3ccff5338ea700537839b21900aa5358a0402c98` (2026-09-15, "Merge pull request #143 from vladimirtsk/docs/shorten-skill-description") |
| Version | 1.0.1 (from upstream's `.claude-plugin/plugin.json` at that commit; upstream has no git tags or releases) |
| License | MIT, see `LICENSE` in this folder (upstream's, unchanged) |
| Verified | 2026-09-28: every skill below is byte-identical to upstream at the pinned commit; the pin was also upstream's HEAD that day (0 commits ahead) |
| Local modifications | none |

## What is vendored, and where it lives

Only each skill's own folder. They are tracked like any other skill in this repo and deployed by
`chezmoi apply` to `~/.claude/skills/<name>/`.

| Skill | Source in this repo |
|---|---|
| `defuddle` | `home/private_dot_claude/skills/defuddle/` |
| `json-canvas` | `home/private_dot_claude/skills/json-canvas/` |
| `knap` | `home/private_dot_claude/skills/knap/` |
| `obsidian-bases` | `home/private_dot_claude/skills/obsidian-bases/` |
| `obsidian-cli` | `home/private_dot_claude/skills/obsidian-cli/` |
| `obsidian-markdown` | `home/private_dot_claude/skills/obsidian-markdown/` |

Deliberately left out: upstream's `.claude-plugin/` (the marketplace manifest, only needed for the
interactive `/plugin marketplace add` flow; filesystem discovery needs just a `SKILL.md`). Upstream's
`README.md` and `LICENSE` are kept once, here, for provenance rather than duplicated per skill.

The copies on the Claude account (uploaded for Claude Desktop) and in Claude Code's `synced/` cache
are **derived** from these; they are never the source.

## Checking for a newer upstream

```sh
gh api repos/kepano/obsidian-skills/compare/3ccff5338ea700537839b21900aa5358a0402c98...HEAD \
  --jq '"commits ahead: \(.ahead_by); skill files changed: \([.files[].filename | select(startswith("skills/"))] | length)"'
```

## Updating the pin

1. Download upstream at the new commit and diff each skill against `home/private_dot_claude/skills/<name>/`:
   `gh api repos/kepano/obsidian-skills/tarball/<sha> > up.tgz`, extract, `diff -r`.
2. Copy the changed skill files into `~/.claude/skills/<name>/`, then pull them into this repo with
   `bin/sync-dotfiles.sh ~/.claude/skills/<name>` (a brand-new file needs `chezmoi add <file>`).
3. Update this file: commit SHA and date, version, the verified date, and any local modification.
   Refresh `LICENSE` and `README.md` if upstream changed them.
4. Review the diff and commit yourself.
5. Re-upload to Claude Desktop, one zip per skill: from `~/.claude/skills/skill-creator-plus/`,
   `python3 -m scripts.package_skill --all ~/.claude/skills ~/Downloads/upload --zip`, upload only the
   changed ones (Customize → Skills), then confirm with
   `python3 -m scripts.verify_desktop_registration <name> ...`.

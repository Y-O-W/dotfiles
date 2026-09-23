# Where finished skills live, and how to mirror between them

Claude Code and Claude Desktop's agent/Cowork mode discover skills from two
separate, non-overlapping locations on disk. Writing a finished or updated
skill to only one leaves it invisible in the other — there is no shared
registry between them.

## Claude Code

`~/.claude/skills/<skill-name>/` — a plain folder per skill: `SKILL.md` plus
any bundled `scripts/`, `references/`, `assets/`, `agents/`, `eval-viewer/`.
Nothing beyond folder presence is required; Claude Code appears to discover
skills by scanning this directory directly.

**Landmine (directly observed, not just suspected):** Claude Code's
discovery appears to use a lightweight, line-based frontmatter reader
rather than a full YAML parser. A `description` field written as a
multi-line YAML block scalar —

```yaml
description: >
  Line one of the description
  line two, folded together by YAML
```

— silently drops the skill from discovery, with no error surfaced
anywhere. The fix is mechanical: keep `description` as one continuous
line, however long. Every other frontmatter field (`version`, multi-line
`allowed-tools:` lists, etc.) has been observed working fine — it is
specifically the block-scalar `description` that breaks discovery.

## Claude Desktop (agent / Cowork mode)

Skills live inside an app-managed plugin bundle, tracked by a
`manifest.json` at the bundle's root that lists every skill's id, name,
description, `creatorType` (`anthropic` vs `user`), and an `enabled` flag.
This is Desktop's own bookkeeping — treat it as something to read or
append to, not restructure.

Confirmed path on macOS:

```
~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/<account-id>/<install-id>/skills/<skill-name>/
```

The `<account-id>` and `<install-id>` segments are per-user, per-install
UUIDs — never hardcode a specific pair; locate the actual bundle by
searching for `skills-plugin` under that base directory, and if more than
one install-id folder exists, pick the one with a `manifest.json` that
looks current (or ask if genuinely ambiguous). The equivalent Windows/Linux
paths haven't been confirmed — look for a similarly-named `Claude`
app-support directory (`%APPDATA%\Claude\...` on Windows,
`~/.config/Claude/...` on Linux are reasonable first guesses) rather than
assuming the macOS path translates directly.

A skill's own folder here also contains a packaged `<skill-name>.skill`
bundle file alongside `SKILL.md` — that's a Desktop-specific distribution
artifact. Exclude it when mirroring into Claude Code's folder; Code doesn't
use it and a copy would just go stale.

## Mirroring a finished skill between them

When you can see both locations on disk (true for most local setups where
the user has both apps), after a skill reaches its final state for this
session, mirror it to the other location too:

1. Copy `SKILL.md` and any bundled `scripts/`, `references/`, `assets/`,
   `agents/`, `eval-viewer/` directories as plain files.
2. Exclude Desktop's `<skill-name>.skill` package artifact from anything
   copied into Claude Code's folder.
3. Never hand-edit Desktop's `manifest.json` to register a mirrored copy.
   Desktop manages that file's contents itself; a plain folder dropped into
   its `skills/` directory that the manifest doesn't yet list may or may
   not be picked up automatically by the app (unconfirmed either way). Treat
   the Code-side mirror as the reliable direction, and the Desktop-side
   mirror as best-effort — worth doing, but don't promise the user it's
   guaranteed to register the same way an in-app creation would.
4. If either location isn't present on this machine at all (the other app
   isn't installed, or agent mode has never been used), skip mirroring to
   it rather than speculatively creating the directory structure.

Tell the user which locations you mirrored to. A fresh Claude Code session
(or reopening Desktop) may be needed before the mirrored copy actually
shows up in that surface's available-skills listing.

## If `~/.claude/skills` is dotfiles-managed

Some setups track `~/.claude/skills` through a dotfiles tool (chezmoi is
the common case) instead of treating it as the real source of truth.
Signs to check for before assuming a plain copy is the last step: a
`.chezmoiroot`/chezmoi source tree, or a sibling dotfiles repo with a
`skills/` directory under a path like `private_dot_claude/skills`; ask the
user if it's genuinely ambiguous.

When that's the case:

- The dotfiles repo's source tree — not `~/.claude/skills` directly — is
  authoritative. A skill folder copied straight into `~/.claude/skills/<name>/`
  is local drift until it's pulled back into that source tree; don't report
  the skill as done until it has been.
- Sync direction depends on which copy you actually edited:
  - If you wrote or copied the skill straight into the live path
    (`~/.claude/skills/<skill-name>/`), pull it into the dotfiles source.
    Look for a sync helper in the repo (commonly something like
    `bin/sync-dotfiles.sh`) that runs the tool's own "pull drift into
    source" command (`chezmoi re-add` for chezmoi), or add just the new
    skill directly (`chezmoi add ~/.claude/skills/<skill-name>`).
  - If you edited the dotfiles source tree directly instead (e.g. you were
    already working inside the dotfiles repo), push that out to the live
    path with a **scoped** apply: `chezmoi apply -- ~/.claude/skills/<skill-name>`.
    Scoping to the one skill's target path is safe to run without asking —
    it's narrow and trivially revertible via git. Never run a bare
    `chezmoi apply` as part of this: with no path argument it applies
    *every* pending change across the whole dotfiles-managed home
    directory, including unrelated drift the user hasn't reviewed yet.
  - Either direction, show the user the resulting diff before committing —
    don't commit automatically as part of finishing a skill.
- Never stage Claude Code's own self-regenerating skill cache (commonly a
  directory named `synced` under `~/.claude/skills/`) into the dotfiles
  repo — it's runtime state Code recreates itself, not authored content.
  If the repo's sync tooling already excludes it, leave that exclusion
  alone; if you don't see one, flag the risk to the user rather than
  silently adding it.

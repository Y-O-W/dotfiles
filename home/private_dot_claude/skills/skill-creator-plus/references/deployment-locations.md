# Where finished skills live, and how to get them to each surface

Claude Code reads skills from a folder on disk. Claude Desktop's Chat and
Cowork do **not** — they load only the skills registered on the user's
account. Writing a finished or updated skill to one place leaves it
invisible in the other, and for Desktop, copying a folder is not
deployment at all (see below).

## Claude Code

`~/.claude/skills/<skill-name>/` — a plain folder per skill: `SKILL.md` plus
any bundled `scripts/`, `references/`, `assets/`, `agents/`, `eval-viewer/`.
Nothing beyond folder presence is required; Claude Code appears to discover
skills by scanning this directory directly. A project's own
`.claude/skills/<skill-name>/` works the same way and keeps the skill scoped
to that project.

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
line, however long. Every other frontmatter field (multi-line
`allowed-tools:` lists, etc.) has been observed working fine — it is
specifically the block-scalar `description` that breaks discovery.
`scripts/quick_validate.py` (run by `package_skill.py`) now rejects this.

**Account skills also arrive here.** Skills registered on the account sync
into Claude Code under `~/.claude/skills/synced/<account>_<install>/`
(Claude Code 2.1.273 or later; at session start, then roughly every 10
minutes, per Anthropic's help article "Use skills in Claude"). That folder is
a runtime cache Claude Code recreates itself — never edit it, never commit
it. Directly observed: six skills uploaded to the account showed up in it
within about ten minutes.

## Claude Desktop (Chat and agent/Cowork mode)

Desktop does not discover skills from disk. It keeps a local cache of the
skills registered on the user's account and reconciles that cache against
the account on every sync. On macOS the cache is:

```
~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/<account-id>/<install-id>/
├── manifest.json
└── skills/<skill-name>/
```

`manifest.json` lists each skill's `skillId`, name, description,
`creatorType` (`anthropic` or `user`), `enabled`, `updatedAt`, and — for user
skills — a `backingPluginId`. The IDs are issued by the server (`skill_…`
for user-uploaded skills). It is a cache of server state, not a registry you
can add to. Locate the bundle by searching for `skills-plugin` under the app
support directory; the `<account-id>`/`<install-id>` UUIDs are per user and
per install, so never hardcode a pair. The Windows and Linux paths
(`%APPDATA%\Claude\...`, `~/.config/Claude/...`) are unconfirmed guesses.

**Directly observed (2026-09-23 and 2026-09-28):**

- Six skill folders copied into the cache's `skills/` directory, with no
  manifest entry, were deleted about 30 minutes later. Desktop's log
  (`~/Library/Logs/Claude/main*.log`) recorded
  `[SkillsPlugin] Sync complete: 0 downloaded, 0 failed, 0 removed, 6 orphans cleaned`.
- After the user uploaded the same six as zips, each sync logged
  `1 downloaded, 0 failed, 0 removed, 0 orphans cleaned`, six
  `creatorType: "user"` entries appeared in `manifest.json`, and the folders
  appeared in `skills/`.

So: **never copy a skill folder into this cache and never hand-edit
`manifest.json`.** Neither registers anything, and the folder is cleaned up
at the next sync while the user believes the skill is installed.

### The supported route: upload

Customize → Skills → + → Create skill → Upload a skill (older UI wording:
Settings → Capabilities → Skills → Add skill → Upload skill). Requirements:

- a zip with the skill folder as its root, so `<skill-name>/SKILL.md`
- folder name equal to the skill's `name`
- exactly one `SKILL.md` in the archive (nested ones are rejected)

A `.zip` is verified to work, both when built by hand (`zip -r`, which adds
directory entries) and when built by `scripts/package_skill.py --zip` (same
files, no directory entries): the dialog accepted `skill-creator-plus.zip` from
the packager on 2026-09-28. A `.skill` file uploaded through this dialog is
not verified; the `.skill` route that *is* documented is the **Save skill**
button on a file card in a chat that can present files. There is no upload
API or CLI (open feature request: anthropics/claude-code#93163), so the user
performs the upload in the UI and an agent cannot do it for them. Say that
plainly rather than implying the skill is installed.

After a change, the skill has to be re-zipped and re-uploaded. Uploading a
skill whose name already exists **replaces it in place** — verified on
2026-09-28: the dialog offered to replace the older version, and afterwards
`manifest.json` still held a single entry with the same `skillId` and
`backingPluginId` (only `updatedAt` moved), the bundle folder matched the
local copy file for file, and the sync logged `1 downloaded, 0 failed,
0 removed, 0 orphans cleaned`. No stale duplicate is left behind. The
Claude Code `synced/` copy lags by up to about ten minutes (or until the next
session) before it shows the new version.

### Confirming it worked

```bash
python -m scripts.verify_desktop_registration <skill-name> [<skill-name> ...]
```

It reads `manifest.json` and reports, per skill, whether it is registered,
enabled and present on disk, and whether it has reached Claude Code's synced
mirror. It is read-only. Treat a skill as deployed to Desktop only when this
reports it registered. Whether the skill actually appears in the Chat or
Cowork skill list can't be seen from Claude Code; ask the user to try a
request that should trigger it.

### Scope

Account skills are available on every surface, and Desktop has no
per-project scoping. A skill kept in a project's `.claude/skills/` stays
scoped to that project in Claude Code, but its uploaded twin does not. If a
skill should only ever trigger inside one project, weigh that before
uploading.

## Deploying a finished skill to each surface

1. **Claude Code:** copy `SKILL.md` and any bundled `scripts/`, `references/`,
   `assets/`, `agents/`, `eval-viewer/` directories as plain files into
   `~/.claude/skills/<skill-name>/` (or the project's `.claude/skills/`).
   Leave out packaging artifacts (`.skill`, `.zip`).
2. **Desktop (Chat/Cowork):** package it and hand the file to the user:
   `python -m scripts.package_skill <skill-folder> <output-dir> --zip`, or
   `--all <skills-dir>` for several at once. Write the output outside any
   repo or vault (`~/Downloads/...`) so nothing commits it. Give the click
   path above, then run the verification command once the user says they've
   uploaded.
3. **Once registered,** the account copy syncs into Claude Code as well. A
   personal copy of the same name is then a duplicate, and which one Claude
   Code loads has not been verified. `verify_desktop_registration` flags
   duplicates; decide deliberately which copy is the source of truth (a
   vault- or dotfiles-versioned copy usually is) rather than keeping three
   silently.
4. If Desktop isn't installed or agent mode has never been used, skip the
   Desktop step rather than creating directories speculatively.

Tell the user which surfaces were done, and which need them.

## If `~/.claude/skills` is dotfiles-managed

Some setups track `~/.claude/skills` through a dotfiles tool (chezmoi is
the common case) instead of treating it as the real source of truth. Signs
to check for before assuming a plain copy is the last step: a
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
    skill directly (`chezmoi add ~/.claude/skills/<skill-name>`). chezmoi
    renames some files in its source tree (for example `literal_run_eval.py`,
    `empty___init__.py`); let it do the copying rather than copying by hand.
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

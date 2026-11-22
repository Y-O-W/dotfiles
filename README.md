# Dotfiles

Personal dev environment, managed with [chezmoi](https://www.chezmoi.io/). `home/` is the source
root (set by `.chezmoiroot`); the repo is expected at `~/Developer/personal/dotfiles`.

## Setup

### New machine

1. `xcode-select --install` (if prompted).
2. Install Homebrew:
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Clone to the expected path, then install chezmoi and apply:
   ```sh
   git clone https://github.com/Y-O-W/dotfiles.git ~/Developer/personal/dotfiles
   brew install chezmoi
   chezmoi init --apply --source ~/Developer/personal/dotfiles
   ```
   You're prompted once for your 42 login and email, your personal email and your Muhlert Digital
   email. They're stored in `~/.config/chezmoi/chezmoi.toml` and rendered into `.vimrc`,
   `.gitconfig` and `.gitconfig-muhlert`, never committed.
4. Do the [manual steps](#manual-steps).

`apply` writes the dotfiles, installs oh-my-zsh and its plugins, runs `brew bundle` on
`~/.Brewfile` (moving `postgresql@17` to port 5433), and installs the pinned Ruby via rbenv.

### Existing machine

```sh
cd ~/Developer/personal/dotfiles
bin/sync-dotfiles          # 1. report local drift (changes nothing)
bin/sync-dotfiles <path>…  # 2. pull the drift you want to keep (or --all)
git diff                      # 3. review, then commit and push yourself
git pull --rebase && chezmoi apply   # 4. take changes from other machines
```

- Run the sync script before starting work: edits made directly on a target (`~/.zshrc`,
  `~/.claude/settings.json`) are lost on restore unless pulled into the source.
- JSON files an app rewrites in its own key order (`settings.json`) are compared as data;
  order-only drift is ignored.
- "config file template has changed" warning: run `chezmoi init`. The template sets `sourceDir`,
  so the config keeps pointing at this repo.
- After `brew install`/`uninstall`: `brew bundle dump --file="$HOME/.Brewfile" --force`, then
  `bin/sync-dotfiles ~/.Brewfile`.

### Manual steps

- `ssh-add --apple-use-keychain ~/.ssh/id_ed25519` (the private key is not in this repo).
- `gh auth login` (needed by the git credential helper and `$GITHUB_USERNAME` in `.zshrc`).
- In this repo: `git config --local agent.protectMain true` (opts in to the
  [protect-main hook](#git-hooks); per-repo config can't be carried by chezmoi).
- Mac App Store apps and Rosetta are out of scope.

## Commands

| Command | What it does |
|---|---|
| `chezmoi edit <file>` / `chezmoi cd` | edit the source, then `chezmoi apply` |
| `chezmoi diff` | preview changes |
| `chezmoi apply` | write source to `$HOME` |
| `chezmoi update` | `git pull` and apply |
| `chezmoi status` | managed files that differ from source |
| `chezmoi unmanaged <path>…` | untracked files under a path (never run without a path) |
| `bin/sync-dotfiles [<path>… \| --all]` | report or pull local drift |
| `bin/update-dev-versions` | bump Ruby and Homebrew packages, see [Dev environment](#dev-environment) |
| `bin/newrepo <name> --public\|--private` | scaffold a GitHub repo for an AI coding agent, see below |

### New repos

`bin/newrepo my-app --private` creates `./my-app` with a README, a baseline `.gitignore`, a LICENSE
(public only), `AGENTS.md` extracted from the vault template note and a one-line `CLAUDE.md`, makes
the first commit, creates the GitHub repo and protects `main`: a ruleset for public repos, the
[protect-main hook](#git-hooks) for private ones. Options: `--openspec`, `--gitignore NAME`,
`--owner OWNER`, `--local-only`; see `bin/newrepo --help`. It reads the template from
`~/Obsidian/Template/template_agents_md.md` (override with `NEWREPO_AGENTS_TEMPLATE`).

## What's managed

| Source (under `home/`) | Target |
|---|---|
| `dot_zshrc`, `dot_zprofile`, `dot_aliases` | shell config, login env, aliases |
| `dot_gitconfig.tmpl`, `dot_gitconfig-muhlert.tmpl`, `dot_gitignore_global` | git config, per-org commit email for `~/Developer/work/muhlertdigitalgmbh/` via `includeIf` (emails from chezmoi data), global ignore |
| `dot_git-hooks/` | four global git hooks, registered in `dot_gitconfig.tmpl`, see [Git hooks](#git-hooks) |
| `dot_irbrc`, `dot_pryrc`, `dot_rspec` | IRB, Pry, RSpec |
| `dot_vimrc.tmpl`, `dot_vim/plugin/stdheader.vim` | Vim (42 Norm) and 42 header plugin; login/email from chezmoi data |
| `dot_Brewfile`, `dot_ruby-version` | Homebrew snapshot, pinned rbenv Ruby |
| `private_dot_ssh/private_config` | `~/.ssh/config` (0600) |
| `private_dot_claude/` | `~/.claude/`: settings, global `CLAUDE.md`, hooks, custom skills, see [Claude Code config](#claude-code-config) |
| `private_Library/…/Code/User/settings.json` | VS Code settings |
| `dot_rails-templates/rails_new.rb` | Rails template used by the `rails-new` alias |
| `.chezmoiscripts/` | oh-my-zsh (once), `brew bundle`, Ruby and brand-tokens gems (on change) |
| `.chezmoiexternal.toml` | Externals: the `brand-tokens` skill, cloned at a pinned tag |

- Outside `home/` and not managed: `bin/`, `vendor/`, `README.md`, `LICENSE`.
- Untracked on purpose: `~/.claude/skills/synced/`, `~/.claude/plugins/synced/` (Claude's own caches),
  and runtime state in `~/.claude/` (`projects/`, `cache/`, `history.jsonl`, …).
- `home/.chezmoiignore` skips `.DS_Store` and `__pycache__`.

## Git hooks

Global hooks are config-based (git >= 2.54): each is a `[hook "<name>"]` block in
`home/dot_gitconfig.tmpl` with an `event` and a `command`, pointing at a script in
`home/dot_git-hooks/` (deployed to `~/.git-hooks/`). They run in addition to a repo's own hooks, so
`core.hooksPath` stays unset; that setting would replace `.git/hooks` and need a dispatcher and a
symlink per hook name.

| Hook | Event | Runs in | Does |
|---|---|---|---|
| `strip-ai-trailers` | `commit-msg` | every repo | strips `Co-Authored-By:` lines that mention Claude or Anthropic, and "Generated with Claude" lines; human co-authors are kept |
| `protect-main` | `pre-push` | repos with `agent.protectMain=true` | blocks any push to `main`/`master` |
| `scan-staged-secrets` | `pre-commit` | every repo | blocks the commit when `gitleaks` finds a secret in the staged changes |
| `lint-shell` | `pre-commit` | every repo | blocks the commit on `shellcheck` warnings in staged shell scripts, and on new scripts that break the [shell conventions](#shell-scripts) |

**strip-ai-trailers.** Claude Code's `attribution.commit = ""` only changes what the model is
offered; it does not scrub a message the model writes itself, so this hook is the enforcement for
every tool that commits.

**protect-main.** Opt in per repo with `git config --local agent.protectMain true`; the setting lives
in untracked `.git/config`, which is why [Manual steps](#manual-steps) lists it and `bin/newrepo`
sets it for new private repos. Merging a PR is not affected: it happens on GitHub's side
(`gh pr merge`, the merge button) and never runs `git push`, so the admin bypass for merging your
own PRs keeps working. Why local: this repo's ruleset has an Admin bypass with mode `always`, which
also lets a direct push to `main` through, including by an agent using your credentials.

**scan-staged-secrets.** GitHub's secret scanning and push protection are not available for private
repos on the Free plan (the API returns no security settings for them), so this is the only scan
those repos get. It runs `gitleaks git --staged` (`gitleaks` comes from `dot_Brewfile`) and redacts
its output. Only a found secret blocks (`--exit-code 2`); a missing or broken gitleaks fails open
with a warning. False positive: add the fingerprint it prints to the repo's `.gitleaksignore`.

Limits: an older git ignores the `[hook]` section silently, `--no-verify` skips every hook, and
only new commits and pushes are affected (`scan-staged-secrets` does not scan history already in a
repo). To add a hook, put a script under `home/dot_git-hooks/` and add a `[hook "<name>"]` block.

## Shell scripts

Conventions for every shell script written on this machine (`bin/`, hooks, one-off tools). What a
linter can decide is enforced by `shellcheck` through the `lint-shell` hook; the rest is written
down here because no tool checks it.

| Topic | Rule |
|---|---|
| Language | Bash for anything with logic. POSIX `#!/bin/sh` only for tiny hooks that must run anywhere (`dot_git-hooks/`). Past about 100 lines, or when you parse JSON or need real data structures, write Python instead (like `private_dot_claude/hooks/`). |
| Shebang | `#!/usr/bin/env bash` (or `#!/bin/sh`), never `#!/bin/bash`. `env` finds the first bash on `PATH`, so a Homebrew bash is used when it exists. |
| Bash version | Write for bash 3.2, the stock `/bin/bash` on macOS, because `env bash` lands there when no newer one is installed. No `mapfile`/`readarray`, associative arrays, `${var,,}`, `&>>` or `\|&`. Check with `/bin/bash -n script`. |
| Name | A command you run (`bin/`) has **no extension**, in kebab-case: `newrepo`, `sync-dotfiles`. A file that is only `source`d is a library: `.sh`, not executable, no `set` flags. The caller should not need to know the language. |
| Header | Shebang, then a comment block (what it does, usage, side effects, env overrides), then `set -euo pipefail`. `--help` prints that comment block. |
| Errors | A `die()` that prints `<script>: <message>` to stderr and exits 1; exit 2 for a usage error. Check each dependency with `command -v` before doing anything. |
| Safety | Quote every expansion. `[[ ]]` over `[ ]`. `local` in functions. `mktemp` plus a `trap ... EXIT` for temp files; a failed run must leave nothing half-built. Pass `--` before user-supplied arguments. `printf` over `echo` for data. Guard `"${arr[@]}"` with a length test (bash 3.2 plus `set -u` errors on an empty array). |
| Lint | `shellcheck` clean. A `# shellcheck disable=SCxxxx` needs a reason on the same line. Formatting is by hand (2 spaces); `shfmt` is not enforced because its default style rewrites the aligned one-line `case` arms. |

**Exceptions.** Files chezmoi runs or names (`home/.chezmoiscripts/*.sh.tmpl`, `executable_*`) keep
the names chezmoi needs. Do not edit the `.chezmoiscripts` only to restyle them: `run_onchange_`
and `run_once_` scripts re-run when their content changes.

**Enforcement.** Two hooks, at different moments, running the same `shellcheck --severity=warning`:

- `shell-write-guard.py` is a Claude Code `PreToolUse` hook on `Write` and `Edit`. It denies the call
  *before* the file is written, so the agent gets the finding and can retry. On a new script it checks
  the shebang and refuses an `executable_*.sh` name; on any shell file it blocks only the shellcheck
  findings the call *introduces*, so a legacy script with old warnings can still be edited. It cannot
  see the file mode, files written through Bash, or edits made outside Claude.
- `lint-shell` is a git `pre-commit` hook and the backstop for what the guard cannot see. It runs
  shellcheck on every staged shell script and checks the shebang and name rules (including plain
  versus executable) on *new* scripts only. `git commit --no-verify` skips it.

`~/.shellcheckrc` comes from `home/dot_shellcheckrc`; `shellcheck` from `dot_Brewfile`. The hooks are
the enforcement; this section and the short rule in `~/.claude/CLAUDE.md` are context.

## Claude Code config

`home/private_dot_claude/` deploys to `~/.claude/`: `settings.json` (hook wiring and deny rules for
`git push` to `main`/`master`), `CLAUDE.md` (global rules: only non-inferable ones, each with its
reason, incident and date), `hooks/` (`epic-handoff-nudge.py`, `shell-write-guard.py`, `skill-usage-tracker.py`) and
`skills/`.

Every personal skill and hook lives here, as plain tracked copies deployed by `chezmoi apply`.
Claude Desktop uploads and the `synced/` cache are derived copies, not backups. Vendored
third-party skills (`kepano/obsidian-skills`) have their provenance pinned in
`vendor/kepano-obsidian-skills/UPSTREAM.md`.

One exception: **`brand-tokens` is an external, not a tracked copy.** `home/.chezmoiexternal.toml`
clones `github.com/Y-O-W/brand` into `~/.claude/skills/brand-tokens`, pinned to a release tag;
that repo is its home, so don't `chezmoi add` it or edit it in place. To upgrade, change the tag
(it appears twice) in `.chezmoiexternal.toml` and run `chezmoi apply --refresh-externals`;
`run_onchange_after_30-brand-tokens-gems.sh` then installs the skill's gems.

To find skills that exist only on the Claude account:

```sh
cd ~/.claude/skills/skill-creator-plus
python3 -m scripts.check_skill_backup             # flag skills with no pushed home
python3 -m scripts.check_skill_backup --harvest   # also copy account-only skills out of Desktop's cache
```

## Dev environment

- `bin/update-dev-versions` bumps Ruby to the latest patch of the pinned minor line, upgrades
  Brewfile packages, refreshes the snapshot, applies it and commits (never pushes). It only
  reports, never applies: Ruby minor/major bumps, PostgreSQL major bumps (need `pg_upgrade` or
  dump/restore), and Rails (pinned per project).
- **New apps** use the global Ruby pin in `home/dot_ruby-version` (existing apps keep their own
  `.ruby-version`) and PostgreSQL 17 on port 5433, alongside `postgresql@15` on 5432.
  `rails-new my_app` expands to `rails new -d postgresql -m ~/.rails-templates/rails_new.rb`,
  which sets `port: 5433`.

### Dev server ports

| Tool | Port | Notes |
|---|---|---|
| Rails (Puma) | 3000 | default |
| Next.js | 3001 | overridden (default 3000 clashes with Rails): `next dev -p 3001` |
| Vite | 5173 | default |
| Django | 8000 | default |
| Flask | 5000 | default; AirPlay Receiver may hold it, falls back to 5001 |
| Vue CLI / Webpack | 8080 | default |
| Angular CLI | 4200 | default |
| PostgreSQL | 5432 (`@15`), 5433 (`@17`) | |
| Redis | 6379 | default |

## Notes and history

- Started as a fork of [`lewagon/dotfiles`](https://github.com/lewagon/dotfiles); since 2026-11 it is
  detached from the fork network and has no `upstream` remote.
- Moved from a hand-rolled `install.sh` to chezmoi on 2026-07-14; the old install scripts and loose
  root-level config files are retired. It now covers the whole dev environment: Homebrew,
  rbenv/Ruby, VS Code, SSH, and Claude Code config, skills and hooks.
- Chezmoi gotchas: a bare `run_` prefix in the source tree is treated as a script (use
  `literal_`), and zero-byte files are dropped unless prefixed `empty_`.
- The locally modified `skill-creator` was retired in favour of `skill-creator-plus`; it remains
  in git history.

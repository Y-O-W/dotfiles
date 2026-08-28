
# Development Environment Recovery System - Chezmoi Dotfiles Manager

## Fork status (as of 2026-07-14)

This is a personal fork (`origin` = `Y-O-W/dotfiles`) with `upstream` still pointing at
[`lewagon/dotfiles`](https://github.com/lewagon/dotfiles) for pulling future curriculum updates.

- **Currency:** fully up to date — 0 commits behind `upstream/master` (last upstream commit:
  2025-12-02), plus personal commits on top.
- **Good practices already in place:** fork + upstream remote (get updates without losing
  customizations), no secrets committed (git credentials go through `gh auth git-credential`,
  SSH config only references Keychain).
- **Known gaps (resolved 2026-07-14):** this repo used to be managed via a hand-rolled
  `install.sh` doing raw `ln -s` into `$HOME`, with no dry-run/diff-before-apply or
  per-machine templating. It's now managed with [chezmoi](https://www.chezmoi.io/) instead —
  see the section below. It also contains personal content (e.g. the `render-cv` alias)
  unrelated to the bootcamp template, so it functions as personal dotfiles rather than a
  clean Le Wagon template — which is fine, since that's the intent of this fork.
- **Recommendation (done 2026-07-14):** keep this fork rather than starting a separate
  personal dotfiles repo. Relocated from `~/code/Y-O-W/dotfiles` (the bootcamp's original
  setup convention) to `~/Developer/personal/dotfiles`.
- **Extended (2026-07-14):** this repo now covers the whole local dev environment, not just
  dotfiles — Homebrew packages, rbenv/Ruby, VS Code settings, SSH config, and Claude Code
  config are all chezmoi-managed too. See "First-time setup on a new machine" below. The old
  `install.sh`, `git_setup.sh`, and loose root-level `pryrc`/`zprofile`/`config`/
  `settings.json`/`keybindings.json` files have been retired — everything they used to handle
  now lives under `home/` and is actually applied by `chezmoi apply`, rather than sitting
  around as unapplied reference copies.
- **Verified (2026-08-24):** still 0 commits behind `upstream/master` (last upstream commit
  unchanged, 2025-12-02). `chezmoi diff` turned up real drift: `~/.zshrc` and
  `~/.claude/settings.json` had been edited directly on this machine (PATH dedup, a
  per-project `bin`/`node_modules/.bin` PATH hook, an async-cached `$GITHUB_USERNAME` lookup,
  `zsh-autosuggestions` enabled, plus two extra Claude settings keys) without those changes
  ever being pulled back into the chezmoi source — a real gap for a "recovery" repo, since
  restoring from it would have silently reverted those improvements. Pulled in with
  `chezmoi re-add` and applied. Also fixed a stale README claim (`postgresql@17` no longer
  needs manual starting — the Brewfile now flags it `restart_service: :changed` same as
  `postgresql@15`) and documented the previously-unlisted oh-my-zsh bootstrap script
  (`run_once_after_00-install-oh-my-zsh.sh.tmpl`) and `dot_gitignore_global`.

## Managed with chezmoi

This repo is managed with [chezmoi](https://www.chezmoi.io/). `home/` is the chezmoi source
root (declared via `.chezmoiroot`) and contains every managed file, using chezmoi's naming
conventions (`dot_` for a leading dot, `private_` for tightened permissions, `.chezmoiscripts/`
for install hooks):

| Source path | Target | What it is |
|---|---|---|
| `home/dot_zshrc` | `~/.zshrc` | shell config |
| `home/dot_zprofile` | `~/.zprofile` | login shell env (`brew shellenv`, pyenv PATH) |
| `home/dot_gitconfig` | `~/.gitconfig` | git config/aliases |
| `home/dot_aliases` | `~/.aliases` | personal shell aliases |
| `home/dot_irbrc` | `~/.irbrc` | IRB config |
| `home/dot_pryrc` | `~/.pryrc` | Pry prompt config |
| `home/dot_rspec` | `~/.rspec` | RSpec config |
| `home/dot_vimrc` | `~/.vimrc` | Vim config (C-focused: tabs, 4-width indent, 80-col guide for 42 Norm) |
| `home/dot_Brewfile` | `~/.Brewfile` | Homebrew formulae/casks/taps snapshot |
| `home/dot_ruby-version` | `~/.ruby-version` | pinned default Ruby version for rbenv |
| `home/private_dot_ssh/private_config` | `~/.ssh/config` | SSH config (0700/0600) |
| `home/private_dot_claude/settings.json` | `~/.claude/settings.json` | Claude Code settings (0700 dir) |
| `home/private_Library/private_Application Support/private_Code/User/settings.json` | VS Code `settings.json` | editor settings |
| `home/dot_gitignore_global` | `~/.gitignore_global` | global gitignore (referenced by `dot_gitconfig`'s `core.excludesFile`) |
| `home/dot_rails-templates/rails_new.rb` | `~/.rails-templates/rails_new.rb` | personal Rails app template (Devise, Tailwind, Solid Cable/Queue/Cache, CLAUDE.md, etc.) used by the `rails-new` alias |
| `home/.chezmoiscripts/run_once_after_00-install-oh-my-zsh.sh.tmpl` | — | installs oh-my-zsh and its `zsh-syntax-highlighting`/`zsh-autosuggestions` custom plugins the first time chezmoi runs on a machine |
| `home/.chezmoiscripts/run_onchange_after_10-install-packages-darwin.sh.tmpl` | — | runs `brew bundle` whenever `dot_Brewfile` changes |
| `home/.chezmoiscripts/run_onchange_after_20-bootstrap-ruby.sh.tmpl` | — | installs/sets the pinned Ruby via rbenv whenever `dot_ruby-version` changes |

`README.md` and `LICENSE` at the repo root are outside `home/` and untouched by chezmoi, as
they aren't machine config.

### First-time setup on a new machine

1. Install Xcode Command Line Tools if prompted (`xcode-select --install`) — required by
   Homebrew, and involves a license prompt that can't be scripted.
2. Install Homebrew:
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Install chezmoi and apply this repo:
   ```sh
   brew install chezmoi
   chezmoi init --apply --ssh Y-O-W/dotfiles
   ```
   This one command now does more than write dotfiles — it also:
   - writes `.zshrc`, `.zprofile`, `.gitconfig`, `.gitignore_global`, `.irbrc`, `.pryrc`,
     `.rspec`, `.vimrc`, `.aliases`, `~/.ssh/config`, VS Code `settings.json`, and
     `~/.claude/settings.json` into place,
   - installs oh-my-zsh plus its `zsh-syntax-highlighting`/`zsh-autosuggestions` custom plugins
     (only on first run, if `~/.oh-my-zsh` doesn't already exist),
   - installs every Homebrew formula/cask/tap/vscode-extension/npm-global-package in
     `~/.Brewfile` (including `postgresql@15` and `postgresql@17`, both flagged
     `restart_service: :changed`, so Homebrew starts both automatically on a fresh install since
     both count as newly installed),
   - moves `postgresql@17` to port 5433 (see "New apps default to Ruby 4.0 / PostgreSQL 17"
     below) so it doesn't fail to bind against `postgresql@15` on the default 5432,
   - installs rbenv's pinned Ruby version (`~/.ruby-version`) and sets it as the rbenv global.

By default chezmoi's source directory is `~/.local/share/chezmoi`. On this machine it's
instead pinned to the existing clone (`~/Developer/personal/dotfiles`) via `sourceDir` in
`~/.config/chezmoi/chezmoi.toml` — update that path if the repo is ever moved.

### Manual-only steps

A few things intentionally aren't automated, either because they need a human judgment call
or can't be scripted at all:

- **Load your SSH key into the keychain:** `ssh-add --apple-use-keychain ~/.ssh/id_ed25519`.
  The private key itself is never chezmoi-managed (it's not in this repo) — it needs to
  already exist or be restored from wherever it's backed up first.
- **Authenticate `gh`:** `gh auth login`. Needed for `dot_gitconfig`'s credential helper
  (`gh auth git-credential`) and `dot_zshrc`'s `$GITHUB_USERNAME` (`gh api user`).
- **Mac App Store / GUI-only apps, and Rosetta 2** (`softwareupdate --install-rosetta`, if you
  ever need an Intel-only tool): out of scope for this repo — `brew bundle` doesn't manage MAS
  apps unless run with `--mas`, which is deliberately not used here to keep the Brewfile to
  what Homebrew itself tracks.

### Keeping this in sync

Since the dev environment keeps changing, refresh the snapshot whenever you install/remove a
brew package, gem, or change your rbenv global:

```sh
brew bundle dump --file="$HOME/.Brewfile" --force   # refresh ~/.Brewfile from what's installed
chezmoi re-add ~/.Brewfile                            # pull the refresh into the chezmoi source
chezmoi diff                                          # review before touching anything
chezmoi apply                                         # usually a no-op here; diff already showed the plan
cd "$(chezmoi source-path)" && git add -A && git commit -m "..." && git pull --rebase && git push
```

Bump `home/dot_ruby-version` the same way when you switch Ruby versions — `chezmoi apply` will
install and switch to it automatically on every machine next time you `chezmoi update`.

### Keeping Ruby/Homebrew/PostgreSQL current

`bin/update-dev-versions.sh` automates the safe part of this: it bumps the Ruby pin to the
latest patch within the currently pinned minor line, runs `brew bundle install --upgrade` so
every Brewfile-tracked formula/cask (including `postgresql@15`/`postgresql@17`) is on its
latest point release, refreshes the Brewfile snapshot, applies the change locally, and commits
— but it never pushes, so you can review with `git show` first. Run it with:

```sh
bin/update-dev-versions.sh
```

It deliberately does **not** auto-apply three things, since each needs a human call:
- **Ruby minor/major bumps** (e.g. 3.3.x → 3.4.x or 4.0.x) — new lines can break native
  extensions in existing gems, so the script only reports that a newer line exists.
- **PostgreSQL major-version bumps** (e.g. `postgresql@17` → `postgresql@18`) — this needs
  `pg_upgrade` or a dump/restore of your actual databases, not just a formula swap. The script
  reports when a newer major is available; bump the Brewfile yourself once you've migrated data.
- **Rails** — it's a per-project gem pinned in each app's `Gemfile.lock`, not something dotfiles
  can own globally. The script just flags if the global `rails` gem is outdated; bump each
  project with `bundle update rails --conservative`.

The same applies to any other managed file: if you ever edit a target directly (e.g. tweak
`~/.zshrc` or `~/.claude/settings.json` instead of going through `chezmoi edit`), run
`chezmoi re-add` for that file before you forget — otherwise the live improvement never makes
it into the source and a future restore silently reverts it. `chezmoi status` shows any target
that's drifted from source.

If this loop starts to feel tedious, wrapping it in a single shell alias is a reasonable next
step — not worth pre-building until it actually is.

### New apps default to Ruby 4.0 / PostgreSQL 17

The global rbenv pin (`home/dot_ruby-version`) is `4.0.6`. Any project directory that doesn't
have its own `.ruby-version` picks this up automatically, and `rails new` bakes whatever Ruby
is currently active into the new app's own `.ruby-version` — so this alone is enough for new
apps to start on Ruby 4.0. **Existing** apps are unaffected, since each already has its own
`.ruby-version` (mostly still `3.3.5`) which always takes precedence over the global default.

PostgreSQL needed more than a version bump: `postgresql@17` and `postgresql@15` both default
to port 5432, and `postgresql@15` is already running there serving several existing apps'
databases. Making `postgresql@17` the default on 5432 would have broken those apps, so instead
`postgresql@17` is moved to **port 5433** — both instances now run side by side, `@15` staying
untouched on 5432 for existing apps. This is done automatically by
`run_onchange_after_10-install-packages-darwin.sh.tmpl` (idempotent — safe to re-run) whenever
the Brewfile changes, so a fresh machine ends up in the same state.

Since a plain `rails new -d postgresql` generates a `config/database.yml` with no port set
(defaulting to 5432 → `postgresql@15`), a new app needs to explicitly target 5433 to actually
land on PostgreSQL 17. `home/dot_rails-templates/rails_new.rb` is a personal Rails app template
(Devise, Tailwind, Solid Cable/Queue/Cache, CLAUDE.md, etc.) that does this — its first step
injects `port: 5433` into `config/database.yml` before `after_bundle` runs `db:create`. Scaffold
a new app with:

```sh
rails-new my_app_name
```

(the `rails-new` alias in `home/dot_aliases`, expands to
`rails new -d postgresql -m ~/.rails-templates/rails_new.rb`).

### Local dev server ports

No framework coordinates its default port with any other, so running two dev servers at once
can collide — Rails (Puma) and Next.js both default to **3000**. This table is a personal
reference for what each stack actually uses, so a clash gets caught by reading this instead of
by a "port already in use" error:

| Framework/tool | Port | Notes |
|---|---|---|
| Rails (Puma) | 3000 | framework default, unchanged |
| Next.js | 3001 | overridden — framework default is 3000, same as Rails |
| Vite | 5173 | framework default, unchanged |
| Django | 8000 | framework default, unchanged |
| Flask | 5000 | framework default; macOS AirPlay Receiver often already holds 5000, falls back to 5001 |
| Vue CLI / Webpack dev server | 8080 | framework default, unchanged |
| Angular CLI | 4200 | framework default, unchanged |
| PostgreSQL | 5432 (`@15`), 5433 (`@17`) | see "New apps default to Ruby 4.0 / PostgreSQL 17" above |
| Redis | 6379 | framework default, unchanged |

To apply an overridden port to a project, set it explicitly rather than relying on the
framework default — e.g. for Next.js, `"dev": "next dev -p 3001"` in `package.json`, or
`PORT=3001` in `.env.local`. This table records intent; it isn't chezmoi-managed, since the
actual port is set per-project, not machine-wide.

### Making a change

- `chezmoi edit ~/.zshrc` opens the source file in `$EDITOR`, then run `chezmoi apply` to
  write it back to `~/.zshrc`.
- Or `chezmoi cd` to jump straight into the source directory and edit/commit/push with
  git as usual, then `chezmoi apply` on any machine to pick up the change.

### Common commands

| Command | What it does |
|---|---|
| `chezmoi diff` | Preview what would change before touching anything |
| `chezmoi apply` | Write the source state to the target files in `$HOME` |
| `chezmoi update` | `git pull` the source repo and apply, in one step |
| `chezmoi status` | Show which managed files differ from source |
| `chezmoi source-path` | Print where the source directory lives locally |

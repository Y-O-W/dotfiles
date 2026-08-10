
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
| `home/dot_Brewfile` | `~/.Brewfile` | Homebrew formulae/casks/taps snapshot |
| `home/dot_ruby-version` | `~/.ruby-version` | pinned default Ruby version for rbenv |
| `home/private_dot_ssh/private_config` | `~/.ssh/config` | SSH config (0700/0600) |
| `home/private_dot_claude/settings.json` | `~/.claude/settings.json` | Claude Code settings (0700 dir) |
| `home/private_Library/private_Application Support/private_Code/User/settings.json` | VS Code `settings.json` | editor settings |
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
   - writes `.zshrc`, `.zprofile`, `.gitconfig`, `.irbrc`, `.pryrc`, `.rspec`, `.aliases`,
     `~/.ssh/config`, VS Code `settings.json`, and `~/.claude/settings.json` into place,
   - installs every Homebrew formula/cask/tap in `~/.Brewfile` (including `postgresql@15` and
     `postgresql@17` — `postgresql@15` is flagged `restart_service: :changed` in the Brewfile,
     so Homebrew starts it automatically on a fresh install; `postgresql@17` installs but stays
     stopped),
   - installs rbenv's pinned Ruby version (`~/.ruby-version`) and sets it as the rbenv global.

By default chezmoi's source directory is `~/.local/share/chezmoi`. On this machine it's
instead pinned to the existing clone (`~/Developer/personal/dotfiles`) via `sourceDir` in
`~/.config/chezmoi/chezmoi.toml` — update that path if the repo is ever moved.

### Manual-only steps

A few things intentionally aren't automated, either because they need a human judgment call
or can't be scripted at all:

- **Start `postgresql@17`, if you need it:** `brew services start postgresql@17` (only
  `postgresql@15` auto-starts, since that's the one actually captured as "changed" in the
  Brewfile — see above).
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

If this loop starts to feel tedious, wrapping it in a single shell alias is a reasonable next
step — not worth pre-building until it actually is.

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

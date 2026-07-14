This repository is used by [Le Wagon](https://www.lewagon.com) students.

## Toolset

- [oh-my-zsh](http://ohmyz.sh/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [git](https://git-scm.com/)

## Fork status (as of 2026-07-14)

This is a personal fork (`origin` = `Y-O-W/dotfiles`) with `upstream` still pointing at
[`lewagon/dotfiles`](https://github.com/lewagon/dotfiles) for pulling future curriculum updates.

- **Currency:** fully up to date — 0 commits behind `upstream/master` (last upstream commit:
  2025-12-02), plus 2 personal commits on top.
- **Good practices already in place:** fork + upstream remote (get updates without losing
  customizations), no secrets committed (git credentials go through `gh auth git-credential`,
  SSH config only references Keychain), idempotent symlink-based `install.sh`.
- **Known gaps (resolved 2026-07-14):** this repo used to be managed via a hand-rolled
  `install.sh` doing raw `ln -s` into `$HOME`, with no dry-run/diff-before-apply or
  per-machine templating. It's now managed with [chezmoi](https://www.chezmoi.io/) instead —
  see the section below. It also contains personal content (e.g. the `render-cv` alias)
  unrelated to the bootcamp template, so it functions as personal dotfiles rather than a
  clean Le Wagon template — which is fine, since that's the intent of this fork.
- **Recommendation:** keep this fork rather than starting a separate personal dotfiles repo;
  eventually relocate it under `~/Developer` (currently lives under `~/code`, following the
  bootcamp's original setup convention).

## Managed with chezmoi

This repo is managed with [chezmoi](https://www.chezmoi.io/) rather than the old
`install.sh` symlink script. `home/` is the chezmoi source root (declared via
`.chezmoiroot`) and contains the actual managed dotfiles using chezmoi's `dot_` naming
convention (e.g. `home/dot_zshrc` → `~/.zshrc`). Everything else at the repo root —
`README.md`, `LICENSE`, `install.sh`, `git_setup.sh`, `pryrc`, `zprofile`, `config`
(SSH), `settings.json`/`keybindings.json` (VS Code) — is untouched by chezmoi and kept
only for reference.

### First-time setup on a new machine

```sh
brew install chezmoi
chezmoi init --apply --ssh Y-O-W/dotfiles
```

This clones the repo as the chezmoi source directory and writes `.zshrc`, `.gitconfig`,
`.irbrc`, `.rspec`, and `.aliases` into `$HOME`.

By default chezmoi's source directory is `~/.local/share/chezmoi`. On this machine it's
instead pinned to the existing clone (currently `~/code/Y-O-W/dotfiles`) via `sourceDir`
in `~/.config/chezmoi/chezmoi.toml` — update that path if the repo is ever moved.

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

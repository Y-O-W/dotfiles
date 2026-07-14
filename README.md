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
- **Known gaps:** hand-rolled `install.sh` rather than a dedicated dotfiles manager (chezmoi/
  yadm/stow) — fine at this size, but no dry-run/diff-before-apply or per-machine templating;
  already contains personal content (e.g. the `render-cv` alias) unrelated to the bootcamp
  template, so it functions as personal dotfiles rather than a clean Le Wagon template.
- **Recommendation:** keep this fork rather than starting a separate personal dotfiles repo;
  relocate it under `~/Developer` and repoint the home-directory symlinks (`.zshrc`,
  `.gitconfig`, `.irbrc`, `.vimrc`, `.tm_properties`, `.aliases`, `.rspec`) to the new path.

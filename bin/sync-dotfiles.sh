#!/bin/bash
# Pulls local drift (files edited directly on this machine instead of through
# `chezmoi edit`) into the chezmoi source before you start adding something
# new to the repo -- see issue #20 for why this exists (issue #14 nearly lost
# a hooks config to exactly this).
#
# Shows the drift via `chezmoi diff`, pulls it in via `chezmoi re-add`, then
# leaves the result unstaged so you can review and commit it yourself. Never
# commits automatically -- unlike version bumps, local drift can be either a
# real improvement worth keeping or something you don't actually want in the
# repo, and only you can tell the difference.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v chezmoi >/dev/null 2>&1; then
  echo "chezmoi not found -- install it first (see README.md)." >&2
  exit 1
fi

source_path="$(chezmoi source-path)"
if [[ "$source_path" != "$REPO_ROOT/home" ]]; then
  echo "chezmoi's source path ($source_path) doesn't match this repo ($REPO_ROOT/home)." >&2
  echo "Refusing to re-add against the wrong source tree." >&2
  exit 1
fi

echo "==> Checking for local drift"
diff_output="$(chezmoi diff)"

if [[ -z "$diff_output" ]]; then
  echo "  Nothing has drifted -- source already matches what's on disk."
else
  echo "$diff_output"
  echo
  echo "==> Pulling drift into the chezmoi source"
  chezmoi re-add

  echo
  echo "==> Pulled in. Review before committing:"
  echo "    git -C '$REPO_ROOT' diff"
  echo "    git -C '$REPO_ROOT' status --short"
fi

echo
echo "==> Unmanaged files worth reviewing"
# Scoped to the directories where hand-authored content actually shows up --
# never the whole home directory, which would be mostly runtime state/cache,
# and deliberately NOT ~/.ssh: everything there besides the already-tracked
# `config` is private key material / known_hosts that must never be
# suggested for `chezmoi add`, let alone committed.
# known_exceptions lists entries already deliberately left untracked (e.g.
# ~/.claude/skills/synced, Claude Code's self-regenerating skill cache from
# issue #14) so the report stays a short, glanceable list.
known_exceptions='^\.claude/skills/synced$'
unmanaged="$(chezmoi unmanaged ~/.claude/skills ~/.claude/hooks | grep -vE "$known_exceptions" || true)"
if [[ -z "$unmanaged" ]]; then
  echo "  none"
else
  echo "$unmanaged" | sed 's/^/  /'
  echo "  -> if any of these should be tracked, add them with 'chezmoi add'."
fi

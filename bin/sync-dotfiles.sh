#!/bin/bash
# Finds local drift (files edited directly on this machine instead of through
# `chezmoi edit`) and pulls it into the chezmoi source on request -- see issue
# #20 for why this exists (issue #14 nearly lost a hooks config to exactly this).
#
#   bin/sync-dotfiles.sh              report drift and the diff; change nothing
#   bin/sync-dotfiles.sh <path>...    pull only those files into the source
#   bin/sync-dotfiles.sh --all        pull every genuinely drifted file
#
# Report-only is the default because a bare `chezmoi re-add` sweeps up *every*
# drifted file, including ones unrelated to whatever you're working on -- pulling
# in ~/.claude/settings.json while syncing one skill, for example. Pulling only
# what you name keeps each commit about one thing.
#
# Never commits: local drift can be a real improvement or something you don't
# want in the repo, and only you can tell the difference. Review with `git diff`.
#
# Some JSON files (notably ~/.claude/settings.json) are rewritten by their own
# app in a different key order on every change. If the file is equal as data to
# its source, that's order-only drift: it's reported and skipped, never pulled.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

mode=report
case "${1:-}" in
  "")        ;;
  -h|--help) usage; exit 0 ;;
  --all)     mode=all; shift
             if [[ $# -gt 0 ]]; then echo "--all takes no other arguments." >&2; exit 2; fi ;;
  -*)        echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  *)         mode=paths ;;
esac

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

# `chezmoi status` prints paths relative to the destination directory.
dest="$(chezmoi execute-template '{{ .chezmoi.destDir }}' 2>/dev/null || true)"
dest="${dest:-$HOME}"

# True if $1 (a path relative to $dest) is a plain JSON file whose source and
# target are equal as data, i.e. they differ only in key order or whitespace.
# Anything unparseable, templated, or when python3 is missing counts as *real*
# drift, so the fallback is to show more, never less.
json_order_only() {
  local rel="$1" src
  [[ "$rel" == *.json ]] || return 1
  command -v python3 >/dev/null 2>&1 || return 1
  src="$(chezmoi source-path "$dest/$rel" 2>/dev/null)" || return 1
  [[ -f "$src" && "$src" != *.tmpl ]] || return 1
  python3 - "$src" "$dest/$rel" <<'PY'
import json, sys
try:
    with open(sys.argv[1]) as a, open(sys.argv[2]) as b:
        sys.exit(0 if json.load(a) == json.load(b) else 1)
except Exception:
    sys.exit(1)
PY
}

# First status column = this machine's copy changed since chezmoi last wrote it
# (local drift, what re-add pulls in). A blank first column with a change in the
# second means the *source* is ahead of this machine (e.g. after a `git pull`).
drifted=()
order_only=()
source_ahead=()
while IFS= read -r line; do
  [[ -n "$line" ]] || continue
  code="${line:0:2}"
  rel="${line:3}"
  if [[ "${code:0:1}" != " " ]]; then
    if json_order_only "$rel"; then order_only+=("$rel"); else drifted+=("$rel"); fi
  else
    source_ahead+=("$rel")
  fi
done < <(chezmoi status)

pull() {
  echo "==> Pulling into the chezmoi source"
  for target in "$@"; do
    echo "  $target"
    chezmoi re-add "$target"
  done
  echo
  echo "==> Pulled in. Review before committing:"
  echo "    git -C '$REPO_ROOT' diff"
  echo "    git -C '$REPO_ROOT' status --short"
}

case "$mode" in
  paths)
    pull "$@"
    ;;
  all)
    if [[ ${#drifted[@]} -eq 0 ]]; then
      echo "==> Nothing to pull -- no genuinely drifted files."
    else
      targets=()
      for rel in "${drifted[@]}"; do targets+=("$dest/$rel"); done
      pull "${targets[@]}"
    fi
    ;;
  report)
    echo "==> Checking for local drift"
    if [[ ${#drifted[@]} -eq 0 ]]; then
      echo "  Nothing has drifted -- source already matches what's on disk."
    else
      targets=()
      for rel in "${drifted[@]}"; do targets+=("$dest/$rel"); done
      # --no-pager: chezmoi's default pager is `less`, which would block a report.
      chezmoi diff --no-pager "${targets[@]}"
      echo
      echo "==> Drifted (${#drifted[@]}):"
      for rel in "${drifted[@]}"; do echo "  ~/$rel"; done
      echo
      echo "  Pull only what you mean to:  bin/sync-dotfiles.sh ~/path/to/file ..."
      echo "  Pull all of the above:       bin/sync-dotfiles.sh --all"
    fi
    ;;
esac

if [[ "$mode" == "report" && ${#order_only[@]} -gt 0 ]]; then
  echo
  echo "==> Order-only drift ignored (${#order_only[@]}) -- equal as data, only the key order differs:"
  for rel in "${order_only[@]}"; do echo "  ~/$rel"; done
  echo "  (The app that owns the file rewrites it in its own order; chezmoi status still"
  echo "   lists it. Pulling it would only create a noisy, meaningless commit.)"
fi

if [[ "$mode" == "report" && ${#source_ahead[@]} -gt 0 ]]; then
  echo
  echo "==> Source is ahead of this machine (${#source_ahead[@]}) -- not drift; apply to update this machine:"
  for rel in "${source_ahead[@]}"; do echo "  ~/$rel   (chezmoi apply ~/$rel)"; done
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

#!/bin/bash
# Checks Ruby/Homebrew/PostgreSQL/Rails for available updates and, for the
# safe cases, applies them to the chezmoi source and commits the result.
#
# Safe (applied automatically):
#   - Ruby patch bump within the currently pinned minor line (e.g. 3.3.5 -> 3.3.12)
#   - Homebrew formula/cask point-release upgrades (brew bundle install --upgrade)
#
# Reported only, never applied automatically -- these need a human decision:
#   - Ruby minor/major line changes (gem native-extension compatibility)
#   - PostgreSQL major version changes (needs pg_upgrade or a dump/restore)
#   - Rails (per-project via Bundler, not chezmoi-managed at all)
#
# Never pushes to GitHub -- review the commit and `git push` yourself.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUBY_VERSION_FILE="$REPO_ROOT/home/dot_ruby-version"
BREWFILE="$REPO_ROOT/home/dot_Brewfile"

changed=()

echo "==> Ruby"
current_ruby="$(cat "$RUBY_VERSION_FILE")"
current_minor="${current_ruby%.*}"
latest_patch_in_line="$(rbenv install -l 2>/dev/null \
  | grep -E "^[[:space:]]*${current_minor//./\\.}\.[0-9]+\$" \
  | tr -d ' ' | sort -V | tail -1)"
latest_overall="$(rbenv install -l 2>/dev/null \
  | grep -E '^[[:space:]]*[0-9]+\.[0-9]+\.[0-9]+$' | tr -d ' ' | sort -V | tail -1)"

echo "  pinned: $current_ruby | latest in ${current_minor}.x: ${latest_patch_in_line:-unknown} | latest overall: $latest_overall"

if [[ -n "$latest_patch_in_line" && "$latest_patch_in_line" != "$current_ruby" ]]; then
  echo "  -> bumping pin to $latest_patch_in_line (same minor line, safe patch update)"
  echo "$latest_patch_in_line" > "$RUBY_VERSION_FILE"
  changed+=("home/dot_ruby-version")
else
  echo "  -> already on the latest patch for ${current_minor}.x"
fi

if [[ "${latest_overall%.*}" != "$current_minor" ]]; then
  echo "  NOTE: a newer Ruby line ($latest_overall) exists. Bumping minor/major is a manual call" \
       "(check gem/native-extension compatibility first) -- edit $RUBY_VERSION_FILE yourself."
fi
echo

echo "==> Homebrew (formulae/casks pinned in the Brewfile, point releases only)"
brew bundle install --upgrade --file="$BREWFILE"
echo

echo "==> PostgreSQL"
pinned_pg_majors="$(grep -oE 'postgresql@[0-9]+' "$BREWFILE" | sort -u)"
latest_pg_major="$(brew search '/^postgresql@[0-9]+$/' 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)"
echo "  pinned: $(echo "$pinned_pg_majors" | tr '\n' ' ') | latest major available: postgresql@${latest_pg_major}"
if ! echo "$pinned_pg_majors" | grep -q "postgresql@${latest_pg_major}\$"; then
  echo "  NOTE: postgresql@${latest_pg_major} exists and isn't pinned. Moving to a new major version needs" \
       "pg_upgrade or a dump/restore of your databases -- do this deliberately, not via this script."
fi
echo

echo "==> Rails (global gem, informational only -- real version control is per-project via Bundler)"
gem outdated 2>/dev/null | grep -w '^rails ' || echo "  global 'rails' gem is current"
echo "  Reminder: bump per-project with 'bundle update rails --conservative' inside each app."
echo

echo "==> Refreshing the Brewfile snapshot"
brew bundle dump --file="$BREWFILE" --force
if ! git -C "$REPO_ROOT" diff --quiet -- "$BREWFILE"; then
  changed+=("home/dot_Brewfile")
fi

if ((${#changed[@]} > 0)); then
  chezmoi apply --force "$RUBY_VERSION_FILE" >/dev/null 2>&1 || chezmoi apply
  cd "$REPO_ROOT"
  git add "${changed[@]}"
  git commit -m "Bump pinned versions ($(date +%Y-%m-%d))"
  echo
  echo "==> Committed locally. Review and push yourself when ready:"
  echo "    git -C '$REPO_ROOT' show"
  echo "    git -C '$REPO_ROOT' push"
else
  echo "==> Nothing changed -- everything already current."
fi

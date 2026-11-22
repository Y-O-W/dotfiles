# Global rules (all projects)

Only rules that apply on every task and cannot be inferred from code or docs. Each carries its reason, the incident behind it and the date it was added, so it can be pruned later.

## Shell

- Write files with the Write tool, never with `cat > file <<'EOF'` in Bash. Use Bash for commands only.
  Why: a stray `cat >` without a heredoc or file argument reads stdin, which the Bash tool never provides, so the command hangs until the timeout and the real command after it never runs.
  Incident: a stray `cat > /tmp/dummy` hung a command that should have posted an issue comment; it had happened before on this machine. Added 2026-11-22.
- Never run a command that waits for input (bare `cat`, `read`, interactive prompts). Pass a non-interactive flag or `</dev/null`.
  Why: the Bash tool has no stdin, so a command that waits for input blocks until the timeout.
  Incident: the same hang. Added 2026-11-22.
- Every line of a Bash command must serve the task: no leftover or scratch commands (`cat > /tmp/x`, test echoes) in front of the real command. Reread the command before sending it.
  Why: a prepended scratch command is how the hang above happens, and it stops the real command from running.
  Incident: a later stray `cat > /dev/null` was harmless only because it carried a heredoc. Added 2026-11-22.

## Maintenance

Rules here are dated assumptions: re-check them at each model release. A rule that is still broken after it was added moves to a hook or permission, not to more prose.

# Global rules (all projects)

Only rules that apply on every task and cannot be inferred from code or docs. Each carries its reason.

## Shell

- Write files with the Write tool, never with `cat > file <<'EOF'` in Bash. Use Bash for commands only.
  Why: a stray `cat >` without a heredoc or file argument reads stdin, which the Bash tool never provides, so the command hangs until the timeout and the real command after it never runs. This has recurred on this machine.
- Never run a command that waits for input (bare `cat`, `read`, interactive prompts). Pass a non-interactive flag or `</dev/null`.
  Why: same hang.
- Every line of a Bash command must serve the task: no leftover or scratch commands (`cat > /tmp/x`, test echoes) in front of the real command. Reread the command before sending it.
  Why: the hang above came from a stray `cat > /tmp/dummy` prepended to an otherwise correct command; the real command never ran. A later stray `cat > /dev/null` was harmless only because it carried a heredoc.

# Global rules (all projects)

Only rules that apply on every task and cannot be inferred from code or docs. Each carries its reason.

## Shell

- Write files with the Write tool, never with `cat > file <<'EOF'` in Bash. Use Bash for commands only.
  Why: a stray `cat >` without a heredoc or file argument reads stdin, which the Bash tool never provides, so the command hangs until the timeout and the real command after it never runs. This has recurred on this machine.
- Never run a command that waits for input (bare `cat`, `read`, interactive prompts). Pass a non-interactive flag or `</dev/null`.
  Why: same hang.

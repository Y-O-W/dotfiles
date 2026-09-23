# Usage-log review pass

An alternate entry point into **Improving the skill** — triggered by usage volume rather than a fresh eval/iterate cycle the user kicked off.

## When this runs

- The `skill-usage-tracker` `PostToolUse` hook (`~/.claude/hooks/skill-usage-tracker.py`) injects a nudge into the conversation once a skill crosses its use threshold since the last review.
- Or on demand — the user asks something like "has skill X been useful lately?" or "review skill X's usage."

## What's available

- `~/.claude/skill-usage.jsonl` — one line per `Skill` invocation: `{timestamp, skill, args, session_id, cwd}`. This is a thin index, not the conversation itself — it tells you *how often, when, with what args*, not *what happened*.
- `~/.claude/skill-usage-counts.json` — per-skill `{count, last_nudge_count}`, maintained by the hook. You don't need to read it directly; the nudge message already tells you the count.
- The actual conversation content lives in session transcripts under `~/.claude/projects/**/*.jsonl`, one file per session, keyed by the `session_id` recorded in each log line.

## Procedure

1. **Filter the log** to the skill under review, e.g. `grep '"skill": "<name>"' ~/.claude/skill-usage.jsonl`. This gives every invocation's timestamp, args, and `session_id`.
2. **Don't stop at the log.** It can tell you a skill fired 14 times, but not whether those firings actually helped. Sample several of the transcripts named by those session IDs and look at what happened around each `Skill` invocation: did the user correct the output afterward? Did they redo the step manually right after? Did the skill's own instructions actually get followed? One transcript is noise; several is a pattern — same instinct as "generalize from the feedback" in **Improving the skill**.
3. **Look specifically for:**
   - A skill invoked often whose intended follow-through never happens (output gets manually redone) — a description or logic problem.
   - The same correction recurring across sessions — bake it into the skill instead of leaving it for the human to keep repeating.
   - A skill rarely used despite matching contexts showing up in transcripts — possible under-triggering; revisit via **Description Optimization**.
   - Inputs/args that keep varying in ways the skill doesn't handle well.
4. **If nothing stands out, say so and move on.** This is a light pass across many examples, not a deep audit of one run — don't manufacture a finding to justify the review.
5. **If something is worth fixing**, treat it exactly like feedback from the human-review step of the main loop: go to **Improving the skill** and follow its process (generalize, keep the prompt lean, explain the why, look for repeated work) rather than making an ad hoc edit here.

## Reporting back

Tell the user what you found in plain terms before touching anything — "skill X has been invoked N times since the last review; I looked at M of those sessions and noticed \<pattern\>" — and let them confirm before editing. This pass surfaces candidates; it doesn't silently rewrite skills based on inferred patterns.

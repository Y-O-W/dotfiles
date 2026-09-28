---
name: skill-creator-plus
description: Create new skills, modify and improve existing skills, and measure skill performance — with a landscape-scan step that checks for existing proven skills (anthropics/skills, community directories) before drafting from scratch. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator Plus

Create skills and improve them iteratively: draft → run realistic test prompts (with-skill vs baseline) → user reviews in the eval viewer → revise → repeat → optimize the description → deploy. Work out where the user is (idea, draft, or existing skill) and start there. If they don't want evals ("just vibe with me"), skip them.

Match jargon to the user: "evaluation" and "benchmark" are fine; explain "JSON" and "assertion" unless they've shown they know them.

## Creating a skill

### Capture intent

If the user says "turn this into a skill", extract answers from the conversation first (tools used, steps, corrections, formats) and have them confirm the gaps. Establish:

1. What should the skill enable Claude to do?
2. When should it trigger (phrases, contexts)?
3. What output format?
4. Test cases? Objectively verifiable outputs (file transforms, extraction, codegen, fixed workflows) benefit; subjective ones (style, art) often don't. Suggest a default; the user decides.

### Interview and research

Ask about edge cases, formats, example files, success criteria and dependencies before writing test prompts. Use available MCPs for research, in parallel via subagents if you have them.

**Landscape scan (before drafting from scratch):** look for an existing skill that solves or nearly solves the problem:
- `github.com/anthropics/skills`: Anthropic's official repo. Prefer adapting a match over writing new.
- Community sources: search the web and GitHub (e.g. repos containing a `SKILL.md` that matches the task's keywords). Weigh trust signals (official/verified, stars, recency). Open any directory or aggregator site before citing it; don't name one from memory, since a made-up source sends the user chasing something that isn't there.

If a close match turns up, tell the user and ask whether to adapt it (layering their conventions on top) or draft from scratch anyway. Don't skip this silently: a five-minute search can save a whole iterate cycle. If nothing turns up, say so briefly and move on.

### Write the SKILL.md

- **name**: skill identifier.
- **description**: the primary trigger mechanism. Say what the skill does AND when to use it; all "when" info goes here, not the body. Claude undertriggers, so be a little pushy (e.g. append "Use whenever the user mentions dashboards, metrics, or company data, even if they don't say 'dashboard'"). Keep it on **one continuous line**: Claude Code silently drops a skill whose description is a multi-line YAML block scalar (`description: >`), with no error. `scripts/quick_validate.py` rejects this.
- **compatibility**: required tools or dependencies (optional, rarely needed).
- **body**: the instructions.

```
skill-name/
├── SKILL.md (required: YAML frontmatter with name + description, then Markdown)
├── scripts/     executable code for deterministic or repetitive tasks
├── references/  docs loaded into context as needed
└── assets/      files used in output (templates, icons, fonts)
```

**Progressive disclosure:** metadata is always in context; the SKILL.md body loads whenever the skill triggers, so keep it under 500 lines and split the rest into `references/` with pointers saying when to read each; bundled resources load as needed (scripts can run without loading). Give reference files over 300 lines a table of contents. For multi-domain skills, keep the workflow and selection logic in SKILL.md and one reference per variant (`aws.md`, `gcp.md`), so Claude reads only the relevant one.

**Safety:** no malware, exploit code, misleading skills, or anything for unauthorized access or data exfiltration. A skill's behavior shouldn't surprise the user given its description. Roleplay skills are fine.

**Style:** imperative form. Explain *why* instead of shouting MUSTs, and write for the general case, not only the test examples. Define output formats with an explicit template and include Input/Output examples. Draft first, then re-read with fresh eyes.

### Test cases

Write 2-3 realistic prompts, the kind a real user would type. Show them ("Do these look right, or do you want to add more?"), then run them. Save to `evals/evals.json` with prompts only; assertions come later while runs are in progress. Full schema in `references/schemas.md`.

```json
{"skill_name": "example-skill", "evals": [{"id": 1, "prompt": "User's task prompt", "expected_output": "Description of expected result", "files": []}]}
```

## Running and evaluating test cases

This is one continuous sequence; don't stop partway. Don't use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/`, as a sibling of the skill directory. Exception: if the skill lives under `~/.claude/skills/`, use a persistent location outside any repo or vault (e.g. `~/skill-workspaces/`). Claude Code scans that folder, dotfiles tooling tracks it, and the baseline snapshot holds a full `SKILL.md` copy, so a workspace inside would register as a second copy of the skill. Organize by `iteration-N/`, then one directory per test case (`eval-0/` or a descriptive name). Create directories as you go.

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn a with-skill and a baseline subagent together, so they finish around the same time.

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about, e.g. "the .docx file">
```

**Baseline:** for a new skill, no skill at all (same prompt, save to `without_skill/outputs/`). For an existing skill, the old version: before editing, `cp -r <skill-path> <workspace>/skill-snapshot/`, point the baseline at the snapshot, and save to `old_skill/outputs/`.

Write an `eval_metadata.json` in each eval directory (assertions may be empty for now), with a descriptive `eval_name` (also used for the directory). Recreate it for any new or modified eval prompt; it doesn't carry over between iterations.

```json
{"eval_id": 0, "eval_name": "descriptive-name-here", "prompt": "The user's task prompt", "assertions": []}
```

### Step 2: While runs are in progress, draft assertions

Draft quantitative assertions for each test case and explain them to the user (if some exist in `evals/evals.json`, review and explain those). Good assertions are objectively verifiable and have descriptive names that read clearly in the viewer. Don't force assertions onto subjective outputs; judge those qualitatively. Write them into `eval_metadata.json` and `evals/evals.json`, and tell the user what the viewer will show.

### Step 3: Capture timing as runs complete

Each subagent's completion notification carries `total_tokens` and `duration_ms`. Save them immediately to `timing.json` in the run directory, one notification at a time; this data isn't persisted anywhere else.

```json
{"total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3}
```

### Step 4: Grade, aggregate, and launch the viewer

1. **Grade each run:** spawn a grader subagent (or grade inline) following `agents/grader.md`, and save `grading.json` in each run directory. The expectations array must use the fields `text`, `passed`, `evidence` exactly; the viewer depends on them. Check programmatically checkable assertions with a script, not by eye.
2. **Aggregate:** from the skill-creator-plus directory, run `python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>`. It writes `benchmark.json` and `benchmark.md` (pass_rate, time, tokens per configuration, mean ± stddev, delta). List each with_skill run before its baseline. For a hand-built `benchmark.json`, follow `references/schemas.md`.
3. **Analyst pass:** read the benchmark for patterns the aggregates hide (see "Analyzing Benchmark Results" in `agents/analyzer.md`): assertions that pass regardless of skill, high-variance (flaky) evals, time/token tradeoffs.
4. **Launch the viewer** (always with `generate_review.py`; never write custom HTML):
   ```bash
   nohup python <skill-creator-plus-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, add `--previous-workspace <workspace>/iteration-<N-1>`. With no display (Cowork, headless), use `--static <output_path>` for a standalone HTML file instead; "Submit All Reviews" then downloads `feedback.json`, which you copy into the workspace for the next iteration.
5. **Tell the user** what they'll see: an *Outputs* tab (one test case at a time: prompt, output files, formal grades, a feedback box that auto-saves, and last iteration's output and feedback from iteration 2) and a *Benchmark* tab (pass rates, timing, tokens, per-eval breakdowns, analyst notes). They navigate with prev/next or arrow keys, click "Submit All Reviews" when done, then come back and tell you.

### Step 5: Read the feedback

Read `feedback.json` (`{"reviews": [{"run_id": "eval-0-with_skill", "feedback": "...", "timestamp": "..."}], "status": "complete"}`). Empty feedback means the user was fine with it; focus on the cases with specific complaints. Then stop the viewer: `kill $VIEWER_PID 2>/dev/null`.

## Improving the skill

**Alternate entry point:** if a `skill-usage-tracker` hook nudge appears ("skill X has hit N uses since the last review"), or the user asks how a skill has performed in real use, read `references/usage-log-review.md` first. It covers sampling `~/.claude/skill-usage.jsonl` and the transcripts it points to. Once something is worth fixing, treat it like any other feedback.

**How to think about it:**
1. **Generalize from the feedback.** The skill will run across many prompts, and you're iterating on a few. Avoid fiddly overfit fixes and oppressive MUSTs; for a stubborn issue, try a different metaphor or working pattern.
2. **Keep the prompt lean.** Read the transcripts, not just the outputs. If the skill makes the model waste time on unproductive steps, cut the part that causes it.
3. **Explain the why.** Capable models act better on understood reasons than rote rules. Understand what the user actually meant, even from terse or frustrated feedback, and pass that understanding into the instructions. ALWAYS/NEVER in caps is a yellow flag: reframe with the reasoning.
4. **Bundle repeated work.** If every test run independently wrote the same helper (`create_docx.py`, `build_chart.py`), write it once into `scripts/` and tell the skill to use it.

Draft a revision, re-read it fresh, and take your time; this step matters more than speed.

**The loop:** apply improvements → rerun all test cases into `iteration-<N+1>/`, baselines included (`without_skill` stays constant for a new skill; for an existing one, choose the original version or the previous iteration) → launch the viewer with `--previous-workspace` → wait for the user's review → read feedback → repeat. Stop when the user is happy, all feedback is empty, or progress stalls. Then deploy (below): an improved skill that exists only where you edited it isn't finished.

## Advanced: Blind comparison

For a rigorous "is the new version actually better?", give two outputs to an independent agent without saying which is which, then analyze why the winner won. Follow `agents/comparator.md` and `agents/analyzer.md`. Optional, needs subagents; the human review loop is usually enough.

## Description Optimization

The description decides whether Claude invokes the skill. After creating or improving a skill, offer to optimize it.

**How triggering works:** skills appear in `available_skills` as name + description, and Claude consults one only for tasks it can't easily handle itself. Simple one-step queries ("read this PDF") may not trigger even a perfect description, so eval queries must be substantive enough to benefit from a skill.

### Step 1: Generate trigger eval queries

Create 20 queries, saved as `[{"query": "...", "should_trigger": true}, ...]`: 8-10 should-trigger, 8-10 should-not-trigger. They must be realistic and detailed, as a real Claude Code or Claude.ai user would type them: file paths, job context, column names, company names, backstory, plus some lowercase, typos and casual phrasing, in mixed lengths. Focus on edge cases, not clear-cut ones. Bad: "Format this data". Good: "ok so my boss just sent me this xlsx (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants a profit margin % column. revenue is in col C and costs in D i think".

- **Should-trigger:** varied phrasings, formal and casual; cases where the user never names the skill or file type but clearly needs it; uncommon use cases; cases where this skill competes with another but should win.
- **Should-not-trigger:** near-misses that share keywords or concepts but need something else: adjacent domains, ambiguous phrasing where naive keyword matching would fire, cases where another tool fits better. Obviously irrelevant negatives ("write a fibonacci function" against a PDF skill) test nothing.

### Step 2: Review with the user

Bad queries produce bad descriptions, so don't skip this. Read `assets/eval_review.html` and replace `__EVAL_DATA_PLACEHOLDER__` (the JSON array, unquoted: it's a JS assignment), `__SKILL_NAME_PLACEHOLDER__` and `__SKILL_DESCRIPTION_PLACEHOLDER__`. Write it to a scratch directory (a session scratchpad if your system prompt names one, else `mktemp -d`) and `open` it. The user edits queries, toggles should-trigger, adds/removes entries, and clicks "Export Eval Set", which downloads `~/Downloads/eval_set.json` (check for the newest copy, e.g. `eval_set (1).json`).

### Step 3: Run the optimization loop

Tell the user it will take a while, save the eval set to the workspace, and run in the background:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt so the test matches what the user experiences. Tail the output periodically and report the iteration and scores. The loop splits the set 60% train / 40% held-out test, runs each query 3 times per description, has Claude propose improvements from the failures, and re-evaluates up to 5 times. It opens an HTML report and returns JSON with `best_description`, chosen by test score to avoid overfitting.

### Step 4: Apply the result

Put `best_description` into the frontmatter (still one line), show the user before/after, and report the scores.

## Deploying a finished skill locally

A finished skill must be visible wherever the user works. Claude Code reads `~/.claude/skills/<name>/`. Desktop's Chat and Cowork load only skills registered on the account, and uploading is the only way to register one; a folder copied into Desktop's app directory is deleted at its next sync. If `~/.claude/skills` is dotfiles-managed (chezmoi etc.), copying into it isn't the last step either. Evidence and per-surface procedures: `references/deployment-locations.md`.

Run these in order after any pass that changed files (skip what doesn't apply and say which; this assumes local Claude Code with chezmoi):

1. **Validate:** `python -m scripts.quick_validate <skill-folder>`; delete any `__pycache__` your runs created.
2. **Pull into the dotfiles source:** the dotfiles repo's `bin/sync-dotfiles.sh <changed paths>` (see the dotfiles section of `references/deployment-locations.md`) for files chezmoi already tracks, and `chezmoi add <path>` for any file you *created*, since the sync script only reports new files and one left out would reach Desktop but never git. Don't commit; that's the user's call.
3. **Package and reveal:** `python -m scripts.package_skill <skill-folder> ~/Downloads/upload --zip`, then `open -R` the zip (`--all <skills-dir>` packages several). With a file-delivery tool (`present_files`, `SendUserFile`), run it without `--zip` and send the `.skill` instead; its **Save skill** button installs it when the org allows.
4. **Hand off:** tell the user to commit and push the dotfiles repo and to upload the zip (Customize → Skills → + → Create skill → Upload a skill, accepting the replace prompt). You can do neither; say so rather than implying the skill is installed.
5. **Verify after they confirm:** `python -m scripts.verify_desktop_registration <skill-name> ...` (read-only: registered in Desktop's manifest? reached the synced mirror? duplicated as account plus personal copy?) and `python -m scripts.check_skill_backup` (flags skills with no pushed git home; `--harvest` copies an account-only skill out of Desktop's cache). Never edit Desktop's manifest or its neighboring folders.

Until steps 4-5 are done, Desktop and the synced mirror hold the old version and the change has no pushed home. Every skill needs exactly one git-backed home because the account copy is not a backup (see "One home per skill" in the deployment reference).

## Claude.ai and Cowork

Claude.ai has no subagents and Cowork has no browser or display. Read `references/environments.md` before running test cases in either. Two things hold everywhere: generate the eval viewer with `eval-viewer/generate_review.py` (add `--static <path>` with no display) and put it in front of the user *before* you judge outputs yourself, and when updating an existing skill keep its original name and deploy the update to every surface it's used from.

## Reference files

- `agents/grader.md`: evaluate assertions against outputs
- `agents/comparator.md`: blind A/B comparison of two outputs
- `agents/analyzer.md`: why one version beat another; analyzing benchmarks
- `references/schemas.md`: JSON structures (evals.json, grading.json, benchmark.json, ...)
- `references/usage-log-review.md`: review real-world usage logs and transcripts, then feed findings into the improvement loop
- `references/environments.md`: Claude.ai (no subagents) and Cowork (no display) adjustments; updating an existing skill there
- `references/deployment-locations.md`: where skills live per surface, the upload procedure, dotfiles sync, the one-home-per-skill backup rule

If you have a TodoList, add the steps above so none get forgotten; in Cowork include "Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases".

---
name: change-to-github-epic
description: Use after /opsx:propose completes and before /opsx:apply, when an OpenSpec change proposal needs to be broken into a GitHub epic with linked issues, a dependency-ordered roadmap, and a developer resource mapping. Trigger phrases: "create an epic", "break this into GitHub issues", "roadmap this change", "who should work on this", "turn this proposal into issues".
version: 1.1.0
---

# Change → GitHub Epic

Converts an OpenSpec change proposal into a structured GitHub epic: linked
issues, a dependency-ordered roadmap, and a developer resource mapping —
drafted for review, never created without explicit confirmation.

## When to use this skill

Run this immediately after `/opsx:propose` has generated a change folder's
artifacts, and before running `/opsx:apply`. This is planning work, not
implementation — the goal is to translate an already-drafted change into
something the team can plan a sprint around.

Do not run this on a change that hasn't been proposed yet, and do not run
it as a substitute for `/opsx:apply` — this skill never writes code.

## Resolving which change

- If invoked with an argument naming a change (or given a path), use that
  change directly.
- Otherwise, list changes (e.g. `openspec list --json`) and find ones whose
  planning artifacts are complete (apply-ready). If exactly one matches,
  use it. If zero or more than one match, ask the user which change to use
  before reading any artifact files — don't guess from conversation context
  alone if it's ambiguous.

## Inputs

Read, in this order, from the relevant change folder
(`openspec/changes/<name>/`):

1. `proposal.md` — scope, intent, what's in/out
2. `design.md` — technical approach; the primary source for dependency detection
3. `tasks.md` — the ordered task list; source material for individual issues
4. `specs/` (delta specs) — cross-check that no requirement is missing an issue

If a project-level `CLAUDE.md` or `AGENTS.md` contains a team/ownership
section (developer names mapped to domains, e.g. "creators/ → Dev B"), read
it too — this is the source for the resource mapping step. If no such
section exists, produce the roadmap without assigning names, and flag
that ownership mapping needs manual input.

## Determining the target repo and project

- Confirm the target GitHub repo from the change's working tree, e.g.
  `git remote -v`. If there's exactly one remote, use it. If there are
  multiple remotes, or none, ask which repo the issues should live in —
  don't default to guessing.
- Confirm the target GitHub Project (the board, e.g.
  `github.com/users/<owner>/projects/<n>`) from what the user names
  explicitly — a URL or a title. If none was given, ask; don't assume a
  default project.

## Workflow

### 1. Draft the epic

The epic is the single top-level artifact — its body should contain the
full picture, not just scope and intent. Compose it from the outputs of
steps 2–5 below, structured as:

- **Title:** the change name, in plain language (not the kebab-case folder name)
- **Summary:** scope and intent from `proposal.md`, condensed to a few sentences
- **Out of scope:** carried over from `proposal.md` if present
- **Issue checklist:** every issue from step 2, as a linked checklist item
- **Roadmap:** the wave breakdown from step 4, embedded directly in the epic body
- **Dependencies:** the issue-to-issue dependency map from step 3
- **Resource mapping:** the ownership assignments from step 5

The epic is not just a header issue that links out to separate planning
docs — it should be readable top to bottom as the single place the team
goes to understand what's being built, in what order, by whom, without
needing to open every linked issue first.

### 2. Convert tasks into issues

Walk `tasks.md` top to bottom. Group related sub-tasks into a single issue
where they represent one reviewable unit of work; don't create one issue
per checklist line if the checklist is already a natural sequence within
one task. Each issue should include:

- A title derived from the task
- Acceptance criteria pulled from the corresponding delta spec scenario,
  if one exists
- A reference back to the OpenSpec change folder path, so reviewers can
  trace the issue to its source spec

### 3. Identify dependencies

Read `design.md` for technical ordering constraints (e.g., "requires the
new `creators` table migration before the profile UI can be built"). Two
issues are dependent if one's implementation is a technical prerequisite
for the other, not merely if they're related in subject matter. Record
dependencies explicitly, issue-to-issue — this feeds directly into both
the epic's dependency section and the wave grouping in step 4, and into
the native blocked-by/blocking links created in "Creating the epic and
issues in GitHub" below.

### 4. Propose a wave-based roadmap

Group issues into waves:

- **Wave 1** — issues with no dependencies; can start immediately, in parallel
- **Wave 2+** — issues that depend on a prior wave's completion

Within a wave, issues touching different OpenSpec domains (see the spec's
domain folder, e.g. `creators/`, `auth/`) can run in parallel; issues
touching the same domain should generally be sequenced to avoid merge
conflicts, even without a hard technical dependency.

### 5. Suggest resource mapping

If ownership information was found in step 1 (Inputs), map each issue to
the developer who owns that domain. If a domain has no established owner,
leave it unassigned and flag it rather than guessing. This same
never-guess rule applies to any other project field that represents a
judgment call (priority, effort, due dates) — see Explicit boundaries.

### 6. Present and stop

Output the full epic — with the issue checklist, roadmap, dependencies,
and resource mapping all embedded in its body as described in step 1 —
as a single reviewable block. **Do not create anything in GitHub yet.**
End the turn here and wait for explicit confirmation on:

- The epic and issue breakdown itself (is the grouping right?)
- The proposed roadmap and wave sequencing
- The resource assignments, especially any that were guessed rather than
  sourced from an ownership doc

Only after explicit confirmation, proceed to create the epic and issues
in GitHub as described below.

## Output format

Present the draft in this structure so it's easy to scan and approve or
correct piece by piece. Note that everything nests inside the epic —
there is no separate top-level roadmap or resource section:

```markdown
## Epic: <title>
<summary>

**Out of scope:** ...

### Issues
- [ ] #1 <title> — depends on: none
      Acceptance criteria: ...
- [ ] #2 <title> — depends on: #1
      Acceptance criteria: ...

### Roadmap
**Wave 1 (parallel)**
- #1 → <owner or "unassigned">

**Wave 2**
- #2 → <owner or "unassigned"> (depends on: #1)

### Notes
- Flag any unassigned issues or guessed dependencies here.
```

## Creating the epic and issues in GitHub

Once the draft is confirmed, prefer the GitHub CLI (`gh`) when it's
available and authenticated (`gh auth status`). Use GitHub's native
relationship features rather than tracking structure only in prose:

- `gh issue create --parent <epic-number>` links a sub-issue to the epic
  natively (populates GitHub's own sub-issue progress, not just a
  hand-written checklist).
- `gh issue create --blocked-by <n1,n2>` (or `--blocking`) encodes the
  dependency map from step 3 as real tracked relationships.
- `gh issue create -p "<project title>"` (or `--project`) adds the issue
  to the target project in the same call.

**Creation order matters.** The epic has no parent and must be created
first. Each sub-issue can then set `--parent` to the epic's number.
Walk the wave order from step 4 — an issue with `--blocked-by` deps must
be created after the issues it depends on, so their numbers already
exist to reference.

**The epic body has a chicken-and-egg problem.** It can't link real issue
numbers until the sub-issues exist, but the sub-issues want `--parent`
pointing at the epic, which must exist first. Resolve this in two passes:
create the epic first with a placeholder note in place of the
issue/roadmap/dependency sections (e.g. "sub-issues and roadmap to be
filled in once created"), create all sub-issues against it, then
`gh issue edit <epic-number>` to rewrite the body with the real checklist,
roadmap, and dependency sections per the Output format template.

**Custom project fields.** Check what fields the target project has (e.g.
`gh project field-list <n> --owner <owner>`) and what a newly added item
defaults to (`gh project item-list <n> --owner <owner>`) before setting
anything manually — many projects already default new items into a
sensible "not started" status. Only set fields with an obvious,
non-judgment default. Never set Priority, Effort, due dates, or any other
field representing a business/personal judgment call without an explicit
source — same rule as resource mapping in step 5, generalized to any
custom field, not just developer names.

## Verification

After creating the epic and all issues, confirm the sequence actually
completed rather than assuming it did — an interrupted or partially
failed run should never be reported as a clean success:

- Confirm every planned issue was created. `gh issue view <epic-number>
  --json subIssuesSummary` should report a total matching the planned
  issue count.
- Spot-check that dependency links landed as intended, especially on the
  issues with the most dependencies.
- Report the epic URL and each issue's URL/number back to the user; if
  anything failed to create or link, say so explicitly rather than
  omitting it from the summary.

## Explicit boundaries

- Never call any GitHub-creating action before the person has reviewed
  and confirmed the draft.
- Never guess a developer's ownership assignment, a priority, an effort
  estimate, or any other project field that represents a judgment call —
  always flag these as unset/unassigned instead of presenting them as
  settled.
- Never guess which repository or which GitHub Project to file into —
  resolve explicitly (see "Determining the target repo and project") or
  ask.
- Never use this skill to skip or replace `/opsx:apply` — it produces
  planning artifacts for the team, not code.

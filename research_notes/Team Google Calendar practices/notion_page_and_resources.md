# Notion page "Software - Calendar" and the resources it names

Scope: the Notion task page "Software - Calendar" (id 421ed4002a8080348bc4f29386228a7b), every resource it lists, and related Notion pages found by search that give calendar and Muhlert Digital team context. Read 2026-11-23. Read only; nothing was edited. "Page says" items are reported faithfully; commentary is under Inferences.

Source shorthand used below:
- [Notion page](https://app.notion.com/p/yowfactor/Software-Calendar-421ed4002a8080348bc4f29386228a7b) = the page itself (last edited 2026-11-23 15:41 UTC; database "YOWfactor - Task"; Status InProgress; Timeline 2026-01-01 to 2026-01-31; Project "YOWfactor - Software - 2026").
- [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40) = GitHub epic "Agentic Workflow - Calendar - Planning", open, created 2026-11-15, updated 2026-11-23, no comments.
- [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md) = local Obsidian note `software_calendar.md`, status draft, updated 2026-11-16.
- [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46) = Notion task "Muhlert - Productive - Setup" (edited 2026-11-23).
- [Muhlert Notes page](https://app.notion.com/p/39fed4002a8080739409fa5ced3a3e00) = Notion "Notes - Muhlert Digital GmbH" (edited 2026-11-23).
- [Onboarding page](https://app.notion.com/p/39fed4002a808019b545d1a45ccfef96) = Notion event "16.07.26 - Onboarding - Nina".

## What does the page contain: goals, current setup, conventions, tools, open questions, TODOs?

### Takeaway
The page is a short, structured working note (Goal / Setup / Process / Feature / Technology / Resource / Question). It sets the goal of making the calendar the central personal and professional productivity tool with AI-native workflows, defines a weekly (Sunday) and daily (evening) planning routine, defines four work event types and three personal event types along two axes (busy vs free, time-tracked vs not), and ends with four open questions: calendar sharing direction, whether the many purpose calendars are overkill, connecting multiple Google calendars to Claude, and naming conventions that let AI agents derive time-tracking context from event titles.

### Cited Findings
Verbatim-faithful content of the page (all from [Notion page](https://app.notion.com/p/yowfactor/Software-Calendar-421ed4002a8080348bc4f29386228a7b)):

**Goal**
- "adopt best practices using a calendar as the most important personal and professional productivity tool".
- "use ai native/enabled workflows to make planning personal and work life easier".

**Setup**
- Personal Calendar.
- Work Calendar -> Permanent Employee; "is connected to a time tracking software (e.g. Productive.io)".
- Work Calendar -> Self Employed; "is connected to a time tracking software (e.g. Productive.io)".

**Process**
- "weekly planning session on Sunday to plan the next week -> window looking back/forward 2 weeks".
- "daily planning session in the evening for the next day -> verify conflicts, rearrange for productivity gains".
- Work Calendar - Event Type:
  - meeting -> scheduled event with attendees, busy/blocked, time tracked.
  - blocker -> scheduled event without attendees, busy/blocked, time tracked.
  - flexible -> scheduled event without attendees, free/flexible, time tracked.
  - reminder -> scheduled event without attendees, free/flexible, not time tracked.
- Personal Calendar - Event Type:
  - meeting -> with attendees, busy/blocked.
  - blocker -> without attendees, busy/blocked.
  - flexible -> without attendees, free/flexible.
  - (no "reminder" type and no time-tracking attribute on the personal side.)

**Feature** (calendar features of interest): reminder, task, label, multiple calendars.

**Technology**: Google Calendar; Google Calendar MCP; Claude Web, Claude Desktop, Claude Code; Productive; Productive MCP.

**Resource**: GitHub issue Y-O-W/dotfiles#40; local vault note `/Users/yowfactor/Obsidian/Software/software_library/software_calendar.md`; a self-link to the Notion page; the Google Calendar web app URL (calendar.google.com).

**Question** (open questions, verbatim in substance):
1. "Do I connect/share my work calendar to my personal calendar or vice versa? Or a both connected/shared to each other?"
2. Personal and self-employed calendars are structured in one Google Workspace account with multiple calendars by event type: business vs personal; health -> sport, doctor etc.; routine -> "generic structuring of the day/week, not actual planned events". The page says "this feels too much and can probably be done easier with other calendar features".
3. "Is it possible to connect multiple Google calendars to Claude?"
4. "What is best practice for naming conventions for calendar entries - especially in a team/work environment - where AI agents need to be able to get context from the entry title (e.g. to track time properly)?"

- No explicit TODO checklist exists on the page; the open questions function as the to-do list — [Notion page](https://app.notion.com/p/yowfactor/Software-Calendar-421ed4002a8080348bc4f29386228a7b).
- The event-type taxonomy and feature list on the page are identical to notes under "20.11.26 - Meeting - Sebastian" on the Productive Setup page, i.e. they were discussed with a Muhlert teammate (Sebastian) in the context of the Productive rollout — [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46).
- Notion Calendar is not mentioned anywhere on the page — [Notion page](https://app.notion.com/p/yowfactor/Software-Calendar-421ed4002a8080348bc4f29386228a7b).

### Inferences
- The two axes on the page (busy/free and tracked/untracked) map neatly onto Google Calendar's "Show as Busy/Free" field plus some marker for "time tracked"; the page does not yet say how "time tracked" or the event type would be encoded (title prefix, colour, label, separate calendar, description tag). That is the gap behind question 4.
- "Self Employed" and "Permanent Employee" work calendars are listed as distinct setups, suggesting the user wants a convention that works whether they act as a Muhlert employee/contractor or as their own company (YOWfactor UG). Which of these the user currently is at Muhlert is not stated on the page.
- The page's Timeline (January 2026) is stale relative to its InProgress status and edit date (2026-11-23); it is likely a reused task card.

### Gaps
- The page does not define naming conventions, colours, or labels; it only asks for best practice.
- The page does not state the size of the purpose-calendar set; the vault note and issue fill this in (see next section).
- Notion Calendar and Notion's own calendar features are not mentioned; no evidence the user uses Notion Calendar.

## What resources are linked or mentioned, and what does each recommend?

### Takeaway
The page links four resources. Two are substantive and both are the user's own prior research: GitHub epic #40 (a detailed plan for an AI-run Sunday/evening planning system across the personal and Muhlert calendars) and the vault note `software_calendar.md` (the research summary behind the epic). Both recommend staying on Google Workspace as a replaceable data store with an owned "intelligence layer", a free/busy convention (fixed/protected = Busy, flexible = Free), a one-way busy mirror between calendars, propose-then-apply agent safety rules, and Google appointment schedules for booking. The other two links (self-link, Google Calendar app URL) carry no content. Spot checks of key external sources cited by those resources were done (Google help, Carly, Productive help).

### Cited Findings

**Resource 1: GitHub issue Y-O-W/dotfiles#40 "Agentic Workflow - Calendar - Planning" (created 2026-11-15, open)**
- Goal: turn "the two Google Calendar setups (YOWfactor UG personal/business and the Muhlert Digital work calendar) into one coordinated, AI-native planning system"; Claude Code CLI is the primary surface (stated 2026-11-19), Desktop and Web optional — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- The calendar "aims to plan 24/7 of the owner's activities, private and business"; Muhlert hours are planned in a separate Google Workspace calendar visible in the personal one, and "both need to be coordinated and synced" — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- Direction (decided 2026-11-15, pending owner confirmation): three layers — data store (Google Calendar; Muhlert calendar "belongs to Muhlert's Workspace and cannot be migrated"), owned intelligence layer (planning skills, event conventions, vault daily notes in plain text, using only generic operations so Google could later be swapped for CalDAV), optional client layer (Morgen as candidate) — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- Explicitly out of scope: replacing Google Calendar; task management beyond calendar plus a daily-note section; changing Muhlert's Workspace admin settings; "Productive.io time tracking"; mobile-only workflows — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- Planned sub-issues (none created yet): verify read/write access from Claude Code; calendar hygiene (fix two UTC calendars, review the 12 purpose calendars for merges); decide event conventions — "`[claude-plan]` description tag, done / carry-over marker, default write calendar per event type, Focus Time, no invitations for solo events, and the free/busy convention ... a visual marker for Free events, agents create flexible events as Free"; agent safety rules each with an enforcement point (permission `ask` on write tools, `deny`/`ask` on respond, PostToolUse logging hook, narrowest OAuth scope, calendar text treated as data in `~/.claude/CLAUDE.md`); busy-mirror evaluation and implementation; booking/team scheduling setup; daily-note "Done / Not done / Carry over" section; two skills (Sunday weekly plan, evening daily plan); scheduled draft-only tasks; one-week close-out comparing planned vs actual — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- Target Sunday procedure: read last and next week across all calendars; list carry-overs; propose three outcomes; propose time blocks using free-slot suggestions; write only after approval. Evening procedure: read today's results and tomorrow; mark done/missed; reschedule misses; refine tomorrow and write after approval — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- Tool criteria for every tool decision: native AI capabilities, dedicated MCP server, bring-your-own-API-key, native web plus macOS plus iOS apps — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- Verification baseline (2026-11-15): connector returns 13 calendars including `Muhlert Digital - Work`, `yowfactor_business`, `yowfactor_business_event`, `yowfactor_personal`, `yowfactor_personal_event`, `yowfactor_personal_health`, `yowfactor_event`, `yowfactor_routine`, a personal Gmail calendar, plus holiday/week-number/Techmeme feeds; Muhlert calendar readable, write untested; Google Workspace has "no native way to subscribe to another calendar and have it default to busy on the primary calendar"; team on Google Workspace Business Standard (stated 2026-11-16); connector tools appear to match the 9 tools of Google's official remote Calendar MCP server (Developer Preview), an inference — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- Decisions still needed from the owner include: whether Desktop/Web need access; third-party busy mirror vs Claude reconciling in sessions; whether Muhlert's Workspace allows mirror access; which of the 12 calendars to merge; whether scheduled tasks only draft; whether to add Morgen; whether Cal.com round-robin is needed; booking page types, hours, buffers, daily cap — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- Note: the issue body links its own epic as "Y-O-W/Y-O-W#28" in the vault note, while the Notion page links dotfiles#40; the content is the same plan (the vault note cites #28, accessed 2026-11-15) — [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md); [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).

**Resource 2: Vault note `software_calendar.md` (research summary 2026-11-15, updated 2026-11-16, status draft)**
- Key takeaways: stay on Google Workspace, treat it as a replaceable data store; both Google (official remote MCP, Developer Preview Sept 2026) and Microsoft (Outlook Calendar MCP, public preview) ship agent interfaces; AI schedulers are "an optional layer, not a foundation" because the category is unstable; CalDAV MCP servers exist but are community-built; "The calendar is a prompt-injection channel"; "Google has no native availability mirror across accounts"; booking and team meetings work inside Google on Business Standard — [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md).
- Scheduler volatility: Clockwise ceased on 2026-03-27 after a Salesforce acquisition; Reclaim.ai is now part of Dropbox (vault note citing Dupple 2026a/b; not independently verified here) — [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md).
- Availability sync: options are a busy-mirror tool (Calendar Busy Sync, CalendarBridge) or Claude reconciling during planning sessions; test recurring events, deletes/moves leaving ghost blocks, declined meetings; mirror must ignore Free events — [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md).
- Team scheduling: 1-2 teammates internal -> event with guests plus Suggested times / Find a time, requiring org-wide free/busy sharing; teammates plus client -> appointment schedule with co-hosts; round-robin/collective across accounts -> not covered by Google, Cal.com fallback. Co-hosts must be same Workspace domain ("A Muhlert teammate counts as external" relative to the YOWfactor account); co-host calendars must be ticked under "Check calendars for availability" — [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md).
- Free/busy convention: Fixed (meetings, client calls, travel, appointments) = Busy; Protected (deep work, lunch, health) = Busy; Flexible (admin, email, planning, untimed tasks) = Free. Give Free events a consistent prefix or single colour; agent-created flexible events must be Free; events RSVP'd Yes/Maybe block booking slots, so keep flexible work as own events without guests — [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md).
- Planning practice: three weekly outcomes (actiTIME); 15-30 min daily review (Weekdone); 10-15 min shutdown (Akiflow); time-block work that matters, not every small task — [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md).
- Agent safety: Gemini invite-borne prompt injection (Bitdefender 2025), Google's mitigations, a zero-click variant (SoftwareSeni 2026); rules adopted: propose-then-apply, external text is data, narrowest OAuth scope, never auto-accept, log every change — [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md).
- The note's own evidence caveat: sources "were read as search-result excerpts, not as full pages", several are vendor blogs; "Google's own documentation was not read" — [Vault note](file:///Users/yowfactor/Obsidian/Software/software_library/software_calendar.md).

**Resource 3: self-link to the Notion page** — no additional content — [Notion page](https://app.notion.com/p/yowfactor/Software-Calendar-421ed4002a8080348bc4f29386228a7b).

**Resource 4: Google Calendar web app URL** — an app entry point, not content; not fetched (authenticated) — [Notion page](https://app.notion.com/p/yowfactor/Software-Calendar-421ed4002a8080348bc4f29386228a7b).

**Spot checks of second-order sources (cited by resources 1-2)**
- Google Help, appointment schedules: "By default, appointment schedules do not check co-host availability"; recommends including co-hosts' calendars "to prevent double-bookings"; "As a co-host, you can't add groups or users outside of your domain"; cannot create schedules in the Android/iOS app; for eligible Workspace accounts the booking page "doesn't show times when you're busy". This confirms the vault note's co-host claims — [Google Calendar Help](https://support.google.com/calendar/answer/10729749).
- Carly, "How to Sync Work and Personal Google Calendars" (published 2026-08-12; vendor with commercial interest): recommends a one-way copy from personal to work primary calendar, titles rewritten to "Busy", attendees/description/location stripped; warns against a reverse rule (work titles would leak to personal); free/busy-only sharing shows under "Other calendars" but does not block the work primary calendar, so coworkers' Find a time may still show you free; ICS subscription unreliable; two-way sync is effectively two one-way rules; failure modes: recurring events, moves, deletes leave ghost blocks, declined invites, private flag does not protect copied details, working hours and focus time do not transfer — [Carly](https://www.usecarly.com/blog/how-to-sync-work-and-personal-google-calendars/).
- Productive help, Google Calendar integration (page says "Updated over 2 weeks ago"; no exact date): sync is one-way Google -> Productive; calendar events show greyed out in My Time calendar view and Day view suggestions; clicking an event pre-fills the time-entry note with the event title and the duration with its time range; the user must manually pick a budget/deal and service; multiple calendars can be connected; the AI Assistant can read connected-calendar events; absence status can sync Productive -> Google separately — [Productive Help](https://help.productive.io/en/articles/6940914-google-calendar-integration).

### Inferences
- The Productive integration copies the event title into the time-entry note and requires manual service selection, so an event title that encodes client/project/service (question 4 on the page) would directly make conversion faster for humans and give an AI agent (Productive's assistant or Claude via Productive MCP) enough context to pick the budget and service. This is my inference; Productive's article on AI conversion of events was not read.
- On question 1 (sharing direction), the cited Carly guidance points to: personal -> work one-way "Busy" copies, never full details into work; the epic reaches the same design ("personal and business events as Busy on the Muhlert calendar").
- Issue #40 excludes Productive time tracking from scope, while the Notion page puts Productive and Productive MCP in its Technology list and makes time tracking a core attribute of the work event types; the Notion page is therefore broader than the epic.

### Gaps
- No resource on the page addresses naming conventions for event titles; neither the epic nor the vault note defines one beyond a `[claude-plan]` description tag, a done/carry-over marker, and a prefix or colour for Free events.
- No resource addresses whether the many purpose calendars (question 2) should be replaced by colours, labels or event types; the epic only lists "review the 12 purpose calendars for merge candidates".
- Question 3 (multiple Google calendars in Claude): the resources show the existing connector already lists 13 calendars in one account, but multi-account access (YOWfactor plus a separate Muhlert Workspace account) is not resolved; the epic names `nspady/google-calendar-mcp` as a multi-account option without testing.
- No books, videos or named methods (e.g. GTD, time blocking books) are linked on the page; method references come only via the vault note's blog sources (actiTIME, Weekdone, Akiflow), which were not re-fetched here.
- The remaining ~25 external sources in the vault note and epic were not individually re-fetched; claims from them (Clockwise shutdown, Reclaim/Dropbox, Google MCP preview dates) are as reported by the user's earlier research.

## Are there sub-pages or linked Notion pages relevant to calendar use?

### Takeaway
The page has no sub-pages. Its parent project "YOWfactor - Software - 2026" is only a container. Relevant related pages found by search are "Muhlert - Productive - Setup" (which contains the identical event-type taxonomy from a 20.11.26 meeting with Sebastian, plus Productive time-tracking and AI/MCP questions), "Notes - Muhlert Digital GmbH", and the "16.07.26 - Onboarding - Nina" event (which records "Time Tracking -> connect calendar" and daily time tracking).

### Cited Findings
- The page content has no child pages or embedded databases — [Notion page](https://app.notion.com/p/yowfactor/Software-Calendar-421ed4002a8080348bc4f29386228a7b).
- Parent project "YOWfactor - Software - 2026" holds Documentation links (Briefing, Notes, Research) and Task/Event/Resource/Content databases; eight tasks linked, including this one — [Software 2026 project](https://app.notion.com/p/31fed4002a808071bf43e2116d5c5eb0).
- Productive Setup page, "20.11.26 - Meeting - Sebastian": same Work/Personal event types and the Calendar features list (reminder, task, label, multiple calendars) — [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46).
- Productive Setup page, Productive meeting agenda: "time tracking tested in combination with Google calendar"; "automatic time tracking in combination with approvals -> best practice?"; "absence best practice"; MCP/AI agent tested in a sandbox; "approval prompts on for every write tool -> in Claude"; "restricted AI user for MCP access"; "Rules of Engagement" are meant to double as "instructions for AI in Productive" — [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46).
- Productive Setup page, 16.11.26 meeting with Nina: "Time Tracking - test native AI agent; guidance needed -> Where do I book reporting?"; "Factorial -> absences in Productive, affects availability" — [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46).
- Productive Setup page: role "Time Tracking -> ... including Time Approval (only approved time counts as recognized toward budget usage)"; "Project Management -> is called Digital Strategy & Planning and part of every service, used internally to monitor time for project management tasks (meeting, documentation, research etc.)" — [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46).
- Onboarding page (16.07.26): "Productive - Time Tracking -> connect calendar; pick items from the calendar and add them to a project; daily time tracking"; "Google - Calendar - schedule off time"; email out-of-office for holidays — [Onboarding page](https://app.notion.com/p/39fed4002a808019b545d1a45ccfef96).

### Inferences
- The Muhlert team's actual time-tracking workflow (per onboarding) is: calendar connected to Productive, events picked daily and assigned to a project. A title convention naming the client and service would serve this directly, and "Where do I book reporting?" shows that service selection is a real friction point.
- Because Project Management ("Digital Strategy & Planning") is a service on every budget, internal meetings with a client context should probably be bookable to that service; a title convention could flag this. (Inference.)

### Gaps
- The Briefing/Notes/Research sub-pages of the parent project were not opened; they are generic for the Software 2026 project and not linked from the calendar page.
- The linked Google Doc "Muhlert Digital - Productive - Setup" was not read (not linked from the calendar page; would need Google Drive access).

## Is there anything indicating the team context at Muhlert Digital?

### Takeaway
Yes, from related Notion pages (not from the calendar page itself, which only mentions a work calendar and Productive). Muhlert Digital GmbH is a digital-marketing agency on Google Workspace Business Standard, Slack, Productive (time tracking, resource planning, invoicing; task management to come last), HubSpot (contact data only), and Factorial (HR/absences). Roughly 15-20 named people appear, several freelancers. Billing is retainer (monthly, hours) or SOW, with time approval, rate cards (EU and US), and budgets per client per period; time tracking is daily, from the calendar.

### Cited Findings
- Team on Google Workspace Business Standard (stated 2026-11-16) — [Issue #40](https://github.com/Y-O-W/dotfiles/issues/40).
- Roles named: Nina Mueller, Operations Lead (ops, HR, PM), owner of Productive administration with the user (Yves) as backup; Christian, Digital Director (brand/design); Quentin (lead on pitches; presumably the founder, given the company name); testers per discipline: Search -> Rob, Nadin; Social -> Sebastian; Programmatic -> Azzurra; SEO -> Joana; Design -> Christian; also Miguel (social/search), Tim (sales lead on pitches), Evelina (SEO owner) — [Onboarding page](https://app.notion.com/p/39fed4002a808019b545d1a45ccfef96); [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46); [Muhlert Notes page](https://app.notion.com/p/39fed4002a8080739409fa5ced3a3e00).
- Client account teams include freelancers across countries (e.g. Tourlane: Miguel in Portugal, freelancers in Canada and France, Robert for Google US) — [Onboarding page](https://app.notion.com/p/39fed4002a808019b545d1a45ccfef96).
- Services: Paid Search, Paid Social, Programmatic, SEO, Analytics, Ad Creative/Design, Digital Strategy & Planning (project management) — [Muhlert Notes page](https://app.notion.com/p/39fed4002a8080739409fa5ced3a3e00); [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46).
- Billing: revenue types Retainer (monthly, recurring) and SOW (one-time); currently actual hours invoiced up to retainer level; overtime only if the client accepts beforehand; rate cards yearly with EU and US rates; templates for deals, budgets, projects; an internal "Agency" yearly budget with non-billable services for 2027; only approved time counts toward budget usage; Overhead Cost allocation planned. Example: Tourlane retainer 120 hours/month at 140 EUR/hour — [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46); [Onboarding page](https://app.notion.com/p/39fed4002a808019b545d1a45ccfef96).
- Clients/pitches referenced include Tourlane, Leica, CAS, Xentral, Klang, Shopware, Advanced Tricology, Occhio — [Muhlert Notes page](https://app.notion.com/p/39fed4002a8080739409fa5ced3a3e00); [Onboarding page](https://app.notion.com/p/39fed4002a808019b545d1a45ccfef96).
- Tools: Slack (internal and external channels; requests for Productive go to a Slack channel), Google Drive shared drives (client external, muhlert internal), Google Meet with Gemini / AI notetaker for meeting notes, HubSpot "not used actively for leads/deals", Factorial for HR/absences (and possibly time tracking, per "Factorial -> Time Tracking" note on 23.11.26) — [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46); [Onboarding page](https://app.notion.com/p/39fed4002a808019b545d1a45ccfef96).
- Office hours: "Tuesday to Thursday as a general rule"; security push for passkeys and 2FA — [Muhlert Notes page](https://app.notion.com/p/39fed4002a8080739409fa5ced3a3e00).
- Management goal: keep meetings and communication in Muhlert's own domain so "an AI Agent can reach every surface/layer and access all information that pertains to our work - especially meetings and notes"; connect Claude to Slack — [Muhlert Notes page](https://app.notion.com/p/39fed4002a8080739409fa5ced3a3e00).
- Rollout priority: resource planning, automated time tracking and invoicing first; project/task management last "as it requires changing behavior from the whole team" — [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46).
- Resource planning decision: monthly total hours booked per person; "one person per service" — [Productive Setup page](https://app.notion.com/p/3abed4002a8080dd8865e3daff46ab46); [Muhlert Notes page](https://app.notion.com/p/39fed4002a8080739409fa5ced3a3e00).

### Inferences
- Team size is not stated; the named internal staff and regular freelancers suggest roughly 10-20 people. Treat as an estimate.
- The user appears to work with Muhlert in an operations/Productive-admin capacity (backup admin, runs setup meetings) from a separate YOWfactor account plus a Muhlert Workspace account — which explains the cross-account calendar and co-host constraints in the resources.
- A team calendar convention must work for a mixed team (staff plus freelancers who may not be on Muhlert's Workspace), which affects free/busy sharing and co-host eligibility.

### Gaps
- Exact headcount, employment status of each person, and whether freelancers use Muhlert Google accounts are not recorded.
- Whether Muhlert teammates already use any calendar naming convention or colours is not recorded anywhere found.
- The 23.11.26 note "Factorial -> Time Tracking" is ambiguous (Factorial may be considered for time tracking or only absences); not clarified.

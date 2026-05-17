---
name: cv-review
description: Use when the user asks to review, audit, critique, score, or improve their CV/resume — applies a 2026 evidence-based rubric (ATS hygiene, top-third real estate, CAR-format quantification, AI-era signals, level-appropriate scope) and outputs prioritised, citation-backed recommendations rather than generic advice. Triggers on phrases like "review my CV", "audit my resume", "critique the CV", "what should I fix on my CV", "score my CV".
user-invocable: true
disable-model-invocation: false
allowed-tools: Read Edit Grep Glob
argument-hint: "[optional: path to CV file, target job title, or target seniority level]"
---

# CV Review (Developer, 2026)

Reviews a developer CV against an evidence-based 2026 rubric and returns **prioritised** recommendations — high-leverage fixes first, every finding tied to a specific rubric rule. Not a generic "tips" generator.

## Core principles (the rubric is non-negotiable)

1. **Calibrate to level before advising.** The same line is good advice for a junior and bad advice for a staff engineer. Detect YOE and target level first; tailor everything else.
2. **Top-third of page 1 does ~80% of the work.** Header, role title, employer, dates, and the first bullet of the most recent role are weighted disproportionately.
3. **Every recommendation cites a rule.** No "consider rewording this" without a reason. Fixes carry a tag like `[ATS]`, `[CAR]`, `[Top-Third]`, `[AI-Era]`, `[Level]`.
4. **Prioritise ruthlessly.** Output is "Top 3 highest-leverage fixes" first, then secondary, then nice-to-haves. No exhaustive line-by-line dump.
5. **No filler advice.** "Add more keywords" without naming which keywords from which JD is filler. Either be specific or stay silent.

## Workflow when invoked

1. **Locate the CV.** Default search: `Careers/CV/CV-COL.md` and any sibling `.md` in `Careers/CV/` (excluding `build/`). If multiple, ask which to review or default to `CV-COL.md`. Outside the vault, ask for a path.
2. **Ask three calibration questions** (only if not supplied):
   - **Target seniority** — junior / mid / senior / staff+ / principal
   - **Target market** — UK/EU / US / FAANG / AI lab / quant / startup / contractor
   - **Target job posting (optional)** — if supplied, JD-specific keyword alignment becomes a check
3. **Read the CV in full.**
4. **Run the rubric below as a checklist.** Score each section pass/warn/fail with one sentence of evidence drawn from the actual CV text.
5. **Synthesise output** in the format below.

## The rubric

### A. Format & ATS hygiene `[ATS]`

For markdown CVs targeting `.docx` export, these checks apply to the rendered output. Flag anything that will produce a parser-hostile artefact.

- [ ] **Single-column layout.** Two-column / sidebar CVs lose 23 percentage points of parse fidelity (Lever data: 71% vs 94%). Tables for layout count as multi-column.
- [ ] **No tables, text boxes, columns, images, skill bars, custom icons, or infographics** in the rendered doc.
- [ ] **Standard section names only** — Summary, Skills, Experience, Education, Projects. "What I Bring" / "My Story" break ATS section mapping.
- [ ] **Contact info in body, not headers/footers.** Greenhouse/Lever/Workday all drop header/footer text.
- [ ] **Consistent date format throughout.** Mixed formats cause Workday/Greenhouse to miscalculate YOE — often a hard filter.
- [ ] **Industry-standard job titles, not internal ones.** "Senior Software Engineer" not "Engineering Wizard III".
- [ ] **35–50% white space.** Cramped layouts drop dwell time from ~9.4 s to ~6.1 s.

### B. Header & top-third real estate `[Top-Third]`

- [ ] **Header line:** Name, City/Country, email, phone, LinkedIn, GitHub (only if it has 1–3 polished pinned projects), portfolio URL.
- [ ] **No photo, no DOB, no GPA past ~3 years out, no "References available on request".**
- [ ] **Section order for tech roles:** Header → Summary → **Skills (before Experience)** → Experience → Education / Projects. UMN gaze data: skills-first lifts callbacks ~27% for technical roles.
- [ ] **First bullet under most recent role does 3.5× the work.** Should be a quantified business-impact bullet. If the first bullet is generic ("Worked on backend services") — that is the single highest-leverage fix on the page.

### C. Bullet quality (CAR format) `[CAR]`

Every Experience bullet should fit Context-Action-Result and end in a **scale, delta, or ownership signal**:

- **Scale:** users, RPS, dataset size, $ owned, headcount
- **Delta:** % improvement, $ saved, time reduced
- **Ownership:** team size, system criticality, scope

Common failures to flag:
- "Responsible for X" → passive, hides ownership.
- "Improved performance" → no metric.
- "Worked on Y" → no outcome.
- "Used technologies including A, B, C" → tech-stack dump, not an achievement.

⚠️ **Senior-level caveat:** unverifiable inflated metrics ("improved performance 40%") are quietly distrusted by FAANG hiring committees. Prefer **scope + ownership** ("owned X service handling Y QPS / Z customers") for senior+ candidates, with the number as scale context rather than self-graded outcome.

### D. Length `[Level]`

- **<5 YOE:** one page. Two-page CVs at this level read as padded.
- **5–10 YOE:** flexible, tilting toward two.
- **10+ YOE / staff+:** two pages (ResumeGo: 2.3× recruiter preference). Density matters more than length — every line must carry signal.
- **Older roles past ~7 years:** compress to 1–2 lines regardless of total YOE. Reviewers don't read in depth.

### E. Skills section `[Skills]`

- [ ] **Top 5–7 languages/frameworks** that match the JD verbatim. Not a 30-item exhaustive list.
- [ ] **Grouped by category with context** (Languages / Frameworks / Cloud / AI Dev Tools / Domain). Not levels — listing "Python: Expert" with one project is actively harmful; interviewers will probe.
- [ ] **No certifications unless target role explicitly requires** (AWS/Azure/Scrum certs are largely ignored at FAANG; relevant for some enterprise roles).
- [ ] **No soft-skill adjective lists** ("passionate, motivated, team player").

### F. AI-era signals `[AI-Era]`

This is the single biggest 2026 shift. Pragmatic Engineer 2026 survey: 95% of devs use AI weekly, 56% for ≥70% of work, 55% use agentic AI (63.5% at staff+).

- [ ] **AI Dev Tools listed as a Skills category**, not absent. Example: *"AI Dev Tools: Claude Code, Cursor, GitHub Copilot — daily driver; built custom Claude Code skills/hooks for [team workflow]."*
- [ ] **AI tool mentions in bullets follow Tool + Task + Output formula.**
  - Weak: *"Used AI tools to write code faster."*
  - Strong: *"Used Claude Code to migrate a 40K-line monolith to microservices; reduced timeline 6 weeks → 11 days."*
- [ ] **Operator-tier usage signalled where true** — custom skills/hooks/agents, agentic workflows, MLOps pipelines, internal dev-tools that multiplied team output. Mid-tier "I use Copilot" mentions are now baseline, not a differentiator.
- [ ] **Verifiable artefacts linked** — every AI-tool claim should be backable by a GitHub repo with real iterative commits, deployed URL, or architecture doc. Single-commit "AI-dump" repos are a negative signal.

### G. AI-detection / authenticity `[Authenticity]`

43% of large employers now run resumes through AI-detection software; 49% of those auto-dismiss. Flag and rewrite anything that pattern-matches as LLM-generated:

| Tell | Why it triggers detectors |
|---|---|
| "Results-driven professional with a proven track record" | #1 generic opener; instant flag |
| Stacked power verbs: "spearheaded, orchestrated, leveraged, transformed" | Convergent LLM phrasing |
| Uniform sentence length / low burstiness | Detectable statistical signature |
| Suspiciously perfect keyword match against JD | Density flag |
| Vocabulary mismatched to seniority | Junior CV with director-tier prose |

**Counter-pattern:** keep idiosyncratic specifics — named projects, exact stack quirks, weird internal-tool names, off-script anecdotes. Uniformity is now the failure mode; idiosyncrasy is the edge.

### H. Level-specific scope `[Level]`

**Junior / mid (≤5 YOE):**
- Project execution and tech stack are appropriate.
- Education stays near top; GPA OK if recent.
- One polished side project beats five abandoned repos.

**Senior (~5–10 YOE):**
- Bullets shift from "what I built" to "what changed because of me."
- Mentorship beginning to appear with named outcomes.
- Tech stack list trimmed; architecture decisions appearing.

**Staff+ (10+ YOE or staff/principal title):**
- Apply Larson's promo-packet structure as a scaffold: Projects → Org Improvement → Quantified Impact → Mentorship Record → Glue Work → Stakeholder Endorsements.
- Apply Reilly's three pillars — every staff+ CV needs evidence of: big-picture thinking, cross-team execution, levelling up others.
- Add a one-line **"Scope:"** header per role: team size, system criticality, product surface area. Lets reviewers calibrate altitude in 2 seconds.
- **Recency-weighted detail.** If the most recent role doesn't read as staff, the CV won't get a staff offer regardless of title.
- Tech stack lists shrink, not grow. Implementation bullets get trimmed if they crowd out higher-leverage contributions.

### I. Brand & title positioning `[Brand]`

- [ ] **Brand-name employers (Big Tech, well-known unicorns, recognised industry leaders) are recognisable on the page.** One Big Tech name is a permanent multiplier in skim-reading.
- [ ] **FAANG title deflation handled.** Amazon L6 / Meta E5 / Google L5 = staff/principal scope but ATS scores them as "Senior". Re-frame: *"Senior SWE (L6 — staff-equivalent scope, owned X)"*.
- [ ] **AI-lab targets only:** consider hoisting independent research, technical blog posts, and OSS contributions **above** employers and education. Anthropic explicitly recommends this; ~half their technical staff had no prior ML experience. (Skip this rule if target isn't an AI lab.)
- [ ] **Quant-shop targets only:** competition results (Putnam, ICPC, IMO/IOI, Kaggle medals, firm datathons) function as the brand-name equivalent. (Skip if not relevant.)

### J. Summary block `[Summary]`

If a Summary section is present:
- Apply the `cv-summary-opener` skill's rubric (formula: `[Job Title] with [N] years' experience in [Specialty]`, third person, no filler adjectives, hard discards).
- **Run the deletion test:** if removing the summary loses no information not already in the most recent role, recommend deletion rather than rewrite. A weak summary is worse than no summary.

## Output format

Always structure the review as four sections, in this order:

```markdown
## CV Review — [filename]

**Calibration:** [target level] · [target market] · [target JD if supplied]
**Length:** [N pages / N words] · **Verdict:** [appropriate / too short / too long for level]

### Top 3 highest-leverage fixes

1. **[Tag]** [One-sentence problem] → [One-sentence fix].
   - Evidence from CV: "[exact quote]"
   - Why it matters: [rule citation, e.g. "First bullet of most recent role gets 3.5× attention (eye-tracking)"]

2. ...

3. ...

### Secondary fixes

[5–10 items, same shape but more compressed]

### Nice-to-haves / polish

[Bullet list, one line each]

### What's working

[2–4 bullets — explicitly note things that are already good. Prevents the user from "fixing" things that don't need fixing.]
```

## Hard rules — what NOT to do

- **Do not output a generic "tips for CVs" list.** Every finding must reference a specific line in the user's CV.
- **Do not flag every bullet that lacks a number.** Pick the top 3–5 highest-impact bullets (most recent role first); ignore the long tail.
- **Do not recommend buzzwords or filler verbs.** "Spearheaded, orchestrated, leveraged" trigger AI-detection — never recommend them.
- **Do not rewrite the entire CV unless asked.** Default output is a review with targeted fixes. Rewriting is a follow-up step the user requests explicitly.
- **Do not invent achievements or metrics.** If a bullet lacks a number, recommend the user supply one — never fabricate.
- **Do not apply staff+ rules to a junior CV** or junior rules to a staff+ CV. Calibrate first.
- **Do not score "ATS friendliness" if the CV is markdown** — markdown isn't what ATS sees. Comment instead on the structure that *will* render to `.docx`. Mention the `cv-export` skill for the export step.

## Vault-aware behaviour

When invoked inside the user's Obsidian vault:

- Default CV path: `Careers/CV/CV-COL.md`. Variants live alongside (e.g. `mcs-full-stack-python-react.md` is a tailored version).
- The `Careers/CV/Achievements.md` file is the user's reference list of quantified outcomes. **Read it when reviewing** — if a Summary or Experience bullet lacks a metric and a relevant one exists in `Achievements.md`, suggest it specifically rather than asking abstractly.
- Preserve Obsidian-compatible Markdown when editing: wiki-links, frontmatter YAML, callouts.
- After review, mention `cv-export` if the next step is exporting to `.docx`, and `cv-summary-opener` if the Summary needs a rewrite.

## Red flags — STOP and reconsider before outputting

| Symptom | What it means |
|---|---|
| Output is >2000 words | You're being exhaustive instead of prioritising. Cut to top 3 + secondary. |
| Recommendation has no quote from the CV | You're advising in the abstract. Either find the line or drop the point. |
| Same advice would fit any developer CV | Generic. Tailor or remove. |
| Recommended a power verb stack | You just made the CV more LLM-detectable. Rewrite. |
| Reviewed without asking calibration questions | Risk of misaligned advice. Ask first or state assumptions. |
| Suggested adding photo / objective / GPA past graduation | These are 2010s rules. Strike. |
| Flagged every quantification gap individually | Pick top 3–5; the long tail is noise. |

## Quick-reference: what 2026 winners look like

A high-leverage 2026 developer CV reads like this:

- **Single column, sans-serif, two pages (or one if <5 YOE).**
- **Header line** with email, phone, LinkedIn, GitHub, portfolio. No photo.
- **Summary** (or no summary, if it adds nothing): `[Title] with [N] years in [stack]. [Quantified flagship]. [Niche differentiator].` Idiosyncratic voice.
- **Skills** as 4–6 categorised one-liners, including an **AI Dev Tools** line that signals operator-tier usage.
- **Experience** with most recent role bulking the page; a one-line **Scope:** header per role at staff+; first bullet always quantified business impact; older roles past ~7 years compressed to 1–2 lines.
- **Projects** (hoisted above Experience for AI lab targets): 2–3 deep-linked artefacts with real commit history.
- **Education** at the bottom unless very recent; no GPA past ~3 years.

If the CV under review departs from this in ways the rubric doesn't justify (e.g. AI lab target, contractor with portfolio-led structure), call that out explicitly rather than silently flagging the deviation.

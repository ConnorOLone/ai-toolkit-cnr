---
name: cv-summary-opener
description: Use when writing or revising the Professional Summary, Overview, Profile, or Personal Statement section at the top of a CV/resume — covers the opening sentence formula, ATS keyword placement, anti-patterns to avoid, and tailoring rules. Triggers on phrases like "write the summary", "fix the overview", "open the profile section", "rework the top of the CV".
user-invocable: true
disable-model-invocation: false
allowed-tools: Read Edit Write Grep Glob
argument-hint: "[optional: target job title or path to CV file]"
---

# Writing the CV Professional Summary / Overview Opener

This skill governs how to write the first 1–4 lines of a CV's summary block. The opener is read in ~6 seconds for triage and is the single highest-leverage piece of keyword real estate on the document. It must answer **who you are, at what level, in what domain** before any prose.

## The dominant formula

Open with a noun phrase in this order:

```
[Job Title] with [N] years' experience in [Specialty / 2–3 named tools]
```

- **Mirror the literal job title from the target posting** — ATS systems do not reliably resolve "Software Engineer" ≈ "Software Developer". Use the exact string.
- **Front-load the years and specialty** — recruiters confirm role-fit in the first horizontal eye sweep.
- **Name 2–3 concrete technologies, domains, or specialisms** — generic adjectives carry no information.

### Sentence 2: one quantified outcome

After identity, follow with a single metric ("…cut the overnight batch from 12h to 90min…"). Numerals draw the eye more than words and read as proof rather than claim. Don't open with the metric unless it's a signature defining number — identity-led is the safer default.

### Sentence 3 (optional): one differentiator

A niche intersection, hard credential, or domain specialism that nothing else on the page conveys. Example: *"Specialise in untangling legacy WCF + workflow integrations in regulated public-sector environments."*

## Length and voice

- **2–4 sentences, ~50–100 words.** UK CVs run slightly longer (3–5 lines) and more capability-led; US CVs are shorter and more metric-heavy.
- **Third person, present tense, no pronouns.** "Full-stack developer with…" not "I am a full-stack developer who…". Pronouns waste keyword budget and break convention.
- **UK English when targeting UK/Ireland**: "specialising", "modernising", "optimisation".

## Hard discards — never use in the opener

| Avoid | Why |
|---|---|
| "Results-driven / passionate / motivated / detail-oriented / hard-working / go-getter / self-starter" | Filler. Fastest discard trigger. ~85% of CVs contain "team player". |
| "Seeking a position where I can leverage…" | Objective-style; centres your wants over the employer's needs. |
| "I am a…" / first-person pronouns | Breaks third-person convention; wastes keyword budget. |
| "Responsible for…" / passive voice | Hides ownership and scale. |
| "Proven track record" / "Excellent communication skills" | Unprovable assertions; the CV body is the proof. |
| Stacked power verbs ("spearheaded, transformed, leveraged") | Pattern-matches as ChatGPT output — recruiter fatigue with AI-styled summaries is well-documented. |
| Adjective stacks ("Highly skilled, results-driven, motivated full-stack developer") | Push the noun phrase further from the eye. Lead with the noun. |
| "Think outside the box / synergy / dynamic" | Buzzwords with zero information content. |

## When to delete the summary instead

Apply the contrarian test: **if removing the summary loses no information, delete it.** Senior candidates whose most-recent-role bullets already convey level, domain, and outcomes often lose nothing by cutting the section. A generic summary at the top of a CV is uniquely expensive — it eats prime real estate and pattern-matches to filler.

Keep the summary only if it adds something the rest of the page can't:
- A niche intersection (e.g. ".NET + ERP + UK public sector")
- A signature quantified outcome
- A hard credential
- A career-change bridge ("Former [old role] with…")

## Industry adaptations

| Field | Lead with | Example |
|---|---|---|
| **Software / tech** | Title + years + named stack | *".NET full-stack developer with 6 years' experience modernising ERP systems with C#, ASP.NET Core and SQL Server."* |
| **Executive / C-suite** | Title + scope + quantified business outcome | *"Marketing Director with 12 years scaling B2B SaaS demand-gen, including a $2.5M ARR programme across EMEA."* |
| **Creative** | Title + named clients or aesthetic specialism | *"Senior graphic designer with 6+ years in brand identity, working with Nike, Mattel and Williams Sonoma."* |
| **Entry-level** | Education + internship/project evidence | *"Recent Marketing graduate with 5 months' internship in digital branding; launched a TikTok account that gained 8,000 followers in 4 months."* |
| **Career-changer** | "Former [old role] with…" bridge → transferable skill | *"Former Data Analyst with 4 years harnessing big data to inform strategic decisions, transitioning into product management."* |

## Tailoring discipline

For every application:

1. **Copy the literal job title** from the posting into slot one of the formula.
2. **Identify 3–5 must-have skills/tools** from the posting's "required" or "responsibilities" section and seed 2–3 of them into the first two sentences (naturally, not stuffed).
3. **Pick the metric** from your experience that most closely matches the posting's language ("reduced X" if they say "improve efficiency"; "scaled Y" if they say "grow").
4. **Run the deletion test** — read the summary, then read the rest of the CV. If the summary repeats what the most recent role already says, rewrite it to add a niche intersection or signature metric, or delete it.

## Workflow when invoked

1. **Confirm the target.** Ask for (or read) the literal job title from the posting if not provided. Without it, you cannot apply the mirroring rule.
2. **Read the existing CV** if a path is provided — extract years of experience, named tools/stack, signature metrics, and any niche intersections.
3. **Draft 2–3 candidate openers** using the formula, varying which specialism/metric leads.
4. **Run each candidate through the discard list** — flag any filler words present.
5. **Run each candidate through the deletion test** — does it add information not in the role bullets below? If no, rewrite or recommend deletion.
6. **Present the winner with one alternative** and a one-line note on why it was chosen (e.g. "leads with ERP niche because the posting names ERP three times").

## Vault-aware behaviour

If invoked inside the user's Obsidian vault (working directory contains `Atlas/`, `Knowledge/`, `Careers/`):

- CV markdown files live under `Careers/` — look there for `CV.md` or named variants (`CV-COL.md`, etc.) before asking for a path.
- Preserve Obsidian-compatible Markdown: wiki-links, frontmatter YAML, callouts.
- After revising the summary, mention the `cv-export` skill if the user wants a polished `.docx`.

---
name: cv-tailor
user-invocable: true
description: Use when the user wants to tailor their CV to a specific job description, role, or company — analyzes requirements, matches against master CV, and produces a targeted variant
---

# CV Tailor

## Overview

Tailors the master `CV-COL.md` to a specific job opportunity. Analyzes the job description for requirements and ATS keywords, compares against the master CV, then produces a strategically adapted variant optimized for both automated screening and human reviewers.

## Inputs

Accept any of:
- **Pasted text** — job description copied directly into the conversation
- **URL** — fetch with `WebFetch`
- **Indeed link/job ID** — use `mcp__claude_ai_Indeed__get_job_details`

If the user provides nothing, ask: *"Paste the job description, or give me the URL / Indeed link."*

## Workflow

### 1. Load the master CV

Read from the canonical location:
```
~/Documents/Main Vault/Careers/CV/CV-COL.md
```

### 2. Analyze the job description

Extract and structure:

| Category | What to capture |
|---|---|
| **Required skills** | Hard must-haves (languages, tools, certs) |
| **Preferred skills** | Nice-to-haves, often listed as "bonus" |
| **ATS keywords** | Exact phrases from the JD — match these verbatim |
| **Seniority signals** | Years of exp, scope of ownership, level indicators |
| **Domain focus** | Industry vertical, product type, scale |
| **Culture signals** | Values, ways of working, team descriptors |
| **Red flags / gaps** | Requirements the CV clearly doesn't address |

### 3. Gap & match analysis

Before tailoring, produce a brief internal summary:
- ✅ Strong matches (lead with these)
- ⚠️ Partial matches (worth reframing)
- ❌ Missing (note honestly — don't fabricate)

### 4. Tailor the CV

Apply these tactics in order:

**Summary / profile statement**
- Rewrite to mirror the role's language and top 2–3 priorities
- Open with the exact seniority level and domain the JD uses

**Skills section**
- Reorder to front-load tools/technologies explicitly mentioned in the JD
- Do not add skills the user doesn't have

**Experience bullets**
- Within each role, reorder bullets to lead with achievements most relevant to this JD
- Rephrase naturally to use ATS keywords where the meaning is equivalent
- Quantify where the master CV already has supporting data — don't invent numbers

**Projects / other sections**
- Surface the most relevant projects; trim or compress less-relevant ones
- If a section adds no signal for this role, consider removing it from the variant

**What NOT to change**
- Do not invent experience, skills, or achievements
- Do not alter dates, titles, or employer names
- Keep the same overall structure and formatting conventions as the master

### 5. Save the variant

Write to the same vault directory:
```
~/Documents/Main Vault/Careers/CV/CV-COL-[Company].md
```
Use a short, clear company name abbreviation (e.g. `CV-COL-Stripe.md`, `CV-COL-DeepMind.md`).

### 6. Report what changed

After saving, summarize:
- Which sections were reordered / rewritten and why
- ATS keywords now present
- Any gaps flagged (skills in JD not covered by CV)
- Suggest running `/cv-export` if a `.docx` is needed

## Key Principles

**ATS first, human second** — exact keyword matching matters. Use the JD's phrasing, not synonyms, when meaning is identical.

**Authentic tailoring only** — reorder, reframe, and emphasize; never fabricate. A gap is better disclosed than invented.

**Variant, not replacement** — the master `CV-COL.md` is never modified. All changes go to the company-specific file.

**One variant per application** — produce a new file each time; don't overwrite a previous company's variant.

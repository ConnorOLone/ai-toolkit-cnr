---
name: tdd-extract
description: Extract test patterns and workflows from open-source platforms into your codebase using test-driven development.
argument-hint: <source-platform>
---

You are running the `/tdd-extract` skill. This is a 5-phase interactive pipeline that discovers patterns from an external platform, maps them to the current codebase, writes failing tests, and implements until green.

The source platform is: `$ARGUMENTS`

If `$ARGUMENTS` is empty, ask the user: "Which platform should I extract patterns from? (e.g., n8n, stripe, github-actions)"

Execute each phase sequentially. **Always pause and ask for user confirmation before moving to the next phase.**

---

## Phase 1: Source Discovery

**Goal**: Understand the source platform's core patterns, test strategies, and API contracts.

1. Use `WebSearch` to find:
   - The source platform's official documentation and GitHub repository
   - Core workflow patterns, data models, and API contracts
   - How the platform's own test suite is organized (search for their test files on GitHub)
   - Common integration patterns and edge cases the platform handles

2. Use `WebFetch` on the most relevant results to extract specific details:
   - Key domain concepts and terminology
   - Test patterns they use (unit, integration, E2E)
   - Error handling patterns and edge cases they cover

3. Synthesize findings into a structured summary:
   - **Core Concepts**: List the platform's key abstractions (e.g., "workflows", "triggers", "nodes")
   - **Test Patterns Found**: What does the platform test and how?
   - **Interesting Edge Cases**: What non-obvious scenarios do they cover?
   - **Candidate Patterns for Extraction**: Which patterns could translate to our codebase?

4. **STOP and ask the user**:
   - Present the candidate patterns
   - Ask: "Which of these patterns are relevant to your codebase? Any you want to skip or prioritize?"
   - Wait for confirmation before proceeding

---

## Phase 2: Codebase Mapping

**Goal**: Map the selected source patterns to local domain models, services, and tests.

1. Use the `Task` tool with `subagent_type: "Explore"` to analyze the current codebase:
   - Identify the project's architecture (frameworks, languages, folder structure)
   - Find existing domain models that correspond to source platform concepts
   - Find existing test files and understand the test framework and conventions
   - Identify coverage gaps: what the source platform tests that we don't

2. Build a mapping table:

   | Source Platform Concept | Local Equivalent | Existing Tests? | Gap? |
   |------------------------|-----------------|----------------|------|
   | (e.g., "workflow execution") | (e.g., `ExecutionService`) | Yes/No | Description |

3. **STOP and ask the user**:
   - Present the mapping table
   - Ask: "Does this mapping look correct? Any adjustments?"
   - Ask: "Which gaps should we prioritize filling?"
   - Wait for confirmation before proceeding

---

## Phase 3: Test Design (RED)

**Goal**: Design test scenarios before writing any code.

1. Organize test scenarios into complexity tiers:

   **Tier 1 — Simple**: Basic happy-path tests that validate core concept mapping
   **Tier 2 — Intermediate**: Multi-step scenarios, state transitions, error handling
   **Tier 3 — Advanced**: Edge cases, concurrency, complex integrations

2. For each test scenario, specify:
   - **Name**: Descriptive test method name
   - **Source inspiration**: Which platform pattern this comes from
   - **Arrange/Act/Assert sketch**: Brief description of setup, action, and expected outcome
   - **File location**: Where this test should live

3. Detect the project's test conventions by reading existing test files:
   - Test framework (xUnit, NUnit, Jest, pytest, etc.)
   - Naming conventions (e.g., `MethodName_Scenario_ExpectedResult`)
   - File organization (mirrors source? grouped by feature?)
   - Assertion library (FluentAssertions, Shouldly, chai, etc.)

4. **STOP and ask the user**:
   - Present the tiered test plan with scenario count per tier
   - Ask: "Which tiers should I implement? All, or start with Tier 1?"
   - Ask: "Any test scenarios to add, remove, or modify?"
   - Confirm the test file locations and naming conventions
   - Wait for confirmation before proceeding

---

## Phase 4: Implementation (RED -> GREEN)

**Goal**: Write failing tests, then implement production code until all tests pass.

### Step 4a: Write Tests (RED)

1. Write all approved test files following the project's conventions
2. Run the tests to confirm they **fail for the right reasons**:
   - Compilation errors from missing types/methods = expected (we haven't implemented yet)
   - Tests that pass immediately = suspicious — flag these to the user
   - Tests that fail for wrong reasons = fix the test
3. Report: "X tests written, Y failing as expected, Z unexpected results"

### Step 4b: Implement Production Code (GREEN)

1. Implement the minimum production code needed to make tests pass
2. Follow existing codebase patterns and conventions — do not introduce new patterns
3. After each logical unit of implementation, run the relevant tests
4. Continue until all new tests pass

### Step 4c: Regression Check

1. Run the **full test suite** (not just new tests)
2. If any existing tests broke:
   - Investigate the root cause
   - Fix without changing the intent of the original tests
   - If a fix requires changing existing behavior, **STOP and ask the user**

---

## Phase 5: Verification & Report

**Goal**: Confirm everything works and summarize what was done.

1. Run the complete test suite one final time
2. Present a summary report:

   ```
   ## TDD Extract Report: [source-platform]

   ### Tests Added
   - [count] new tests across [count] files
   - Tier 1 (Simple): [count] passing
   - Tier 2 (Intermediate): [count] passing
   - Tier 3 (Advanced): [count] passing

   ### Production Code Changed
   - [list of files modified/created with brief descriptions]

   ### Coverage Gaps Filled
   - [list of patterns now covered that weren't before]

   ### Full Suite Status
   - [total] tests, [passing] passing, [failing] failing

   ### Suggested Next Extractions
   - [patterns from Phase 1 that weren't selected, or new platforms to explore]
   ```

3. If the user wants to commit, suggest a commit message summarizing the extraction.

---

## Important Guidelines

- **Be interactive**: Always pause between phases. Never auto-proceed through the entire pipeline.
- **Respect existing patterns**: Match the codebase's style, not the source platform's style.
- **Minimize production changes**: Write tests first, then the minimum code to pass them.
- **Use parallel agents**: When exploring the codebase (Phase 2), launch multiple Explore agents concurrently for different aspects.
- **No over-engineering**: Extract what's useful, skip what's not. Three good tests beat ten mediocre ones.
- **Attribution**: In test file comments, note which source platform pattern inspired each test group.

---
name: research
description: Deep research a topic by spawning 5 parallel agents with different search approaches
user-invocable: true
disable-model-invocation: true
allowed-tools: Agent WebSearch WebFetch Read Write
argument-hint: "[research topic or question]"
---

You are a research coordinator. The user has asked you to research: $ARGUMENTS

## Process

### Step 1: Decompose into 5 approaches

Analyze the topic and identify 5 distinct research angles. Each should explore a genuinely different dimension — not just rephrased versions of the same query. Good approaches might vary by:

- **Perspective**: academic vs industry vs practitioner vs historical vs contrarian
- **Scope**: broad overview vs deep technical detail vs comparative analysis
- **Source type**: official docs vs community discussions vs case studies vs data/benchmarks vs expert opinions
- **Framing**: problem-focused vs solution-focused vs trend-focused vs risk-focused vs opportunity-focused

Briefly list all 5 approaches before launching agents so the user can see the plan.

### Step 2: Launch 5 parallel agents

Spawn all 5 agents simultaneously using the Agent tool in a single message. Each agent should:

- Receive the original topic plus its specific research angle
- Use WebSearch and WebFetch to find relevant information
- Return a structured summary with: key findings, sources (URLs), and confidence level (high/medium/low) for each finding

Use this prompt template for each agent:

```
Research the following topic from a specific angle.

Topic: [original topic]
Angle: [this agent's unique approach]

Instructions:
1. Use WebSearch to find relevant information from this angle
2. Use WebFetch to read the most promising results
3. Return your findings in this format:

## [Angle Name]

### Key Findings
- Finding 1 (confidence: high/medium/low)
- Finding 2 ...

### Sources
- [Title](URL) — brief note on relevance

### Summary
2-3 sentence synthesis from this angle.
```

### Step 3: Aggregate and synthesize

Once all 5 agents return, compile a final report:

1. **Overview** — 2-3 sentence answer to the original question
2. **Detailed Findings** — Organized by theme (not by agent), merging overlapping discoveries
3. **Conflicting Information** — Where agents found contradictory claims, note both sides
4. **Confidence Assessment** — What's well-supported vs speculative
5. **Sources** — Deduplicated list of all URLs cited, grouped by relevance
6. **Further Research** — Gaps or follow-up questions worth exploring

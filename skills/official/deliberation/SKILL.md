---
name: deliberation
description: >
  Multi-model deliberation for high-stakes or complex tasks. Triggers when accuracy matters
  more than speed — research questions, architectural decisions, medical/legal/financial analysis,
  fact-checking, comparing tradeoffs, debugging elusive issues, or any question where a single
  model's blind spot could lead to a wrong answer. Also triggers on explicit user requests for
  "multiple perspectives", "get a second opinion", "deliberate", "fusion", "panel", or "consensus".
  Do NOT trigger for simple tasks (quick lookups, formatting, single-file edits, casual conversation).
---

# Multi-Model Deliberation

Get better answers by consulting multiple models in parallel, then synthesizing their strengths.

## When to Deliberate

**Deliberate when:**
- The cost of being wrong is high (architecture decisions, research, analysis)
- The question has genuine debate or tradeoffs
- You need fact-checking across sources
- A single model might hallucinate or miss something
- User explicitly asks for multiple perspectives

**Don't deliberate for:**
- Simple lookups or formatting
- Single-file code edits
- Casual conversation
- Tasks where you're already confident

## How It Works

```
Your task → N subagents (different models, same task) → Judge synthesizes → Final answer
```

Each subagent gets the same prompt but uses a different model. Their responses are compared for consensus, contradictions, and blind spots. You (the main agent) produce the final answer informed by all perspectives.

## Execution Steps

### Step 1: Determine if deliberation is worth it

Ask yourself: "Would asking 3 smart people independently produce meaningfully different answers?" If yes, deliberate. If no, just answer.

### Step 2: Choose panel models

Pick 2-3 models that are **diverse** (different training, different strengths). Good defaults:

- A reasoning-focused model (e.g. Claude, o3/o4-mini)
- A different family (e.g. Gemini, GPT)
- Optionally a third wildcard

Use whatever models are available in the catalog. Diversity matters more than quantity — 3 diverse models beats 5 similar ones.

### Step 3: Fan out with delegate calls

Launch subagents **in parallel** (multiple `delegate` calls in one response). Each subagent:

- Gets the **same task description** — identical problem, identical constraints
- Uses a **different model** via `modelProfileId` parameter
- Has access to the **same tools** (bash, browser) if research is needed
- Is told to be thorough and independent

Example delegate call:
```
delegate(
  task: "<the full question/problem, same for all panelists>",
  modelProfileId: "<model-id-for-this-panelist>",
  systemPrompt: "You are an independent expert. Answer thoroughly. Don't hedge."
)
```

**Critical:** Launch ALL delegate calls in the SAME response so they run in parallel. Do not wait for one to finish before launching the next.

### Step 4: Analyze the responses

Once all subagents return, compare their outputs. Look for:

| Category | What it means | Action |
|---|---|---|
| **Consensus** | All/most models agree | High confidence — use directly |
| **Contradiction** | Models disagree | Investigate why, present both sides |
| **Partial coverage** | Only some addressed an angle | Fill gaps from others |
| **Unique insight** | Only one model raised a point | Evaluate merit, include if valid |
| **Blind spot** | Nobody addressed something | Flag it, try to answer yourself |

### Step 5: Synthesize and deliver

Write the **final answer** for the user. Structure it based on confidence:

**When models agree (high confidence):**
Just give the answer directly. Don't mention the panel — the user wants results, not process.

**When models disagree (flag it):**
```
<your best synthesis of the answer>

⚠️ Note: Models disagreed on [topic].
- Position A (model X): ...
- Position B (model Y): ...
I'm going with [A/B/nuanced] because [reasoning].
```

**When uncertainty remains:**
Be honest. Present what the panel found, note the disagreement, and let the user decide.

## Guidelines

- **Never mention "the panel" or "deliberation process" when models agree** — just deliver the synthesized answer as if it's yours. The user doesn't need to know you consulted multiple models unless there's meaningful disagreement worth surfacing.
- **Always launch delegates in parallel** — never sequentially.
- **Diversity > quantity** — 3 diverse models is the sweet spot. More than 4 is diminishing returns.
- **Keep subagent tasks focused** — don't overcomplicate the prompt. Same question, different models.
- **You are the judge** — don't just concatenate responses. Synthesize. Add your own analysis. Make a call.
- **Cost awareness** — each delegate is a full conversation. Don't deliberate on trivia.
- **If a subagent fails** — work with what you have. One good response beats zero.

## Quick Reference: Confidence Scoring

```
consensus_ratio = models_agreeing / total_models

> 0.67  → High confidence. Answer directly.
0.34-0.67 → Mixed. Present main answer, note disagreement.
< 0.34  → Low confidence. Present all sides, let user decide.
```

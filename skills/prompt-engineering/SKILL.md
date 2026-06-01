---
name: prompt-engineering
description: >-
  Write, refine, and debug prompts for Claude and other LLMs. Use when the user
  asks to improve a prompt, craft a system prompt, design a prompt template,
  reduce hallucinations, get more reliable structured output, build few-shot
  examples, or troubleshoot why a model is ignoring instructions. TRIGGER on
  phrases like "write a prompt", "improve this prompt", "system prompt",
  "the model keeps doing X", "make the output more consistent", or "prompt
  template". SKIP for general coding tasks that don't involve crafting model
  instructions.
---

# Prompt Engineering

A practical playbook for writing prompts that get reliable, high-quality output
from Claude. Apply these techniques when authoring or fixing prompts — don't
just describe them, rewrite the user's prompt to demonstrate.

## Core workflow

1. **Clarify the job.** Before writing, pin down: What is the task? Who/what
   produces the input? What does a great output look like? What are the failure
   modes to avoid? If any of these are unknown, ask one or two sharp questions.
2. **Draft with structure** (see below).
3. **Test against edge cases** — empty input, adversarial input, ambiguous
   input. A prompt that only works on the happy path isn't done.
4. **Iterate on the actual failures**, not hypothetical ones. Change one thing
   at a time so you know what helped.

## The anatomy of a strong prompt

Order matters. Put long, static content (instructions, examples, documents)
*early* and the specific request *late* — this also maximizes prompt-cache hits.

1. **Role / context** — who the model is and the situation. One or two sentences.
2. **Task** — the single, explicit thing to do. Lead with the verb.
3. **Reference material** — documents, data, examples, wrapped in clear
   delimiters (XML tags work well with Claude: `<document>...</document>`).
4. **Detailed instructions / rules** — numbered constraints, edge-case handling.
5. **Output format** — exact shape expected (JSON schema, headings, length).
6. **The actual input / request** — last, so the model acts on it freshly.

## High-leverage techniques

- **Be explicit, not implicit.** State what you *want*, not just what to avoid.
  "Respond in 2-3 sentences" beats "don't be too long."
- **Show, don't only tell (few-shot).** 2-5 diverse examples of input→output
  outperform paragraphs of description. Include a tricky/edge-case example.
- **Give Claude room to think.** For reasoning-heavy tasks, ask it to work
  through the problem before answering — e.g. "Think step by step in
  `<scratchpad>` tags, then give your final answer in `<answer>` tags." Keep
  thinking and answer separated so you can parse the answer cleanly.
- **Use XML tags to delimit.** Tags reduce the chance the model confuses
  instructions with data, and make outputs parseable.
- **Prefill the response** when you need a specific format — start the
  assistant turn with `{` for JSON, or a heading, to lock the shape.
- **Assign a persona** when tone/expertise matters: "You are a senior security
  reviewer." It shifts vocabulary and rigor.
- **Positive framing for tools/agents.** Tell the model what to do in each
  situation rather than listing prohibitions it then fixates on.

## Reliability & reducing hallucination

- Give Claude an out: "If the document doesn't contain the answer, say
  'Not stated in the source.'" This sharply cuts fabrication.
- Ground answers in provided material: "Answer **only** using the text in
  `<context>`. Quote the supporting sentence."
- For high-stakes facts, ask the model to first extract relevant quotes, then
  reason from those quotes.
- Constrain the output space: enums, schemas, and explicit allowed values beat
  free text when you need consistency.

## Structured output (JSON, etc.)

- Provide the exact schema and a filled-in example.
- Say "Output **only** valid JSON, no prose, no markdown fences."
- Prefill with `{` to prevent preamble.
- For lists, specify whether empty is allowed and what an empty result looks like.

## System prompts

- Reserve the system prompt for durable role, rules, and constraints; put the
  per-request specifics in the user turn.
- Lead with identity and the most important rules — earlier instructions carry
  more weight.
- Be concrete about scope and refusals so behavior is predictable.

## Debugging a misbehaving prompt

| Symptom | Likely cause | Fix |
|---|---|---|
| Ignores an instruction | Buried in the middle / competing with others | Move it up, isolate it, restate at the end |
| Output format drifts | Format described, not shown | Add an example + prefill the response |
| Too verbose / too terse | Length not specified | Give an explicit length or sentence count |
| Makes things up | No grounding or escape hatch | Restrict to provided context; allow "I don't know" |
| Inconsistent across runs | Open-ended task | Constrain with schema/enums; add examples |
| Refuses a legitimate task | Ambiguous, sounds risky | Add context/authorization, state the benign intent |

## Quick checklist before shipping a prompt

- [ ] Task stated in one clear sentence, leading with a verb
- [ ] Reference material delimited with tags
- [ ] Output format specified (and shown via example if non-trivial)
- [ ] Edge cases and "I don't know" path handled
- [ ] Tested on at least one adversarial / empty input
- [ ] Static content first, the specific request last

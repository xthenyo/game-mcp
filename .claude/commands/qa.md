---
description: "QA — 5-check verification gate, testing, bug tracking, build pipeline"
autoApply: false
---

# QA

5-check verification gate. Systematically verify every change.

## Activation

1. `get_context("QA")` → start from `next_task` field
2. `claim_task(id, "QA")`
3. Follow `agent_prompt` exactly
4. Run the 5-Check Gate
5. `log_decision("QA", "finding", tag="BUG|PERF")`
6. `complete_task(id, "QA", self_review="5-check results: X pass, Y fail")`

## 5-Check Verification Gate

Run all 5 checks in order for every review. Report results.

### 1. Coherence — Is the logic correct?
- Is the code logically consistent?
- Are edge cases handled? (null, empty, zero, negative)
- Any race condition risks?

### 2. Convention — Does it follow project standards?
- All English? Any non-English identifiers/comments?
- Correct naming? (`_camelCase` private, `PascalCase` method)
- VContainer DI used, not manual wiring?

### 3. Build — Does it compile?
- Assembly references correct?
- Missing `using` statements?
- Any deprecated Unity 6 APIs?

### 4. Regression — Does it break existing code?
- Does the change affect other systems?
- Are existing EventBus subscribers broken?
- Have Inspector serialized fields changed? (data loss risk)

### 5. Performance — Any GC/frame budget issues?
- GetComponent/FindObjectOfType in Update?
- new List/new Dictionary in hot paths?
- String concatenation in loops?
- LINQ in performance-critical code?

## Bug Report Format

```yaml
id: BUG-XXX
severity: P0|P1|P2|P3  # P0=crash, P1=core broken, P2=non-critical, P3=cosmetic
file: "path/to/file.cs:line"
steps: [1, 2, 3]
expected: "..."
actual: "..."
gate_failed: "coherence|convention|build|regression|performance"
```

## Research if needed

```bash
gemini "Unity 6 NUnit [topic] testing best practices 2026"
```

## Don't

- Write gameplay code (only test code)
- Edit Bible directly (only validate, report issues via log_decision)
- Shallow reviews — check all 5 gates one by one
- Off-task "improvement" suggestions

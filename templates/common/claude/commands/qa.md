---
description: "QA — 5-check verification gate, testing, bug tracking, build pipeline"
autoApply: false
---

# QA

5-check verification gate. Systematically verify every change.

## Activation

1. `get_context("QA")` -> start from `next_task` field
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
- Correct naming conventions?
- Proper patterns used (DI, events, async)?

### 3. Build — Does it compile/run?
- All imports/references correct?
- No deprecated APIs?

### 4. Regression — Does it break existing code?
- Does the change affect other systems?
- Are existing integrations broken?

### 5. Performance — Any performance issues?
- Expensive operations in hot paths?
- Memory allocations in loops?
- String concatenation in loops?

### 6. Error Monitoring (if Sentry configured)
- Check Sentry dashboard for new errors after deployment
- Verify error breadcrumbs are meaningful
- Confirm no PII leaking in error reports
- Check error rate trends

## Verification Tools

| Tool | When to use |
|------|-------------|
| `gemini "..."` | Research known issues, best practices for a pattern |
| Context7 MCP | Check official docs for API correctness (Unity, VContainer, etc.) |
| Sequential Thinking MCP | Systematic root cause analysis for complex bugs |
| Sentry MCP (if enabled) | `sentry_search_issues()`, `sentry_get_issue_details()` — production error dashboard |

## Bug Report Format

```yaml
id: BUG-XXX
severity: P0|P1|P2|P3
file: "path/to/file:line"
steps: [1, 2, 3]
expected: "..."
actual: "..."
gate_failed: "coherence|convention|build|regression|performance"
```

## Don't

- Write gameplay code (only test code)
- Edit Bible directly (only validate, report issues)
- Shallow reviews — check all 5 gates
- Off-task "improvement" suggestions

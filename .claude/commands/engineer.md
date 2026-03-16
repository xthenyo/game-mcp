---
description: "Engineer — all Unity C# code: gameplay, systems, infrastructure"
autoApply: false
---

# ENGINEER

Unity C# code: gameplay systems, infrastructure, editor tools, UI code-behind.

## Activation

1. `get_context("ENGINEER")` → start from `next_task` field
2. `claim_task(id, "ENGINEER")`
3. Follow `agent_prompt` exactly
4. When done: `log_decision("ENGINEER", "decision", tag="ARCH|BUG|PERF")`
5. `complete_task(id, "ENGINEER", self_review="what I did + requirements met?")`
6. Continue to next OPEN task if available

## Read-Before-Write Gate

BEFORE writing code:
1. `Read` the file you're about to change
2. Summarize in 2-3 sentences: what does existing code do, how does your change fit
3. Only then write

## Atomic Change Rule

- One task = one focused change. If changing 3+ files, stop and tell Lead.
- Don't break existing working code. Think about side effects.
- Refactor only if requested in the task. No unsolicited "improvements".

## Research if needed

```bash
gemini "Unity 6 [topic] best practices 2026"
```

## Code Patterns

```csharp
// VContainer DI — constructor injection for pure C#, [Inject] for MonoBehaviour
public class GameService : IAsyncStartable {
    [Inject] readonly IEventBus _eventBus;
    public async UniTask StartAsync(CancellationToken ct) { ... }
}

// Event — struct, zero allocation
public struct ScoreChangedEvent { public int NewScore; }

// UniTask — CancellationToken mandatory, use destroyCancellationToken
async UniTask LoadAsync(CancellationToken ct) {
    await UniTask.Delay(1000, cancellationToken: ct);
}

// Inspector — [SerializeField] private, never public
[SerializeField] private float _moveSpeed = 5f;
```

## Don't

- Write/Edit without Read first
- GetComponent in Update, FindObjectOfType, new List in hot paths
- Leave empty Start()/Update() — delete them
- `using` for packages not in project (VContainer, UniTask, UI Toolkit exist; DOTween, Zenject DON'T)
- Assembly layer violations (Core → Gameplay → UI → App, no reverse references)
- Off-task "improvements" — only make the requested change

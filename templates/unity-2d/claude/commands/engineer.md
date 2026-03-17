---
description: "Engineer — Unity C# code: gameplay systems, 2D mechanics, infrastructure"
autoApply: false
---

# ENGINEER — Unity 2D

Unity C# code: 2D gameplay systems, infrastructure, editor tools, UI code-behind.

## Activation

1. `get_context("ENGINEER")` -> start from `next_task` field
2. `claim_task(id, "ENGINEER")`
3. Follow `agent_prompt` exactly
4. When done: `log_decision("ENGINEER", "decision", tag="ARCH|BUG|PERF")`
5. `complete_task(id, "ENGINEER", self_review="what I did + requirements met?")`
6. Continue to next OPEN task if available

## Read-Before-Write Gate

BEFORE writing code:
1. `Read` the file you're about to change
2. Summarize: what does existing code do, how does your change fit
3. Only then write

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

## 2D-Specific Patterns

```csharp
// Movement — Rigidbody2D in FixedUpdate
private void FixedUpdate() {
    _rigidbody.MovePosition(_rigidbody.position + _velocity * Time.fixedDeltaTime);
}

// Sprite animation — Animator with states
_animator.Play("Walk");

// Tilemap interaction
var cellPos = _tilemap.WorldToCell(worldPos);
var tile = _tilemap.GetTile(cellPos);

// 2D Physics — use layers for collision filtering
[SerializeField] private LayerMask _groundLayer;
var hit = Physics2D.Raycast(origin, Vector2.down, distance, _groundLayer);
```

## Don't

- Write/Edit without Read first
- GetComponent in Update, FindObjectOfType, new List in hot paths
- Leave empty Start()/Update() — delete them
- Use packages not in manifest (VContainer, UniTask, UI Toolkit exist)
- Assembly layer violations (Core -> Gameplay -> UI -> App)
- Off-task "improvements"

# Unity Project Structure

This folder contains the game code. The framework provides a ready-to-use base structure.

## Folder Structure

```
_Project/
├── Scripts/
│   ├── Core/              # Framework - DO NOT MODIFY
│   │   ├── Bootstrap.cs   # DI container setup
│   │   ├── EventBus.cs    # Event system
│   │   └── GameState.cs   # Game state management
│   │
│   ├── Gameplay/          # Game logic - WRITE HERE
│   │   ├── Systems/       # Turn, Combat, etc.
│   │   ├── Entities/      # Player, NPC, etc.
│   │   └── Controllers/   # Input, Camera, etc.
│   │
│   ├── Services/          # Services - WRITE HERE
│   │   ├── Save/          # Save/Load system
│   │   ├── Audio/         # Audio management
│   │   └── Platform/      # Steam, iOS, Android
│   │
│   └── UI/                # Interface - WRITE HERE
│       ├── Screens/       # MainMenu, Pause, etc.
│       ├── Components/    # Button, Panel, etc.
│       └── Presenters/    # MVP/MVVM presenters
│
├── Scenes/
├── Prefabs/
├── Resources/
├── ScriptableObjects/
└── Art/
```

## Core Systems

### Bootstrap (DI Setup)

```csharp
protected override void Configure(IContainerBuilder builder)
{
    // Framework services (built-in)
    builder.Register<EventBus>(Lifetime.Singleton).As<IEventBus>();
    builder.Register<GameState>(Lifetime.Singleton).As<IGameState>();

    // Your services
    builder.Register<SaveSystem>(Lifetime.Singleton).As<ISaveSystem>();
}
```

### EventBus

```csharp
// Define event
public struct PlayerDiedEvent
{
    public string PlayerId;
}

// Publish
_eventBus.Publish(new PlayerDiedEvent { PlayerId = "player_1" });

// Subscribe
_eventBus.Subscribe<PlayerDiedEvent>(OnPlayerDied);
```

### GameState

```csharp
_gameState.SetPhase(GamePhase.Playing);
_gameState.AdvanceTurn();
_gameState.OnTurnAdvanced += (turn) => Debug.Log($"Turn {turn}");
```

## Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Class | PascalCase | `PlayerController` |
| Interface | IPascalCase | `ISaveSystem` |
| Private field | _camelCase | `_playerHealth` |
| Constant | UPPER_SNAKE | `MAX_HEALTH` |

## Adding New Systems

1. Create class in `Gameplay/Systems/`
2. Define interface
3. Register in `Bootstrap.cs`
4. Inject with `[Inject]`

```csharp
// Interface
public interface ITurnSystem
{
    int CurrentTurn { get; }
    void AdvanceTurn();
}

// Implementation
public class TurnSystem : ITurnSystem { ... }

// Register
builder.Register<TurnSystem>(Lifetime.Singleton).As<ITurnSystem>();

// Use
[Inject] private readonly ITurnSystem _turnSystem;
```

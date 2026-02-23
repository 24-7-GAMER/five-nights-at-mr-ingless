# Five Nights at Mr Ingles - Unity C# Conversion Guide

## Overview
This guide helps you convert the Python/Pygame game to Unity/C#. The game has approximately 4913 lines of Python code that need to be restructured for Unity's architecture.

## Key Differences: Pygame vs Unity

### Architecture Changes
| Pygame (Python) | Unity (C#) |
|----------------|------------|
| Manual game loop | MonoBehaviour lifecycle (Update, FixedUpdate) |
| Single `main.py` file | Multiple C# scripts on GameObjects |
| Manual rendering | Scene-based rendering |
| Manual sprite loading | Asset import & references |
| Dictionary-based rooms | Scene or ScriptableObject rooms |

## Unity Project Setup

### 1. Create New Unity Project
1. Open Unity Hub
2. Create **New Project** → **2D Core** template
3. Name it: `FiveNightsAtMrIngles`
4. Unity version: 2022.3 LTS or newer

### 2. Folder Structure
Create this folder structure in your Unity `Assets/` folder:

```
Assets/
├── Scripts/
│   ├── Core/
│   │   ├── GameManager.cs
│   │   ├── GameState.cs
│   │   ├── SaveLoadManager.cs
│   │   └── Constants.cs
│   ├── Systems/
│   │   ├── PowerSystem.cs
│   │   ├── CameraSystem.cs
│   │   ├── OfficeController.cs
│   │   └── DoorController.cs
│   ├── AI/
│   │   ├── Animatronic.cs
│   │   ├── AIBehavior.cs
│   │   ├── PathfindingManager.cs
│   │   └── RoomGraph.cs
│   ├── UI/
│   │   ├── UIManager.cs
│   │   ├── MenuController.cs
│   │   ├── HUDController.cs
│   │   └── CameraUIController.cs
│   ├── Effects/
│   │   ├── VisualEffectsManager.cs
│   │   ├── ParticleController.cs
│   │   └── PostProcessController.cs
│   └── Audio/
│       ├── AudioManager.cs
│       └── SFXController.cs
├── Sprites/
│   ├── Characters/
│   ├── Environment/
│   ├── UI/
│   └── Effects/
├── Audio/
│   ├── Music/
│   └── SFX/
├── Prefabs/
│   ├── Animatronics/
│   ├── UI/
│   └── Effects/
├── Scenes/
│   ├── MainMenu.unity
│   ├── Office.unity
│   └── Cameras.unity
├── ScriptableObjects/
│   ├── Rooms/
│   └── Animatronics/
└── Resources/
    └── Data/
```

## Core Systems Conversion

### 1. GameState → GameManager.cs
**Python Concept:**
```python
class GameState:
    def __init__(self):
        self.state = "splash"
        self.night = 1
        self.hour = 12
```

**Unity C# Pattern:**
```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }
    
    public enum GameState { Splash, Menu, Playing, Paused, Jumpscare, Win }
    public GameState currentState = GameState.Splash;
    
    public int currentNight = 1;
    public int currentHour = 12;
    
    void Awake()
    {
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
        DontDestroyOnLoad(gameObject);
    }
}
```

### 2. Room Navigation → ScriptableObjects
**Python Concept:**
```python
ROOM_GRAPH = {
    "Office": ["West Hall", "East Hall"],
    "West Hall": ["Office", "Cafeteria"]
}
```

**Unity C# Pattern:**
```csharp
[CreateAssetMenu(fileName = "RoomData", menuName = "Game/Room")]
public class RoomData : ScriptableObject
{
    public string roomName;
    public List<RoomData> connectedRooms;
    public Vector2 minimapPosition;
    public Sprite roomSprite;
}
```

### 3. Animatronic AI → MonoBehaviour
**Python Concept:**
```python
class Animatronic:
    def update(self, dt, game_state):
        self.timer += dt
        if self.move_cooldown <= 0:
            self.move_patrol()
```

**Unity C# Pattern:**
```csharp
public class Animatronic : MonoBehaviour
{
    public string characterName;
    public RoomData currentRoom;
    public float aggression = 1f;
    
    private float moveTimer;
    private float moveInterval = 5f;
    
    void Update()
    {
        moveTimer += Time.deltaTime;
        if (moveTimer >= moveInterval)
        {
            moveTimer = 0f;
            MoveToNextRoom();
        }
    }
    
    void MoveToNextRoom() { /* AI logic */ }
}
```

### 4. Power System → Singleton Pattern
**Python Concept:**
```python
class PowerSystem:
    def __init__(self):
        self.current = 100
        self.base_drain = 0.16
```

**Unity C# Pattern:**
```csharp
public class PowerSystem : MonoBehaviour
{
    public static PowerSystem Instance;
    
    public float maxPower = 100f;
    public float currentPower = 100f;
    public float baseDrain = 0.16f;
    
    void Awake()
    {
        Instance = this;
    }
    
    void Update()
    {
        DrainPower(baseDrain * Time.deltaTime);
    }
    
    public void DrainPower(float amount)
    {
        currentPower = Mathf.Max(0, currentPower - amount);
    }
}
```

### 5. Visual Effects → Post-Processing + Shaders
**Python Concept:**
```python
self.chromatic_aberration = 0.0
self.screen_distortion = 0.0
self.vhs_effect = 0.0
```

**Unity Approach:**
- Use **Unity's Post-Processing Stack V2** or **URP Post-Processing**
- Create custom shader graphs for VHS, chromatic aberration
- Use Renderer Features for scanlines

## Step-by-Step Conversion Process

### Phase 1: Core Framework (Week 1)
1. ✅ Create Unity project
2. ✅ Set up folder structure
3. ✅ Create GameManager singleton
4. ✅ Create GameState enum and data structures
5. ✅ Implement SaveLoadManager using JSON

### Phase 2: Office Mechanics (Week 2)
1. ✅ Create Office scene
2. ✅ Implement PowerSystem
3. ✅ Create DoorController (left/right doors)
4. ✅ Add light toggle system
5. ✅ Implement camera switching UI

### Phase 3: Room System (Week 3)
1. ✅ Create RoomData ScriptableObjects
2. ✅ Build room graph connections
3. ✅ Implement minimap display
4. ✅ Create camera view system

### Phase 4: AI System (Week 4)
1. ✅ Create Animatronic base class
2. ✅ Implement patrol routes
3. ✅ Add AI decision-making
4. ✅ Implement attack logic
5. ✅ Create jumpscare system

### Phase 5: Audio & Effects (Week 5)
1. ✅ Implement AudioManager
2. ✅ Add ambient sounds
3. ✅ Create visual effects (VHS, chromatic aberration)
4. ✅ Implement particle systems

### Phase 6: UI & Menus (Week 6)
1. ✅ Create main menu
2. ✅ Build night selection
3. ✅ Create HUD (power, time, camera buttons)
4. ✅ Add pause menu
5. ✅ Create win/lose screens

## Critical Unity Concepts to Learn

### 1. MonoBehaviour Lifecycle
```csharp
void Awake()    // Initialization
void Start()    // Called before first Update
void Update()   // Called every frame
void FixedUpdate() // Fixed time intervals for physics
void OnDestroy() // Cleanup
```

### 2. Singleton Pattern
```csharp
public class Manager : MonoBehaviour
{
    public static Manager Instance { get; private set; }
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
}
```

### 3. Coroutines (Replace Python threading/timers)
```csharp
IEnumerator MoveAfterDelay(float delay)
{
    yield return new WaitForSeconds(delay);
    MoveToNextRoom();
}

// Start coroutine
StartCoroutine(MoveAfterDelay(2f));
```

### 4. Events & Delegates
```csharp
public delegate void PowerOutageEvent();
public static event PowerOutageEvent OnPowerOutage;

// Trigger event
OnPowerOutage?.Invoke();

// Subscribe to event
void OnEnable()
{
    PowerSystem.OnPowerOutage += HandlePowerOutage;
}
```

## Python → C# Syntax Quick Reference

| Python | C# |
|--------|-----|
| `def function(param):` | `void Function(Type param) { }` |
| `self.variable = value` | `this.variable = value;` |
| `if condition:` | `if (condition) { }` |
| `for item in list:` | `foreach (var item in list) { }` |
| `random.randint(1, 10)` | `Random.Range(1, 11)` |
| `time.time()` | `Time.time` |
| `dt` (delta time) | `Time.deltaTime` |
| `math.clamp(x, min, max)` | `Mathf.Clamp(x, min, max)` |
| `dict = {}` | `Dictionary<K, V> dict = new Dictionary<K, V>()` |
| `list = []` | `List<T> list = new List<T>()` |

## Key Unity Packages to Install

1. **Post-Processing Stack** (Visual effects)
   - Window → Package Manager → Post Processing

2. **TextMeshPro** (Better text rendering)
   - Comes pre-installed in modern Unity

3. **Universal Render Pipeline (URP)** - Optional but recommended
   - Better performance and more visual options

## Asset Migration

### Copy Your Assets:
1. **Images:** Copy `assets/img/*` → `Assets/Sprites/`
2. **Music:** Copy `assets/music/*` → `Assets/Audio/Music/`
3. **SFX:** Copy `assets/sfx/*` → `Assets/Audio/SFX/`

### Import Settings:
- **Sprites:** Texture Type = Sprite (2D and UI)
- **Audio:** Compress audio (Vorbis for music, ADPCM for SFX)

## Debugging Tips

### Print Debug Logs
```csharp
Debug.Log("Message");
Debug.LogWarning("Warning");
Debug.LogError("Error");
```

### Inspector Variables
```csharp
[SerializeField] private float speed = 5f;  // Private but visible in Inspector
public float publicSpeed = 5f;              // Public and visible
[HideInInspector] public float hidden;      // Public but hidden
```

### Gizmos for Visualization
```csharp
void OnDrawGizmos()
{
    Gizmos.color = Color.red;
    Gizmos.DrawWireSphere(transform.position, 2f);
}
```

## Common Pitfalls to Avoid

1. **❌ Don't use `new GameObject().AddComponent<T>()`** in Update() → Create prefabs instead
2. **❌ Don't use `Find()` every frame** → Cache references in Start()
3. **❌ Don't forget semicolons** → C# requires them
4. **❌ Don't use `==` for null checks on Unity objects** → Use `== null` or `is null`
5. **❌ Don't forget to unsubscribe from events** → Memory leaks

## Performance Optimization

### Object Pooling (For particles, effects)
```csharp
public class ObjectPool : MonoBehaviour
{
    public GameObject prefab;
    private Queue<GameObject> pool = new Queue<GameObject>();
    
    public GameObject Get()
    {
        if (pool.Count > 0)
        {
            GameObject obj = pool.Dequeue();
            obj.SetActive(true);
            return obj;
        }
        return Instantiate(prefab);
    }
    
    public void Return(GameObject obj)
    {
        obj.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

## Next Steps

1. **Install Unity** (if you haven't)
2. **Create a new 2D project**
3. **Set up the folder structure** above
4. **Start with GameManager.cs** (I'll help you create this)
5. **Migrate assets** (copy images, audio files)
6. **Build systems one at a time** (Power → Doors → Cameras → AI)

## Resources to Learn Unity C#

- **Unity Learn:** https://learn.unity.com/
- **Brackeys YouTube:** Classic Unity tutorials
- **Code Monkey:** Advanced C# patterns
- **Unity Documentation:** https://docs.unity3d.com/

---

## Ready to Start?

I can help you create the core C# scripts to get started. Would you like me to:

1. ✅ Create **GameManager.cs**
2. ✅ Create **PowerSystem.cs**
3. ✅ Create **Animatronic.cs**
4. ✅ Create **RoomData.cs** (ScriptableObject)
5. ✅ Create **OfficeController.cs**

Let me know which scripts you'd like me to generate first, and I'll create professional, well-commented C# code that matches your Python game's functionality!

# Five Nights at Mr Ingles - Unity Implementation Roadmap

## Week 1: Project Setup & Core Systems

### Day 1-2: Unity Setup
- [ ] Install Unity Hub (if not installed)
- [ ] Install Unity 2022.3 LTS
- [ ] Create new 2D project: "FiveNightsAtMrIngles"
- [ ] Set up version control (Git recommended)
- [ ] Copy all scripts from `Unity_Scripts/` to `Assets/Scripts/`
- [ ] Wait for compilation, fix any errors

### Day 3-4: Core Managers Setup
1. Create GameObject hierarchy:
```
--- GameSystems (Empty GameObject)
    --- GameManager (Add GameManager.cs)
    --- SaveLoadManager (Add SaveLoadManager.cs)
    --- PowerSystem (Add PowerSystem.cs)
    --- OfficeController (Add OfficeController.cs)
    --- CameraSystem (Add CameraSystem.cs)
    --- AudioManager (Add AudioManager.cs)
```

2. Mark `GameSystems` as DontDestroyOnLoad:
```csharp
// Add to GameSystems parent object
void Awake()
{
    DontDestroyOnLoad(gameObject);
}
```

3. Test in Play Mode - should see debug logs confirming initialization

### Day 5-7: Asset Import
1. Create folder structure:
```
Assets/
├── Sprites/
│   ├── Rooms/      (Copy from assets/img/)
│   ├── Characters/ (Animatronic sprites)
│   └── UI/         (Buttons, icons)
├── Audio/
│   ├── Music/      (Copy from assets/music/)
│   └── SFX/        (Copy from assets/sfx/)
```

2. Import all assets:
   - Copy Python game's `assets/img/` to `Assets/Sprites/Rooms/`
   - Copy Python game's `assets/music/` to `Assets/Audio/Music/`
   - Copy Python game's `assets/sfx/` to `Assets/Audio/SFX/`

3. Configure import settings:
   - Sprites: Set Texture Type = "Sprite (2D and UI)"
   - Audio: Music = Vorbis, SFX = PCM/ADPCM

---

## Week 2: Room System & ScriptableObjects

### Day 1-3: Create Room Data
1. Create folder: `Assets/Data/Rooms/`
2. Right-click → `Create → Five Nights → Room Data`
3. Create 14 RoomData assets (one per room):

**Office** (isOffice = true)
- Connected Rooms: West Hall, East Hall, Supply Closet, Restrooms
- Minimap Position: X=0.5, Y=0.85

**Stage** (isStartingRoom = true)
- Connected Rooms: Dining Area, Backstage
- Minimap Position: X=0.5, Y=0.1

**Dining Area**
- Connected Rooms: Stage, West Hall, Kitchen
- Minimap Position: X=0.3, Y=0.25

**Backstage**
- Connected Rooms: Stage, East Hall, Kitchen
- Minimap Position: X=0.7, Y=0.25

**Kitchen**
- Connected Rooms: Dining Area, Backstage, Cafeteria
- Minimap Position: X=0.5, Y=0.35

**West Hall**
- Connected Rooms: Office, Cafeteria, Dining Area, Supply Closet
- Minimap Position: X=0.25, Y=0.65

**East Hall**
- Connected Rooms: Office, Gym, Backstage, Restrooms
- Minimap Position: X=0.75, Y=0.65

**Cafeteria**
- Connected Rooms: West Hall, Kitchen, Library
- Minimap Position: X=0.12, Y=0.45

**Gym**
- Connected Rooms: East Hall, Bathrooms
- Minimap Position: X=0.88, Y=0.45

**Library**
- Connected Rooms: Cafeteria, Bathrooms
- Minimap Position: X=0.12, Y=0.65

**Bathrooms**
- Connected Rooms: Gym, Library, Vent
- Minimap Position: X=0.88, Y=0.65

**Vent**
- Connected Rooms: Bathrooms, Supply Closet, Restrooms
- Minimap Position: X=0.82, Y=0.78

**Supply Closet**
- Connected Rooms: Office, West Hall, Vent
- Minimap Position: X=0.18, Y=0.78

**Restrooms**
- Connected Rooms: Office, East Hall, Vent
- Minimap Position: X=0.68, Y=0.52

### Day 4-5: Assign Camera Sprites
1. For each RoomData asset:
   - Assign the corresponding room sprite to "Camera View Sprite"
   - Enable "Has Camera" checkbox

2. Test room connections:
   - Select each RoomData asset
   - Verify "Connected Rooms" list is correct
   - Check minimap positions make sense

### Day 6-7: Hook Up Camera System
1. Select `CameraSystem` GameObject
2. Drag all 14 RoomData assets into "All Rooms" list
3. Test camera switching:
   - Press Play
   - Use debug menu: Right-click CameraSystem → "Next Camera"
   - Verify room changes work

---

## Week 3: Office Scene & UI

### Day 1-2: Create Office Scene
1. Create new scene: `Scenes/Office.unity`
2. Add background sprite (office image)
3. Create UI Canvas:
   - Right-click Hierarchy → `UI → Canvas`
   - Set Canvas Scaler to "Scale With Screen Size"
   - Reference Resolution: 1280 x 720

### Day 3-4: Build HUD
Create these UI elements:

**Power Display:**
```
Canvas/
└── HUD/
    └── PowerPanel/
        ├── PowerSlider (UI Slider)
        ├── PowerText (Text: "100%")
        └── PowerIcon (Image)
```

**Time Display:**
```
HUD/
└── TimePanel/
    ├── TimeText (Text: "12 AM")
    └── ClockIcon (Image)
```

**Camera Button:**
```
HUD/
└── CameraButton (Button)
    └── Text ("CAMERA")
```

**Door Buttons:**
```
HUD/
├── LeftDoorButton (Button - Position: Left side)
│   └── Text ("DOOR")
└── RightDoorButton (Button - Position: Right side)
    └── Text ("DOOR")
```

### Day 5-7: Create UI Scripts
Create `Assets/Scripts/UI/HUDController.cs`:

```csharp
using UnityEngine;
using UnityEngine.UI;
using FiveNightsAtMrIngles;

public class HUDController : MonoBehaviour
{
    public Slider powerSlider;
    public Text powerText;
    public Text timeText;
    public Button cameraButton;
    public Button leftDoorButton;
    public Button rightDoorButton;

    void OnEnable()
    {
        PowerSystem.OnPowerChanged += UpdatePower;
        GameManager.OnHourChange += UpdateTime;
    }

    void OnDisable()
    {
        PowerSystem.OnPowerChanged -= UpdatePower;
        GameManager.OnHourChange -= UpdateTime;
    }

    void Start()
    {
        // Hook up button listeners
        cameraButton.onClick.AddListener(() => 
            OfficeController.Instance?.ToggleCameras());
        
        leftDoorButton.onClick.AddListener(() => 
            OfficeController.Instance?.ToggleDoorLeft());
        
        rightDoorButton.onClick.AddListener(() => 
            OfficeController.Instance?.ToggleDoorRight());
    }

    void UpdatePower(float percent)
    {
        powerSlider.value = percent / 100f;
        powerText.text = $"{percent:F0}%";
    }

    void UpdateTime(int hour)
    {
        timeText.text = $"{hour} AM";
    }
}
```

---

## Week 4: Animatronics & AI

### Day 1-2: Create Animatronic GameObjects
1. Create folder: `Assets/Prefabs/Animatronics/`
2. Create GameObject: "MrIngles"
3. Add SpriteRenderer component
4. Add Animatronic.cs component
5. Configure:
   - Character Name: "Mr Ingles"
   - Starting Room: Stage RoomData
   - Patrol Route: Stage → Dining → West Hall → Office
   - Base Aggression: 1.0
   - Base Move Interval: 5.0
   - Movement Style: Patrol
   - Personality: Aggressive
   - Special Ability: Speed Demon
   - Attack From Left: true

6. Create 3-5 more animatronics with varied settings:
   - Different patrol routes
   - Different personalities
   - Different special abilities
   - Different start delays (0, 1, 2, 3 minutes)

### Day 3-4: Test AI Behavior
1. Press Play
2. Use GameManager debug menu:
   - Right-click GameManager → "Win Current Night" to fast-forward
3. Watch Console for animatronic movement logs
4. Test door blocking:
   - Wait for animatronic to reach hallway
   - Close corresponding door
   - Verify animatronic retreats

### Day 5-7: Create Animatronic ScriptableObject (Advanced)
Optional: Create `AnimatronicData.cs` ScriptableObject to store configurations separately from scene.

---

## Week 5: Camera UI & Minimap

### Day 1-3: Create Camera Panel
```
Canvas/
└── CameraPanel/ (Disable by default)
    ├── Background (Black semi-transparent)
    ├── CameraFeed/ (Image showing room sprite)
    ├── RoomNameText (Text: "Stage")
    ├── Minimap/ (UI Image with minimap background)
    │   └── RoomDots/ (Generate dynamically)
    └── CloseButton (Button: "X")
```

### Day 4-5: Create Camera UI Controller
Create `Assets/Scripts/UI/CameraUIController.cs`:

```csharp
using UnityEngine;
using UnityEngine.UI;
using FiveNightsAtMrIngles;

public class CameraUIController : MonoBehaviour
{
    public GameObject cameraPanel;
    public Image cameraFeed;
    public Text roomNameText;

    void OnEnable()
    {
        OfficeController.OnCameraToggle += HandleCameraToggle;
        CameraSystem.OnCameraSwitch += HandleCameraSwitch;
    }

    void OnDisable()
    {
        OfficeController.OnCameraToggle -= HandleCameraToggle;
        CameraSystem.OnCameraSwitch -= HandleCameraSwitch;
    }

    void HandleCameraToggle(bool open)
    {
        cameraPanel.SetActive(open);
        
        if (open)
        {
            UpdateCameraView();
        }
    }

    void HandleCameraSwitch(RoomData room)
    {
        UpdateCameraView();
    }

    void UpdateCameraView()
    {
        RoomData currentRoom = CameraSystem.Instance?.GetCurrentRoom();
        if (currentRoom == null) return;

        cameraFeed.sprite = currentRoom.cameraViewSprite;
        roomNameText.text = currentRoom.roomName;
    }
}
```

### Day 6-7: Implement Minimap
Create minimap dots for each room that light up when selected.

---

## Week 6: Polish & Effects

### Day 1-2: Audio Integration
1. Assign audio clips to AudioManager:
   - Menu Music
   - Night Ambience (1-5)
   - Door Open/Close SFX
   - Light Switch SFX
   - Camera Toggle SFX
   - Jumpscare SFX
   - Clock Chime SFX

2. Test audio:
   - Press Play
   - Toggle doors/lights
   - Listen for SFX
   - Switch cameras

### Day 3-4: Visual Effects (Post-Processing)
1. Install Post-Processing package:
   - Window → Package Manager → Post Processing → Install

2. Create Post-Process Volume:
   - GameObject → Volume → Global Volume
   - Add Profile → Create new

3. Add effects:
   - Vignette (darkness in corners)
   - Chromatic Aberration (RGB split)
   - Film Grain (VHS effect)
   - Color Grading (desaturate for horror)

### Day 5-6: Jumpscare System
1. Create Jumpscare Canvas:
```
Canvas/
└── JumpscarePanel/ (Disable by default)
    ├── JumpscareImage (Fullscreen image)
    └── JumpscareAnim (Animator)
```

2. Create script: `JumpscareController.cs`
3. Subscribe to `GameManager.OnGameOver`
4. Play jumpscare animation + sound
5. Wait 2 seconds → Show death screen

### Day 7: Main Menu
1. Create scene: `Scenes/MainMenu.unity`
2. Create UI:
   - Title
   - Night selection buttons (1-5)
   - Settings panel
   - Quit button

3. Create `MenuController.cs` script
4. Hook up night selection buttons to `GameManager.StartNight(night)`

---

## Week 7: Testing & Bug Fixes

### Day 1-3: Gameplay Testing
- [ ] Test Night 1 (easy difficulty)
- [ ] Test Night 2 (medium difficulty)
- [ ] Test Night 3 (hard difficulty)
- [ ] Test Night 4 (very hard)
- [ ] Test Night 5 (extreme)

### Day 4-5: Balance Tuning
- Adjust animatronic aggression
- Tweak power drain rates
- Adjust night length
- Test difficulty curve

### Day 6-7: Bug Fixes
- Fix any crashes
- Fix UI issues
- Fix audio glitches
- Optimize performance

---

## Week 8: Build & Deployment

### Day 1-2: Build Settings
1. File → Build Settings
2. Add scenes in order:
   - MainMenu
   - Office
3. Select platform (Windows/Mac/Linux)
4. Configure Player Settings:
   - Company Name
   - Product Name
   - Icon
   - Resolution (1280x720 default)

### Day 3-4: Build Testing
1. Build executable
2. Test on different computers
3. Fix any build-specific bugs
4. Create installer (optional)

### Day 5-7: Final Polish
- Add credits screen
- Add tutorial (optional)
- Create README.txt for players
- Package for distribution

---

## 🎯 Success Criteria

Your Unity conversion is complete when:

- [x] All scripts compile without errors
- [ ] GameManager transitions through all states correctly
- [ ] Power system drains and triggers outage
- [ ] Doors open/close with animations
- [ ] Cameras switch between rooms
- [ ] Animatronics move through rooms autonomously
- [ ] Animatronics attack when doors are open
- [ ] Jumpscare plays on death
- [ ] Night progression works (12 AM - 6 AM)
- [ ] Save/Load system persists progress
- [ ] Audio plays correctly
- [ ] UI is fully functional
- [ ] Game builds to executable

---

## 💡 Tips for Success

1. **Work incrementally** - Don't try to do everything at once
2. **Test frequently** - Press Play often to catch bugs early
3. **Use Debug.Log** - Print everything to understand flow
4. **Read Unity docs** - When stuck, search Unity documentation
5. **Ask for help** - Unity community is very helpful
6. **Start simple** - Get basic functionality working first
7. **Polish later** - Don't worry about graphics until gameplay works

---

## 📚 Learning Resources

### Unity Basics
- Unity Learn: C# Scripting for Beginners
- Brackeys: "How to make a Video Game" series
- Unity Manual: MonoBehaviour Lifecycle

### Specific Topics
- **UI:** Unity UI Essentials tutorial
- **Audio:** Audio Mixer tutorial
- **Save/Load:** Saving and Loading Data
- **Events:** Unity Events & Delegates
- **ScriptableObjects:** Game Architecture with ScriptableObjects

---

**Good luck! You've got all the tools you need. Take it one week at a time and you'll have a fully functional Unity version of Five Nights at Mr Ingles!** 🎮

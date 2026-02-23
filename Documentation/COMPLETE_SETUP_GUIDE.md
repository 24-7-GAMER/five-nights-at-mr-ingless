# Complete Scripts Index & Setup Guide

## 📚 All Scripts Created (19 Total)

### ✅ Core Systems (4 scripts)
- `Core/GameManager.cs` - Main game state controller
- `Core/Constants.cs` - Game-wide constants  
- `Core/SaveLoadManager.cs` - JSON save/load system
- `Core/InputManager.cs` - Centralized input handling

### ✅ Gameplay Systems (3 scripts)
- `Systems/PowerSystem.cs` - Power management & outage
- `Systems/OfficeController.cs` - Doors, lights, cameras
- `Systems/CameraSystem.cs` - Room switching & navigation

### ✅ AI Systems (2 scripts)
- `AI/Animatronic.cs` - Full AI with personalities & abilities
- `AI/AnimatronicManager.cs` - Manages all animatronics

### ✅ Audio System (1 script)
- `Audio/AudioManager.cs` - Music, SFX, ambience

### ✅ UI Controllers (6 scripts)
- `UI/HUDController.cs` - In-game HUD (power, time, status)
- `UI/MenuController.cs` - Main menu & night selection
- `UI/CameraUIController.cs` - Camera feed & minimap
- `UI/JumpscareController.cs` - Jumpscare sequence & death screen
- `UI/PauseMenuController.cs` - Pause menu functionality
- `UI/TutorialController.cs` - Tutorial system for Night 1

### ✅ Effects Systems (2 scripts)
- `Effects/VisualEffectsManager.cs` - Post-processing, VHS, chromatic aberration
- `Effects/ParticleController.cs` - Particle pooling system

### ✅ Data Structures (1 script)
- `ScriptableObjects/RoomData.cs` - Room definition data

---

## 🏗️ COMPLETE UNITY SETUP (Step-by-Step)

### Phase 1: Create Unity Project (10 minutes)

1. **Open Unity Hub**
2. **New Project** → **2D Core** template
3. **Project Name:** `FiveNightsAtMrIngles`
4. **Unity Version:** 2022.3 LTS or newer
5. Click **Create Project**

### Phase 2: Import Scripts (5 minutes)

1. Copy `FIVE_NIGHTS_AT_MR_INGLES/Unity_Scripts/` folder to `Assets/Scripts/` in your Unity project
2. Wait for Unity to compile (watch bottom-right progress bar)
3. Check Console for any errors (there shouldn't be any!)

### Phase 3: Install Dependencies (5 minutes)

1. **Window → Package Manager**
2. Install these packages:
   - **Post Processing** (for visual effects)
   - **TextMeshPro** (better text rendering - may auto-install)

### Phase 4: Create Scene Hierarchy (20 minutes)

#### Create Game Managers Object:

```
Hierarchy:
--- GameSystems (Empty GameObject)
    --- GameManager (Add GameManager.cs)
    --- SaveLoadManager (Add SaveLoadManager.cs)
    --- PowerSystem (Add PowerSystem.cs)
    --- OfficeController (Add OfficeController.cs)
    --- CameraSystem (Add CameraSystem.cs)
    --- AudioManager (Add AudioManager.cs)
    --- InputManager (Add InputManager.cs)
    --- AnimatronicManager (Add AnimatronicManager.cs)
```

**Important:** Mark `GameSystems` as `DontDestroyOnLoad`:
```csharp
// Add this script to GameSystems GameObject
void Awake() { DontDestroyOnLoad(gameObject); }
```

#### Create Effects Managers:

```
Hierarchy:
--- EffectsSystems (Empty GameObject)
    --- VisualEffectsManager (Add VisualEffectsManager.cs)
    --- ParticleController (Add ParticleController.cs)
```

#### Create Post-Processing Volume:

Right-click Hierarchy → **Volume → Global Volume**
- Check "Is Global"
- Create new Profile
- Add: Vignette, Chromatic Aberration, Film Grain, Color Grading

### Phase 5: Create Room Data Assets (30 minutes)

1. Create folder: `Assets/Data/Rooms/`
2. Right-click → **Create → Five Nights → Room Data**
3. Create 14 RoomData assets (one per room):

**Office.asset:**
- Room Name: `Office`
- Is Office: ☑️
- Minimap X: `0.5`
- Minimap Y: `0.85`
- Connected Rooms: [Drag West Hall, East Hall, Supply Closet, Restrooms]

**Stage.asset:**
- Room Name: `Stage`
- Is Starting Room: ☑️
- Minimap X: `0.5`
- Minimap Y: `0.1`
- Connected Rooms: [Drag Dining Area, Backstage]

*...repeat for all 14 rooms (see UNITY_IMPLEMENTATION_ROADMAP.md for full coordinates)*

4. **Assign to CameraSystem:**
   - Select `CameraSystem` GameObject
   - Drag all 14 RoomData assets into "All Rooms" list

### Phase 6: Import Assets (15 minutes)

1. Copy assets from Python game:
   - `FIVE_NIGHTS_AT_MR_INGLES/assets/img/` → `Assets/Sprites/Rooms/`
   - `FIVE_NIGHTS_AT_MR_INGLES/assets/music/` → `Assets/Audio/Music/`
   - `FIVE_NIGHTS_AT_MR_INGLES/assets/sfx/` → `Assets/Audio/SFX/`

2. Configure import settings:
   - Select all sprites → **Texture Type: Sprite (2D and UI)**
   - Select all audio → **Music: Vorbis, SFX: ADPCM**

3. Assign sprites to RoomData:
   - Select each RoomData asset
   - Drag corresponding room sprite to "Camera View Sprite"

### Phase 7: Create Animatronics (20 minutes)

1. Create empty GameObject: `MrIngles`
2. Add components:
   - `SpriteRenderer` (assign animatronic sprite)
   - `Animatronic.cs`

3. Configure Inspector:
   - **Character Name:** `Mr Ingles`
   - **Starting Room:** Drag Stage RoomData
   - **Patrol Route:** [Stage, Dining Area, West Hall, Supply Closet]
   - **Base Aggression:** `1.0`
   - **Base Move Interval:** `5.0`
   - **Movement Style:** `Patrol`
   - **Personality:** `Aggressive`
   - **Special Ability:** `Speed Demon`
   - **Attack From Left:** ☑️ (or uncheck for right)

4. Duplicate for more animatronics, change names and routes

### Phase 8: Create UI Scenes (45 minutes)

#### Main Menu Scene:

1. **File → New Scene → Save as `MainMenu`**
2. Create UI Canvas (Right-click → **UI → Canvas**)
3. Set Canvas Scaler:
   - **UI Scale Mode:** `Scale With Screen Size`
   - **Reference Resolution:** `1280 x 720`

4. Create UI hierarchy:
```
Canvas/
├── Background (Image)
├── Title (Text/TextMeshPro)
├── NightButtonsPanel/
│   ├── Night1Button
│   ├── Night2Button
│   ├── Night3Button
│   ├── Night4Button
│   └── Night5Button
├── SettingsPanel/ (inactive by default)
│   ├── NightLengthSlider
│   ├── DifficultySlider
│   └── CloseButton
└── MenuController (Empty GameObject)
    └── Add MenuController.cs
```

5. Assign UI elements to MenuController in Inspector
6. Hook up buttons to MenuController methods

#### Office Scene:

1. **File → New Scene → Save as `Office`**
2. Create UI Canvas (same settings as Main Menu)
3. Create UI hierarchy:
```
Canvas/
├── HUD/
│   ├── PowerPanel/
│   │   ├── PowerSlider
│   │   ├── PowerText
│   │   └── PowerIcon
│   ├── TimePanel/
│   │   ├── TimeText
│   │   └── NightText
│   ├── StatusText
│   └── ControlsPanel/ (toggle with H key)
├── CameraPanel/ (inactive by default)
│   ├── CameraFeed (Image)
│   ├── RoomNameText
│   ├── Minimap/
│   ├── PrevButton
│   ├── NextButton
│   └── CloseButton
├── PauseMenu/ (inactive by default)
│   ├── ResumeButton
│   ├── RestartButton
│   ├── SettingsButton
│   ├── MenuButton
│   └── QuitButton
├── JumpscarePanel/ (inactive by default)
│   ├── JumpscareImage
│   └── JumpscareText
├── TutorialPanel/ (inactive by default)
│   ├── TitleText
│   ├── DescriptionText
│   └── SkipHintText
└── UIControllers (Empty GameObject)
    ├── Add HUDController.cs
    ├── Add CameraUIController.cs
    ├── Add PauseMenuController.cs
    ├── Add JumpscareController.cs
    └── Add TutorialController.cs
```

4. Assign all UI elements to respective controllers in Inspector

### Phase 9: Configure Audio (10 minutes)

1. Select `AudioManager` GameObject
2. Assign audio clips in Inspector:
   - **Menu Music:** Drag menu music file
   - **Night Ambience:** Drag ambience files (array of 5)
   - **Door Open SFX:** Drag sound file
   - **Door Close SFX:** Drag sound file
   - **Light Switch SFX:** Drag sound file
   - **Camera Toggle SFX:** Drag sound file
   - **Jumpscare SFX:** Drag sound file
   - **Clock Chime SFX:** Drag sound file
   - etc.

3. Adjust volumes:
   - **Music Volume:** `0.7`
   - **SFX Volume:** `0.8`
   - **Ambience Volume:** `0.6`

### Phase 10: Build Settings (5 minutes)

1. **File → Build Settings**
2. **Add Open Scenes:**
   - Drag `MainMenu` scene
   - Drag `Office` scene
3. Set `MainMenu` as first scene (index 0)
4. Select platform (Windows/Mac/Linux)

---

## 🎮 TESTING CHECKLIST

After setup, test each system:

### GameManager Tests:
- [ ] Press Play → GameManager initializes
- [ ] Check Console for "🐍 Running as Python script" or initialization logs
- [ ] No errors in Console

### PowerSystem Tests:
- [ ] Press Play in Office scene
- [ ] Power drains over time
- [ ] Right-click PowerSystem → "Drain 50% Power" works
- [ ] Right-click → "Trigger Power Outage" works

### OfficeController Tests:
- [ ] Press Q → Left door toggles
- [ ] Press E → Right door toggles
- [ ] Press TAB → Cameras toggle
- [ ] Check Console for door toggle logs

### CameraSystem Tests:
- [ ] Open cameras (TAB)
- [ ] Press 1-6 → Switches cameras
- [ ] Camera feed updates
- [ ] Room name displays correctly

### Animatronic Tests:
- [ ] Create Night 1 in menu
- [ ] Watch Console for animatronic movement logs
- [ ] Wait 5+ seconds → Animatronics start moving
- [ ] Close door when animatronic in hallway → They retreat

### Audio Tests:
- [ ] Menu music plays
- [ ] Door sounds play when toggling
- [ ] Camera sounds play when switching
- [ ] Ambience plays during gameplay

### UI Tests:
- [ ] Main menu night selection works
- [ ] Settings sliders work
- [ ] Pause menu (ESC) works
- [ ] Tutorial displays (if Night 1)

---

## 🐛 COMMON ISSUES & FIXES

### Issue: "NullReferenceException" errors
**Fix:** Ensure all GameObject references are assigned in Inspector

### Issue: Animatronics not moving
**Fix:** 
1. Check `startDelayMinutes` (must be less than current time)
2. Verify patrol route is assigned
3. Ensure GameManager.currentState == Playing

### Issue: No sound playing
**Fix:** 
1. Check AudioManager has audio clips assigned
2. Verify audio is not muted in Editor (Game view speaker icon)
3. Check system volume

### Issue: Cameras not switching
**Fix:** 
1. Verify all 14 RoomData assets are in CameraSystem.allRooms list
2. Check RoomData assets have sprites assigned

### Issue: UI buttons don't work
**Fix:** 
1. Ensure EventSystem exists in scene
2. Check button OnClick events are hooked up
3. Verify UI Controller scripts are attached

---

## ✅ COMPLETION CHECKLIST

Your game is ready to play when:

- [ ] All 19 scripts compile without errors
- [ ] GameSystems hierarchy created with all managers
- [ ] 14 RoomData assets created and assigned
- [ ] UI scenes created (MainMenu, Office)
- [ ] All UI controllers assigned in Inspector
- [ ] Audio clips assigned to AudioManager
- [ ] Animatronic GameObjects created and configured
- [ ] Build Settings configured with both scenes
- [ ] Game runs without errors
- [ ] Can start Night 1 from menu
- [ ] Power drains, doors work, cameras work
- [ ] Animatronics move and attack
- [ ] Jumpscare plays on death
- [ ] Can survive to 6 AM and win

---

## 🚀 FINAL STEPS

1. **Test Night 1** - Play through entire night
2. **Test Jumpscare** - Let animatronic attack you
3. **Test Win Condition** - Survive to 6 AM
4. **Test Save/Load** - Win night, restart game, verify Night 2 unlocked
5. **Build Executable** - File → Build and Run
6. **Share Your Game!** 🎉

---

## 📚 Script Dependencies

If you get compilation errors, ensure these namespaces are in order:

1. **Constants.cs** - No dependencies
2. **RoomData.cs** - No dependencies
3. **GameManager.cs** - Uses Constants
4. **PowerSystem.cs** - Uses GameManager
5. **OfficeController.cs** - Uses GameManager, PowerSystem
6. **CameraSystem.cs** - Uses RoomData
7. **Animatronic.cs** - Uses RoomData, GameManager, OfficeController, CameraSystem
8. **AnimatronicManager.cs** - Uses Animatronic, RoomData
9. All others build on these foundations

Scripts are designed to work even if some managers don't exist (null checks included).

---

**Your game is now 100% code-complete and ready to run! Just add assets (images/sounds) and configure the Inspector fields!**

See **REQUIRED_ASSETS_LIST.md** for exactly what images and sounds you need.

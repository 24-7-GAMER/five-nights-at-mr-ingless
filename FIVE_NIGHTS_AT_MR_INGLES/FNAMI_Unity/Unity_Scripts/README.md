# Unity C# Scripts for Five Nights at Mr Ingles

This folder contains all converted Unity C# scripts from the original Python/Pygame game.

## 📁 Folder Structure

```
Unity_Scripts/
├── Core/                    # Core game systems
│   ├── GameManager.cs       # Main game state & night progression
│   ├── Constants.cs         # Game constants
│   └── SaveLoadManager.cs   # Save/Load system (JSON)
│
├── Systems/                 # Gameplay systems
│   ├── PowerSystem.cs       # Power management & outage
│   ├── OfficeController.cs  # Door, light, camera controls
│   └── CameraSystem.cs      # Camera switching & room viewing
│
├── AI/                      # Animatronic AI
│   └── Animatronic.cs       # Full AI behavior system
│
├── Audio/                   # Audio management
│   └── AudioManager.cs      # Music, SFX, ambience control
│
└── ScriptableObjects/       # Data assets
    └── RoomData.cs          # Room definitions & connections
```

## 🚀 Quick Start Guide

### 1. Copy Scripts to Unity
1. Open your Unity project
2. Create folder: `Assets/Scripts/`
3. Copy all folders from `Unity_Scripts/` to `Assets/Scripts/`
4. Wait for Unity to compile

### 2. Set Up Game Manager
1. Create empty GameObject: `GameObject → Create Empty`
2. Name it: `GameManager`
3. Add component: `GameManager.cs`
4. Add component: `SaveLoadManager.cs`

### 3. Set Up Systems
1. Create empty GameObject: `SystemsManager`
2. Add components:
   - `PowerSystem.cs`
   - `OfficeController.cs`
   - `CameraSystem.cs`
   - `AudioManager.cs`

### 4. Create Room Data Assets
1. Right-click in Project: `Create → Five Nights → Room Data`
2. Create one for each room:
   - Office
   - Stage
   - West Hall
   - East Hall
   - Kitchen
   - Dining Area
   - Backstage
   - Cafeteria
   - Gym
   - Library
   - Bathrooms
   - Vent
   - Supply Closet
   - Restrooms

3. For each room, configure:
   - **Room Name:** e.g., "Office"
   - **Connected Rooms:** Drag other RoomData assets
   - **Minimap Position:** X/Y coordinates (0-1)
   - **Camera View Sprite:** Assign camera image

4. Assign all rooms to `CameraSystem.allRooms` list in Inspector

### 5. Create Animatronics
1. Create GameObject for each animatronic
2. Add `Animatronic.cs` component
3. Configure in Inspector:
   - **Character Name:** "Mr Ingles", etc.
   - **Starting Room:** Drag RoomData asset
   - **Patrol Route:** Add RoomData assets in order
   - **Base Aggression:** 1.0 (higher = more aggressive)
   - **Base Move Interval:** 5.0 seconds
   - **Movement Style:** Patrol/Hunter/Wander/Teleport
   - **Personality:** Choose from dropdown
   - **Special Ability:** Choose from dropdown
   - **Attack From Left:** True/False (which door)

## 🎮 Input Setup

### Keyboard Controls (set these up in Unity Input System or use Input.GetKeyDown)

**Office Controls:**
- `Q` - Toggle Left Door
- `E` - Toggle Right Door
- `F` - Toggle Flashlight
- `TAB` - Toggle Cameras

**Camera Controls:**
- `1-6` - Switch to specific camera
- Arrow Keys - Navigate cameras

**Menu Controls:**
- `ESC` - Pause / Back to Menu
- `P` - Pause Game

### Setting Up Input (Old Input System)
The scripts use Unity's Input system. No additional setup needed if using default keyboard.

### Setting Up Input (New Input System)
1. Install Input System package
2. Create Input Actions asset
3. Modify `OfficeController.cs` to use new Input System

## 📊 Event System

All scripts use C# events for communication:

```csharp
// Example: Subscribe to door toggle event
void OnEnable()
{
    OfficeController.OnLeftDoorToggle += HandleDoorToggle;
}

void OnDisable()
{
    OfficeController.OnLeftDoorToggle -= HandleDoorToggle;
}

void HandleDoorToggle(bool closed)
{
    Debug.Log($"Door is now: {(closed ? "CLOSED" : "OPEN")}");
}
```

### Available Events

**GameManager:**
- `OnHourChange(int hour)` - Hour changed
- `OnNightStart(int night)` - Night started
- `OnNightWin()` - Night completed
- `OnGameOver()` - Player died
- `OnStateChange(GameState from, GameState to)` - State changed

**PowerSystem:**
- `OnPowerOutage()` - Power ran out
- `OnPowerChanged(float percent)` - Power level changed
- `OnPowerRestored()` - Power restored

**OfficeController:**
- `OnLeftDoorToggle(bool closed)` - Left door toggled
- `OnRightDoorToggle(bool closed)` - Right door toggled
- `OnLightToggle(bool on)` - Light toggled
- `OnCameraToggle(bool open)` - Cameras toggled
- `OnNoiseMakerDeploy(string room)` - Noisemaker deployed

**CameraSystem:**
- `OnCameraSwitch(RoomData room)` - Camera switched
- `OnCameraChange(RoomData from, RoomData to)` - Camera changed (with from/to)

**Animatronic:**
- `OnAnimatronicMove(Animatronic animatronic, RoomData room)` - Animatronic moved
- `OnAnimatronicAttack(Animatronic animatronic)` - Animatronic attacked
- `OnAnimatronicSpotted(Animatronic animatronic, RoomData room)` - Animatronic spotted on camera

## 🎨 UI Implementation

You'll need to create UI elements for:

1. **Main Menu:**
   - Night selection buttons (1-5)
   - Settings sliders (difficulty, night length)
   - Start button

2. **In-Game HUD:**
   - Power gauge
   - Time display (12 AM - 6 AM)
   - Camera button/indicator
   - Door status indicators

3. **Camera UI:**
   - Room name display
   - Camera feed (Sprite)
   - Minimap
   - Room selection buttons

4. **Pause Menu:**
   - Resume
   - Restart
   - Quit to Menu

### Example: Power Display
```csharp
using UnityEngine;
using UnityEngine.UI;
using FiveNightsAtMrIngles;

public class PowerDisplay : MonoBehaviour
{
    public Slider powerSlider;
    public Text powerText;

    void OnEnable()
    {
        PowerSystem.OnPowerChanged += UpdatePowerDisplay;
    }

    void OnDisable()
    {
        PowerSystem.OnPowerChanged -= UpdatePowerDisplay;
    }

    void UpdatePowerDisplay(float powerPercent)
    {
        powerSlider.value = powerPercent / 100f;
        powerText.text = $"{powerPercent:F0}%";
    }
}
```

## 🔧 Debugging Tools

Each manager has debug commands accessible via Inspector:

**GameManager:**
- `Win Current Night` - Instantly win
- `Trigger Test Jumpscare` - Test jumpscare

**PowerSystem:**
- `Drain 50% Power` - Remove half power
- `Trigger Power Outage` - Force outage
- `Restore Full Power` - Restore power

**OfficeController:**
- `Reset Office` - Reset all states
- `Jam Left Door` - Jam left door
- `Jam Right Door` - Jam right door

**Animatronic:**
- `ForceMove to Office` - Teleport to office
- `Trigger Attack` - Test attack
- `Start Hunting Office` - Begin hunting mode

## 📝 Checklist: Full Conversion

### Core Systems
- [x] GameManager
- [x] PowerSystem
- [x] OfficeController
- [x] CameraSystem
- [x] SaveLoadManager
- [x] AudioManager
- [ ] UIManager (you create this)
- [ ] Visual Effects Manager (you create this)

### Content Creation
- [ ] Create all RoomData assets (14 rooms)
- [ ] Assign room sprites
- [ ] Set up room connections
- [ ] Create animatronic GameObjects
- [ ] Configure animatronic AI parameters
- [ ] Import audio files
- [ ] Import sprite assets
- [ ] Create UI canvases
- [ ] Design main menu
- [ ] Design in-game HUD
- [ ] Design camera UI

### Advanced Features
- [ ] Implement flashlight system
- [ ] Implement barricade system
- [ ] Implement noise maker system
- [ ] Implement vent system
- [ ] Create jumpscare animations
- [ ] Add post-processing effects
- [ ] Add particle effects
- [ ] Implement tutorial system
- [ ] Add achievement system (optional)

## ⚡ Performance Tips

1. **Object Pooling:** Pool particle effects and UI elements
2. **Coroutines:** Use for timed events instead of Update()
3. **Event Unsubscribe:** Always unsubscribe in OnDisable()
4. **ScriptableObjects:** Use for data instead of prefabs
5. **Sprite Atlases:** Combine sprites into atlases
6. **Audio Compression:** Use Vorbis for music, ADPCM for SFX

## 🐛 Common Issues

### "Cannot find GameManager.Instance"
**Solution:** Ensure GameManager GameObject exists in scene and has GameManager component.

### Events not firing
**Solution:** Check you subscribed in `OnEnable()` and the target component exists.

### Animatronics not moving
**Solution:** 
1. Ensure `isActive` is true
2. Check `startDelayMinutes` hasn't passed
3. Verify patrol route is assigned
4. Ensure GameManager.currentState == Playing

### Save file not found
**Solution:** SaveLoadManager creates save file automatically. Check `Application.persistentDataPath`.

## 📚 Next Steps

1. **Read the main conversion guide:** `UNITY_CONVERSION_GUIDE.md`
2. **Create UI scenes:** Follow Unity UI tutorials
3. **Implement visual effects:** Use Post-Processing and Shader Graph
4. **Test gameplay:** Playtest each night's difficulty
5. **Polish:** Add animations, sounds, and juice
6. **Build:** Create standalone executable

## 🆘 Need Help?

- **Unity Documentation:** https://docs.unity3d.com/
- **Unity Learn:** https://learn.unity.com/
- **Brackeys Tutorials:** YouTube
- **Unity Forums:** https://forum.unity.com/

---

**Good luck with your Unity conversion! 🎮**

# Five Nights at Mr Ingles's — Unity Port ✅

This folder **is** the complete Unity project. It contains the C# implementation of **Five Nights at Mr Ingles's**, faithfully ported from the Python/Pygame version with identical gameplay, UI, and mechanics — plus improved performance.

## Status: ✅ COMPLETE & READY TO PLAY

### What's Included
- ✅ Complete Unity project structure (compatible with Unity 6000.0.62f1 and other versions)
- ✅ All 25+ C# gameplay/UI scripts fully implemented
- ✅ All original sprites copied to `Assets/Sprites/`
- ✅ All original audio (SFX + music) copied to `Assets/Audio/`
- ✅ One-click scene setup via Unity Editor menu
- ✅ Identical gameplay to Python version
- ✅ Native fullscreen resolution support
- ✅ 60 FPS target with Unity performance improvements

---

## 🚀 Quick Setup (3 Steps)

### Prerequisites
1. Install [Unity Hub](https://unity.com/download)
2. Install **Unity 6000.0.62f1** (or a compatible version) via Unity Hub
   - When installing, include: **Windows Build Support** (or Mac/Linux as needed)
   - The project targets Unity 6000.0.62f1 but should open without issues in other Unity 6 and Unity 2022.3 LTS releases

### Step 1: Open Project
1. Open Unity Hub
2. Click **"Add"** → **"Add project from disk"**
3. Navigate to this folder (`FNAMI_Unity/`) and select it
4. Unity will import and compile all scripts automatically (~1-2 minutes)

### Step 2: Auto-Setup Scenes
Once Unity finishes compiling:
1. In the top menu bar, click: **Five Nights → Setup Full Game**
2. Wait for the dialog: *"Five Nights at Mr Ingles's setup complete!"*
3. Click **OK**

This automatically:
- Creates all 14 Room ScriptableObject assets in `Assets/Data/Rooms/`
- Builds the **MainMenu** scene with title, night selection, and settings
- Builds the **Office** scene with all game systems, HUD, and animatronics
- Wires all audio clips, room connections, and UI references
- Configures build settings

### Step 3: Play!
1. Open `Assets/Scenes/MainMenu.unity` (double-click in Project window)
2. Press **▶ Play** in the Unity Editor
3. Or build a standalone: **File → Build Settings → Build**

---

## 🎮 Controls (Identical to Python Version)

| Key | Action |
|-----|--------|
| **Q** | Toggle Left Door |
| **E** | Toggle Right Door |
| **Tab** | Toggle Cameras |
| **L** | Toggle Flashlight |
| **F / F11** | Toggle Fullscreen (native resolution) |
| **Escape / P** | Pause Menu |
| **H** | Show/Hide Controls |
| **1–6** | Quick-switch cameras (when cameras open) |

---

## 🏗 Project Structure

```
FNAMI_Unity/                    ← Unity Project Root
├── Assets/
│   ├── Audio/
│   │   ├── Music/              ← menu_theme.ogg, ambience.mp3
│   │   └── SFX/                ← jumpscare.ogg, door_open.ogg, etc.
│   ├── Data/
│   │   └── Rooms/              ← 14 RoomData ScriptableObjects (auto-created)
│   ├── Scenes/                 ← MainMenu.unity, Office.unity (auto-created)
│   ├── Scripts/
│   │   ├── AI/                 ← Animatronic.cs, AnimatronicManager.cs
│   │   ├── Audio/              ← AudioManager.cs
│   │   ├── Core/               ← GameManager.cs, InputManager.cs, etc.
│   │   ├── Editor/             ← GameSetup.cs (one-click scene builder)
│   │   ├── Effects/            ← VisualEffectsManager.cs, ParticleController.cs
│   │   ├── ScriptableObjects/  ← RoomData.cs
│   │   ├── Systems/            ← OfficeController.cs, PowerSystem.cs, etc.
│   │   └── UI/                 ← HUDController.cs, MenuController.cs, etc.
│   └── Sprites/                ← All game images
├── Packages/
│   └── manifest.json           ← Unity packages (PostProcessing, InputSystem, etc.)
└── ProjectSettings/
    └── ProjectSettings.asset   ← 1280×720 default, FullScreenWindow mode
```

---

## 🎭 Animatronics

| Character | Start Delay | Attack Side | Style |
|-----------|------------|-------------|-------|
| Scary Mr Ingles | Immediate | Right (East Hall) | Normal patrol |
| Freaky Temi | 30 min | Right (East Hall) | Teleport |
| Librarian | 60 min | Left (West Hall) | Teleport |
| Vent Crawler | 90 min | Vent | Vent crawl |

---

## 🗺 Room Layout

All 14 rooms with bidirectional connections:
```
Office ↔ West Hall ↔ Cafeteria ↔ Library ↔ Bathrooms ↔ Vent ↔ Supply Closet ↔ Office
Office ↔ East Hall ↔ Gym ↔ Bathrooms
Office ↔ Restrooms ↔ Vent
Stage ↔ Dining Area ↔ West Hall / Kitchen
Stage ↔ Backstage ↔ East Hall / Kitchen
Kitchen ↔ Cafeteria
```

---

## ⚙️ Performance & Settings

- **Target FPS**: 60 (capped, adjustable in menu)
- **Fullscreen**: FullScreenWindow mode (native monitor resolution)
- **Post-Processing**: Optional VHS, chromatic aberration, vignette effects
- **Scripting Backend**: Mono (Editor) / IL2CPP recommended for Release builds
- **API Compatibility**: .NET Standard 2.1

---

## 🔧 Troubleshooting

**Compilation errors?**
- Make sure a compatible Unity version is installed (Unity 6000.0.62f1 or Unity 2022.3 LTS recommended)
- Check the Console window for specific errors
- PostProcessing errors: The package is optional. Remove `UNITY_POST_PROCESSING_STACK_V2` from Project Settings → Player → Scripting Define Symbols if you don't want PostProcessing

**Scenes not found after setup?**
- Run **Five Nights → Setup Full Game** again
- Check `Assets/Scenes/` folder for `MainMenu.unity` and `Office.unity`

**No audio?**
- The AudioManager clips are auto-wired during scene setup
- Re-run **Five Nights → Setup Full Game** if audio is missing
- Verify audio files exist in `Assets/Audio/`

**Wrong resolution?**
- Press F or F11 to toggle fullscreen (uses native monitor resolution)
- Change default in Project Settings → Player → Resolution and Presentation

---

## 📝 Differences from Python Version

| Feature | Python | Unity |
|---------|--------|-------|
| Performance | ~60 FPS (optimized) | 60+ FPS (native) |
| Fullscreen | Borderless window | FullScreenWindow (native res) |
| Save file | `mr_ingles_save.json` | `PlayerPrefs` (platform default) |
| Effects | Software scanlines/VHS | Post-Processing Stack V2 |
| Input | Pygame keyboard | Unity InputManager |

Gameplay mechanics, room layout, animatronic AI, power system, and all game rules are **identical** to the Python version.

---

*Built with Unity 6000.0.62f1 | Compatible with Unity 6 and Unity 2022.3 LTS | Ported from Python/Pygame by 24-7-GAMER*

# 🎮 Five Nights at Mr Ingles - Python to Unity C# Conversion

## 📋 Quick Navigation

This repository contains everything you need to convert your Python/Pygame game to Unity C#:

### 📖 Documentation
1. **[UNITY_CONVERSION_GUIDE.md](UNITY_CONVERSION_GUIDE.md)** - Comprehensive conversion guide
   - Key differences between Pygame and Unity
   - Python → C# syntax reference
   - Architecture patterns
   - Complete folder structure
   - Phase-by-phase conversion process

2. **[UNITY_IMPLEMENTATION_ROADMAP.md](UNITY_IMPLEMENTATION_ROADMAP.md)** - Week-by-week implementation plan
   - 8-week detailed roadmap
   - Day-by-day tasks
   - Step-by-step setup instructions
   - Success criteria checklist

3. **[../FIVE_NIGHTS_AT_MR_INGLES/Unity_Scripts/README.md](../FIVE_NIGHTS_AT_MR_INGLES/Unity_Scripts/README.md)** - Scripts documentation
   - Folder structure explanation
   - Quick start guide
   - Event system reference
   - Common issues & solutions

### 🔧 Unity C# Scripts

All converted scripts are in the `FIVE_NIGHTS_AT_MR_INGLES/Unity_Scripts/` folder:

```
FIVE_NIGHTS_AT_MR_INGLES/Unity_Scripts/
├── Core/
│   ├── GameManager.cs       ✅ Complete - Main game controller
│   ├── Constants.cs         ✅ Complete - Game constants
│   └── SaveLoadManager.cs   ✅ Complete - Save/Load with JSON
│
├── Systems/
│   ├── PowerSystem.cs       ✅ Complete - Power management
│   ├── OfficeController.cs  ✅ Complete - Door/light/camera control
│   └── CameraSystem.cs      ✅ Complete - Camera switching
│
├── AI/
│   └── Animatronic.cs       ✅ Complete - Full AI with personalities
│
├── Audio/
│   └── AudioManager.cs      ✅ Complete - Music/SFX management
│
└── ScriptableObjects/
    └── RoomData.cs          ✅ Complete - Room definitions
```

## 🚀 Getting Started

### Option 1: Quick Start (Experienced Unity Developers)
1. Read [UNITY_CONVERSION_GUIDE.md](UNITY_CONVERSION_GUIDE.md)
2. Copy `FIVE_NIGHTS_AT_MR_INGLES/Unity_Scripts/` to your Unity `Assets/Scripts/` folder
3. Follow [../FIVE_NIGHTS_AT_MR_INGLES/Unity_Scripts/README.md](../FIVE_NIGHTS_AT_MR_INGLES/Unity_Scripts/README.md) quick start section
4. Start building!

### Option 2: Step-by-Step (New to Unity)
1. Read [UNITY_CONVERSION_GUIDE.md](UNITY_CONVERSION_GUIDE.md) first
2. Follow [UNITY_IMPLEMENTATION_ROADMAP.md](UNITY_IMPLEMENTATION_ROADMAP.md) week by week
3. Use [Unity_Scripts/README.md](Unity_Scripts/README.md) as reference
4. Work through each phase carefully

## 📊 Conversion Status

### ✅ Completed Systems
- [x] **GameManager** - State management, night progression, time system
- [x] **PowerSystem** - Power drain, outage mechanics, emergency mode
- [x] **OfficeController** - Doors, lights, cameras, advanced features
- [x] **CameraSystem** - Room switching, room graph navigation
- [x] **Animatronic AI** - Full AI with personalities, special abilities, patrol routes
- [x] **SaveLoadManager** - JSON save/load, progress persistence
- [x] **AudioManager** - Music, SFX, ambience, event-driven audio
- [x] **RoomData** - ScriptableObject room system

### 🔨 You Need to Create
- [ ] UI Systems (HUD, Menus, Camera UI)
- [ ] Visual Effects (Post-processing, VHS effects, particles)
- [ ] Jumpscare System (Animations, sequences)
- [ ] Tutorial System
- [ ] Main Menu Scene
- [ ] Office Scene layout
- [ ] Room ScriptableObject assets (14 rooms)
- [ ] Animatronic prefabs configuration

## 📁 Project Structure

```
five-nights-at-mr-ingless/
├── FIVE_NIGHTS_AT_MR_INGLES/          # Original Python game
│   ├── main.py                        # 4913 lines of Python
│   ├── assets/
│   │   ├── img/                       # → Copy to Unity Sprites/
│   │   ├── music/                     # → Copy to Unity Audio/Music/
│   │   ├── sfx/                       # → Copy to Unity Audio/SFX/
│   │   └── ...
│   │
│   └── Unity_Scripts/                 # ✅ All converted C# scripts
│       ├── Core/
│       ├── Systems/
│       ├── AI/
│       ├── Audio/
│       ├── ScriptableObjects/
│       └── README.md
│
├── Documentation/                     # 📖 All guides
│   ├── UNITY_CONVERSION_GUIDE.md
│   ├── UNITY_IMPLEMENTATION_ROADMAP.md
│   ├── COMPLETE_SETUP_GUIDE.md
│   ├── REQUIRED_ASSETS_LIST.md
│   └── ...
│
└── README.md                          # 📍 You are here
```

## 🎯 Key Features Converted

### Game Systems
✅ Night progression (12 AM - 6 AM)  
✅ Power management with drain rates  
✅ Door control (left/right)  
✅ Light system  
✅ Camera switching  
✅ Save/Load progress  
✅ Difficulty scaling  

### AI Features
✅ Patrol routes  
✅ Room-to-room navigation  
✅ Adaptive aggression  
✅ 8 AI personalities (Aggressive, Patient, Stalker, etc.)  
✅ 8 Special abilities (Speed Demon, Door Breaker, etc.)  
✅ Mood system (Hunting, Retreating, Cautious, etc.)  
✅ Attack behavior  
✅ Door blocking/retreat mechanics  
✅ Staggered activation delays  

### Advanced Systems
✅ Room graph navigation (14 rooms)  
✅ Minimap positioning  
✅ Event-driven architecture  
✅ Singleton managers  
✅ Debug tools & context menus  
✅ Noise maker system hooks  
✅ Barricade system hooks  
✅ Flashlight system hooks  

## 🔑 Key Differences: Python → Unity

| Feature | Python/Pygame | Unity/C# |
|---------|---------------|----------|
| **Game Loop** | Manual `while running:` | Automatic `Update()` |
| **Time** | `dt = clock.tick(60) / 1000.0` | `Time.deltaTime` |
| **Objects** | Classes with `__init__` | MonoBehaviour with `Awake()` |
| **Events** | Direct function calls | C# events & delegates |
| **Data** | Dictionaries | ScriptableObjects |
| **Audio** | `pygame.mixer` | AudioSource components |
| **Graphics** | Manual surface blitting | Automatic sprite rendering |
| **State** | Global variables | Singleton managers |

## 📚 What You'll Learn

By completing this conversion, you'll master:

1. **Unity Fundamentals**
   - MonoBehaviour lifecycle
   - Component-based architecture
   - Scene management

2. **C# Programming**
   - Events & delegates
   - Singleton pattern
   - ScriptableObjects
   - Coroutines

3. **Game Development**
   - State machines
   - AI systems
   - Save/Load systems
   - Audio management
   - UI architecture

4. **Unity Tools**
   - Inspector debugging
   - Context menus
   - Asset management
   - Prefab workflow

## 🎓 Required Knowledge

### Minimum Requirements
- Basic Python understanding (you already have this!)
- Willingness to learn C#
- Unity installed (2022.3 LTS recommended)

### Helpful But Not Required
- Previous Unity experience
- C# experience
- Game design knowledge

## ⏱️ Time Estimate

- **Experienced Unity developer:** 2-3 weeks
- **New to Unity:** 6-8 weeks (following roadmap)
- **Complete beginner:** 10-12 weeks (with learning)

## 🆘 Getting Help

### Documentation in This Repo
1. Start with [UNITY_CONVERSION_GUIDE.md](UNITY_CONVERSION_GUIDE.md)
2. Follow [UNITY_IMPLEMENTATION_ROADMAP.md](UNITY_IMPLEMENTATION_ROADMAP.md)
3. Reference [Unity_Scripts/README.md](Unity_Scripts/README.md)

### External Resources
- **Unity Learn:** https://learn.unity.com/
- **Unity Documentation:** https://docs.unity3d.com/
- **Brackeys YouTube:** Classic Unity tutorials
- **Unity Forums:** https://forum.unity.com/
- **Stack Overflow:** Unity3D tag

### Debugging Tips
Every script has:
- ✅ Debug context menus (right-click in Inspector)
- ✅ Detailed Debug.Log messages
- ✅ Inspector variable exposure
- ✅ Clear comments explaining functionality

## 🎨 Asset Migration

Your Python game's assets can be directly used in Unity:

```bash
# Images (JPG, PNG, etc.)
FIVE_NIGHTS_AT_MR_INGLES/assets/img/* 
  → Unity_Project/Assets/Sprites/

# Music (MP3, OGG, WAV)
FIVE_NIGHTS_AT_MR_INGLES/assets/music/* 
  → Unity_Project/Assets/Audio/Music/

# SFX (WAV, MP3)
FIVE_NIGHTS_AT_MR_INGLES/assets/sfx/* 
  → Unity_Project/Assets/Audio/SFX/
```

Just copy-paste the folders!

## 🔧 System Requirements

### Unity Editor
- Windows 10/11, macOS, or Linux
- 4GB RAM minimum (8GB+ recommended)
- DirectX 11 or Metal support
- 5-10GB free space

### Build Targets
Your game will work on:
- ✅ Windows (64-bit)
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux
- ✅ WebGL (with some modifications)

## 🏆 Success Stories

This conversion provides:
- ✨ **Better performance** - Unity's optimized rendering
- 🎯 **Easier modding** - Visual editor instead of code
- 🔧 **Better tools** - Profiler, debugger, inspector
- 📦 **Easier distribution** - One-click builds
- 🎨 **Better graphics** - Post-processing, shaders
- 🔊 **Better audio** - Audio mixer, 3D sound
- 📱 **More platforms** - Easy mobile/web ports

## 📝 Next Steps

### Step 1: Read the Guides
Start with [UNITY_CONVERSION_GUIDE.md](UNITY_CONVERSION_GUIDE.md)

### Step 2: Set Up Unity
Follow Week 1 of [UNITY_IMPLEMENTATION_ROADMAP.md](UNITY_IMPLEMENTATION_ROADMAP.md)

### Step 3: Copy Scripts
Import all scripts from `FIVE_NIGHTS_AT_MR_INGLES/Unity_Scripts/` folder to your Unity `Assets/Scripts/`

### Step 4: Build Systems
Follow the roadmap week by week

### Step 5: Test & Polish
Playtest, fix bugs, add polish

### Step 6: Ship It!
Build executable and share your game!

---

## 📄 License

Same as your original Python game.

## 🙏 Credits

Original Python game by you  
Unity C# conversion scripts provided as-is  
Use and modify freely!

---

**Ready to start? Open [UNITY_CONVERSION_GUIDE.md](UNITY_CONVERSION_GUIDE.md) and let's begin! 🚀**

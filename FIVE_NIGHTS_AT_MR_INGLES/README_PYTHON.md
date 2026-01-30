# Five Nights at Mr Ingles's - Python Edition

This is a complete rewrite of the LOVE2D Lua game into Python using **Pygame**.

## What Changed

- **Engine**: LOVE2D (Lua) → Pygame (Python)
- **File**: `main.lua` → `main.py`
- **All game mechanics preserved**: Full feature parity with original

## Game Features (All Intact)

??? **5 Nights** with increasing difficulty  
??? **Power Management** - drain system with door/light/camera usage  
??? **Door Integrity + Jam** - doors wear down and can jam open  
??? **Open Door Limit** - doors auto-close if left open too long  
??? **Instant Door Recovery** - door integrity fully restores when open  
??? **Deterministic Animatronics AI** - fixed patrols, side attacks, staggered activation, and hunting phases  
??? **Mood System** - animatronics have dynamic emotional states that affect behavior  
??? **Adaptive Learning** - animatronics learn from player patterns and adjust strategy  
??? **Hunting Mode** - coordinated pursuits with pathfinding and pack tactics  
??? **Office & Camera Systems** - switch between office view and 6 camera feeds  
??? **Camera Heat** - cameras can overheat and lock out temporarily  
??? **Door & Light Controls** - manage power-draining systems  
??? **Interactive Minimap** - clickable camera map with animatronic tracking  
??? **Time System** - survive from 12 AM to 6 AM (configurable night length)  
??? **Difficulty Slider** - scales AI speed, power drain, and door wear  
??? **Run Variability** - per-run AI profiles keep behavior different each time  
??? **Retreat Cooldowns** - blocked animatronics back off briefly  
??? **Hallway Retreats** - door blockers withdraw instead of camping  
??? **Save System** - progress unlocks saved to JSON  
??? **Sound & Music** - full audio support with ambience per night  
??? **Jumpscare Events** - animatronics attack when doors are breached  
??? **Win/Lose States** - complete game flow  
??? **Creepy Atmosphere** - static effects, flickering lights, screen shake  
??? **Splash Screen** - intro image with fade in/out on launch (unskippable)  
??? **TOS Splash** - second splash (tos_splash.png) with longer hold  
??? **Pause Menu** - ESC/P to pause with resume/restart/menu/quit  
??? **HUD Expansion** - threat meters, power breakdown, event log, night progress bar  
??? **Jumpscare Fly-in** - animatronic rushes the camera before red screen  


## Installation

### Requirements
- Python 3.7+
- Pygame 2.1.0+

### Setup

```bash
pip install -r requirements.txt
```

### macOS Notes (If Pygame Fails)
If Pygame fails to install when running `main.py`, try the manual install steps below in Terminal:
```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```
If you have multiple Pythons installed, make sure `python3` and `pip` are the same install by always using `python3 -m pip`.
If you see `fatal error: 'SDL.h' file not found`, install Xcode Command Line Tools and SDL2:
```bash
xcode-select --install
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf
```

## Running

```bash
python main.py
```

### Launcher scripts

There are convenience scripts included to start the game:

- `run.bat` — Windows launcher. Checks for Python, ensures dependencies, then runs `python main.py`.
- `run.sh` — Unix/Linux/Mac launcher. Checks for `python3`, ensures dependencies, then runs `python3 main.py`.

Both scripts are optional; you can run `python main.py` directly.
On macOS, double‑clicking `run.sh` may open it in Xcode because it is a shell script. Run it from Terminal instead:
```bash
chmod +x run.sh
./run.sh
```

## Controls

| Key | Action |
|-----|--------|
| **1-5** | Start Night (menu), Switch Camera (gameplay) |
| **Q** | Toggle Left Door |
| **E** | Toggle Right Door |
| **F** | Toggle Light/Flashlight |
| **TAB** | Toggle Camera View |
| **6** | Switch to Vent Camera |
| **CLICK** | Click minimap to switch cameras |
| **R** | Restart to Night 1 |
| **M** | Return to Menu |
| **P / ESC** | Pause (gameplay) |
| **A/D** | Adjust Difficulty (menu) |
| **H** | Toggle HUD Help |
| **ESC** | Quit Game |

## Architecture

### Core Classes
- `GameState` - Main game state container
- `PowerSystem` - Power drain mechanics
- `Office` - Office state and visual effects
- `CameraSystem` - Camera switching logic
- `Animatronic` - Individual animatronic with advanced AI (mood, learning, hunting, coordination)
- `AssetManager` - Image/sound/music loading
- `Game` - Main game engine with AI coordination

### Advanced AI Features
See **[AI_FEATURES.md](AI_FEATURES.md)** for comprehensive documentation of:
- Mood system (5 emotional states)
- Adaptive aggression learning
- Hunting mode with pathfinding
- AI communication & pack tactics
- Dynamic difficulty scaling
- Player behavior memory
```
assets/
  img/              # All sprite images
  sfx/              # Sound effects & ambience
  music/            # Menu theme
```

## Original Lua Features Perfectly Replicated

### Game Systems
- ✅ Smooth door animation (0-1 progress)
- ✅ Light dimming overlay
- ✅ Power outage mechanics
- ✅ Camera static flash effect
- ✅ Animatronic wobble animation
- ✅ Room graph navigation
- ✅ Night progression unlocking

### Audio
- ✅ SFX playback (door, light, jumpscare, bell)
- ✅ Streaming music per night
- ✅ Menu theme
- ✅ Volume control

### Visuals
- ✅ Office background scaling
- ✅ Animatronic sprite rendering
- ✅ Door overlays
- ✅ Vignette effect
- ✅ Camera scanlines
- ✅ Static flash noise
- ✅ Pulsing jumpscare screen

## Differences from Lua Version

**Advantages of Python:**
- Cleaner OOP structure
- Easier to extend and modify
- Better cross-platform compatibility
- Larger ecosystem of libraries
- More readable code

**Intentional Simplifications:**
- No audio streaming loop management (Pygame handles this natively)
- Fixed font sizes (vs LOVE2D dynamic scaling)
- Simplified vignette rendering (same visual effect, cleaner code)

## Save File

Progress is saved to `mr_ingles_save.json` with structure:
```json
{
  "max_night": 5,
  "difficulty": 1.2
}
```

## Future Enhancements

Potential additions now that we're in Python:
- Modern graphics enhancements
- Additional animatronics
- Custom difficulty presets
- Modding support
- Analytics/statistics tracking
- Mobile port (Kivy)

## Latest Updates

**January 30, 2026**: 
- ✨ Implemented advanced AI system with mood, learning, and coordination
- 💡 Increased flashlight brightness for better visibility
- 📋 See [CHANGELOG.md](CHANGELOG.md) for complete update history

---

**Last Updated**: January 30, 2026  
**Engine**: Pygame 2.1.0+  
**Python**: 3.7+

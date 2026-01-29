# Five Nights at Mr Ingles's - Python Edition

This is a complete rewrite of the LOVE2D Lua game into Python using **Pygame**.

## What Changed

- **Engine**: LOVE2D (Lua) → Pygame (Python)
- **File**: `main.lua` → `main.py`
- **All game mechanics preserved**: Full feature parity with original

## Game Features (All Intact)

✅ **5 Nights** with increasing difficulty  
✅ **Power Management** - drain system with door/light/camera usage  
✅ **Limited Door Uses** - 3 uses per door, restored when blocking attacks
✅ **Advanced Animatronics AI** - 4 animatronics with cutting-edge learning & coordination  
✅ **Mood System** - animatronics have dynamic emotional states that affect behavior  
✅ **Adaptive Learning** - animatronics learn from player patterns and adjust strategy  
✅ **Hunting Mode** - coordinated pursuits with pathfinding and pack tactics  
✅ **Office & Camera Systems** - switch between office view and 6 camera feeds  
✅ **Door & Light Controls** - manage power-draining systems  
✅ **Interactive Minimap** - clickable camera map with animatronic tracking
✅ **Time System** - survive from 12 AM to 6 AM (configurable night length)  
✅ **Save System** - progress unlocks saved to JSON  
✅ **Sound & Music** - full audio support with ambience per night  
✅ **Jumpscare Events** - animatronics attack when doors are breached  
✅ **Win/Lose States** - complete game flow  
✅ **Creepy Atmosphere** - static effects, flickering lights, screen shake  

## Installation

### Requirements
- Python 3.7+
- Pygame 2.1.0+

### Setup

```bash
pip install -r requirements.txt
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

## Controls

| Key | Action |
|-----|--------|
| **1-5** | Start Night (menu), Switch Camera (gameplay) |
| **Q** | Toggle Left Door (3 uses max) |
| **E** | Toggle Right Door (3 uses max) |
| **F** | Toggle Light/Flashlight |
| **TAB** | Toggle Camera View |
| **6** | Switch to Vent Camera |
| **CLICK** | Click minimap to switch cameras |
| **R** | Restart to Night 1 |
| **M** | Return to Menu |
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
  "max_night": 5
}
```

## Future Enhancements

Potential additions now that we're in Python:
- Modern graphics enhancements
- Additional animatronics
- Custom difficulty settings
- Modding support
- Analytics/statistics tracking
- Mobile port (Kivy)

## Latest Updates

**January 29, 2026**: 
- ✨ Implemented advanced AI system with mood, learning, and coordination
- 💡 Increased flashlight brightness for better visibility
- 📋 See [CHANGELOG.md](CHANGELOG.md) for complete update history

---

**Last Updated**: January 29, 2026  
**Engine**: Pygame 2.1.0+  
**Python**: 3.7+

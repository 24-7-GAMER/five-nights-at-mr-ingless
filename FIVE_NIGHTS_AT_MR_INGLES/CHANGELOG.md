# Changelog - Five Nights at Mr Ingles's (Python Edition)

## Recent Updates (January 30, 2026)

### Deterministic Difficulty Overhaul
- Removed all randomness from AI and visual noise to make behavior fully predictable and skill-based
- Rebuilt animatronic logic with fixed patrol routes, deterministic moods, and timed hunting phases
- Side-based attacks: each animatronic now commits to a door side (or vent) and pressures it consistently
- Hallway pressure forces entry when a door is open; closed doors take integrity damage over time
- Attack windup ensures consistent, fair timing while still punishing slow reactions

### New Difficulty Systems and Mechanics
- Added difficulty slider (0.8x-2.0x) on the menu with Easy/Normal/Hard/Brutal/Nightmare labels
- Difficulty scales AI speed, power drain, door wear, hallway pressure, and attack windup
- Difficulty setting persists to the save file and loads on startup
- Added camera heat and overload cooldown when cameras are used too long
- Added deterministic power surges at fixed times (:15, :30, :45 each hour)

### Door Integrity and Jam System
- Replaced limited door uses with integrity and jam timers
- Doors wear down while closed and under pressure; they can jam open if overused
- HUD now shows door integrity and jam timers

### Bug Fixes
- Fixed Vent Crawler attacking through closed doors

### UI
- Added intro splash screen with full-screen fade in/out before the main menu

---

## Recent Updates (January 29, 2026)

### 🧠 Advanced AI System Implementation
**Major Feature Addition** - Complete rewrite of animatronic intelligence system to distinguish from basic FNAF clones.

#### AI Features Added:
- **Mood System**: Animatronics now have 5 emotional states (neutral, cautious, aggressive, hunting, retreating) that affect behavior
- **Adaptive Learning**: Animatronics learn from player defense patterns and adjust strategy accordingly
  - Block counter tracks successful player defenses
  - Aggression increases by 0.05 per 5 blocks
  - Remembers which door side is preferred by player
- **Hunting Mode**: Triggered when blocked 2+ times, enters pursuit state with 1.6× aggression and pathfinding
- **Player Action Memory**: Records last 60 seconds of player blocks with side/time information
- **Strategic Pathfinding**: 
  - 60% chance to use learned efficient routes
  - 40% random wandering for unpredictability
  - Greedy algorithm to move closer to target
- **AI Communication & Coordination**:
  - Animatronics share hunting targets
  - 40% chance others join active hunts
  - Communication cooldowns (5-10s) prevent spam
  - Pack hunting increases frustration when 2+ at office
- **Adaptive Difficulty Scaling**:
  - Base difficulty increases 15% per night
  - Analyzes player success and boosts accordingly
  - Applied automatically at night start
  - Successful defense (5+ blocks) triggers +20% difficulty boost
- **Mood-Based Behavior Multipliers**: Movement patterns and aggression vary by emotional state
- **Time-Based Escalation**: Animatronics become more aggressive as night progresses

**Technical Details**: See [AI_FEATURES.md](AI_FEATURES.md) for comprehensive documentation

---

### 💡 Flashlight Brightness Enhancement
- Increased flashlight/light visibility significantly
- Added white brightness overlay (80 alpha) when light is on
- Makes the flashlight effect much more noticeable and impactful
- Improved visual feedback for light toggling

---

## Previous Session Updates

### Menu & UI Enhancements
- Implemented title image loading from `assets/img/title.png`
- Title sizing: 100% width, capped at 60% height
- Added pulsing title animation (±8% scale over 1.5s cycle)
- Added blurred background image support (`assets/img/menu_background.png`)
- Enhanced menu animations:
  - Color-shifting gradient background
  - Dynamic button colors with per-night pulses
  - Glowing button effects with varying alpha
  - Pulsing record box with glow border

### Time & Difficulty System
- Implemented minute-by-minute time progression
- Changed from hour-only display to HH:MM format
- Added night-length slider on menu (15-180 seconds/hour)
- Slider controls:
  - Mouse drag support
  - Keyboard ←/→ arrow key adjustment (±5s/hour)
- Win condition at 360 minutes (6 AM)

### Camera & Visual Improvements
- Reduced scanline brightness significantly (alpha 20 instead of full)
- Subtle teal scanlines for authentic camera feel
- Improved camera visual clarity without loss of retro aesthetic

### Night 1 Intro Sequence
- Fading text messages for atmospheric introduction
- 5 messages: "YOU'RE IN THE SCIENCE BLOCK" → "ALONE" → "HIDING IN MR. INGLES'S OFFICE" → "MR. INGLES AND HIS ARMY ARE WATCHING" → "DON'T GET CAUGHT"
- Fade timing: 1.5 seconds per message
- Smooth transitions with drop shadows

### Documentation & Launcher Updates
- Updated all launcher scripts with explanatory comments
- Added comprehensive markdown documentation
- Created conversion report detailing LOVE2D → Pygame migration

---

## Version History

### v1.0 (Original Python Conversion)
- Complete Lua to Python conversion from LOVE2D
- Full feature parity with original game
- All 5 nights with increasing difficulty
- Power management system
- 4 animatronics with basic AI
- Camera system with minimap
- Save/progress system
- Full audio support

---

## Known Features

??? 5 Nights with increasing difficulty  
??? Power Management with drain system  
??? Door Integrity + Jam system  
??? Advanced Animatronic AI with deterministic behavior  
??? Office & 6-camera switching system  
??? Interactive Minimap  
??? Time system (12 AM - 6 AM)  
??? Save/Progress system  
??? Full audio with night ambience  
??? Jumpscare events  
??? Win/Lose game states  
??? Atmospheric effects (scanlines, static, flickering)  
??? Configurable night length via slider  
??? Difficulty slider with persistent save  
??? Intro splash screen (fade in/out, unskippable)  
??? Title screen with animations  
??? Night 1 intro sequence  

---

## Future Enhancement Ideas

- Animatronic personality traits (some naturally more aggressive)
- Voice communication during coordination
- Collective tactics (pack formations, flanking)
- Fear learning (hiding from frequently used cameras)
- Save animations/cinematics for key moments
- Difficulty presets (Easy, Normal, Hard, Extreme)
- Custom night mode with individual animatronic sliders

---

## Development Notes

**Last Updated**: January 30, 2026  
**Python Version**: 3.7+  
**Pygame Version**: 2.1.0+  
**Total Lines of Code**: ~1,900 (main.py)

For technical implementation details, see [AI_FEATURES.md](AI_FEATURES.md) and [CONVERSION_REPORT.md](CONVERSION_REPORT.md).

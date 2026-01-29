# Advanced AI Features

## Overview
The Five Nights at Mr Ingles's game now features cutting-edge AI systems that make animatronics intelligent, adaptive, and coordinated. These features distinguish this game from basic FNAF clones.

## Core AI Features

### 1. **Mood System**
Animatronics have dynamic mood states that affect their behavior:
- **Neutral** (1.0× aggression) - Default calm state
- **Cautious** (0.7× aggression) - Careful, defensive approach
- **Aggressive** (1.4× aggression) - Frustrated and attacking harder
- **Hunting** (1.6× aggression) - Active pursuit of player
- **Retreating** (0.5× aggression) - Backing off (rare)

Moods shift every 8-15 seconds based on situation and create emergent behavior.

### 2. **Adaptive Aggression**
Each animatronic learns from player behavior:
- **Block Counter**: Tracks how many times the player successfully blocks them (0-5+)
- **Adaptive Multiplier**: For every 5 blocks, aggression increases by 0.05
- **Dynamic Intervals**: Movement intervals decrease as frustration increases
- **Learning Curve**: Early nights are gentle, but repeated success makes them progressively more aggressive

Formula: `adaptive_aggro = base_aggro + (block_count * 0.05)`

### 3. **Player Action Memory**
Animatronics remember recent player actions:
- Tracks which door was used to block (left/right)
- Records timestamps of blocks
- Analyzes last 5 blocks to detect player patterns
- Adapts preferred attack direction if player favors one side

Memory retention: Last 60 seconds of actions

### 4. **Hunting Mode**
When blocked by doors 2+ times in a short period:
- Enters "hunting mode" (1.6× aggression)
- Moves toward target room with 70% pursuance (30% random wandering for unpredictability)
- Uses simple pathfinding to move closer to "Office"
- Mood becomes "hunting" automatically
- Exits hunting mode after 20 seconds without new blocks

### 5. **Strategic Pathfinding**
Instead of pure random movement:
- **Learned Paths**: 60% chance to use learned efficient routes
- **Greedy Pathfinding**: Moves closer to target using distance heuristic
- **Preferred Sides**: Develops left/right preferences based on player block patterns
- **Escape Routes**: Can backup and find alternative paths when blocked

### 6. **AI Communication & Coordination**
Multiple animatronics communicate and coordinate attacks:
- **Hunting Intelligence Sharing**: If one animatronic enters hunting mode, others have 40% chance to join
- **Shared Target**: All hunting animatronics share the same target room
- **Communication Cooldown**: Prevents spam coordination (5-10 second cooldowns)
- **Pack Hunting**: Multiple animatronics at office increase each other's frustration
- **Coordinated Attack**: When 2+ animatronics are at office, aggression multiplier increases further

### 7. **Adaptive Difficulty System**
Game difficulty scales based on player performance across nights:
- **Base Night Factor**: +15% aggro per night (Night 1→2→3→4→5)
- **Performance Analysis**:
  - **Successful Defense** (5+ blocks): +20% difficulty boost
  - **Moderate Defense** (2-5 blocks): +10% difficulty boost
  - **Weak Defense** (0-2 blocks): No boost
- **Dynamic Aggression**: Applied to all animatronics at night start
- **Learning Reset**: Block counts reset between nights but reduce by 3 (learning persists slightly)

### 8. **Mood-Based Movement Multipliers**
Movement patterns change with mood:
- **Hunting**: 70% pursue target, 30% random (focused but unpredictable)
- **Aggressive**: Standard pathfinding with higher frequency
- **Cautious**: Slower, more deliberate approach
- **Neutral/Retreating**: Standard or reduced movement

### 9. **Time-Based Behavior Evolution**
Animatronics become more aggressive over time within a night:
- Start calm, progressively get more agitated
- Each successful block accumulates frustration
- By hour 5-6 AM, animatronics are highly aggressive if player has blocked many times
- Last hour (5 AM) is critical as mood shifts to "hunting" more frequently

## Technical Implementation

### Animatronic Class Enhanced Fields
```python
# Mood and psychology
mood: str  # Current emotional state
mood_timer: float  # How long in current mood
mood_duration: float  # Randomized 8-15 seconds

# Learning systems
player_action_memory: list  # Recent blocks with timestamps
target_player_room: str  # Predicted player location
adaptive_aggro: float  # Aggression increased by learning
block_count: int  # How many times blocked

# Hunting behavior
hunting_mode: bool  # Active pursuit state
hunt_target_room: str  # Where to hunt
last_blocked_time: float  # Last block timestamp

# Pathfinding
preferred_path: list  # Learned efficient routes
```

### Key Methods
- `update_mood(game_state)` - Changes mood based on frustration
- `get_mood_multiplier()` - Returns aggression × mood
- `move_toward_target(target_room)` - Pathfinding pursuit
- `handle_blocked(side)` - Records block and enters hunting mode
- `_distance_to_room()` - Simple BFS distance heuristic

### Game Class Enhancements
- `coordinate_animatronics(dt)` - AI-to-AI communication
- `apply_adaptive_difficulty()` - Dynamic difficulty scaling

## Gameplay Impact

### Early Game (Night 1-2)
- Animatronics are cautious and exploratory
- Rare hunting mode triggers
- Player mistakes are forgiving
- Helps new players learn mechanics

### Mid Game (Night 3)
- Aggression increases noticeably
- Hunting mode becomes more common
- Coordinated attacks start appearing
- Player must adapt strategy

### Late Game (Night 4-5)
- Animatronics remember player patterns
- Frequent hunting mode and coordinated attacks
- Very aggressive by 5+ AM
- Player must mix up defense strategy or lose

## Distinguishing Features

These AI systems make this FNAF homage unique:
1. **Memory-based gameplay** - Players must vary their strategies or face predictable attacks
2. **Emergent behavior** - Mood changes and hunting coordination feel unpredictable yet fair
3. **Learning curve** - The game feels progressively harder as animatronics "learn" the player
4. **Communication mechanics** - Pack hunting creates dynamic tactical situations
5. **Personality differences** - Each animatronic has unique aggression baselines that interact with mood

## Balance Considerations

The AI is designed to:
- Remain beatable with skill (blocks reduce aggression)
- Feel intelligent without being unfair (communication cooldowns, mood randomness)
- Scale with player performance (adaptive difficulty prevents both boredom and frustration)
- Create varied playthroughs (mood randomness, path learning, communication delays)

## Future Enhancement Ideas

- **Pattern Recognition**: Animatronics recognize specific door-check patterns
- **Personality Traits**: Some animatronics are naturally more aggressive/cautious
- **Collective Tactics**: Pack hunting formations (flank, surround, distract)
- **Voice Lines**: Animatronics "communicate" with growls/beeps when coordinating
- **Fear Learning**: Animatronics learn which cameras player uses most and hide from them

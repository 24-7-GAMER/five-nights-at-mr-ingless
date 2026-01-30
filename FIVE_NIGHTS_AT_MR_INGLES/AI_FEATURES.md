# Advanced AI Features

## Overview
The game now uses a fully deterministic AI system designed to be skill-based and predictable. Animatronics follow fixed patrol routes, use side-based attacks, and ramp pressure on a consistent timeline. No RNG influences gameplay behavior.

## Core AI Features

### 1) Deterministic Mood System
Animatronics cycle moods based on time, blocks, and hunting state:
- Neutral: default early behavior
- Cautious: mid-night or after a few blocks
- Aggressive: late-night or heavy blocking
- Hunting: active pursuit state

Mood updates are time-based (every ~2 seconds) and do not use randomness.

### 2) Fixed Patrol Routes
Each animatronic follows a predefined route across rooms and repeats it. This creates consistent patterns players can learn, but the pace accelerates with difficulty, night, and block counts.

### 3) Side-Based Attacks
Each animatronic commits to a side:
- Left attackers pressure the left door
- Right attackers pressure the right door
- Vent attacker requires at least one door open

This makes door choice meaningful and predictable.

### 4) Hallway Pressure
When an animatronic reaches the Hallway:
- If its target door is open, it will enter after a short, fixed delay
- If closed, it damages door integrity while waiting

### 5) Attack Windup
Attacks require a short windup in the Office. The windup shortens with higher nights and difficulty, ensuring fair but punishing reactions.

### 6) Hunting Mode
Hunting mode triggers after blocks and lasts a fixed duration. In this state, animatronics aggressively path toward the Office on a deterministic timer.

### 7) Coordination
Animatronics share hunting targets on a fixed cooldown. When multiple are at the Office, they increase each other's aggression deterministically.

### 8) Adaptive Aggression (Deterministic)
Aggression scales predictably based on:
- Night number
- Minutes elapsed in the night
- Block count against doors
- Difficulty slider value

## Difficulty Integration
The menu difficulty slider scales AI and pressure systems:
- Movement interval
- Aggression multipliers
- Attack windup duration
- Door pressure damage
- Power drain

This slider is saved to disk and loads on startup.

## Design Goals
- No luck-based outcomes; players can learn and counter patterns
- Consistent escalation through the night
- High pressure from door integrity, power surges, and camera heat
- Clear cause-and-effect for every loss

## Related Mechanics
- Door integrity and jam timers replace limited door uses
- Camera heat and overloads force timed camera usage
- Power surges occur at fixed times (:15, :30, :45 each hour)

For full gameplay changes and history, see CHANGELOG.md.

## Run-to-Run Variability (Fair, Non-Luck-Based)
Each new game run generates a deterministic profile using a per-run seed. This changes:
- Patrol route rotations
- Activation delays
- Movement intervals and aggression ramps
- Hallway entry timing

Fairness constraints ensure runs are never impossible:
- Side entry cooldowns prevent rapid back-to-back entries
- Max simultaneous office attackers is capped
- Door logic remains strict (closed doors always block correctly)

This keeps every run different without random breach outcomes.

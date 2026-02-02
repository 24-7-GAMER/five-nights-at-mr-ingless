#!/usr/bin/env python3
"""
Five Nights at Mr Ingles's (Pygame)
LUA -> PYTHON PORT (this took 6 way too long)
"""

import sys
import os

# =====================================================
# CROSS-PLATFORM PATH HANDLING
# =====================================================
# Define BASE_DIR for all asset loading - works on Windows, Mac, Linux
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

import subprocess

def install_required_packages():
    """Install required packages if not already installed"""
    required = ["pygame"]
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            print(f"\n Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installed successfully!\n")
            except subprocess.CalledProcessError:
                print(f"\n❌ ERROR: Failed to install {package}")
                print(f"Please install it manually: pip install {package}\n")
                sys.exit(1)

# Install packages before importing them
install_required_packages()

import json
import math
import time
import random
import pygame

# =====================================================
# CONSTANTS
# =====================================================

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Five Nights at Mr Ingles's"
FPS = 60
SAVE_FILE = os.path.join(BASE_DIR, "mr_ingles_save.json")

# =====================================================
# GAME STATE
# =====================================================

class GameState:
    """Main game state container"""
    def __init__(self):
        self.state = "splash"  # "splash", "menu", "playing", "paused", "jumpscare", "win", "anti_cheat", "anti_cheat_message"
        self.night = 1
        self.max_night_unlocked = 1
        self.hour = 12
        self.hour_timer = 0
        self.seconds_per_hour = 60
        self.minutes_elapsed = 0  # minutes since 12:00 for current night
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.status = ""
        self.start_time = time.time()
        
        # Environmental Events
        self.active_events = []
        self.event_cooldown = 0
        self.lights_flickering = False
        self.flicker_timer = 0
        self.hallway_darkness = 0
        self.temperature = 70  # Room temperature affects mechanics
        self.ventilation_blocked = False
        self.phantom_sounds = []

    def elapsed_time(self):
        """Get elapsed time since game start"""
        return time.time() - self.start_time


class PowerSystem:
    """Power management system"""
    def __init__(self):
        self.max = 100
        self.current = 100
        self.base_drain = 0.16  # higher baseline drain
        self.door_drain = 0.24  # higher door drain
        self.light_drain = 0.24  # higher light drain
        self.cam_drain = 0.32   # higher camera drain
        self.outage = False

    def reset(self):
        self.current = self.max
        self.outage = False
        self.emergency_mode = False
        self.emergency_timer = 0
        self.reserve_power = 0  # Hidden reserve for emergencies


class Office:
    """Office state and controls"""
    def __init__(self):
        self.door_left_closed = False
        self.door_right_closed = False
        self.light_on = True
        self.cams_open = False
        self.door_left_progress = 0.0   # 0 = open, 1 = closed
        self.door_right_progress = 0.0
        self.light_dim = 0.0             # darkness overlay
        self.cam_flash = 0.0             # static flash
        self.door_left_health = 100.0
        self.door_right_health = 100.0
        self.door_left_jam_timer = 0.0
        self.door_right_jam_timer = 0.0
        self.door_left_open_timer = 0.0
        self.door_right_open_timer = 0.0
        
        # New features
        self.flashlight_battery = 100.0
        self.vent_system_active = True
        self.barricade_left = 0  # 0-3 levels
        self.barricade_right = 0
        self.noise_maker_charges = 3
        self.safe_mode_timer = 0.0
        self.movement_noise_level = 0.0

    def reset(self):
        self.door_left_closed = False
        self.door_right_closed = False
        self.light_on = True
        self.cams_open = False
        self.door_left_progress = 0.0
        self.door_right_progress = 0.0
        self.light_dim = 0.0
        self.cam_flash = 0.0
        self.door_left_health = 100.0
        self.door_right_health = 100.0
        self.door_left_jam_timer = 0.0
        self.door_right_jam_timer = 0.0
        self.door_left_open_timer = 0.0
        self.door_right_open_timer = 0.0


class CameraSystem:
    """Camera switching system"""
    def __init__(self):
        self.cameras = [
            "Stage", "Dining Area", "Backstage", "Kitchen",
            "West Hall", "East Hall", "Cafeteria", "Gym",
            "Library", "Bathrooms", "Vent", "Supply Closet", "Restrooms"
        ]
        self.current_index = 0

    def switch(self, index):
        if 0 <= index < len(self.cameras):
            self.current_index = index

    def current_camera(self):
        return self.cameras[self.current_index]


class Jumpscare:
    """Jumpscare event"""
    def __init__(self):
        self.active = False
        self.timer = 0
        self.duration = 2.0
        self.killer = "Mr Ingles"
        self.zoom = 0.0
        self.fly_duration = 0.6

    def reset(self):
        self.active = False
        self.timer = 0
        self.zoom = 0.0


# =====================================================
# ROOM GRAPH AND NAVIGATION
# =====================================================

ROOM_GRAPH = {
    "Office": ["West Hall", "East Hall"],
    "West Hall": ["Office", "Cafeteria", "Gym", "Supply Closet"],
    "East Hall": ["Office", "Library", "Bathrooms", "Restrooms"],
    "Cafeteria": ["West Hall", "Dining Area", "Library"],
    "Dining Area": ["Cafeteria", "Stage", "Kitchen"],
    "Stage": ["Dining Area", "Backstage"],
    "Backstage": ["Stage", "Kitchen"],
    "Kitchen": ["Dining Area", "Backstage", "East Hall"],
    "Gym": ["West Hall", "Cafeteria"],
    "Library": ["Cafeteria", "East Hall", "Bathrooms"],
    "Bathrooms": ["Library", "East Hall", "Vent"],
    "Vent": ["Bathrooms", "Restrooms"],
    "Supply Closet": ["West Hall"],
    "Restrooms": ["East Hall", "Vent"],
}


def room_position(room, width, height):
    """Get the visual position of a room"""
    positions = {
        "Office": (width * 0.5, height * 0.7),
        "Hallway": (width * 0.5, height * 0.4),
        "Cafeteria": (width * 0.3, height * 0.4),
        "Gym": (width * 0.7, height * 0.4),
        "Library": (width * 0.25, height * 0.3),
        "Bathrooms": (width * 0.75, height * 0.3),
        "Vent": (width * 0.5, height * 0.2),
    }
    return positions.get(room, (width * 0.5, height * 0.5))


def get_neighbors(room):
    """Get adjacent rooms"""
    return ROOM_GRAPH.get(room, [])


# =====================================================
# ANIMATRONIC
# =====================================================

class Animatronic:
    """Animatronic character with deterministic AI"""
    def __init__(self, name, start_room, base_aggro, base_interval, style="teleport",
                 attack_side="left", patrol_route=None, start_delay_minutes=0,
                 hallway_entry_delay=2.0, aggression_ramp=0.25, rng=None):
        self.name = name
        self.room = start_room
        self.base_aggro = base_aggro
        self.base_interval = base_interval
        self.aggro = base_aggro
        self.move_interval = base_interval
        self.timer = 0
        self.style = style
        self.attack_side = attack_side
        self.rng = rng
        route = patrol_route or [start_room]
        if self.rng and len(route) > 1:
            # Rotate route per run to keep patterns unique without breaking graph
            offset = self.rng.randint(0, len(route) - 1)
            route = route[offset:] + route[:offset]
        self.patrol_route = route
        self.patrol_index = 0
        self.move_cooldown = base_interval
        self.hallway_timer = 0.0
        self.attack_windup = 0.0
        self.attack_windup_required = 1.2
        self.start_delay_minutes = start_delay_minutes
        self.hallway_entry_delay = hallway_entry_delay
        self.aggression_ramp = aggression_ramp
        self.x, self.y = room_position(start_room, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.target_x = self.x
        self.target_y = self.y
        self.visible_on_cam = True
        
        # Advanced AI features (deterministic)
        self.mood = "neutral"  # neutral, aggressive, cautious, hunting, retreating
        self.mood_timer = 0
        self.player_action_memory = []  # remember recent player actions
        self.target_player_room = None  # predicted player location
        self.communication_cooldown = 0
        self.hunting_mode = False
        self.hunting_timer = 0.0
        self.hunt_target_room = None
        self.adaptive_aggro = base_aggro  # adjusts based on learning
        self.last_blocked_time = 0
        self.block_count = 0
        self.retreat_timer = 0.0
        self.retreat_target = None
        self.last_room = start_room
        self.hallway_block_timer = 0.0
        
        # AI Personality System (randomized each night)
        self.personality = self.assign_personality(rng)
        self.patience = rng.uniform(0.5, 2.0)  # How long they wait before moving
        self.curiosity = rng.uniform(0.3, 1.5)  # How likely to investigate player actions
        self.persistence = rng.uniform(0.4, 1.8)  # How often they retry after being blocked
        self.teamwork = rng.uniform(0.2, 1.3)  # How well they coordinate with others
        self.deception = rng.uniform(0.1, 1.2)  # How likely to fake movements
        self.sound_sensitivity = rng.uniform(0.5, 1.5)  # How much they react to sounds
        self.camera_awareness = rng.uniform(0.3, 1.4)  # How they react to being watched
        
        # Behavior state
        self.is_decoy = False
        self.decoy_timer = 0.0
        self.last_player_action_time = 0
        self.stalking_mode = False
        self.ambush_position = None
        self.fake_movement_cooldown = 0.0
        
        # Special abilities
        self.special_ability = self.assign_special_ability(rng)
        self.ability_cooldown = 0.0
        self.ability_active = False
        self.can_disable_lights = False
        self.can_jam_cameras = False
        self.can_drain_power = False
        self.speed_boost_active = False
    
    def assign_special_ability(self, rng):
        """Assign a unique special ability"""
        abilities = [
            "light_killer",     # Can disable lights temporarily
            "camera_jammer",    # Can jam cameras
            "power_drainer",    # Extra power drain
            "speed_demon",      # Periodic speed boosts
            "door_breaker",     # Extra damage to doors
            "silent_stalker",   # Makes no sound when moving
            "mimic",            # Can appear in multiple cameras
            "teleporter"        # Can skip rooms
        ]
        return rng.choice(abilities) if rng else "speed_demon"
    
    def assign_personality(self, rng):
        """Assign a random personality archetype"""
        personalities = [
            "aggressive",    # Moves fast, attacks often
            "patient",       # Waits for perfect opportunity
            "erratic",       # Unpredictable movements
            "stalker",       # Follows player patterns
            "team_player",   # Coordinates with others
            "trickster",     # Uses fake movements
            "cautious",      # Retreats often, slow approach
            "relentless"     # Never gives up, constant pressure
        ]
        return rng.choice(personalities) if rng else "aggressive"

    def update(self, dt, game_state=None, difficulty=1.0):
        """Update animatronic with deterministic AI"""
        self.timer += dt
        self.mood_timer += dt

        # Staggered activation to avoid instant dogpiles
        minutes = game_state.minutes_elapsed if game_state else 0
        if minutes < self.start_delay_minutes:
            return

        if self.retreat_timer > 0:
            self.retreat_timer = max(0.0, self.retreat_timer - dt)
            return

        if self.hunting_timer > 0:
            self.hunting_timer -= dt
            self.hunting_mode = True
        else:
            self.hunting_mode = False
            # Clear temporary lure targets so they don't stick forever
            if self.hunt_target_room and self.hunt_target_room != "Office":
                self.hunt_target_room = None
                if self.mood == "hunting":
                    self.mood = "neutral"

        # Update mood state (affects behavior)
        if self.mood_timer >= 2.0:
            self.update_mood(game_state)
            self.mood_timer = 0

        # Adaptive aggression based on learning and time
        night = game_state.night if game_state else 1
        time_factor = (minutes / 360.0) * self.aggression_ramp
        night_factor = (night - 1) * 0.12
        self.adaptive_aggro = (self.base_aggro * difficulty) + (self.block_count * 0.05) + time_factor + night_factor
        self.adaptive_aggro = min(self.adaptive_aggro, 2.0)
        interval = max(0.7, (self.move_interval / max(0.6, difficulty)) / (1.0 + self.adaptive_aggro * 0.6))
        self.move_cooldown -= dt

        if self.move_cooldown <= 0:
            self.move_cooldown += interval
            if self.hunting_mode or self.mood in ("aggressive", "hunting"):
                self.move_toward_target(self.hunt_target_room or "Office")
            else:
                self.move_patrol()

        # Smooth position toward target
        speed = 4 * dt
        self.x += (self.target_x - self.x) * speed
        self.y += (self.target_y - self.y) * speed
        
        # Communication cooldown
        if self.communication_cooldown > 0:
            self.communication_cooldown -= dt
        
        # Execute personality-specific behaviors
        self.update_personality_behavior(dt, game_state)

    def update_personality_behavior(self, dt, game_state=None):
        """Execute personality-specific behaviors"""
        if not game_state:
            return
        
        # Update decoy status
        if self.decoy_timer > 0:
            self.decoy_timer -= dt
            if self.decoy_timer <= 0:
                self.is_decoy = False
        
        if self.fake_movement_cooldown > 0:
            self.fake_movement_cooldown -= dt
        
        # Personality-specific behaviors
        if self.personality == "trickster" and self.fake_movement_cooldown <= 0:
            if self.rng and self.rng.random() < (0.1 * self.deception * dt):
                self.create_fake_movement(game_state)
                self.fake_movement_cooldown = self.rng.uniform(8, 15)
        
        elif self.personality == "stalker":
            # Track player patterns and predict movements
            if len(self.player_action_memory) > 3:
                self.stalking_mode = True
                self.ambush_position = self.predict_player_weakness()
        
        elif self.personality == "patient":
            # Wait longer before moving, but move with purpose
            self.move_interval = self.base_interval * (1.5 * self.patience)
        
        elif self.personality == "aggressive":
            # Increase move speed and aggression
            self.adaptive_aggro = min(2.5, self.adaptive_aggro * 1.1)
        
        elif self.personality == "erratic":
            # Randomize behavior to be unpredictable
            if self.rng and self.rng.random() < 0.05:
                self.mood = self.rng.choice(["aggressive", "cautious", "neutral"])
    
    def create_fake_movement(self, game_state):
        """Create a fake movement sound/event"""
        if hasattr(game_state, 'phantom_sounds'):
            fake_location = self.rng.choice(list(ROOM_GRAPH.keys()))
            game_state.phantom_sounds.append({
                'location': fake_location,
                'time': time.time(),
                'type': 'fake_movement'
            })
    
    def predict_player_weakness(self):
        """Analyze player patterns to find weaknesses"""
        if not self.player_action_memory:
            return None
        
        # Count door usage patterns
        left_blocks = sum(1 for action in self.player_action_memory if action.get('side') == 'left')
        right_blocks = sum(1 for action in self.player_action_memory if action.get('side') == 'right')
        
        # Attack the less-defended side
        if left_blocks < right_blocks:
            return "left"
        elif right_blocks < left_blocks:
            return "right"
        return None
    
    def update_mood(self, game_state=None):
        """Update mood based on situation (deterministic)"""
        minutes = game_state.minutes_elapsed if game_state else 0
        night = game_state.night if game_state else 1
        if self.hunting_mode:
            self.mood = "hunting"
        elif self.block_count >= 3:  # If frustrated enough, go hunting
            self.mood = "hunting"
        elif self.block_count >= 4 or minutes >= 180 or night >= 2:
            self.mood = "aggressive"
        elif self.block_count >= 2 or minutes >= 60:
            self.mood = "cautious"
        else:
            self.mood = "hunting"  # Always lean toward hunting/office-seeking

    def get_mood_multiplier(self):
        """Get aggression multiplier based on mood"""
        mood_map = {
            "neutral": 1.0,
            "cautious": 0.7,
            "aggressive": 1.4,
            "hunting": 1.6,
            "retreating": 0.5
        }
        return mood_map.get(self.mood, 1.0)

    def move_patrol(self):
        """Move along a fixed patrol route"""
        if not self.patrol_route:
            return
        self.patrol_index = (self.patrol_index + 1) % len(self.patrol_route)
        next_room = self.patrol_route[self.patrol_index]
        if next_room != self.room:
            self.last_room = self.room
            self.room = next_room
            self.target_x, self.target_y = room_position(self.room, WINDOW_WIDTH, WINDOW_HEIGHT)

    def move_toward_target(self, target_room):
        """Move toward a specific target room"""
        if not target_room or target_room == self.room:
            return
        
        neighbors = get_neighbors(self.room)
        if not neighbors:
            return
        
        # Simple pathfinding: move toward target
        best_room = self.room
        if target_room in neighbors:
            best_room = target_room
        else:
            # Move closer to target (greedy pathfinding)
            for neighbor in neighbors:
                if self._distance_to_room(neighbor, target_room) < self._distance_to_room(best_room, target_room):
                    best_room = neighbor
        
        if best_room != self.room:
            self.last_room = self.room
            self.room = best_room
            self.target_x, self.target_y = room_position(self.room, WINDOW_WIDTH, WINDOW_HEIGHT)

    def _distance_to_room(self, from_room, to_room):
        """Estimate distance between rooms"""
        if from_room == to_room:
            return 0
        # Simple heuristic: count edges to target
        visited = {from_room}
        queue = [(from_room, 0)]
        while queue:
            current, dist = queue.pop(0)
            if current == to_room:
                return dist
            for neighbor in get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        return 999

    def try_attack(self, office):
        """Try to attack if in office"""
        if self.room == "Office":
            if self.attack_side == "left":
                return not office.door_left_closed
            if self.attack_side == "right":
                return not office.door_right_closed
            if self.attack_side == "vent":
                # Vent crawler only succeeds if at least one door is open
                return not (office.door_left_closed and office.door_right_closed)
        return False
    
    def get_blocked_side(self, office):
        """Check which door is blocking this animatronic (if any)"""
        if self.room == "Office":
            if self.attack_side == "left" and office.door_left_closed:
                self.handle_blocked("left")
                return "left"
            if self.attack_side == "right" and office.door_right_closed:
                self.handle_blocked("right")
                return "right"
            if self.attack_side == "vent" and (office.door_left_closed and office.door_right_closed):
                self.handle_blocked("both")
                return "both"
        return None

    def handle_blocked(self, side):
        """Handle being blocked - learning and mood change"""
        self.block_count += 1
        self.last_blocked_time = time.time()
        self.hunting_timer = 12.0
        self.hunt_target_room = "Office"
        self.mood = "aggressive"
        # MUST leave the office - find a neighboring room and move there immediately
        if self.room == "Office":
            neighbors = get_neighbors(self.room)
            if neighbors:
                # Pick a deterministic neighbor, avoid immediate hallway if possible
                retreat_candidates = [r for r in neighbors if r != "Hallway"]
                if not retreat_candidates:
                    retreat_candidates = neighbors
                self.last_room = self.room
                self.room = retreat_candidates[self.block_count % len(retreat_candidates)]
                self.target_x, self.target_y = room_position(self.room, 1280, 720)
                self.x = self.target_x
                self.y = self.target_y
                self.retreat_timer = 4.0
                self.retreat_target = self.room
        # Record this memory for future behavior
        self.player_action_memory.append({"action": "blocked", "side": side, "time": time.time()})


# =====================================================
# ASSET MANAGER
# =====================================================

class AssetManager:
    """Manages all game assets"""
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.music = {}
        self.static_source = None
        self.ambience_source = None
        self.current_music = None

    def load_image(self, name, path):
        """Safely load an image"""
        full_path = os.path.join(BASE_DIR, path)
        if os.path.exists(full_path):
            try:
                self.images[name] = pygame.image.load(full_path).convert_alpha()
                return self.images[name]
            except:
                return None
        return None

    def load_sound(self, name, path):
        """Safely load a sound"""
        full_path = os.path.join(BASE_DIR, path)
        if os.path.exists(full_path):
            try:
                self.sounds[name] = pygame.mixer.Sound(full_path)
                return self.sounds[name]
            except:
                return None
        return None

    def load_music(self, name, path):
        """Safely load music"""
        full_path = os.path.join(BASE_DIR, path)
        if os.path.exists(full_path):
            try:
                # For streaming music, we'll use pygame.mixer.music
                self.music[name] = full_path
                return full_path
            except:
                return None
        return None

    def load_all_assets(self):
        """Load all game assets"""
        # Images
        self.load_image("office", "assets/img/office.png")
        self.load_image("door_left", "assets/img/office_door_left.png")
        self.load_image("door_right", "assets/img/office_door_right.png")
        # Room cameras
        self.load_image("cam_stage", "assets/img/cam_stage.png")
        self.load_image("cam_dining_area", "assets/img/cam_dining_area.png")
        self.load_image("cam_backstage", "assets/img/cam_backstage.png")
        self.load_image("cam_kitchen", "assets/img/cam_kitchen.png")
        self.load_image("cam_west_hall", "assets/img/cam_west_hall.png")
        self.load_image("cam_east_hall", "assets/img/cam_east_hall.png")
        self.load_image("cam_cafeteria", "assets/img/cam_cafeteria.png")
        self.load_image("cam_gym", "assets/img/cam_gym.png")
        self.load_image("cam_library", "assets/img/cam_library.png")
        self.load_image("cam_bathrooms", "assets/img/cam_bathrooms.png")
        self.load_image("cam_vent", "assets/img/cam_vent.png")
        self.load_image("cam_supply_closet", "assets/img/cam_supply_closet.png")
        self.load_image("cam_restrooms", "assets/img/cam_restrooms.png")
        self.load_image("title", "assets/img/title.png")
        self.load_image("menu_background", "assets/img/menu_background.png")
        self.load_image("intro_splash", "assets/img/intro_splashscreen.png")
        self.load_image("tos_splash", "assets/img/tos_splash.png")
        # Animatronics
        self.load_image("anim_mr_ingles", "assets/img/anim_mr_ingles.png")
        self.load_image("anim_scary_ingles", "assets/img/anim_scary_ingles.png")  # Optional
        self.load_image("anim_guard_ingles", "assets/img/anim_guard_ingles.png")  # Optional
        self.load_image("anim_janitor", "assets/img/anim_janitor.png")
        self.load_image("anim_librarian", "assets/img/anim_librarian.png")
        self.load_image("anim_vent_crawler", "assets/img/anim_vent.png")  # Using existing anim_vent.png
        self.load_image("mr_ingles_office", "assets/img/mr_ingles_office.png")
        self.load_image("mr_hall_anti_cheater", "assets/img/mr_hall_anti_cheater.png")

        # Sounds
        self.load_sound("door_close", "assets/sfx/door_close.ogg")
        self.load_sound("door_open", "assets/sfx/door_open.ogg")
        self.load_sound("light_toggle", "assets/sfx/light_toggle.ogg")
        self.load_sound("jumpscare", "assets/sfx/jumpscare.ogg")
        self.load_sound("nice_try", "assets/sfx/NICE_TRY.mp3")
        self.load_sound("intro_msg", "assets/sfx/intro_msg.mp3")
        self.load_sound("bell_6am", "assets/sfx/bell_6am.ogg")
        self.load_sound("static_loop", "assets/sfx/static_loop.ogg")

        # Music/Ambience
        self.load_music("ambience", "assets/music/ambience.mp3")
        self.load_music("menu_theme", "assets/music/menu_theme.ogg")

    def play_sound(self, name):
        """Play a sound effect"""
        if name in self.sounds:
            self.sounds[name].stop()
            self.sounds[name].play()

    def play_music(self, name, loops=-1):
        """Play music (streaming)"""
        # If trying to play ambience (any night), use the single ambience.mp3
        if name and name.startswith("ambience"):
            name = "ambience"
        
        if name in self.music:
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.load(self.music[name])
                pygame.mixer.music.set_volume(1.0)
                pygame.mixer.music.play(loops)
                self.current_music = name
            except Exception as e:
                pass

    def stop_music(self):
        """Stop current music"""
        pygame.mixer.music.stop()
        self.current_music = None

    def get_image(self, name):
        """Get an image, return None if not loaded"""
        return self.images.get(name)


# =====================================================
# GAME ENGINE
# =====================================================

class Game:
    """Main game engine"""
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Create resizable window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Track window size for scaling
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        # Render to this surface at fixed resolution, then scale to screen
        self.render_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        # Temporarily swap so all existing code renders to render_surface
        self.screen, self.render_surface = self.render_surface, self.screen

        # Game components
        self.game_state = GameState()
        self.power = PowerSystem()
        self.office = Office()
        self.cameras = CameraSystem()
        self.jumpscare = Jumpscare()
        self.assets = AssetManager()

        # Animatronics list
        self.animatronics = []

        # Fonts (scaled for 1280x720 resolution)
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 64)
        self.font_title = pygame.font.Font(None, 80)
        self.font_button = pygame.font.Font(None, 36)
        
        # Visual effects
        self.screen_shake = 1
        self.flicker_timer = 0
        self.static_intensity = 1
        self.noise_phase = 0.0
        self.flicker_phase = 0.0
        self.run_seed = int(time.time() * 1000) % 1000000
        self.rng = random.Random(self.run_seed)
        self.side_entry_cooldown = {"left": 0.0, "right": 0.0, "vent": 0.0}
        self.entry_cooldown_seconds = 6.0
        self.max_office_attackers = 2
        self.jam_grace_timer = 0.0
        self.overload_grace_timer = 0.0
        self.door_open_limit = 7.0
        self.power_usage = {"base": 0.0, "doors": 0.0, "lights": 0.0, "cams": 0.0, "surge": 1.0}
        self.show_controls = True
        
        # Environmental event system
        self.phantom_sound_cooldown = 0
        self.environmental_event_timer = 0
        self.next_event_time = 30  # First event after 30 seconds
        self.hallucination_mode = False
        self.hallucination_timer = 0
        
        # Animatronic coordination
        self.coordinated_attack_cooldown = 0
        self.active_coordination = None
        
        # Dynamic stats tracking
        self.total_door_closes = 0
        self.total_camera_checks = 0
        self.perfect_blocks = 0
        self.failed_blocks = 0
        self.performance_score = 0
        self.high_scores = {}  # Night -> score mapping
        
        # Screen effects
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0
        self.color_overlay = None  # (r, g, b, alpha) or None
        self.color_overlay_timer = 0
        self.particles = []  # List of particle effects
        
        # Amazing new features
        self.threat_level = 0  # Real-time threat assessment 0-100
        self.audio_distraction_cooldown = 0
        self.generator_minigame_active = False
        self.generator_progress = 0
        self.generator_target_keys = []
        self.nightmare_mode = False
        self.safe_spots_available = ["Closet", "Under Desk", "Vent"]
        self.current_safe_spot = None
        self.safe_spot_duration = 0
        self.footstep_sounds = []  # Track animatronic movements
        self.breathing_intensity = 0  # Increases with danger
        self.heartbeat_active = False
        self.last_noise_time = 0
        self.combo_blocks = 0  # Consecutive perfect blocks
        self.combo_timer = 0
        
        # Noise maker menu state
        self.noise_maker_menu_active = False
        self.noise_maker_rooms = ["Cafeteria", "Gym", "Library", "Bathrooms", "Dining Area", "Kitchen", "Vent"]
        self.noise_maker_buttons = {}  # Room index -> button rect
        self.night_buttons = {}  # Night number -> button rect

        # Anti-cheat: reflex door spam detection
        self.reflex_blocks = 0
        self.last_reflex_time = 0.0
        self.last_office_entry_time = {"left": -999.0, "right": -999.0, "vent": -999.0}
        self.anti_cheat_active = False
        self.anti_cheat_timer = 0.0
        self.anti_cheat_pending = False
        
        # Minimap data
        self.minimap_room_positions = {}
        self.coordination_timer = 0.0

        # Menu slider (night length)
        self.slider_min = 15.0   # seconds per in-game hour (fast)
        self.slider_max = 180.0  # seconds per in-game hour (slow)
        self.dragging_slider = False
        self.slider_hover = False
        # Difficulty slider
        self.difficulty_min = 0.8
        self.difficulty_max = 2.0
        self.difficulty = 1.2
        self.dragging_difficulty = False

        # Intro sequence (Night 1)
        self.intro_messages = []
        self.intro_index = 0
        self.intro_timer = 0.0
        self.intro_message_duration = 1.5  # seconds per message (incl fade in/out)
        self.intro_message_durations = []

        # Splash screen (on boot)
        self.splash_timer = 0.0
        self.splash_stage = 0
        self.splash_sequence = [
            {"key": "intro_splash", "fade_in": 1.0, "hold": 1.0, "fade_out": 1.0},
            {"key": "tos_splash", "fade_in": 1.0, "hold": 3.5, "fade_out": 1.0},
        ]

        # Tutorial slideshow (after intro)
        self.tutorial_index = 0
        self.tutorial_timer = 0.0
        self.tutorial_slide_duration = 5.0  # seconds per slide (increased for more content)
        self.tutorial_slides = [
            {"title": "BASIC CONTROLS", "text": "Use Q and E to control doors\nPress F to toggle flashlight\nPress TAB to open cameras\nClose doors when animatronics approach"},
            {"title": "CAMERA SYSTEM", "text": "Watch 10 different rooms\nAnimatronics move through them\nClick minimap to jump to rooms\nStay vigilant at all times"},
            {"title": "MULTIPLE PATHS", "text": "Two hallways lead to your office\nWest Hall on the left side\nEast Hall on the right side\nMonitor both carefully"},
            {"title": "POWER MANAGEMENT", "text": "Power surges at :15, :30, :45\nCameras drain power when viewing\nDoors drain power when closed\nBalance usage to survive"},
            {"title": "AI BEHAVIOR", "text": "Each animatronic has unique traits\nThey patrol different routes\nSome are fast, others are sneaky\nLearn their patterns"},
            {"title": "DOOR HEALTH", "text": "Doors can jam if damaged\nAnimatronics wear them down\nJammed doors leave you exposed\nPrevent attacks to preserve them"},
            {"title": "SURVIVE UNTIL 6 AM", "text": "Each hour lasts several minutes\nWatch the clock in top-right\nManage resources carefully\nMake it through the night"},
            {"title": "GOOD LUCK", "text": "Stay alert and aware\nUse cameras to track movement\nDon't waste power\nYou can do this"},
        ]

        # Load everything
        self.assets.load_all_assets()
        self.load_save()

        if self.game_state.state == "menu":
            self.play_menu_music()

    def clamp(self, x, a, b):
        """Clamp value between a and b"""
        return max(a, min(x, b))
    
    def scale_mouse_pos(self, pos):
        """Scale mouse position from window coordinates to game coordinates"""
        mx, my = pos
        # Calculate scale factors
        scale_x = WINDOW_WIDTH / self.window_width
        scale_y = WINDOW_HEIGHT / self.window_height
        # Use the smaller scale to maintain aspect ratio
        scale = min(scale_x, scale_y)
        # Calculate scaled dimensions
        scaled_w = WINDOW_WIDTH / scale
        scaled_h = WINDOW_HEIGHT / scale
        # Calculate offset for centering
        offset_x = (self.window_width - scaled_w) / 2
        offset_y = (self.window_height - scaled_h) / 2
        # Scale and offset mouse position
        game_x = (mx - offset_x) * scale
        game_y = (my - offset_y) * scale
        return (game_x, game_y)
    
    def scale_and_blit_to_screen(self):
        """Scale the render surface to the actual window while maintaining aspect ratio"""
        # Calculate scale to fit window while maintaining aspect ratio
        scale_x = self.window_width / WINDOW_WIDTH
        scale_y = self.window_height / WINDOW_HEIGHT
        scale = min(scale_x, scale_y)
        
        # Calculate scaled dimensions
        scaled_width = int(WINDOW_WIDTH * scale)
        scaled_height = int(WINDOW_HEIGHT * scale)
        
        # Calculate position to center the scaled surface
        x = (self.window_width - scaled_width) // 2
        y = (self.window_height - scaled_height) // 2
        
        # Fill screen with black bars
        self.render_surface.fill((0, 0, 0))
        
        # Scale and blit the game surface
        scaled_surface = pygame.transform.scale(self.screen, (scaled_width, scaled_height))
        self.render_surface.blit(scaled_surface, (x, y))
    
    def set_status(self, msg=""):
        """Set status message"""
        self.game_state.status = msg or ""

    def log_event(self, msg, add_personality_hint=False):
        """Event log disabled"""
        pass

    def break_door(self, side):
        """Force a door to jam open when its health is depleted"""
        if side == "left":
            self.office.door_left_closed = False
            self.office.door_left_jam_timer = 4.5
            self.set_status("Left door jammed open!")
            self.log_event("Left door jammed")
        elif side == "right":
            self.office.door_right_closed = False
            self.office.door_right_jam_timer = 4.5
            self.set_status("Right door jammed open!")
            self.log_event("Right door jammed")
        self.jam_grace_timer = max(self.jam_grace_timer, 3.0)

    def check_reflex_cheat(self, side):
        """Detect reflex door slams right after an animatronic enters."""
        if self.anti_cheat_active:
            return
        entry_time = self.last_office_entry_time.get(side, -999.0)
        if entry_time <= 0:
            return
        now = time.time()
        # If the door is slammed within a very short window, count it
        if now - entry_time <= 1.2:
            # Decay the counter if it's been a while
            if now - self.last_reflex_time > 20.0:
                self.reflex_blocks = 0
            self.reflex_blocks += 1
            self.last_reflex_time = now
            if self.reflex_blocks >= 1:
                self.trigger_anti_cheat()

    def trigger_anti_cheat(self):
        """Trigger anti-cheat punishment sequence."""
        if self.anti_cheat_active:
            return
        self.anti_cheat_active = True
        self.anti_cheat_timer = 0.0
        self.anti_cheat_pending = False
        # Force office view and hide animatronics during the warning
        self.office.cams_open = False
        self.office.light_on = False
        for anim in self.animatronics:
            anim.room = "Hidden"
        self.assets.stop_music()
        self.assets.play_sound("nice_try")
        self.set_status("")
        self.game_state.state = "anti_cheat"
    
    def apply_creepy_static(self, intensity=0.3):
        """Apply creepy static/noise overlay"""
        static_surface = pygame.Surface((self.game_state.width, self.game_state.height))
        static_surface.set_alpha(int(255 * intensity * 0.4))
        count = max(1, int(100 * intensity))
        for i in range(count):
            t = self.noise_phase + i * 0.17
            x = int((math.sin(t * 1.7) * 0.5 + 0.5) * self.game_state.width)
            y = int((math.sin(t * 2.3 + 1.1) * 0.5 + 0.5) * self.game_state.height)
            c = 180 + int((math.sin(t * 4.2) * 0.5 + 0.5) * 70)
            color = (c, c, c)
            length = 1 + int((math.sin(t * 3.1 + 2.2) * 0.5 + 0.5) * 2)
            pygame.draw.line(static_surface, color, (x, y), (x + length, y + 1), 1)
        self.screen.blit(static_surface, (0, 0))
    
    def draw_minimap(self, opacity=255):
        """Draw camera minimap showing room layout and animatronic positions"""
        # Minimap dimensions
        minimap_width = 340
        minimap_height = 240
        minimap_x = self.game_state.width - minimap_width - 20
        minimap_y = 80
        
        # Background panel with opacity
        panel_surface = pygame.Surface((minimap_width, minimap_height))
        panel_surface.set_alpha(opacity)
        panel_surface.fill((10, 10, 30))
        self.screen.blit(panel_surface, (minimap_x, minimap_y))
        
        # Border
        pygame.draw.rect(self.screen, (100, 150, 200), (minimap_x, minimap_y, minimap_width, minimap_height), 2)
        
        # Title
        map_title = self.font_small.render("CAMERA MAP", True, (100, 200, 255))
        self.screen.blit(map_title, (minimap_x + 10, minimap_y + 5))
        
        # Scale and position for minimap rooms
        room_positions = {
            "Office": (minimap_x + 170, minimap_y + 200),
            "West Hall": (minimap_x + 100, minimap_y + 200),
            "East Hall": (minimap_x + 240, minimap_y + 200),
            "Cafeteria": (minimap_x + 100, minimap_y + 150),
            "Gym": (minimap_x + 50, minimap_y + 150),
            "Library": (minimap_x + 240, minimap_y + 150),
            "Bathrooms": (minimap_x + 290, minimap_y + 150),
            "Stage": (minimap_x + 170, minimap_y + 35),
            "Dining Area": (minimap_x + 170, minimap_y + 90),
            "Backstage": (minimap_x + 240, minimap_y + 35),
            "Kitchen": (minimap_x + 240, minimap_y + 90),
            "Supply Closet": (minimap_x + 40, minimap_y + 200),
            "Restrooms": (minimap_x + 300, minimap_y + 200),
            "Vent": (minimap_x + 290, minimap_y + 120),
        }
        
        # Store positions for click detection
        self.minimap_room_positions = room_positions
        
        # Draw room connections
        for room, neighbors in ROOM_GRAPH.items():
            if room in room_positions:
                for neighbor in neighbors:
                    if neighbor in room_positions:
                        pygame.draw.line(self.screen, (60, 100, 150), 
                                       room_positions[room], room_positions[neighbor], 1)
        
        # Draw rooms
        for room, pos in room_positions.items():
            # Highlight current camera room
            is_current_room = room == self.cameras.current_camera()
            room_color = (50, 255, 100) if is_current_room else (60, 120, 180)
            pygame.draw.circle(self.screen, room_color, pos, 12)
            pygame.draw.circle(self.screen, (100, 200, 255), pos, 12, 2)
            
            # Room label (abbreviated)
            label = room[:3].upper()
            label_text = self.font_small.render(label, True, (200, 200, 200))
            label_rect = label_text.get_rect(center=pos)
            self.screen.blit(label_text, (label_rect.x - 2, label_rect.y - 3))
        
        # Legend
        legend_y = minimap_y + minimap_height - 25
        green_dot = pygame.Surface((6, 6))
        green_dot.fill((50, 255, 100))
        self.screen.blit(green_dot, (minimap_x + 10, legend_y))
        legend_text = self.font_small.render("Current Cam", True, (150, 200, 150))
        self.screen.blit(legend_text, (minimap_x + 20, legend_y - 2))
        
        orange_dot = pygame.Surface((6, 6))
        orange_dot.fill((255, 150, 50))
        self.screen.blit(orange_dot, (minimap_x + 150, legend_y))
        anim_text = self.font_small.render("Animatronic", True, (255, 180, 100))
        self.screen.blit(anim_text, (minimap_x + 160, legend_y - 2))
    
    def get_clicked_room(self, mouse_pos):
        """Check if a room was clicked on the minimap"""
        for room, pos in self.minimap_room_positions.items():
            distance = math.sqrt((mouse_pos[0] - pos[0])**2 + (mouse_pos[1] - pos[1])**2)
            if distance <= 15:  # Click radius
                return room
        return None

    def load_save(self):
        """Load save file"""
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.game_state.max_night_unlocked = self.clamp(data.get("max_night", 1), 1, 5)
                    if "difficulty" in data:
                        self.difficulty = self.clamp(float(data.get("difficulty", self.difficulty)),
                                                     self.difficulty_min, self.difficulty_max)
                    if "high_scores" in data:
                        self.high_scores = {int(k): v for k, v in data["high_scores"].items()}
            except:
                self.game_state.max_night_unlocked = 1
        else:
            self.game_state.max_night_unlocked = 1

    def save_progress(self):
        """Save progress to file"""
        data = {
            "max_night": self.clamp(self.game_state.max_night_unlocked, 1, 5),
            "difficulty": self.clamp(self.difficulty, self.difficulty_min, self.difficulty_max),
            "high_scores": self.high_scores,
        }
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass

    def reset_animatronics(self):
        """Reset animatronics to starting positions"""
        def jitter(base, spread):
            return base + self.rng.uniform(-spread, spread)

        self.animatronics = [
            Animatronic("Scary Mr Ingles", "Supply Closet", jitter(0.52, 0.08), jitter(5.0, 0.5), "normal",
                        attack_side="right",
                        patrol_route=["Supply Closet", "West Hall", "Gym", "Cafeteria", "Dining Area"],
                        start_delay_minutes=self.rng.randint(2, 5),
                        hallway_entry_delay=jitter(2.2, 0.4),
                        aggression_ramp=jitter(0.25, 0.06),
                        rng=self.rng),
            Animatronic("Janitor Bot", "Backstage", jitter(0.34, 0.05), jitter(6.5, 0.7), "teleport",
                        attack_side="right",
                        patrol_route=["Backstage", "Kitchen", "East Hall", "Bathrooms"],
                        start_delay_minutes=self.rng.randint(5, 10),
                        hallway_entry_delay=jitter(2.6, 0.4),
                        aggression_ramp=jitter(0.22, 0.06),
                        rng=self.rng),
            Animatronic("Librarian", "Stage", jitter(0.32, 0.05), jitter(6.8, 0.6), "teleport",
                        attack_side="left",
                        patrol_route=["Stage", "Dining Area", "Cafeteria", "Library"],
                        start_delay_minutes=self.rng.randint(6, 11),
                        hallway_entry_delay=jitter(2.4, 0.4),
                        aggression_ramp=jitter(0.24, 0.06),
                        rng=self.rng),
            Animatronic("Vent Crawler", "Vent", jitter(0.38, 0.05), jitter(5.8, 0.6), "vent",
                        attack_side="vent",
                        patrol_route=["Vent", "Bathrooms", "Restrooms", "East Hall"],
                        start_delay_minutes=self.rng.randint(15, 21),
                        hallway_entry_delay=jitter(2.0, 0.3),
                        aggression_ramp=jitter(0.28, 0.06),
                        rng=self.rng),
        ]

    def start_night(self, night):
        """Start a new night"""
        self.assets.stop_music()
        self.game_state.night = self.clamp(night, 1, 5)
        self.set_status("")
        self.power.reset()
        self.office.reset()
        self.reset_animatronics()
        self.jumpscare.reset()
        self.cameras.current_index = 0
        # Reset time counters
        self.game_state.hour = 12
        self.game_state.hour_timer = 0
        self.game_state.minutes_elapsed = 0
        # Reset safe spot state for new night
        self.current_safe_spot = None
        self.safe_spot_duration = 0
        self.safe_spots_available = ["Closet", "Under Desk", "Vent"]

        # Reset anti-cheat state
        self.reflex_blocks = 0
        self.last_reflex_time = 0.0
        self.last_office_entry_time = {"left": -999.0, "right": -999.0, "vent": -999.0}
        self.anti_cheat_active = False
        self.anti_cheat_timer = 0.0
        self.anti_cheat_pending = False
        
        # Apply adaptive difficulty based on previous performance
        self.apply_adaptive_difficulty()

        # Intro sequence only for Night 1
        if self.game_state.night == 1:
            self.game_state.state = "intro"
            self.intro_messages = [
                "YOU'RE IN THE SCIENCE BLOCK.",
                "ALONE.",
                "HIDING IN MR. INGLES'S OFFICE.",
                "MR. INGLES AND HIS ARMY ARE WATCHING.",
                "DON'T GET CAUGHT.",
            ]
            self.intro_index = 0
            self.intro_timer = 0.0
            # Play intro voice/message and sync timings
            intro_sound = self.assets.sounds.get("intro_msg")
            if intro_sound:
                self.assets.play_sound("intro_msg")
                total_len = max(0.5, intro_sound.get_length())
                weights = [1.0, 0.6, 1.0, 1.0, 1.0]
                if len(weights) != len(self.intro_messages):
                    weights = [1.0] * len(self.intro_messages)
                weight_sum = max(0.1, sum(weights))
                self.intro_message_durations = [
                    max(0.4, total_len * (w / weight_sum)) for w in weights
                ]
                self.intro_message_duration = max(0.6, total_len / max(1, len(self.intro_messages)))
            else:
                self.intro_message_duration = 1.5
                self.intro_message_durations = []
        else:
            # Load and play night ambience
            ambience_key = f"ambience_n{self.game_state.night}"
            self.assets.play_music(ambience_key)
            self.game_state.state = "playing"
            self.game_state.start_time = time.time()
            self.game_state.hour_timer = 0
            self.game_state.minutes_elapsed = 0

    def apply_adaptive_difficulty(self):
        """Adjust animatronic difficulty based on player performance"""
        if self.game_state.night < 2:
            return
        
        # Base difficulty increases per night
        night_factor = 0.15 * (self.game_state.night - 1)
        
        # Analyze player performance from previous nights (use door usage patterns)
        successful_defenses = sum([a.block_count for a in self.animatronics]) / max(1, len(self.animatronics))
        
        # If player was very successful at blocking, make animatronics more aggressive
        if successful_defenses > 5:
            difficulty_boost = 0.2
        elif successful_defenses > 2:
            difficulty_boost = 0.1
        else:
            difficulty_boost = 0.0
        
        # Apply difficulty adjustments to animatronics
        for anim in self.animatronics:
            anim.base_aggro = anim.base_aggro * (1.0 + night_factor + difficulty_boost)
            anim.aggro = anim.base_aggro
            # Reset learning for new night but keep personality
            anim.block_count = max(0, anim.block_count - 3)
            anim.player_action_memory.clear()

    def restart_from_menu(self):
        """Return to menu"""
        self.enter_menu()

    def enter_menu(self):
        """Enter main menu state"""
        self.game_state.state = "menu"
        self.set_status("")
        self.assets.stop_music()
        self.play_menu_music()

    def play_menu_music(self):
        """Play menu theme"""
        self.assets.play_music("menu_theme")

    # =====================================================
    # UPDATE FUNCTIONS
    # =====================================================
    
    def add_screen_shake(self, intensity, duration):
        """Add screen shake effect"""
        self.screen_shake_intensity = max(self.screen_shake_intensity, intensity)
        self.screen_shake_duration = max(self.screen_shake_duration, duration)
    
    def add_color_overlay(self, color, duration):
        """Add temporary color overlay (r, g, b, alpha)"""
        self.color_overlay = color
        self.color_overlay_timer = duration
    
    def add_particle_burst(self, x, y, count, color, speed_range=(1, 3)):
        """Create a burst of particles at position"""
        for _ in range(count):
            angle = self.rng.uniform(0, math.pi * 2)
            speed = self.rng.uniform(*speed_range)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color,
                'life': 1.0,
                'size': self.rng.randint(2, 5)
            })
    
    def update_screen_effects(self, dt):
        """Update all screen effects"""
        # Update screen shake
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= dt
            if self.screen_shake_duration <= 0:
                self.screen_shake_intensity = 0
        
        # Update color overlay
        if self.color_overlay_timer > 0:
            self.color_overlay_timer -= dt
            if self.color_overlay_timer <= 0:
                self.color_overlay = None
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """Draw all active particles"""
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = particle['color'][:3]
            size = max(1, int(particle['size'] * particle['life']))
            pos = (int(particle['x']), int(particle['y']))
            pygame.draw.circle(self.screen, color, pos, size)
    
    def apply_screen_shake(self):
        """Get screen shake offset"""
        if self.screen_shake_intensity > 0:
            shake_x = self.rng.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_y = self.rng.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            return int(shake_x), int(shake_y)
        return 0, 0
    
    def apply_color_overlay(self):
        """Apply color overlay to screen"""
        if self.color_overlay:
            overlay = pygame.Surface((self.game_state.width, self.game_state.height))
            overlay.set_alpha(self.color_overlay[3] if len(self.color_overlay) > 3 else 128)
            overlay.fill(self.color_overlay[:3])
            self.screen.blit(overlay, (0, 0))

    def update_office_effects(self, dt):
        """Update office visual effects"""
        # Door animations
        door_speed = 5 * dt
        left_target = 1 if self.office.door_left_closed else 0
        right_target = 1 if self.office.door_right_closed else 0
        self.office.door_left_progress += (left_target - self.office.door_left_progress) * door_speed
        self.office.door_right_progress += (right_target - self.office.door_right_progress) * door_speed

        # Light dimming
        dim_target = 0 if self.office.light_on else 0.6
        dim_speed = 3 * dt
        self.office.light_dim += (dim_target - self.office.light_dim) * dim_speed

        # Camera flash fade
        if self.office.cam_flash > 0:
            self.office.cam_flash = max(0, self.office.cam_flash - dt * 2.8)

        # Door jam timers
        if self.office.door_left_jam_timer > 0:
            self.office.door_left_jam_timer = max(0, self.office.door_left_jam_timer - dt * 1.5)
        if self.office.door_right_jam_timer > 0:
            self.office.door_right_jam_timer = max(0, self.office.door_right_jam_timer - dt * 1.5)

        # Doors stay open/closed until player toggles them - no auto-close
        # This gives players full control

        # Entry cooldown timers (fairness)
        for side in self.side_entry_cooldown:
            if self.side_entry_cooldown[side] > 0:
                self.side_entry_cooldown[side] = max(0.0, self.side_entry_cooldown[side] - dt)

        if self.jam_grace_timer > 0:
            self.jam_grace_timer = max(0.0, self.jam_grace_timer - dt)
        if self.overload_grace_timer > 0:
            self.overload_grace_timer = max(0.0, self.overload_grace_timer - dt)

        # Door wear and passive recovery
        wear_rate = (1.2 * self.difficulty) * dt
        recover_rate = (0.6 / max(0.8, self.difficulty)) * dt
        if self.office.door_left_closed:
            self.office.door_left_health = max(0, self.office.door_left_health - wear_rate)
        else:
            self.office.door_left_health = 100.0
        if self.office.door_right_closed:
            self.office.door_right_health = max(0, self.office.door_right_health - wear_rate)
        else:
            self.office.door_right_health = 100.0

        if self.office.door_left_closed and self.office.door_left_health <= 0 and self.office.door_left_jam_timer <= 0:
            self.break_door("left")
        if self.office.door_right_closed and self.office.door_right_health <= 0 and self.office.door_right_jam_timer <= 0:
            self.break_door("right")

        self.update_fairness_caps()

    def update_fairness_caps(self):
        """Compute real-time caps to prevent impossible states"""
        doors_open = int(not self.office.door_left_closed) + int(not self.office.door_right_closed)
        avg_health = (self.office.door_left_health + self.office.door_right_health) / 2.0
        low_power = self.power.current < 20
        cam_disabled = self.power.outage
        jam_active = self.office.door_left_jam_timer > 0 or self.office.door_right_jam_timer > 0

        cap = 2
        if doors_open >= 2:
            cap = 1
        if low_power or cam_disabled or avg_health < 30 or jam_active:
            cap = 1
        if self.jam_grace_timer > 0 or self.overload_grace_timer > 0:
            cap = 1

        self.max_office_attackers = cap

        # Entry cooldown scales with defensive weakness
        cooldown = 6.0
        if low_power:
            cooldown += 2.0
        if cam_disabled:
            cooldown += 1.5
        if avg_health < 30:
            cooldown += 2.0
        if doors_open >= 2:
            cooldown += 1.0
        self.entry_cooldown_seconds = max(6.0, min(12.0, cooldown))
        
        # Screen shake decay
        if self.screen_shake > 0:
            self.screen_shake *= 0.95
        
        # Static intensity decay (but stay high during outage)
        if self.power.outage:
            self.static_intensity = 0.6
        elif self.static_intensity > 0:
            self.static_intensity *= 0.98

    def update_power(self, dt):
        """Update power drain"""
        if self.game_state.state != "playing":
            return

        # Creepy flickering when low power
        if self.power.current < 30:
            self.flicker_phase += dt * 6
            flicker = (math.sin(self.flicker_phase * 3.0) * 0.5 + 0.5) * 0.3
            self.office.light_dim += (flicker - 0.15)
            self.office.light_dim = self.clamp(self.office.light_dim, 0, 0.8)

        if self.power.current <= 0:
            self.power.current = 0
            if not self.power.outage:
                self.power.outage = True
                self.power.emergency_mode = True
                self.power.emergency_timer = 45  # 45 seconds of emergency power
                self.power.reserve_power = 15  # Hidden reserve
                self.office.door_left_closed = False
                self.office.door_right_closed = False
                self.office.light_on = False
                self.office.cams_open = False
                self.set_status("POWER OUTAGE - EMERGENCY MODE ACTIVE")
                self.static_intensity = 0.8
                self.screen_shake = 3
                self.log_event("EMERGENCY: Backup power engaged!")
        
        # Emergency mode countdown
        if self.power.outage and self.power.emergency_mode:
            self.power.emergency_timer -= dt
            if self.power.emergency_timer <= 0:
                self.power.emergency_mode = False
                self.set_status("BACKUP POWER DEPLETED")
                # After emergency mode, animatronics get more aggressive
                for anim in self.animatronics:
                    anim.mood = "hunting"
                    anim.hunting_mode = True
                    anim.hunting_timer = 30
                    anim.adaptive_aggro += 0.3
            return

        # Camera power drain (no heat mechanic - cameras just drain power when open)
        # Power drain happens in the power system update below

        # Scale drain based on night length - gentler scaling
        # Default is 60 seconds/hour, scale from 0.7 to 1.3 across the range
        speed_ratio = self.game_state.seconds_per_hour / 60.0
        speed_multiplier = 0.5 + (speed_ratio * 0.5)  # Ranges from 0.75 (at 15s) to 1.25 (at 180s)

        # Deterministic power surges at fixed times
        minute_in_hour = self.game_state.minutes_elapsed % 60
        surge_active = (15 <= minute_in_hour <= 17) or (30 <= minute_in_hour <= 32) or (45 <= minute_in_hour <= 47)
        surge_multiplier = 1.35 if surge_active else 1.0
        self.power_usage["surge"] = surge_multiplier
        
        diff_multiplier = self.difficulty
        drain_base = self.power.base_drain * speed_multiplier * surge_multiplier * diff_multiplier
        drain_doors = 0.0
        drain_lights = 0.0
        drain_cams = 0.0
        drain = drain_base
        if self.office.door_left_closed or self.office.door_right_closed:
            drain_doors = self.power.door_drain * speed_multiplier * surge_multiplier * diff_multiplier
            drain += drain_doors
        if self.office.light_on:
            drain_lights = self.power.light_drain * speed_multiplier * surge_multiplier * diff_multiplier
            drain += drain_lights
        if self.office.cams_open:
            drain_cams = self.power.cam_drain * speed_multiplier * surge_multiplier * diff_multiplier
            drain += drain_cams

        self.power_usage["base"] = drain_base
        self.power_usage["doors"] = drain_doors
        self.power_usage["lights"] = drain_lights
        self.power_usage["cams"] = drain_cams

        self.power.current -= drain * dt
        if self.power.current < 0:
            self.power.current = 0
        
        # Screen shake on critical power
        if 0 < self.power.current < 10:
            self.screen_shake = 1 + (10 - self.power.current) * 0.1

    def update_time(self, dt):
        """Update in-game time"""
        if self.game_state.state != "playing":
            return
        # advance time by minutes using configured seconds_per_hour
        seconds_per_minute = max(0.01, self.game_state.seconds_per_hour / 60.0)
        self.game_state.hour_timer += dt
        # increment minutes as many as passed
        while self.game_state.hour_timer >= seconds_per_minute:
            self.game_state.hour_timer -= seconds_per_minute
            self.game_state.minutes_elapsed += 1

            # Win condition: reached 6 AM (6 hours after 12:00)
            if self.game_state.minutes_elapsed >= 6 * 60:
                self.calculate_performance_score()
                self.game_state.state = "win"
                self.determine_ending()
                self.assets.play_sound("bell_6am")
                self.assets.stop_music()

                # Save high score if it's better
                night_key = self.game_state.night
                if night_key not in self.high_scores or self.performance_score > self.high_scores[night_key]:
                    self.high_scores[night_key] = self.performance_score
                
                if (self.game_state.night < 5 and
                        self.game_state.night + 1 > self.game_state.max_night_unlocked):
                    self.game_state.max_night_unlocked = self.game_state.night + 1
                    self.save_progress()
                break

    def update_animatronics(self, dt):
        """Update all animatronics with advanced AI coordination"""
        # First pass: update each animatronic
        for anim in self.animatronics:
            anim.update(dt, self.game_state, self.difficulty)
        
        # Second pass: AI coordination and communication
        self.coordinate_animatronics(dt)
        
        # Third pass: check for attacks and blocked behaviors
        for anim in self.animatronics:
            # Check if animatronic is adjacent to office (West Hall, East Hall, or Supply Closet on left side)
            is_adjacent_to_office = anim.room in get_neighbors("Office")
            
            if is_adjacent_to_office:
                # Determine which door(s) they're trying to pressure based on their position
                if anim.room == "West Hall":
                    door_closed = self.office.door_left_closed
                    pressure_left = True
                    pressure_right = False
                elif anim.room == "East Hall":
                    door_closed = self.office.door_right_closed
                    pressure_left = False
                    pressure_right = True
                else:
                    door_closed = self.office.door_left_closed or self.office.door_right_closed
                    pressure_left = True
                    pressure_right = True

                if door_closed:
                    anim.hallway_timer = 0.0
                    anim.hallway_block_timer += dt
                    pressure = 3.2 * self.difficulty
                    
                    if pressure_left:
                        self.office.door_left_health = max(0.0, self.office.door_left_health - pressure * dt)
                        if self.office.door_left_health <= 0 and self.office.door_left_jam_timer <= 0:
                            self.break_door("left")
                    if pressure_right:
                        self.office.door_right_health = max(0.0, self.office.door_right_health - pressure * dt)
                        if self.office.door_right_health <= 0 and self.office.door_right_jam_timer <= 0:
                            self.break_door("right")
                    
                    # If blocked too long, they get frustrated and leave temporarily
                    if anim.hallway_block_timer >= 3.0:
                        neighbors = [r for r in get_neighbors(anim.room) if r != "Office"]
                        if neighbors:
                            anim.last_room = anim.room
                            anim.room = neighbors[anim.block_count % len(neighbors)]
                            anim.target_x, anim.target_y = room_position(anim.room, WINDOW_WIDTH, WINDOW_HEIGHT)
                            anim.x = anim.target_x
                            anim.y = anim.target_y
                            anim.retreat_timer = 8.0  # Stay away for 8 seconds
                            anim.retreat_target = anim.room
                            anim.hallway_block_timer = 0.0
                else:
                    # Door is open, can try to enter
                    anim.hallway_timer += dt
                    anim.hallway_block_timer = 0.0
                    side = anim.attack_side
                    office_count = sum(1 for a in self.animatronics if a.room == "Office")
                    same_side_in_office = any(a.room == "Office" and a.attack_side == side for a in self.animatronics)
                    can_enter = (
                        anim.hallway_timer >= anim.hallway_entry_delay and
                        self.side_entry_cooldown.get(side, 0.0) <= 0.0 and
                        not same_side_in_office and
                        office_count < self.max_office_attackers and
                        self.jam_grace_timer <= 0.0 and
                        self.overload_grace_timer <= 0.0
                    )
                    if can_enter:
                        anim.room = "Office"
                        anim.target_x, anim.target_y = room_position("Office", WINDOW_WIDTH, WINDOW_HEIGHT)
                        anim.hallway_timer = 0.0
                        anim.attack_windup = 0.0
                        self.side_entry_cooldown[side] = self.entry_cooldown_seconds
                        self.last_office_entry_time[side] = time.time()
                        self.log_event(f"{anim.name} entered Office")
            else:
                anim.hallway_timer = 0.0
                anim.hallway_block_timer = 0.0

            # Check if animatronic was blocked by a door
            anim.get_blocked_side(self.office)
            # Check if animatronic should attack (windup required)
            # But only if player isn't hiding!
            if anim.room == "Office" and anim.try_attack(self.office) and not self.current_safe_spot:
                anim.attack_windup += dt
                required = max(0.45, (anim.attack_windup_required / max(0.8, self.difficulty)) - (self.game_state.night - 1) * 0.1)
                if anim.attack_windup >= required:
                    self.jumpscare.killer = anim.name
                    self.jumpscare.active = True
                    self.jumpscare.timer = 0
                    self.game_state.state = "jumpscare"
                    self.add_screen_shake(15, 2.0)
                    self.add_color_overlay((255, 0, 0, 150), 2.0)
                    self.assets.play_sound("jumpscare")
                    self.assets.stop_music()
                    self.log_event(f"{anim.name} attacked")
                    break
            else:
                anim.attack_windup = 0.0

    def coordinate_animatronics(self, dt):
        """AI coordination: animatronics communicate and plan coordinated attacks"""
        if len(self.animatronics) < 2:
            return
        
        # Check if any animatronic is in hunting mode and communicate
        hunters = [a for a in self.animatronics if a.hunting_mode]
        
        if hunters:
            # Share intelligence: if one is hunting, spread the target
            target_room = hunters[0].hunt_target_room
            for anim in self.animatronics:
                if not anim.hunting_mode and anim.communication_cooldown <= 0:
                    anim.hunting_mode = True
                    anim.hunt_target_room = target_room
                    anim.mood = "hunting"
                    anim.hunting_timer = 10.0
                    anim.communication_cooldown = 6.0
        
        # Predict player door preference and adapt strategy
        for anim in self.animatronics:
            if anim.player_action_memory:
                recent_actions = [a for a in anim.player_action_memory if time.time() - a["time"] < 60]
                if len(recent_actions) > 2:
                    # Player is blocking a specific side repeatedly
                    blocked_sides = [a["side"] for a in recent_actions[-5:]]
                    if blocked_sides.count("left") > blocked_sides.count("right"):
                        if anim.attack_side != "vent":
                            anim.attack_side = "right"  # Try to attack from other side
                    elif blocked_sides.count("right") > blocked_sides.count("left"):
                        if anim.attack_side != "vent":
                            anim.attack_side = "left"
        
        # Pack hunting behavior: multiple animatronics moving together
        if not hasattr(self, 'coordination_timer'):
            self.coordination_timer = 0
        at_office = [a for a in self.animatronics if a.room == "Office"]
        if self.coordination_timer > 0:
            self.coordination_timer -= dt
        if len(at_office) >= 2 and self.coordination_timer <= 0 and self.game_state.minutes_elapsed >= 60:
            # Increase mood and aggression for coordinated attack
            for anim in at_office:
                anim.mood = "aggressive"
                anim.adaptive_aggro += 0.10
                anim.block_count += 1  # simulate frustration from failed attacks
            self.coordination_timer = 12.0
    
    def update_environmental_events(self, dt):
        """Trigger random environmental events to add variety and tension"""
        self.environmental_event_timer += dt
        
        # Trigger events at random intervals
        if self.environmental_event_timer >= self.next_event_time:
            self.trigger_random_event()
            self.environmental_event_timer = 0
            self.next_event_time = self.rng.uniform(20, 45)  # Next event in 20-45 seconds
        
        # Update light flickering
        if self.game_state.lights_flickering:
            self.game_state.flicker_timer += dt
            if self.game_state.flicker_timer >= self.rng.uniform(2, 4):
                self.game_state.lights_flickering = False
                self.game_state.flicker_timer = 0
        
        # Update hallucination mode
        if self.hallucination_timer > 0:
            self.hallucination_timer -= dt
            if self.hallucination_timer <= 0:
                self.hallucination_mode = False
    
    def trigger_random_event(self):
        """Trigger a random environmental event"""
        events = [
            "lights_flicker",
            "temperature_drop",
            "phantom_sound",
            "camera_glitch",
            "ventilation_block",
            "power_surge",
            "hallucination",
            "door_malfunction"
        ]
        
        # Weight events based on night and current situation
        night = self.game_state.night
        minutes = self.game_state.minutes_elapsed
        
        # More intense events on later nights
        if night >= 3:
            events.extend(["power_drain", "system_overload"])
        if night >= 4:
            events.extend(["blackout_threat", "animatronic_rush"])
        
        event = self.rng.choice(events)
        
        if event == "lights_flicker":
            self.game_state.lights_flickering = True
            self.game_state.flicker_timer = 0
            self.add_screen_shake(3, 0.3)
            self.add_color_overlay((255, 255, 200, 80), 0.5)
            self.log_event("Lights flickering...")
        
        elif event == "temperature_drop":
            self.game_state.temperature -= self.rng.randint(5, 15)
            self.add_color_overlay((100, 150, 255, 60), 2.0)
            if self.game_state.temperature < 50:
                self.log_event("Temperature critical!")
                # Cold affects animatronic behavior (slower but more aggressive)
                for anim in self.animatronics:
                    anim.move_interval *= 1.2
                    anim.adaptive_aggro += 0.1
            else:
                self.log_event(f"Temperature dropped to {self.game_state.temperature}°F")
        
        elif event == "phantom_sound":
            fake_rooms = ["Cafeteria", "Hallway", "Gym", "Library", "Bathrooms"]
            fake_room = self.rng.choice(fake_rooms)
            self.game_state.phantom_sounds.append({
                'location': fake_room,
                'time': time.time(),
                'type': 'phantom'
            })
            self.log_event(f"Strange noise from {fake_room}")
        
        elif event == "camera_glitch":
            if self.office.cams_open:
                self.office.cam_flash = 1.5
                self.add_screen_shake(5, 0.4)
                # Create static particles
                for _ in range(15):
                    x = self.rng.randint(0, self.game_state.width)
                    y = self.rng.randint(0, self.game_state.height)
                    self.add_particle_burst(x, y, 3, (200, 200, 255), (0.5, 2))
                self.log_event("Camera system glitching!")
        
        elif event == "ventilation_block":
            if not self.game_state.ventilation_blocked:
                self.game_state.ventilation_blocked = True
                self.log_event("Ventilation blocked - power drain increased!")
                self.power.base_drain *= 1.3
        
        elif event == "power_surge":
            surge_amount = self.rng.uniform(5, 15)
            self.power.current = max(0, self.power.current - surge_amount)
            self.add_screen_shake(8, 0.5)
            self.add_color_overlay((255, 255, 100, 120), 0.3)
            # Electric sparks
            for _ in range(20):
                x = self.rng.randint(0, self.game_state.width)
                y = self.rng.randint(0, 100)
                self.add_particle_burst(x, y, 5, (255, 255, 100), (2, 5))
            self.log_event(f"Power surge! Lost {int(surge_amount)}% power")
        
        elif event == "hallucination":
            if night >= 3:
                self.hallucination_mode = True
                self.hallucination_timer = self.rng.uniform(10, 20)
                self.add_color_overlay((180, 100, 255, 100), 15.0)
                self.add_screen_shake(2, 15.0)
                self.log_event("You feel disoriented...")
        
        elif event == "door_malfunction":
            if self.rng.random() < 0.5:
                self.office.door_left_health = max(20, self.office.door_left_health - 25)
                self.log_event("Left door malfunctioning!")
            else:
                self.office.door_right_health = max(20, self.office.door_right_health - 25)
                self.log_event("Right door malfunctioning!")
        
        elif event == "power_drain" and night >= 3:
            # Gradual power drain over time
            drain_amount = self.rng.uniform(2, 5)
            self.power.current = max(0, self.power.current - drain_amount)
            self.log_event("Unusual power drain detected")
        
        elif event == "animatronic_rush" and night >= 4:
            # All animatronics become aggressive temporarily
            for anim in self.animatronics:
                anim.mood = "aggressive"
                anim.hunting_mode = True
                anim.hunting_timer = self.rng.uniform(15, 25)
                anim.hunt_target_room = "Office"
            self.add_screen_shake(6, 1.0)
            self.add_color_overlay((255, 50, 50, 100), 2.0)
            self.log_event("WARNING: Unusual activity detected!")
    
    def update_phantom_sounds(self, dt):
        """Update and clean up phantom sound events"""
        current_time = time.time()
        self.game_state.phantom_sounds = [
            sound for sound in self.game_state.phantom_sounds
            if current_time - sound['time'] < 5  # Remove after 5 seconds
        ]
    
    def calculate_performance_score(self):
        """Calculate player performance score for the night"""
        score = 1000  # Base score
        
        # Bonus for efficient power usage
        power_efficiency = (self.power.current / self.power.max) * 100
        score += int(power_efficiency * 2)
        
        # Penalty for excessive door usage
        score -= (self.total_door_closes * 5)
        
        # Bonus for camera usage (awareness)
        score += min(self.total_camera_checks * 10, 300)
        
        # Bonus for perfect blocks
        score += (self.perfect_blocks * 50)
        
        # Penalty for failed blocks
        score -= (self.failed_blocks * 30)
        
        # Night multiplier
        score = int(score * (1.0 + (self.game_state.night - 1) * 0.25))
        
        # Difficulty multiplier
        score = int(score * self.difficulty)
        
        self.performance_score = max(0, score)
    
    def determine_ending(self):
        """Determine the ending based on performance and night"""
        night = self.game_state.night
        score = self.performance_score
        power_left = self.power.current
        
        if night == 5 and score >= 2000:
            self.set_status("6 AM! PERFECT NIGHT - You've mastered survival!")
            self.game_state.ending_type = "perfect"
        elif night == 5:
            self.set_status("6 AM! You survived all nights - VICTORY!")
            self.game_state.ending_type = "victory"
        elif power_left > 50 and score >= 1500:
            self.set_status(f"6 AM! Flawless performance on Night {night}!")
            self.game_state.ending_type = "flawless"
        elif power_left < 10:
            self.set_status(f"6 AM! You barely made it through Night {night}...")
            self.game_state.ending_type = "barely"
        else:
            self.set_status(f"6 AM! You survived Night {night}!")
            self.game_state.ending_type = "standard"
    

    def update_threat_assessment(self, dt):
        """Calculate real-time threat level 0-100"""
        threat = 0
        
        # Animatronics in office or hallway = major threat
        for anim in self.animatronics:
            if anim.room == "Office":
                threat += 30
            elif anim.room == "Hallway":
                threat += 15
            elif anim._distance_to_room(anim.room, "Office") <= 2:
                threat += 8
        
        # Low power = threat
        if self.power.current < 20:
            threat += 20
        elif self.power.current < 50:
            threat += 10
        
        # Door health = threat
        avg_door_health = (self.office.door_left_health + self.office.door_right_health) / 2
        if avg_door_health < 30:
            threat += 15
        
        # Both doors open = vulnerability
        if not self.office.door_left_closed and not self.office.door_right_closed:
            threat += 10
        
        # Emergency mode = maximum threat
        if self.power.outage and self.power.emergency_mode:
            threat += 30
        
        self.threat_level = min(100, threat)
    
    def update_audio_system(self, dt):
        """Update footstep sounds and audio cues"""
        current_time = time.time()
        
        # Clean up old footsteps
        self.footstep_sounds = [
            sound for sound in self.footstep_sounds
            if current_time - sound['time'] < 3
        ]
        
        # Add footsteps for moving animatronics
        for anim in self.animatronics:
            if anim.room != anim.last_room:
                # Animatronic moved!
                if anim.special_ability != "silent_stalker":
                    self.footstep_sounds.append({
                        'name': anim.name,
                        'location': anim.room,
                        'time': current_time,
                        'intensity': anim.adaptive_aggro
                    })
                    
                    # Log if close enough
                    if anim._distance_to_room(anim.room, "Office") <= 2:
                        direction = "nearby" if anim.room == "Hallway" else anim.room
                        self.log_event(f"Footsteps from {direction}", True)

    def update(self, dt):
        """Main update loop"""
        self.noise_phase += dt * 5.0
        if self.game_state.state == "splash":
            self.update_splash(dt)
            return
        if self.game_state.state == "paused":
            return
        if self.game_state.state == "menu":
            return

        if self.game_state.state == "anti_cheat":
            self.anti_cheat_timer += dt
            if self.anti_cheat_timer >= 2.0 and not self.anti_cheat_pending:
                self.jumpscare.killer = "Mr Hall"
                self.jumpscare.active = True
                self.jumpscare.timer = 0
                self.game_state.state = "jumpscare"
                self.assets.play_sound("jumpscare")
                self.anti_cheat_pending = True
            return

        if self.game_state.state == "anti_cheat_message":
            return

        if self.game_state.state == "intro":
            self.update_intro(dt)
            # keep updating visual effects (optional)
            self.update_office_effects(dt)
            return

        if self.game_state.state == "tutorial":
            self.update_tutorial(dt)
            return

        if self.game_state.state == "playing":
            # Decrement safe spot protection timer
            if self.current_safe_spot:
                self.safe_spot_duration = max(0, self.safe_spot_duration - dt)
                # Exit safe spot when timer runs out
                if self.safe_spot_duration <= 0:
                    self.current_safe_spot = None
            
            self.update_power(dt)
            self.update_time(dt)
            self.update_animatronics(dt)
            self.update_environmental_events(dt)
            self.update_phantom_sounds(dt)
            self.update_screen_effects(dt)
            self.update_threat_assessment(dt)
            self.update_audio_system(dt)
        elif self.game_state.state == "jumpscare":
            self.update_screen_effects(dt)
            self.jumpscare.timer += dt
            if self.jumpscare.timer > self.jumpscare.duration:
                self.jumpscare.timer = self.jumpscare.duration
                if self.anti_cheat_pending:
                    self.game_state.state = "anti_cheat_message"

        self.update_office_effects(dt)

    def update_splash(self, dt):
        """Update splash screen timing"""
        current = self.splash_sequence[self.splash_stage]
        total = current["fade_in"] + current["hold"] + current["fade_out"]
        self.splash_timer += dt
        if self.splash_timer >= total:
            self.splash_timer = 0.0
            self.splash_stage += 1
            if self.splash_stage >= len(self.splash_sequence):
                self.enter_menu()

    def update_intro(self, dt):
        """Update intro message sequence (fade in/out per message)"""
        if self.game_state.state != "intro":
            return

        self.intro_timer += dt
        durations = self.intro_message_durations
        if len(durations) != len(self.intro_messages):
            durations = [self.intro_message_duration] * len(self.intro_messages)
        # determine current message based on cumulative durations
        elapsed = 0.0
        index = 0
        for d in durations:
            if self.intro_timer < elapsed + d:
                break
            elapsed += d
            index += 1
        self.intro_index = index

        # If finished all messages, show tutorial (only on Night 1)
        if self.intro_index >= len(self.intro_messages):
            if self.game_state.night == 1:
                # Show tutorial slideshow
                self.game_state.state = "tutorial"
                self.tutorial_index = 0
                self.tutorial_timer = 0.0
            else:
                # Skip tutorial on other nights, go straight to playing
                ambience_key = f"ambience_n{self.game_state.night}"
                self.assets.play_music(ambience_key)
                self.game_state.state = "playing"
                self.game_state.start_time = time.time()
                self.game_state.hour_timer = 0
                self.game_state.minutes_elapsed = 0
            # reset intro trackers
            self.intro_messages = []
            self.intro_index = 0
            self.intro_timer = 0.0
            self.intro_message_durations = []

    def draw_splash(self):
        """Draw splash screen with fade in/out"""
        current = self.splash_sequence[self.splash_stage]
        splash = self.assets.get_image(current["key"])
        if splash:
            scaled = pygame.transform.scale(splash, (self.game_state.width, self.game_state.height))
            self.screen.blit(scaled, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
            text = self.font_large.render("FIVE NIGHTS AT MR INGLES'S", True, (200, 200, 255))
            rect = text.get_rect(center=(self.game_state.width // 2, self.game_state.height // 2))
            self.screen.blit(text, rect)

        t = self.splash_timer
        if t <= current["fade_in"]:
            alpha = t / max(0.001, current["fade_in"])
        elif t <= current["fade_in"] + current["hold"]:
            alpha = 1.0
        else:
            alpha = 1.0 - ((t - current["fade_in"] - current["hold"]) / max(0.001, current["fade_out"]))

        fade_surface = pygame.Surface((self.game_state.width, self.game_state.height))
        fade_surface.set_alpha(int(255 * (1.0 - self.clamp(alpha, 0.0, 1.0))))
        fade_surface.fill((0, 0, 0))
        self.screen.blit(fade_surface, (0, 0))

    def draw_intro(self):
        """Draw the fading intro messages"""
        # dark background
        self.screen.fill((0, 0, 0))

        if not self.intro_messages:
            return

        durations = self.intro_message_durations
        if len(durations) != len(self.intro_messages):
            durations = [self.intro_message_duration] * len(self.intro_messages)
        total = durations[self.intro_index] if self.intro_index < len(durations) else self.intro_message_duration
        # local time within current message
        elapsed = sum(durations[:self.intro_index])
        t = self.intro_timer - elapsed
        if t < 0:
            t = 0.0

        # fade timings
        # fade timings as fractions of total duration
        fade_in = total * 0.2
        hold = total * 0.6
        fade_out = max(0.0, total - (fade_in + hold))

        if t < fade_in:
            alpha = t / fade_in
        elif t < (fade_in + hold):
            alpha = 1.0
        elif fade_out > 0:
            alpha = 1.0 - ((t - fade_in - hold) / fade_out)
        else:
            alpha = 0.0

        alpha = self.clamp(alpha, 0.0, 1.0)
        color_val = int(255 * alpha)

        msg = self.intro_messages[self.intro_index] if self.intro_index < len(self.intro_messages) else ""
        # choose a prominent font; use font_large
        text_surf = self.font_large.render(msg, True, (color_val, color_val, color_val))
        text_rect = text_surf.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.45)))
        # draw a subtle drop shadow for readability
        shadow = self.font_large.render(msg, True, (10, 10, 10))
        shadow_rect = shadow.get_rect(center=(text_rect.centerx + 4, text_rect.centery + 4))
        shadow.set_alpha(int(200 * alpha))
        self.screen.blit(shadow, shadow_rect)
        text_surf.set_alpha(int(255 * alpha))
        self.screen.blit(text_surf, text_rect)

    def update_tutorial(self, dt):
        """Update tutorial slideshow"""
        if self.game_state.state != "tutorial":
            return
        
        self.tutorial_timer += dt
        
        # Advance to next slide
        if self.tutorial_timer >= self.tutorial_slide_duration:
            self.tutorial_index += 1
            self.tutorial_timer = 0.0
        
        # If tutorial finished, start actual gameplay
        if self.tutorial_index >= len(self.tutorial_slides):
            ambience_key = f"ambience_n{self.game_state.night}"
            self.assets.play_music(ambience_key)
            self.game_state.state = "playing"
            self.game_state.start_time = time.time()
            self.game_state.hour_timer = 0
            self.game_state.minutes_elapsed = 0
            self.tutorial_index = 0
            self.tutorial_timer = 0.0

    def draw_tutorial(self):
        """Draw tutorial slideshow"""
        # Dark background
        self.screen.fill((5, 5, 15))
        
        if self.tutorial_index >= len(self.tutorial_slides):
            return
        
        slide = self.tutorial_slides[self.tutorial_index]
        
        # Fade effect
        fade_in_time = 0.5
        fade_out_time = self.tutorial_slide_duration - 0.5
        
        if self.tutorial_timer < fade_in_time:
            alpha_ratio = self.tutorial_timer / fade_in_time
        elif self.tutorial_timer > fade_out_time:
            alpha_ratio = 1.0 - (self.tutorial_timer - fade_out_time) / 0.5
        else:
            alpha_ratio = 1.0
        
        # Gradient background (dark to darker)
        for y in range(self.game_state.height):
            ratio = y / self.game_state.height
            r = int(10 * (1 - ratio * 0.3))
            g = int(10 * (1 - ratio * 0.3))
            b = int(20 * (1 - ratio * 0.2))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.game_state.width, y))
        
        # Main content panel with border
        panel_width = int(self.game_state.width * 0.75)
        panel_height = int(self.game_state.height * 0.65)
        panel_x = (self.game_state.width - panel_width) // 2
        panel_y = int(self.game_state.height * 0.15)
        
        # Panel background with semi-transparency
        panel_surf = pygame.Surface((panel_width, panel_height))
        panel_surf.set_alpha(int(220 * alpha_ratio))
        panel_surf.fill((25, 35, 50))
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        # Panel border
        border_color = (100, 200, 255)
        pygame.draw.rect(self.screen, border_color, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title with glow effect
        title_text = self.font_title.render(slide["title"], True, (100, 220, 255))
        title_rect = title_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.22)))
        
        # Glow effect (draw shadow multiple times)
        for i in range(3, 0, -1):
            glow = self.font_title.render(slide["title"], True, (50, 120, 150))
            glow.set_alpha(int(100 * (3-i) * alpha_ratio / 3))
            glow_rect = glow.get_rect(center=(title_rect.centerx, title_rect.centery))
            self.screen.blit(glow, (glow_rect.x + i, glow_rect.y + i))
        
        title_text.set_alpha(int(255 * alpha_ratio))
        self.screen.blit(title_text, title_rect)
        
        # Content lines
        content_lines = slide["text"].split("\n")
        y_offset = int(self.game_state.height * 0.35)
        line_spacing = int(self.game_state.height * 0.06)  # Reduced spacing for more lines
        
        for line in content_lines:
            line_text = self.font_medium.render(line, True, (220, 220, 220))
            line_text.set_alpha(int(255 * alpha_ratio))
            line_rect = line_text.get_rect(center=(self.game_state.width // 2, y_offset))
            self.screen.blit(line_text, line_rect)
            y_offset += line_spacing
        
        # Progress bar at bottom
        progress_ratio = (self.tutorial_index + 1) / len(self.tutorial_slides)
        progress_bar_width = int(self.game_state.width * 0.6)
        progress_bar_height = 20
        progress_bar_x = (self.game_state.width - progress_bar_width) // 2
        progress_bar_y = int(self.game_state.height * 0.8)
        
        # Background bar
        pygame.draw.rect(self.screen, (40, 40, 60), (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
        # Progress bar
        pygame.draw.rect(self.screen, (100, 200, 255), (progress_bar_x, progress_bar_y, int(progress_bar_width * progress_ratio), progress_bar_height))
        # Border
        pygame.draw.rect(self.screen, (150, 200, 255), (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), 2)
        
        # Progress text
        progress_text = self.font_small.render(f"Slide {self.tutorial_index + 1} / {len(self.tutorial_slides)}", True, (150, 200, 220))
        progress_text.set_alpha(int(220 * alpha_ratio))
        progress_rect = progress_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.86)))
        self.screen.blit(progress_text, progress_rect)
        
        # Skip instruction with highlight
        skip_text = self.font_small.render("Press SPACE to skip", True, (180, 180, 200))
        skip_text.set_alpha(int(180 * alpha_ratio))
        skip_rect = skip_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.93)))
        self.screen.blit(skip_text, skip_rect)

    # =====================================================
    # DRAWING FUNCTIONS
    # =====================================================

    def draw_background(self):
        """Draw office background"""
        office_img = self.assets.get_image("office")
        if office_img:
            scaled = pygame.transform.scale(office_img, (self.game_state.width, self.game_state.height))
            self.screen.blit(scaled, (0, 0))
        else:
            self.screen.fill((12, 12, 12))

    def get_anim_sprite(self, name, is_attacking=False):
        """Get sprite for animatronic"""
        sprites = {
            "Mr Ingles": "anim_scary_ingles" if is_attacking else "anim_mr_ingles",
            "Scary Mr Ingles": "anim_scary_ingles",
            "Janitor Bot": "anim_janitor",
            "Librarian": "anim_librarian",
            "Vent Crawler": "anim_vent_crawler",
            "Mr Hall": "mr_hall_anti_cheater",
        }
        sprite_name = sprites.get(name, "mr_ingles_office")
        return self.assets.get_image(sprite_name)

    def draw_office_anim(self, anim, current_time):
        """Draw animatronic in office view"""
        # Only draw if actually in the office (not just hallway)
        if anim.room != "Office":
            return

        sprite = self.get_anim_sprite(anim.name)
        if sprite:
            wobble = math.sin(current_time * 2 + anim.x * 0.01) * 0.02
            scale = 0.4 * (self.game_state.width / 1280) * (1 + wobble)
            scaled = pygame.transform.scale(sprite, 
                (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
            rect = scaled.get_rect(center=(anim.x, anim.y + wobble * 40))
            self.screen.blit(scaled, rect)
        else:
            pygame.draw.circle(self.screen, (255, 0, 0), (int(anim.x), int(anim.y)), 25)

    def draw_office_overlays(self):
        """Draw door and light overlays"""
        # Left door
        if (self.office.door_left_closed or self.office.door_left_progress > 0.01):
            door_img = self.assets.get_image("door_left")
            if door_img:
                scale = self.game_state.height / door_img.get_height()
                scaled = pygame.transform.scale(door_img, 
                    (int(door_img.get_width() * scale), int(door_img.get_height() * scale)))
                # When progress=0 (open): x=-width, when progress=1 (closed): x=0
                x = -scaled.get_width() + scaled.get_width() * self.office.door_left_progress
                self.screen.blit(scaled, (int(x), 0))

        # Right door
        if (self.office.door_right_closed or self.office.door_right_progress > 0.01):
            door_img = self.assets.get_image("door_right")
            if door_img:
                scale = self.game_state.height / door_img.get_height()
                scaled = pygame.transform.scale(door_img,
                    (int(door_img.get_width() * scale), int(door_img.get_height() * scale)))
                slide = 1 - self.office.door_right_progress
                x = self.game_state.width - scaled.get_width() + scaled.get_width() * slide
                self.screen.blit(scaled, (int(x), 0))

        # Light dim overlay
        if self.office.light_dim > 0:
            dim_surface = pygame.Surface((self.game_state.width, self.game_state.height))
            dim_surface.set_alpha(int(255 * self.office.light_dim))
            dim_surface.fill((0, 0, 0))
            self.screen.blit(dim_surface, (0, 0))
        
        # Flashlight brightness boost - bright white overlay when light is on
        if self.office.light_on:
            brightness_boost = pygame.Surface((self.game_state.width, self.game_state.height))
            brightness_boost.set_alpha(80)  # Strong brightness boost
            brightness_boost.fill((255, 255, 255))
            self.screen.blit(brightness_boost, (0, 0))

        # Vignette
        for i in range(1, 7):
            alpha = int(255 * 0.05 * i)
            vignette = pygame.Surface((self.game_state.width, self.game_state.height))
            vignette.set_alpha(alpha)
            vignette.fill((0, 0, 0))
            pygame.draw.rect(vignette, (0, 0, 0), (10 * i, 10 * i,
                self.game_state.width - 20 * i, self.game_state.height - 20 * i), 1)
            self.screen.blit(vignette, (0, 0))

    def draw_office_view(self):
        """Draw office view with animatronics"""
        current_time = self.game_state.elapsed_time()
        for anim in self.animatronics:
            self.draw_office_anim(anim, current_time)
        self.draw_office_overlays()

    def draw_camera_feed(self):
        """Draw camera feed"""
        cam_name = self.cameras.current_camera()
        cam_key = f"cam_{cam_name.lower().replace(' ', '_')}"
        cam_img = self.assets.get_image(cam_key)

        # Camera background
        if cam_img:
            scaled = pygame.transform.scale(cam_img, (self.game_state.width, self.game_state.height))
            self.screen.blit(scaled, (0, 0))
        else:
            self.screen.fill((0, 0, 25))

        # Draw animatronics on this camera
        current_time = self.game_state.elapsed_time()
        for anim in self.animatronics:
            if anim.room == cam_name:
                sprite = self.get_anim_sprite(anim.name)
                if sprite:
                    wobble = math.sin(current_time * 2 + anim.x * 0.01) * 0.02
                    scale = 0.45 * (self.game_state.width / 1280) * (1 + wobble)
                    scaled = pygame.transform.scale(sprite,
                        (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
                    rect = scaled.get_rect(center=(anim.x, anim.y + wobble * 40))
                    self.screen.blit(scaled, rect)
                else:
                    pygame.draw.circle(self.screen, (178, 255, 255), (int(anim.x), int(anim.y)), 20)

        # Camera UI text
        cam_text = self.font_medium.render(f"CAM: {cam_name}", True, (0, 255, 255))
        self.screen.blit(cam_text, (20, 20))

        # Scanlines overlay - subtle and dim
        for y in range(0, self.game_state.height, 8):
            scanline = pygame.Surface((self.game_state.width, 1))
            scanline.set_alpha(20)  # very subtle
            scanline.fill((0, 200, 200))
            self.screen.blit(scanline, (0, y))

        # Static flash overlay
        if self.office.cam_flash > 0:
            flash_surface = pygame.Surface((self.game_state.width, self.game_state.height))
            flash_surface.set_alpha(int(255 * 0.8 * self.office.cam_flash))
            flash_surface.fill((255, 255, 255))
            self.screen.blit(flash_surface, (0, 0))

            # Random noise
            noise_surface = pygame.Surface((self.game_state.width, self.game_state.height))
            noise_surface.set_alpha(int(255 * 0.4 * self.office.cam_flash))
            for i in range(30):
                t = self.noise_phase + i * 0.21
                x = int((math.sin(t * 1.4) * 0.5 + 0.5) * self.game_state.width)
                y = int((math.sin(t * 2.1 + 0.7) * 0.5 + 0.5) * self.game_state.height)
                w = 4 + int((math.sin(t * 3.3 + 1.3) * 0.5 + 0.5) * 10)
                pygame.draw.rect(noise_surface, (0, 0, 51), (x, y, w, 2))
            self.screen.blit(noise_surface, (0, 0))
        
        # Draw faint minimap when viewing cameras
        self.draw_minimap(opacity=120)

    def draw_anims(self):
        """Draw animatronics (office or camera view)"""
        if self.office.cams_open:
            self.draw_camera_feed()
        else:
            self.draw_office_view()

    def draw_hud(self):
        """Draw heads-up display"""
        # Power indicator with bar
        power_val = int(self.power.current + 0.5)
        power_color = (255, 50, 50) if power_val <= 20 else (100, 255, 100) if power_val > 50 else (255, 200, 0)
        
        # Power bar background
        bar_width = 200
        bar_height = 20
        pygame.draw.rect(self.screen, (40, 40, 40), (20, self.game_state.height - 50, bar_width, bar_height))
        pygame.draw.rect(self.screen, power_color, (20, self.game_state.height - 50, 
                         int(bar_width * power_val / 100), bar_height))
        pygame.draw.rect(self.screen, (150, 150, 150), (20, self.game_state.height - 50, bar_width, bar_height), 2)
        
        # Power text with dark background for contrast
        power_text = self.font_small.render(f"POWER: {power_val}%", True, (255, 255, 255))
        power_rect = power_text.get_rect(topleft=(30, self.game_state.height - 47))
        pygame.draw.rect(self.screen, (0, 0, 0), (power_rect.x - 3, power_rect.y - 2, power_rect.width + 6, power_rect.height + 4))
        self.screen.blit(power_text, power_rect)
        
        # Door integrity + camera heat
        left_health = int(self.office.door_left_health + 0.5)
        right_health = int(self.office.door_right_health + 0.5)
        left_jam = int(self.office.door_left_jam_timer + 0.5)
        right_jam = int(self.office.door_right_jam_timer + 0.5)
        left_label = f"L-DOOR {left_health}%"
        right_label = f"R-DOOR {right_health}%"
        if left_jam > 0:
            left_label += f" JAM {left_jam}s"
        if right_jam > 0:
            right_label += f" JAM {right_jam}s"
        door_text = self.font_small.render(f"{left_label}  |  {right_label}", True, (200, 200, 200))
        self.screen.blit(door_text, (30, self.game_state.height - 25))

        # Camera status display
        cam_text = self.font_small.render("CAM SYSTEM", True, (200, 200, 200))
        self.screen.blit(cam_text, (30, self.game_state.height - 70))

        # Power usage breakdown
        usage_y = self.game_state.height - 110
        usage = self.power_usage
        usage_text = self.font_small.render(
            f"USAGE  Base:{usage['base']:.2f}  Doors:{usage['doors']:.2f}  Lights:{usage['lights']:.2f}  Cams:{usage['cams']:.2f}  Surge:{usage['surge']:.2f}x",
            True, (160, 200, 220))
        self.screen.blit(usage_text, (30, usage_y))

        # Time indicator with minute-by-minute display
        hours_elapsed = self.game_state.minutes_elapsed // 60
        display_hour = 12 if hours_elapsed == 0 else hours_elapsed
        minute = self.game_state.minutes_elapsed % 60
        time_color = (255, 100, 100) if hours_elapsed >= 5 else (100, 200, 255)
        time_text = self.font_medium.render(f"{display_hour:02d}:{minute:02d} AM", True, time_color)
        time_rect = time_text.get_rect(topright=(self.game_state.width - 30, 20))
        
        # Time box
        pygame.draw.rect(self.screen, (30, 30, 60), (time_rect.x - 15, time_rect.y - 10, 
                         time_rect.width + 30, time_rect.height + 20), 0)
        pygame.draw.rect(self.screen, time_color, (time_rect.x - 15, time_rect.y - 10,
                         time_rect.width + 30, time_rect.height + 20), 2)
        self.screen.blit(time_text, time_rect)

        # Night indicator with box
        night_text = self.font_small.render(f"NIGHT {self.game_state.night}", True, (200, 100, 200))
        night_rect = night_text.get_rect(topleft=(20, 20))
        pygame.draw.rect(self.screen, (40, 20, 40), (night_rect.x - 10, night_rect.y - 5,
                         night_rect.width + 20, night_rect.height + 10), 0)
        pygame.draw.rect(self.screen, (200, 100, 200), (night_rect.x - 10, night_rect.y - 5,
                         night_rect.width + 20, night_rect.height + 10), 2)
        self.screen.blit(night_text, night_rect)

        # Status message with urgency
        if self.game_state.status:
            status_color = (255, 50, 50) if "OUTAGE" in self.game_state.status else (100, 255, 100)
            status_text = self.font_medium.render(self.game_state.status, True, status_color)
            text_rect = status_text.get_rect(center=(self.game_state.width // 2, 
                int(self.game_state.height * 0.08)))
            # Add background box
            pygame.draw.rect(self.screen, (20, 20, 20), (text_rect.x - 20, text_rect.y - 10,
                             text_rect.width + 40, text_rect.height + 20), 0)
            pygame.draw.rect(self.screen, status_color, (text_rect.x - 20, text_rect.y - 10,
                             text_rect.width + 40, text_rect.height + 20), 2)
            self.screen.blit(status_text, text_rect)
        
        # Emergency mode indicator
        if self.power.outage and self.power.emergency_mode:
            emergency_time = int(self.power.emergency_timer)
            emergency_text = self.font_large.render(f"BACKUP POWER: {emergency_time}s", True, (255, 150, 0))
            emergency_rect = emergency_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.15)))
            # Pulsing effect
            pulse = math.sin(time.time() * 5) * 0.3 + 0.7
            emergency_surf = pygame.Surface((emergency_rect.width + 60, emergency_rect.height + 30))
            emergency_surf.set_alpha(int(180 * pulse))
            emergency_surf.fill((100, 50, 0))
            self.screen.blit(emergency_surf, (emergency_rect.x - 30, emergency_rect.y - 15))
            self.screen.blit(emergency_text, emergency_rect)
        
        # Hallucination mode indicator
        if self.hallucination_mode:
            halluc_text = self.font_small.render("Vision blurred...", True, (150, 150, 255))
            halluc_rect = halluc_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.92)))
            self.screen.blit(halluc_text, halluc_rect)
        
        # NEW FEATURES HUD
        # Flashlight battery indicator
        battery = int(self.office.flashlight_battery)
        battery_color = (255, 50, 50) if battery < 20 else (255, 200, 0) if battery < 50 else (100, 255, 100)
        battery_text = self.font_small.render(f"BATTERY: {battery}%", True, battery_color)
        self.screen.blit(battery_text, (30, self.game_state.height - 90))
        
        # Threat level indicator
        threat_color = (255, 50, 50) if self.threat_level > 70 else (255, 200, 0) if self.threat_level > 40 else (100, 255, 100)
        threat_text = self.font_small.render(f"THREAT: {int(self.threat_level)}%", True, threat_color)
        self.screen.blit(threat_text, (self.game_state.width - 150, self.game_state.height - 160))
        
        # Noise makers
        noise_text = self.font_small.render(f"NOISE MAKERS: {self.office.noise_maker_charges}", True, (200, 200, 255))
        self.screen.blit(noise_text, (self.game_state.width - 200, self.game_state.height - 180))
        
        # Barricade levels
        if self.office.barricade_left > 0 or self.office.barricade_right > 0:
            barricade_text = self.font_small.render(f"BARRICADES: L{self.office.barricade_left} R{self.office.barricade_right}", True, (200, 255, 200))
            self.screen.blit(barricade_text, (self.game_state.width - 230, self.game_state.height - 200))
        
        # Combo counter
        if self.combo_blocks > 0:
            combo_text = self.font_large.render(f"COMBO x{self.combo_blocks}!", True, (255, 255, 100))
            combo_rect = combo_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.20)))
            self.screen.blit(combo_text, combo_rect)
        
        # Safe spot indicator
        if self.current_safe_spot:
            safe_time = int(self.safe_spot_duration)
            safe_text = self.font_medium.render(f"HIDING IN {self.current_safe_spot.upper()} - {safe_time}s", True, (100, 255, 100))
            safe_rect = safe_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.50)))
            self.screen.blit(safe_text, safe_rect)

        # Controls help moved to above (door integrity display replaced it)
        # Draw minimap when not using cameras
        if not self.office.cams_open:
            self.draw_minimap()

        # Threat meters removed for better suspense

        # Night progress bar
        progress = min(1.0, self.game_state.minutes_elapsed / 360.0)
        bar_x = (self.game_state.width - 300) // 2
        bar_y = self.game_state.height - 85
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, 300, 10))
        pygame.draw.rect(self.screen, (80, 200, 120), (bar_x, bar_y, int(300 * progress), 10))
        pygame.draw.rect(self.screen, (120, 120, 120), (bar_x, bar_y, 300, 10), 1)

        # Controls overlay (toggle H)
        if self.show_controls:
            cx = 20
            cy = 80
            lines = [
                "CONTROLS",
                "Q/E: Doors",
                "F: Flashlight",
                "TAB: Cameras",
                "1-6: Switch Cam",
                "--- NEW ABILITIES ---",
                "B: Barricade Door",
                "N: Noise Maker",
                "V: Ventilation",
                "C: Safe Spot",
                "H: Toggle Help",
                "ESC/P: Pause",
            ]
            for i, line in enumerate(lines):
                txt = self.font_small.render(line, True, (170, 200, 220) if i == 0 or i == 5 else (150, 180, 200))
                self.screen.blit(txt, (cx, cy + i * 16))

    def draw_noise_maker_menu(self):
        """Draw noise maker room selection menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.game_state.width, self.game_state.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("SELECT ROOM FOR NOISE MAKER", True, (255, 200, 100))
        title_rect = title.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.15)))
        self.screen.blit(title, title_rect)
        
        # Room options in grid
        cols = 2
        start_y = int(self.game_state.height * 0.30)
        start_x = int(self.game_state.width * 0.2)
        
        self.noise_maker_buttons = {}  # Store for click detection
        
        for i, room in enumerate(self.noise_maker_rooms):
            row = i // cols
            col = i % cols
            x = start_x + col * int(self.game_state.width * 0.4)
            y = start_y + row * 70
            
            # Room button
            button_color = (100, 150, 255)
            button_rect = pygame.Rect(x, y, 300, 50)
            self.noise_maker_buttons[i] = button_rect  # Store for click detection
            
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, (200, 200, 255), button_rect, 3)
            
            # Room text with number
            room_text = self.font_small.render(f"{i+1}. {room}", True, (255, 255, 255))
            text_rect = room_text.get_rect(center=(x + 150, y + 25))
            self.screen.blit(room_text, text_rect)
        
        # Instructions
        inst_text = self.font_small.render("Press 1-7, Click a room, or ESC to cancel", True, (200, 255, 200))
        inst_rect = inst_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.85)))
        self.screen.blit(inst_text, inst_rect)
        
        # Charges left
        charges_text = self.font_small.render(f"Charges: {self.office.noise_maker_charges}", True, (255, 255, 100))
        self.screen.blit(charges_text, (20, self.game_state.height - 50))

    def draw_anti_cheat_warning(self):
        """Draw anti-cheat warning overlay with fading text."""
        self.draw_background()

        # Draw Mr Hall in the office, staring
        sprite = self.get_anim_sprite("Mr Hall", is_attacking=False)
        if sprite:
            base_scale = 0.7 * (self.game_state.width / 1280)
            scaled = pygame.transform.scale(
                sprite,
                (int(sprite.get_width() * base_scale), int(sprite.get_height() * base_scale))
            )
            rect = scaled.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.60)))
            self.screen.blit(scaled, rect)

        t = self.anti_cheat_timer
        duration = 2.0
        fade = max(0.0, min(1.0, t / duration))
        alpha = int(255 * (1.0 - abs(fade - 0.5) * 2.0))

        overlay = pygame.Surface((self.game_state.width, self.game_state.height))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        text = "MR. HALL WAS SUMMONED. COWER IN FEAR."
        text_surf = self.font_medium.render(text, True, (255, 80, 80))
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(self.game_state.width // 2, self.game_state.height // 2))
        self.screen.blit(text_surf, rect)

    def draw_anti_cheat_message(self):
        """Draw anti-cheat black screen message."""
        self.screen.fill((0, 0, 0))
        lines = [
            "WE DON'T LIKE CHEATERS.",
            "PLAY THE GAME NORMALLY, WITHOUT ABUSING REFLEXES.",
            "PRESS M TO RETURN TO MENU",
        ]
        for i, line in enumerate(lines):
            color = (255, 255, 255) if i < 2 else (200, 255, 200)
            text = self.font_medium.render(line, True, color)
            rect = text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.40) + i * 50))
            self.screen.blit(text, rect)

    def draw_menu(self):
        """Draw main menu"""
        # Draw background image if available, otherwise use gradient
        bg_img = self.assets.get_image("menu_background")
        if bg_img:
            scaled_bg = pygame.transform.scale(bg_img, (self.game_state.width, self.game_state.height))
            self.screen.blit(scaled_bg, (0, 0))
        else:
            # Fallback to gradient if no background image
            time_offset = time.time() * 0.5
            color_shift = math.sin(time.time() * 0.5) * 30
            for y in range(self.game_state.height):
                ratio = y / self.game_state.height
                wave = math.sin(time_offset + ratio * 3) * 0.1
                r = int(self.clamp(10 + 35 * ratio + wave * 20 + color_shift * 0.3, 0, 255))
                g = int(self.clamp(10 + 15 * ratio + color_shift * 0.1, 0, 255))
                b = int(self.clamp(50 + 25 * ratio + wave * 10 + color_shift * 0.2, 0, 255))
                pygame.draw.line(self.screen, (r, g, b), (0, y), (self.game_state.width, y))

        # Pulsing glow effect behind title
        pulse = math.sin(time.time() * 2) * 0.2 + 0.8
        glow_color = (int(100 * pulse), int(255 * pulse), int(255 * pulse))
        
        # Title image (fallback to text if missing)
        title_img = self.assets.get_image("title")
        if title_img:
            # pulsing scale animation for title
            pulse_scale = math.sin(time.time() * 1.5) * 0.08 + 1.0
            target_w = int(self.game_state.width * 1.0 * pulse_scale)
            scale = target_w / title_img.get_width()
            target_h = int(title_img.get_height() * scale)
            # allow massive height (up to 60% of screen)
            max_h = int(self.game_state.height * 0.60)
            if target_h > max_h:
                scale = max_h / title_img.get_height()
                target_h = int(title_img.get_height() * scale)
                target_w = int(title_img.get_width() * scale)
            scaled = pygame.transform.smoothscale(title_img, (target_w, target_h))
            rect = scaled.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.25)))
            # glowing aura behind title
            glow_alpha = int(100 * (math.sin(time.time() * 2) * 0.3 + 0.5))
            self.screen.blit(scaled, rect)
        else:
            # Glow shadow effect
            shadow_color = (int(30 * pulse), int(80 * pulse), int(100 * pulse))
            shadow = self.font_title.render("FIVE NIGHTS", True, shadow_color)
            shadow2 = self.font_title.render("AT MR INGLES'S", True, shadow_color)
            shadow_rect = shadow.get_rect(center=(self.game_state.width // 2 + 3, int(self.game_state.height * 0.15) + 3))
            shadow_rect2 = shadow2.get_rect(center=(self.game_state.width // 2 + 3, int(self.game_state.height * 0.25) + 3))
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(shadow2, shadow_rect2)

            # Title with glow
            title = self.font_title.render("FIVE NIGHTS", True, glow_color)
            title2 = self.font_title.render("AT MR INGLES'S", True, glow_color)
            title_rect = title.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.15)))
            title2_rect = title2.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.25)))
            self.screen.blit(title, title_rect)
            self.screen.blit(title2, title2_rect)

        # Night selection buttons with animations
        button_width = 110
        button_height = 70
        button_spacing = 145
        start_x = self.game_state.width // 2 - (button_spacing * 2) - button_width // 2
        button_y = int(self.game_state.height * 0.42)
        
        self.night_buttons = {}  # Store for click detection

        for night in range(1, 6):
            button_x = start_x + (night - 1) * button_spacing
            is_available = night <= self.game_state.max_night_unlocked
            is_locked = night > self.game_state.max_night_unlocked

            # Bobbing animation with enhanced effects
            bob = math.sin(time.time() * 2 + night) * 5 if is_available else 0
            button_y_actual = button_y + bob

            # Store button rect for click detection (use base y, not animated)
            self.night_buttons[night] = pygame.Rect(button_x, button_y, button_width, button_height)

            # Button background with gradient
            if is_available:
                # color pulse based on night
                color_pulse = math.sin(time.time() * 2 + night * 0.5) * 30 + 20
                button_color = (int(20 + color_pulse * 0.2), int(150 - color_pulse * 0.1), int(220 + color_pulse * 0.3))
                border_color = (int(100 + color_pulse * 0.3), int(255), int(255))
                text_color = (255, 255, 255)
                # Enhanced glow effect
                glow_intensity = int(150 + math.sin(time.time() * 3 + night) * 50)
                glow_rect = pygame.Rect(button_x - 5, button_y_actual - 5, button_width + 10, button_height + 10)
                glow_surface = pygame.Surface((button_width + 10, button_height + 10))
                glow_surface.set_alpha(glow_intensity // 3)
                glow_surface.fill((100, 200, 255))
                self.screen.blit(glow_surface, glow_rect)
                pygame.draw.rect(self.screen, (int(20 + color_pulse * 0.5), int(100 + color_pulse * 0.2), int(150 + color_pulse * 0.3)), glow_rect, 2)
            else:
                button_color = (40, 40, 80)
                border_color = (70, 70, 120)
                text_color = (80, 80, 140)

            pygame.draw.rect(self.screen, button_color, (button_x, button_y_actual, button_width, button_height))
            pygame.draw.rect(self.screen, border_color, (button_x, button_y_actual, button_width, button_height), 3)

            # Night text with shadow
            night_shadow = self.font_button.render(str(night), True, (0, 0, 0))
            night_shadow_rect = night_shadow.get_rect(center=(button_x + button_width // 2 + 2, button_y_actual + button_height // 2 + 2))
            self.screen.blit(night_shadow, night_shadow_rect)
            
            night_text = self.font_button.render(str(night), True, text_color)
            night_rect = night_text.get_rect(center=(button_x + button_width // 2, button_y_actual + button_height // 2))
            self.screen.blit(night_text, night_rect)

            # Lock indicator for unavailable nights
            if is_locked:
                lock_text = self.font_small.render("🔒", True, (200, 100, 100))
                lock_rect = lock_text.get_rect(center=(button_x + button_width // 2, button_y_actual + button_height + 30))
                self.screen.blit(lock_text, lock_rect)

        # Instructions
        inst_text = self.font_medium.render("Select a night to survive", True, (200, 255, 200))
        inst_rect = inst_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.70)))
        self.screen.blit(inst_text, inst_rect)

        # Survival record with styling and glow
        if self.game_state.max_night_unlocked == 1:
            record_text = "No nights survived yet"
            record_color = (255, 100, 100)
        else:
            record_text = f"Your Record: Night {self.game_state.max_night_unlocked}"
            record_color = (100, 255, 150)
        
        # record pulsing effect
        record_pulse = math.sin(time.time() * 2) * 0.2 + 0.8
        pulsed_color = (int(record_color[0] * record_pulse), int(record_color[1] * record_pulse), int(record_color[2] * record_pulse))
        
        record = self.font_medium.render(record_text, True, pulsed_color)
        record_rect = record.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.75)))
        # Record box with glow
        box_alpha = int(200 + math.sin(time.time() * 2) * 50)
        box_surface = pygame.Surface((record_rect.width + 40, record_rect.height + 20))
        box_surface.set_alpha(box_alpha // 2)
        box_surface.fill((20, 20, 40))
        box_rect = box_surface.get_rect(center=(record_rect.centerx, record_rect.centery))
        self.screen.blit(box_surface, box_rect)
        pygame.draw.rect(self.screen, pulsed_color, (box_rect.x, box_rect.y,
                         box_rect.width, box_rect.height), 3)
        self.screen.blit(record, record_rect)

        # Key hint
        hint_text = self.font_small.render("[1-5] Select  |  [ESC] Quit", True, (150, 180, 200))
        hint_rect = hint_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.90)))
        self.screen.blit(hint_text, hint_rect)

        slider_width = 420
        slider_height = 8
        slider_x = (self.game_state.width - slider_width) // 2

        # Night length slider
        slider_y = int(self.game_state.height * 0.82)
        pygame.draw.rect(self.screen, (60, 60, 90), (slider_x, slider_y, slider_width, slider_height))
        val = self.clamp(self.game_state.seconds_per_hour, self.slider_min, self.slider_max)
        t = (val - self.slider_min) / (self.slider_max - self.slider_min)
        fill_w = int(slider_width * t)
        pygame.draw.rect(self.screen, (20, 150, 220), (slider_x, slider_y, fill_w, slider_height))
        knob_x = slider_x + fill_w
        knob_rect = pygame.Rect(knob_x - 8, slider_y - 6, 16, 20)
        pygame.draw.rect(self.screen, (200, 200, 255), knob_rect)

        night_seconds = int(self.game_state.seconds_per_hour)
        minutes_total = int((self.game_state.seconds_per_hour * 6) / 60)
        label = self.font_small.render(f"Night Length: {night_seconds}s/hour  (~{minutes_total} min/night)", True, (200, 255, 200))
        label_rect = label.get_rect(center=(self.game_state.width // 2, slider_y - 18))
        self.screen.blit(label, label_rect)

        # Difficulty slider
        diff_y = int(self.game_state.height * 0.88)
        pygame.draw.rect(self.screen, (60, 60, 90), (slider_x, diff_y, slider_width, slider_height))
        dval = self.clamp(self.difficulty, self.difficulty_min, self.difficulty_max)
        dt = (dval - self.difficulty_min) / (self.difficulty_max - self.difficulty_min)
        dfw = int(slider_width * dt)
        pygame.draw.rect(self.screen, (220, 120, 60), (slider_x, diff_y, dfw, slider_height))
        dknob_x = slider_x + dfw
        dknob_rect = pygame.Rect(dknob_x - 8, diff_y - 6, 16, 20)
        pygame.draw.rect(self.screen, (255, 210, 180), dknob_rect)

        if dval < 0.95:
            diff_label = "EASY"
        elif dval < 1.15:
            diff_label = "NORMAL"
        elif dval < 1.4:
            diff_label = "HARD"
        elif dval < 1.7:
            diff_label = "BRUTAL"
        else:
            diff_label = "NIGHTMARE"
        dlabel = self.font_small.render(f"Difficulty: {diff_label} ({dval:.2f}x)", True, (255, 220, 200))
        dlabel_rect = dlabel.get_rect(center=(self.game_state.width // 2, diff_y - 18))
        self.screen.blit(dlabel, dlabel_rect)

        slider_hint = self.font_small.render("Drag sliders or use ?/? for night length, A/D for difficulty", True, (150, 180, 200))
        hint_rect2 = slider_hint.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.94)))
        self.screen.blit(slider_hint, hint_rect2)

# Subtle static for creepy vibe
        self.apply_creepy_static(0.05)

    def draw_jumpscare(self):
        """Draw jumpscare screen"""
        t = self.jumpscare.timer
        fly_t = min(1.0, t / self.jumpscare.fly_duration)
        ease = 1 - (1 - fly_t) * (1 - fly_t)
        self.jumpscare.zoom = ease

        self.screen.fill((0, 0, 0))
        sprite = self.get_anim_sprite(self.jumpscare.killer, is_attacking=True)
        if sprite:
            base_scale = 0.6 * (self.game_state.width / 1280)
            scale = base_scale * (1.0 + 2.2 * self.jumpscare.zoom)
            scaled = pygame.transform.scale(sprite,
                (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
            rect = scaled.get_rect(center=(self.game_state.width // 2,
                int(self.game_state.height * (0.55 - 0.25 * self.jumpscare.zoom))))
            self.screen.blit(scaled, rect)
        else:
            size = int(80 + 320 * self.jumpscare.zoom)
            pygame.draw.circle(self.screen, (200, 200, 200),
                               (self.game_state.width // 2, self.game_state.height // 2), size)

        # After the fly-in, flood red
        if t >= self.jumpscare.fly_duration:
            intensity = 0.7 + 0.3 * math.sin((t - self.jumpscare.fly_duration) * 15)
            self.screen.fill((int(100 * intensity), 0, 0))
            for i in range(3):
                alpha = int(255 * (0.3 + 0.4 * math.sin((t - self.jumpscare.fly_duration) * (20 + i * 5))))
                jumpscare_surface = pygame.Surface((self.game_state.width, self.game_state.height))
                jumpscare_surface.set_alpha(alpha)
                jumpscare_surface.fill((255, 20, 20))
                self.screen.blit(jumpscare_surface, (0, 0))

            # Determine jumpscare message
            jumpscare_msg = "MR. INGLES GOT YOU!" if self.jumpscare.killer == "Scary Mr Ingles" else f"{self.jumpscare.killer} GOT YOU!"
            jumpscare_text = self.font_large.render(jumpscare_msg, True, (255, 255, 255))
            jumpscare_rect = jumpscare_text.get_rect(center=(self.game_state.width // 2,
                int(self.game_state.height * 0.3)))
            self.screen.blit(jumpscare_text, jumpscare_rect)

            # Static overlay
            self.apply_creepy_static(0.8)

            # Restart instructions
            restart_text = self.font_medium.render("Press [R] to restart  |  [M] for Menu",
                True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.game_state.width // 2,
                int(self.game_state.height * 0.65)))
            self.screen.blit(restart_text, restart_rect)

    def draw_win(self):
        """Draw win screen"""
        # Green tinted background with gradient
        for y in range(self.game_state.height):
            ratio = y / self.game_state.height
            r = int(10 * ratio)
            g = int(40 + 30 * ratio)
            b = int(10 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.game_state.width, y))

        # Pulsing green overlay
        pulse = math.sin(time.time() * 2) * 0.2 + 0.6
        win_surface = pygame.Surface((self.game_state.width, self.game_state.height))
        win_surface.set_alpha(int(100 * pulse))
        win_surface.fill((100, 255, 100))
        self.screen.blit(win_surface, (0, 0))

        # Win text with scale effect
        win_text = self.font_title.render("6 AM", True, (100, 255, 100))
        win_shadow = self.font_title.render("6 AM", True, (20, 80, 20))
        win_rect = win_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.25)))
        win_shadow_rect = win_shadow.get_rect(center=(self.game_state.width // 2 + 3, int(self.game_state.height * 0.25) + 3))
        self.screen.blit(win_shadow, win_shadow_rect)
        self.screen.blit(win_text, win_rect)

        # Survived message
        survived_text = self.font_large.render(f"Night {self.game_state.night} Survived!", True, (200, 255, 200))
        survived_rect = survived_text.get_rect(center=(self.game_state.width // 2, 
            int(self.game_state.height * 0.40)))
        self.screen.blit(survived_text, survived_rect)
        
        # Performance score and stats
        score_text = self.font_medium.render(f"Performance Score: {self.performance_score}", True, (255, 255, 150))
        score_rect = score_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.50)))
        self.screen.blit(score_text, score_rect)
        
        # Ending type message
        ending_type = getattr(self.game_state, 'ending_type', 'standard')
        ending_messages = {
            'perfect': "★ PERFECT PERFORMANCE ★",
            'victory': "All Nights Completed!",
            'flawless': "Flawless Victory!",
            'barely': "Close Call...",
            'standard': "Well Done!"
        }
        ending_text = self.font_medium.render(ending_messages.get(ending_type, "Well Done!"), True, (255, 255, 100))
        ending_rect = ending_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.56)))
        self.screen.blit(ending_text, ending_rect)
        
        # Celebration text for final night
        if self.game_state.night == 5:
            special_text = self.font_medium.render("🎉 YOU BEAT THE GAME! 🎉", True, (255, 255, 100))
            special_rect = special_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.63)))
            pygame.draw.rect(self.screen, (80, 80, 0), (special_rect.x - 20, special_rect.y - 10,
                             special_rect.width + 40, special_rect.height + 20), 0)
            pygame.draw.rect(self.screen, (255, 255, 100), (special_rect.x - 20, special_rect.y - 10,
                             special_rect.width + 40, special_rect.height + 20), 2)
            self.screen.blit(special_text, special_rect)
        
        # High score display
        night_key = self.game_state.night
        if night_key in self.high_scores:
            high_score = self.high_scores[night_key]
            hs_y = int(self.game_state.height * 0.70) if self.game_state.night != 5 else int(self.game_state.height * 0.72)
            if self.performance_score >= high_score:
                hs_text = self.font_small.render(f"NEW HIGH SCORE!", True, (255, 255, 100))
            else:
                hs_text = self.font_small.render(f"High Score: {high_score}", True, (200, 200, 150))
            hs_rect = hs_text.get_rect(center=(self.game_state.width // 2, hs_y))
            self.screen.blit(hs_text, hs_rect)

        # Restart instructions
        restart_text = self.font_medium.render("[R] Next Night  |  [M] Menu",
            True, (200, 255, 200))
        restart_y = int(self.game_state.height * 0.78) if night_key in self.high_scores else int(self.game_state.height * 0.70)
        restart_rect = restart_text.get_rect(center=(self.game_state.width // 2, restart_y))
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        """Main draw loop"""
        if self.game_state.state == "splash":
            self.draw_splash()
            return
        if self.game_state.state == "paused":
            self.draw_background()
            self.draw_anims()
            self.draw_hud()
            self.draw_pause()
            return
        if self.game_state.state == "menu":
            self.draw_menu()
            return

        if self.game_state.state == "anti_cheat":
            self.draw_anti_cheat_warning()
            return

        if self.game_state.state == "intro":
            self.draw_intro()
            return

        if self.game_state.state == "tutorial":
            self.draw_tutorial()
            return

        if self.game_state.state == "jumpscare":
            self.draw_jumpscare()
            return

        if self.game_state.state == "anti_cheat_message":
            self.draw_anti_cheat_message()
            return

        if self.game_state.state == "win":
            self.draw_win()
            return

        # Playing state
        self.draw_background()
        self.draw_anims()
        self.draw_hud()
        
        # Draw noise maker menu if active
        if self.noise_maker_menu_active:
            self.draw_noise_maker_menu()
        
        # Draw particles
        self.draw_particles()
        
        # Apply color overlay
        self.apply_color_overlay()
        
        # Apply creepy effects
        if self.static_intensity > 0:
            self.apply_creepy_static(self.static_intensity)
        
        # Low power flickering
        if self.power.current < 20 and self.power.current > 0:
            if int(time.time() * 10) % 2 == 0:
                flicker = pygame.Surface((self.game_state.width, self.game_state.height))
                flicker.set_alpha(30)
                flicker.fill((255, 100, 0))
                self.screen.blit(flicker, (0, 0))

    def draw_pause(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((self.game_state.width, self.game_state.height))
        overlay.set_alpha(180)
        overlay.fill((10, 10, 20))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("PAUSED", True, (200, 220, 255))
        title_rect = title.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.25)))
        self.screen.blit(title, title_rect)

        options = [
            "ESC / P: Resume",
            "R: Restart Night",
            "M: Menu",
            "Q: Quit Game",
        ]
        for i, opt in enumerate(options):
            text = self.font_medium.render(opt, True, (220, 220, 220))
            rect = text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.40) + i * 40))
            self.screen.blit(text, rect)

    # =====================================================
    # INPUT HANDLING
    # =====================================================

    def toggle_door(self, side):
        """Toggle a door"""
        if self.power.outage:
            return

        if side == "left":
            if self.office.door_left_closed:
                # Opening door
                self.office.door_left_closed = False
                sound = "door_open"
            else:
                # Closing door - requires health and no jam
                if self.office.door_left_jam_timer > 0 or self.office.door_left_health <= 0:
                    self.set_status("Left door jammed!")
                    return
                self.office.door_left_closed = True
                self.office.door_left_health = max(0, self.office.door_left_health - 6)
                sound = "door_close"
                self.total_door_closes += 1
                # Check if this was a perfect block
                if any(a.room == "Hallway" and a.attack_side == "left" for a in self.animatronics):
                    self.perfect_blocks += 1
                    self.combo_blocks += 1
                    self.combo_timer = 5.0  # 5 seconds to chain
                    self.add_screen_shake(2, 0.2)
                self.check_reflex_cheat("left")
            self.assets.play_sound(sound)
        elif side == "right":
            if self.office.door_right_closed:
                # Opening door
                self.office.door_right_closed = False
                sound = "door_open"
            else:
                # Closing door - requires health and no jam
                if self.office.door_right_jam_timer > 0 or self.office.door_right_health <= 0:
                    self.set_status("Right door jammed!")
                    return
                self.office.door_right_closed = True
                self.office.door_right_health = max(0, self.office.door_right_health - 6)
                sound = "door_close"
                self.total_door_closes += 1
                # Check if this was a perfect block
                if any(a.room == "Hallway" and a.attack_side == "right" for a in self.animatronics):
                    self.perfect_blocks += 1
                    self.combo_blocks += 1
                    self.combo_timer = 5.0  # 5 seconds to chain
                    self.add_screen_shake(2, 0.2)
                self.check_reflex_cheat("right")
            self.assets.play_sound(sound)

    def toggle_flashlight(self):
        """Toggle flashlight"""
        if self.power.outage:
            return
        self.office.light_on = not self.office.light_on
        self.assets.play_sound("light_toggle")

    def toggle_cameras(self):
        """Toggle camera view"""
        if self.power.outage:
            return
        self.office.cams_open = not self.office.cams_open
        if self.office.cams_open:
            self.office.cam_flash = 1.0
            self.total_camera_checks += 1
        else:
            pass  # No static loop needed in this version

    def switch_camera(self, index):
        """Switch to a specific camera"""
        if 0 <= index < len(self.cameras.cameras):
            self.cameras.switch(index)
            if self.office.cams_open:
                self.office.cam_flash = 1.0
    
    def use_barricade(self):
        """Reinforce doors with barricades"""
        if self.power.current < 15:
            self.set_status("Not enough power for barricade!")
            return
        
        # Toggle which side to barricade based on which door is weaker
        if self.office.door_left_health < self.office.door_right_health:
            if self.office.barricade_left < 3:
                self.office.barricade_left += 1
                self.office.door_left_health = min(100, self.office.door_left_health + 25)
                self.power.current = max(0, self.power.current - 10)
                self.log_event(f"Left door barricaded (Lvl {self.office.barricade_left})")
                self.add_screen_shake(3, 0.3)
            else:
                self.set_status("Left door fully barricaded!")
        else:
            if self.office.barricade_right < 3:
                self.office.barricade_right += 1
                self.office.door_right_health = min(100, self.office.door_right_health + 25)
                self.power.current = max(0, self.power.current - 10)
                self.log_event(f"Right door barricaded (Lvl {self.office.barricade_right})")
                self.add_screen_shake(3, 0.3)
            else:
                self.set_status("Right door fully barricaded!")
    
    def deploy_noise_maker(self, room):
        """Deploy noise maker to specific room to lure animatronics"""
        if self.office.noise_maker_charges <= 0:
            self.set_status("No noise makers left!")
            return
        
        if self.audio_distraction_cooldown > 0:
            self.set_status(f"Noise maker cooling down: {int(self.audio_distraction_cooldown)}s")
            return
        
        self.office.noise_maker_charges -= 1
        self.audio_distraction_cooldown = 15
        
        # All animatronics head to the selected room thinking they heard something
        lured = 0
        for anim in self.animatronics:
            # Set them to hunt the lure location
            anim.hunt_target_room = room
            # Each animatronic has different time based on their traits
            # sound_sensitivity: 0.5-1.5, patience: 0.5-2.0 (from Animatronic.__init__)
            # Formula: 6.0 + (sensitivity * 3.0) + (patience * 2.0) = 5.0-12.0 seconds
            # More sensitive/patient animatronics stay distracted longer
            base_duration = 6.0 + (anim.sound_sensitivity * 3.0) + (anim.patience * 2.0)
            anim.hunting_timer = min(12.0, max(5.0, base_duration))
            anim.hunting_mode = True
            anim.mood = "hunting"
            lured += 1
        
        if lured > 0:
            self.set_status(f"Deployed noise maker in {room}! Lured {lured} animatronic(s)!")
            self.add_screen_shake(3, 0.8)
            self.add_color_overlay((100, 255, 100, 100), 1.2)
            self.log_event(f"Noise maker deployed in {room}")
        else:
            self.set_status("No animatronics to lure!")
    
    def use_noise_maker(self):
        """Legacy method - shows menu instead"""
        self.noise_maker_menu_active = True
        self.set_status("Choose room (1-7) or ESC to cancel")
    
    def toggle_vent_system(self):
        """Toggle ventilation to reduce camera heat"""
        if self.power.current < 5:
            self.set_status("Not enough power for ventilation!")
            return
        
        self.office.vent_system_active = not self.office.vent_system_active
        
        if self.office.vent_system_active:
            self.log_event("Ventilation system ON")
            self.power.base_drain += 0.05  # Small power cost
        else:
            self.log_event("Ventilation system OFF")
            self.power.base_drain = max(0.16, self.power.base_drain - 0.05)
    
    def use_safe_spot(self):
        """Hide in a safe spot temporarily"""
        if self.current_safe_spot:
            self.set_status("Already in safe spot!")
            return
        
        if not self.safe_spots_available:
            self.set_status("No safe spots available!")
            return
        
        # Can only use if threat is high enough
        if self.threat_level < 50:
            self.set_status("Not dangerous enough to hide!")
            return
        
        # Choose random safe spot
        spot = self.rng.choice(self.safe_spots_available)
        self.current_safe_spot = spot
        self.safe_spot_duration = 8.0  # 8 seconds of safety
        self.safe_spots_available.remove(spot)
        
        self.log_event(f"Hiding in {spot}!")
        self.add_color_overlay((50, 50, 50, 200), 8.0)
        
        # Animatronics lose track temporarily
        for anim in self.animatronics:
            if anim.room == "Office":
                anim.room = "Hallway"
                anim.target_x, anim.target_y = room_position("Hallway", WINDOW_WIDTH, WINDOW_HEIGHT)

    def handle_input(self):
        """Handle all input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.window_width = event.w
                self.window_height = event.h
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Menu slider handling
                if self.game_state.state == "menu":
                    # Scale mouse position to game coordinates
                    mx, my = self.scale_mouse_pos(event.pos)
                    slider_width = 420
                    slider_x = (self.game_state.width - slider_width) // 2
                    slider_y = int(self.game_state.height * 0.82)
                    diff_y = int(self.game_state.height * 0.88)
                    if slider_x <= mx <= slider_x + slider_width and slider_y - 12 <= my <= slider_y + 24:
                        # start dragging and update value
                        self.dragging_slider = True
                        t = (mx - slider_x) / slider_width
                        self.game_state.seconds_per_hour = self.clamp(self.slider_min + t * (self.slider_max - self.slider_min), self.slider_min, self.slider_max)
                        continue
                    if slider_x <= mx <= slider_x + slider_width and diff_y - 12 <= my <= diff_y + 24:
                        self.dragging_difficulty = True
                        t = (mx - slider_x) / slider_width
                        self.difficulty = self.clamp(self.difficulty_min + t * (self.difficulty_max - self.difficulty_min), self.difficulty_min, self.difficulty_max)
                        continue
                    
                    # Check night button clicks
                    for night, button_rect in self.night_buttons.items():
                        if button_rect.collidepoint(mx, my) and night <= self.game_state.max_night_unlocked:
                            self.start_night(night)
                            break

                # Handle noise maker menu clicks
                if self.noise_maker_menu_active and self.game_state.state == "playing":
                    mx, my = self.scale_mouse_pos(event.pos)
                    for i, button_rect in self.noise_maker_buttons.items():
                        if button_rect.collidepoint(mx, my):
                            selected_room = self.noise_maker_rooms[i]
                            self.deploy_noise_maker(selected_room)
                            self.noise_maker_menu_active = False
                            break

                # Handle minimap clicks when playing
                if self.game_state.state == "playing" and not self.noise_maker_menu_active:
                    clicked_room = self.get_clicked_room(self.scale_mouse_pos(event.pos))
                    if clicked_room:
                        # Find camera index for this room
                        try:
                            cam_index = self.cameras.cameras.index(clicked_room)
                            # If not viewing cameras, open them
                            if not self.office.cams_open:
                                self.toggle_cameras()
                            # Switch to the clicked camera
                            self.switch_camera(cam_index)
                        except ValueError:
                            pass
            elif event.type == pygame.MOUSEBUTTONUP:
                # stop dragging slider
                if self.dragging_slider:
                    self.dragging_slider = False
                if self.dragging_difficulty:
                    self.dragging_difficulty = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_slider and self.game_state.state == "menu":
                    mx, my = self.scale_mouse_pos(event.pos)
                    slider_width = 420
                    slider_x = (self.game_state.width - slider_width) // 2
                    t = (mx - slider_x) / slider_width
                    self.game_state.seconds_per_hour = self.clamp(self.slider_min + t * (self.slider_max - self.slider_min), self.slider_min, self.slider_max)
                if self.dragging_difficulty and self.game_state.state == "menu":
                    mx, my = self.scale_mouse_pos(event.pos)
                    slider_width = 420
                    slider_x = (self.game_state.width - slider_width) // 2
                    t = (mx - slider_x) / slider_width
                    self.difficulty = self.clamp(self.difficulty_min + t * (self.difficulty_max - self.difficulty_min), self.difficulty_min, self.difficulty_max)
            elif event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)

                if key == "escape":
                    self.running = False

                elif self.game_state.state == "anti_cheat_message":
                    if key == "m":
                        self.anti_cheat_active = False
                        self.anti_cheat_pending = False
                        self.enter_menu()

                elif self.game_state.state == "menu":
                    if key == "1":
                        self.start_night(1)
                    elif key == "2" and self.game_state.max_night_unlocked >= 2:
                        self.start_night(2)
                    elif key == "3" and self.game_state.max_night_unlocked >= 3:
                        self.start_night(3)
                    elif key == "4" and self.game_state.max_night_unlocked >= 4:
                        self.start_night(4)
                    elif key == "5" and self.game_state.max_night_unlocked >= 5:
                        self.start_night(5)
                    elif key == "left":
                        # decrease night length
                        step = 5.0
                        self.game_state.seconds_per_hour = self.clamp(self.game_state.seconds_per_hour - step, self.slider_min, self.slider_max)
                    elif key == "right":
                        step = 5.0
                        self.game_state.seconds_per_hour = self.clamp(self.game_state.seconds_per_hour + step, self.slider_min, self.slider_max)
                    elif key == "a":
                        step = 0.05
                        self.difficulty = self.clamp(self.difficulty - step, self.difficulty_min, self.difficulty_max)
                    elif key == "d":
                        step = 0.05
                        self.difficulty = self.clamp(self.difficulty + step, self.difficulty_min, self.difficulty_max)

                elif self.game_state.state == "playing":
                    if key == "q":
                        self.toggle_door("left")
                    elif key == "e":
                        self.toggle_door("right")
                    elif key == "f":
                        self.toggle_flashlight()
                    elif key == "tab":
                        self.toggle_cameras()
                    elif key == "h":
                        self.show_controls = not self.show_controls
                    elif key == "1":
                        self.switch_camera(0)
                    elif key == "2":
                        self.switch_camera(1)
                    elif key == "3":
                        self.switch_camera(2)
                    elif key == "4":
                        self.switch_camera(3)
                    elif key == "5":
                        self.switch_camera(4)
                    elif key == "6":
                        self.switch_camera(5)
                    elif key == "b":
                        self.use_barricade()
                    elif key == "n":
                        self.noise_maker_menu_active = True
                        self.set_status("Choose room (1-7) or ESC to cancel")
                    elif key == "v":
                        self.toggle_vent_system()
                    elif key == "c":
                        self.use_safe_spot()
                    elif key in ("escape", "p"):
                        if self.noise_maker_menu_active:
                            self.noise_maker_menu_active = False
                            self.set_status("")
                        else:
                            self.game_state.state = "paused"
                
                elif self.game_state.state == "playing" and self.noise_maker_menu_active:
                    # Handle room selection for noise maker
                    if key in ("1", "2", "3", "4", "5", "6", "7"):
                        room_index = int(key) - 1
                        if room_index < len(self.noise_maker_rooms):
                            selected_room = self.noise_maker_rooms[room_index]
                            self.deploy_noise_maker(selected_room)
                            self.noise_maker_menu_active = False
                    elif key == "escape":
                        self.noise_maker_menu_active = False
                        self.set_status("")

                elif self.game_state.state == "paused":
                    if key in ("escape", "p"):
                        self.game_state.state = "playing"
                    elif key == "r":
                        self.start_night(self.game_state.night)
                    elif key == "m":
                        self.restart_from_menu()
                    elif key == "q":
                        self.running = False

                elif self.game_state.state == "jumpscare":
                    if key == "r":
                        self.start_night(1)
                    elif key == "m":
                        self.restart_from_menu()

                elif self.game_state.state == "win":
                    if key == "r":
                        self.start_night(1)
                    elif key == "m":
                        self.restart_from_menu()

                elif self.game_state.state == "tutorial":
                    if key == "space":
                        # Skip tutorial - go directly to playing
                        ambience_key = f"ambience_n{self.game_state.night}"
                        self.assets.play_music(ambience_key)
                        self.game_state.state = "playing"
                        self.game_state.start_time = time.time()
                        self.game_state.hour_timer = 0
                        self.game_state.minutes_elapsed = 0
                        self.tutorial_index = 0
                        self.tutorial_timer = 0.0

    # =====================================================
    # MAIN LOOP
    # =====================================================

    def run(self):
        """Main game loop - Optimized for 60 FPS"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Skip heavy updates if running slow
            if dt > 0.033:  # More than 30ms per frame
                dt = 0.033  # Cap dt to prevent spiral of death

            self.handle_input()
            self.update(dt)
            self.draw()

            # Scale render surface to window with aspect ratio preservation
            self.scale_and_blit_to_screen()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    game = Game()
    game.run()

#!/usr/bin/env python3
"""
Five Nights at Mr Ingles's - Python Edition (Pygame)
Faithful port of the LOVE2D game to Python
"""

import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
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
WINDOW_TITLE = "Five Nights at Mr Ingles's (Python Edition)"
FPS = 60
SAVE_FILE = "mr_ingles_save.json"

# =====================================================
# GAME STATE
# =====================================================

class GameState:
    """Main game state container"""
    def __init__(self):
        self.state = "splash"  # "splash", "menu", "playing", "paused", "jumpscare", "win"
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
        self.cam_heat = 0.0
        self.cam_overload_timer = 0.0

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
        self.cam_heat = 0.0
        self.cam_overload_timer = 0.0


class CameraSystem:
    """Camera switching system"""
    def __init__(self):
        self.cameras = ["Cafeteria", "Hallway", "Gym", "Library", "Bathrooms", "Vent"]
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
    "Office": ["Hallway"],
    "Hallway": ["Office", "Cafeteria", "Gym", "Bathrooms"],
    "Cafeteria": ["Hallway", "Library"],
    "Gym": ["Hallway"],
    "Library": ["Cafeteria"],
    "Bathrooms": ["Hallway", "Vent"],
    "Vent": ["Bathrooms", "Hallway"],
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

    def update_mood(self, game_state=None):
        """Update mood based on situation (deterministic)"""
        minutes = game_state.minutes_elapsed if game_state else 0
        night = game_state.night if game_state else 1
        if self.hunting_mode:
            self.mood = "hunting"
        elif self.block_count >= 4 or minutes >= 240 or night >= 3:
            self.mood = "aggressive"
        elif self.block_count >= 2 or minutes >= 120:
            self.mood = "cautious"
        else:
            self.mood = "neutral"

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
        if os.path.exists(path):
            try:
                self.images[name] = pygame.image.load(path).convert_alpha()
                return self.images[name]
            except:
                return None
        return None

    def load_sound(self, name, path):
        """Safely load a sound"""
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
                return self.sounds[name]
            except:
                return None
        return None

    def load_music(self, name, path):
        """Safely load music"""
        if os.path.exists(path):
            try:
                # For streaming music, we'll use pygame.mixer.music
                self.music[name] = path
                return path
            except:
                return None
        return None

    def load_all_assets(self):
        """Load all game assets"""
        # Images
        self.load_image("office", "assets/img/office.png")
        self.load_image("door_left", "assets/img/office_door_left.png")
        self.load_image("door_right", "assets/img/office_door_right.png")
        self.load_image("cam_cafeteria", "assets/img/cam_cafeteria.png")
        self.load_image("cam_hallway", "assets/img/cam_hallway.png")
        self.load_image("cam_gym", "assets/img/cam_gym.png")
        self.load_image("cam_library", "assets/img/cam_library.png")
        self.load_image("cam_bathrooms", "assets/img/cam_bathrooms.png")
        self.load_image("cam_vent", "assets/img/cam_vent.png")
        self.load_image("title", "assets/img/title.png")
        self.load_image("menu_background", "assets/img/menu_background.png")
        self.load_image("intro_splash", "assets/img/intro_splashscreen.png")
        self.load_image("tos_splash", "assets/img/tos_splash.png")
        self.load_image("anim_mr_ingles", "assets/img/anim_mr_ingles.png")
        self.load_image("anim_janitor", "assets/img/anim_janitor.png")
        self.load_image("anim_librarian", "assets/img/anim_librarian.png")
        self.load_image("anim_vent", "assets/img/anim_vent.png")
        self.load_image("mr_ingles_office", "assets/img/mr_ingles_office.png")

        # Sounds
        self.load_sound("door_close", "assets/sfx/door_close.ogg")
        self.load_sound("door_open", "assets/sfx/door_open.ogg")
        self.load_sound("light_toggle", "assets/sfx/light_toggle.ogg")
        self.load_sound("jumpscare", "assets/sfx/jumpscare.ogg")
        self.load_sound("bell_6am", "assets/sfx/bell_6am.ogg")
        self.load_sound("static_loop", "assets/sfx/static_loop.ogg")

        # Music/Ambience
        self.load_music("ambience_n1", "assets/sfx/ambience_n1.ogg")
        self.load_music("ambience_n2", "assets/sfx/ambience_n2.ogg")
        self.load_music("ambience_n3", "assets/sfx/ambience_n3.ogg")
        self.load_music("ambience_n4", "assets/sfx/ambience_n4.ogg")
        self.load_music("ambience_n5", "assets/sfx/ambience_n5.ogg")
        self.load_music("menu_theme", "assets/music/menu_theme.ogg")

    def play_sound(self, name):
        """Play a sound effect"""
        if name in self.sounds:
            self.sounds[name].stop()
            self.sounds[name].play()

    def play_music(self, name, loops=-1):
        """Play music (streaming)"""
        if name in self.music:
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.load(self.music[name])
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(loops)
                self.current_music = name
            except:
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

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

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
        self.event_log = []
        self.event_log_max = 6
        self.show_controls = True
        
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
        self.tutorial_slide_duration = 4.0  # seconds per slide
        self.tutorial_slides = [
            {"title": "CONTROLS", "text": "Use Q and E to control the doors\nQ = LEFT DOOR  |  E = RIGHT DOOR"},
            {"title": "MANAGING POWER", "text": "F toggles the office light\nPower surges at :15, :30, :45\nKeep an eye on the power bar"},
            {"title": "CAMERAS", "text": "Press TAB to open/close cameras\nCams overheat if used too long\nClick the minimap to jump to rooms"},
            {"title": "SURVIVAL", "text": "Doors have integrity and can jam\nAnimatronics attack from a side\nSurvive until 6 AM to win!"},
            {"title": "GOOD LUCK!", "text": "Watch the animatronics carefully\nThey learn from your patterns\nStay alert and survive the night!"},
        ]

        # Load everything
        self.assets.load_all_assets()
        self.load_save()

        if self.game_state.state == "menu":
            self.play_menu_music()

    def clamp(self, x, a, b):
        """Clamp value between a and b"""
        return max(a, min(x, b))
    
    def set_status(self, msg=""):
        """Set status message"""
        self.game_state.status = msg or ""

    def log_event(self, msg):
        """Add an event to the HUD log"""
        stamp = f"{self.game_state.minutes_elapsed // 60:02d}:{self.game_state.minutes_elapsed % 60:02d}"
        entry = f"{stamp} - {msg}"
        self.event_log.insert(0, entry)
        if len(self.event_log) > self.event_log_max:
            self.event_log = self.event_log[:self.event_log_max]

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
        minimap_width = 280
        minimap_height = 200
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
            "Office": (minimap_x + 140, minimap_y + 140),
            "Hallway": (minimap_x + 140, minimap_y + 90),
            "Cafeteria": (minimap_x + 80, minimap_y + 90),
            "Gym": (minimap_x + 200, minimap_y + 90),
            "Library": (minimap_x + 60, minimap_y + 40),
            "Bathrooms": (minimap_x + 220, minimap_y + 40),
            "Vent": (minimap_x + 140, minimap_y + 20),
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
            except:
                self.game_state.max_night_unlocked = 1
        else:
            self.game_state.max_night_unlocked = 1

    def save_progress(self):
        """Save progress to file"""
        data = {
            "max_night": self.clamp(self.game_state.max_night_unlocked, 1, 5),
            "difficulty": self.clamp(self.difficulty, self.difficulty_min, self.difficulty_max),
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
            Animatronic("Mr Ingles", "Cafeteria", jitter(0.40, 0.06), jitter(5.5, 0.6), "teleport",
                        attack_side="left",
                        patrol_route=["Cafeteria", "Hallway", "Cafeteria", "Library"],
                        start_delay_minutes=self.rng.randint(3, 7),
                        hallway_entry_delay=jitter(2.2, 0.4),
                        aggression_ramp=jitter(0.30, 0.08),
                        rng=self.rng),
            Animatronic("Janitor Bot", "Bathrooms", jitter(0.34, 0.05), jitter(6.5, 0.7), "teleport",
                        attack_side="right",
                        patrol_route=["Bathrooms", "Hallway", "Bathrooms", "Gym"],
                        start_delay_minutes=self.rng.randint(12, 18),
                        hallway_entry_delay=jitter(2.6, 0.4),
                        aggression_ramp=jitter(0.22, 0.06),
                        rng=self.rng),
            Animatronic("Librarian", "Library", jitter(0.32, 0.05), jitter(6.8, 0.6), "teleport",
                        attack_side="left",
                        patrol_route=["Library", "Cafeteria", "Hallway"],
                        start_delay_minutes=self.rng.randint(8, 13),
                        hallway_entry_delay=jitter(2.4, 0.4),
                        aggression_ramp=jitter(0.24, 0.06),
                        rng=self.rng),
            Animatronic("Vent Crawler", "Vent", jitter(0.38, 0.05), jitter(5.8, 0.6), "vent",
                        attack_side="vent",
                        patrol_route=["Vent", "Bathrooms", "Hallway"],
                        start_delay_minutes=self.rng.randint(18, 24),
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

        # Door open limit (auto-close if open too long; recovers immediately when closed)
        if not self.office.door_left_closed:
            self.office.door_left_open_timer += dt
            if self.office.door_left_open_timer >= self.door_open_limit:
                self.office.door_left_closed = True
                self.office.door_left_open_timer = 0.0
                self.log_event("Left door auto-closed (open limit)")
        else:
            self.office.door_left_open_timer = 0.0

        if not self.office.door_right_closed:
            self.office.door_right_open_timer += dt
            if self.office.door_right_open_timer >= self.door_open_limit:
                self.office.door_right_closed = True
                self.office.door_right_open_timer = 0.0
                self.log_event("Right door auto-closed (open limit)")
        else:
            self.office.door_right_open_timer = 0.0

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
        cam_disabled = self.office.cam_overload_timer > 0 or self.power.outage
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
                self.office.door_left_closed = False
                self.office.door_right_closed = False
                self.office.light_on = False
                self.office.cams_open = False
                self.office.cam_heat = 0.0
                self.office.cam_overload_timer = 0.0
                self.set_status("POWER OUTAGE.")
                self.static_intensity = 0.8
                self.screen_shake = 3
            return

        # Camera heat and overload
        if self.office.cam_overload_timer > 0:
            self.office.cam_overload_timer = max(0, self.office.cam_overload_timer - dt)
        if self.office.cams_open:
            self.office.cam_heat = min(100.0, self.office.cam_heat + 18.0 * dt)
            if self.office.cam_heat >= 100.0:
                self.office.cam_heat = 100.0
                self.office.cams_open = False
                self.office.cam_overload_timer = 8.0
                self.office.cam_flash = 1.0
                self.set_status("CAMERAS OVERHEATED!")
                self.log_event("Cameras overheated")
                self.overload_grace_timer = max(self.overload_grace_timer, 3.0)
        else:
            self.office.cam_heat = max(0.0, self.office.cam_heat - 12.0 * dt)

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
                self.game_state.state = "win"
                self.set_status(f"6 AM! You survived Night {self.game_state.night}!")
                self.assets.play_sound("bell_6am")
                self.assets.stop_music()

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
            # Hallway pressure: force entry if door is open, strain if closed
            if anim.room == "Hallway":
                if anim.attack_side == "left":
                    door_closed = self.office.door_left_closed
                elif anim.attack_side == "right":
                    door_closed = self.office.door_right_closed
                else:
                    door_closed = self.office.door_left_closed and self.office.door_right_closed

                if door_closed:
                    anim.hallway_timer = 0.0
                    anim.hallway_block_timer += dt
                    pressure = 3.2 * self.difficulty
                    if anim.attack_side in ("left", "vent"):
                        self.office.door_left_health = max(0.0, self.office.door_left_health - pressure * dt)
                        if self.office.door_left_health <= 0 and self.office.door_left_jam_timer <= 0:
                            self.break_door("left")
                    if anim.attack_side in ("right", "vent"):
                        self.office.door_right_health = max(0.0, self.office.door_right_health - pressure * dt)
                        if self.office.door_right_health <= 0 and self.office.door_right_jam_timer <= 0:
                            self.break_door("right")
                    # If blocked too long in hallway, force a retreat
                    if anim.hallway_block_timer >= 2.5:
                        neighbors = [r for r in get_neighbors("Hallway") if r != "Office"]
                        if neighbors:
                            anim.last_room = anim.room
                            anim.room = neighbors[anim.block_count % len(neighbors)]
                            anim.target_x, anim.target_y = room_position(anim.room, WINDOW_WIDTH, WINDOW_HEIGHT)
                            anim.x = anim.target_x
                            anim.y = anim.target_y
                            anim.retreat_timer = 4.0
                            anim.retreat_target = anim.room
                            anim.hallway_block_timer = 0.0
                else:
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
                        self.log_event(f"{anim.name} entered Office")
            else:
                anim.hallway_timer = 0.0
                anim.hallway_block_timer = 0.0

            # Check if animatronic was blocked by a door
            anim.get_blocked_side(self.office)
            # Check if animatronic should attack (windup required)
            if anim.room == "Office" and anim.try_attack(self.office):
                anim.attack_windup += dt
                required = max(0.45, (anim.attack_windup_required / max(0.8, self.difficulty)) - (self.game_state.night - 1) * 0.1)
                if anim.attack_windup >= required:
                    self.jumpscare.killer = anim.name
                    self.jumpscare.active = True
                    self.jumpscare.timer = 0
                    self.game_state.state = "jumpscare"
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

        if self.game_state.state == "intro":
            self.update_intro(dt)
            # keep updating visual effects (optional)
            self.update_office_effects(dt)
            return

        if self.game_state.state == "tutorial":
            self.update_tutorial(dt)
            return

        if self.game_state.state == "playing":
            self.update_power(dt)
            self.update_time(dt)
            self.update_animatronics(dt)
        elif self.game_state.state == "jumpscare":
            self.jumpscare.timer += dt
            if self.jumpscare.timer > self.jumpscare.duration:
                self.jumpscare.timer = self.jumpscare.duration

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
        total = self.intro_message_duration
        # determine if we should advance to next message
        if self.intro_timer >= (self.intro_index + 1) * total:
            self.intro_index += 1

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

        total = self.intro_message_duration
        # local time within current message
        t = self.intro_timer - (self.intro_index * total)
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
        content_lines = slide["text"].split("\\n")
        y_offset = int(self.game_state.height * 0.35)
        line_spacing = int(self.game_state.height * 0.12)
        
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

    def get_anim_sprite(self, name):
        """Get sprite for animatronic"""
        sprites = {
            "Mr Ingles": "anim_mr_ingles",
            "Janitor Bot": "anim_janitor",
            "Librarian": "anim_librarian",
            "Vent Crawler": "anim_vent",
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
        cam_key = f"cam_{cam_name.lower()}"
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

        cam_heat = int(self.office.cam_heat + 0.5)
        cam_label = f"CAM HEAT: {cam_heat}%"
        if self.office.cam_overload_timer > 0:
            cam_label += f"  OVERLOAD {int(self.office.cam_overload_timer + 0.5)}s"
        cam_text = self.font_small.render(cam_label, True, (200, 200, 200))
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

        # Controls help moved to above (door integrity display replaced it)
        # Draw minimap when not using cameras
        if not self.office.cams_open:
            self.draw_minimap()

        # Threat meters
        meter_x = self.game_state.width - 250
        meter_y = self.game_state.height - 140
        for i, anim in enumerate(self.animatronics):
            dist = anim._distance_to_room(anim.room, "Office")
            threat = max(0.0, 1.0 - (dist / 4.0))
            bar_w = int(120 * threat)
            label = self.font_small.render(anim.name, True, (200, 200, 200))
            self.screen.blit(label, (meter_x, meter_y + i * 18))
            pygame.draw.rect(self.screen, (80, 80, 80), (meter_x + 90, meter_y + i * 18 + 4, 120, 8))
            pygame.draw.rect(self.screen, (255, 80, 80), (meter_x + 90, meter_y + i * 18 + 4, bar_w, 8))

        # Night progress bar
        progress = min(1.0, self.game_state.minutes_elapsed / 360.0)
        bar_x = (self.game_state.width - 300) // 2
        bar_y = self.game_state.height - 85
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, 300, 10))
        pygame.draw.rect(self.screen, (80, 200, 120), (bar_x, bar_y, int(300 * progress), 10))
        pygame.draw.rect(self.screen, (120, 120, 120), (bar_x, bar_y, 300, 10), 1)

        # Event log
        log_x = self.game_state.width - 320
        log_y = 20
        log_title = self.font_small.render("EVENT LOG", True, (180, 200, 220))
        self.screen.blit(log_title, (log_x, log_y))
        for i, entry in enumerate(self.event_log):
            text = self.font_small.render(entry, True, (180, 180, 180))
            self.screen.blit(text, (log_x, log_y + 18 + i * 16))

        # Controls overlay (toggle H)
        if self.show_controls:
            cx = 20
            cy = 80
            lines = [
                "CONTROLS",
                "Q/E: Doors",
                "F: Light",
                "TAB: Cameras",
                "1-6: Switch Cam",
                "H: Toggle HUD Help",
                "ESC/P: Pause",
            ]
            for i, line in enumerate(lines):
                txt = self.font_small.render(line, True, (170, 200, 220) if i == 0 else (150, 180, 200))
                self.screen.blit(txt, (cx, cy + i * 16))

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

        for night in range(1, 6):
            button_x = start_x + (night - 1) * button_spacing
            is_available = night <= self.game_state.max_night_unlocked
            is_locked = night > self.game_state.max_night_unlocked

            # Bobbing animation with enhanced effects
            bob = math.sin(time.time() * 2 + night) * 5 if is_available else 0
            button_y_actual = button_y + bob

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
        sprite = self.get_anim_sprite(self.jumpscare.killer)
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

            jumpscare_text = self.font_large.render(f"{self.jumpscare.killer} GOT YOU!", True, (255, 255, 255))
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
            int(self.game_state.height * 0.45)))
        self.screen.blit(survived_text, survived_rect)
        
        # Celebration text for final night
        if self.game_state.night == 5:
            special_text = self.font_medium.render("🎉 YOU BEAT THE GAME! 🎉", True, (255, 255, 100))
            special_rect = special_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.55)))
            pygame.draw.rect(self.screen, (80, 80, 0), (special_rect.x - 20, special_rect.y - 10,
                             special_rect.width + 40, special_rect.height + 20), 0)
            pygame.draw.rect(self.screen, (255, 255, 100), (special_rect.x - 20, special_rect.y - 10,
                             special_rect.width + 40, special_rect.height + 20), 2)
            self.screen.blit(special_text, special_rect)

        # Restart instructions
        restart_text = self.font_medium.render("[R] Next Night  |  [M] Menu",
            True, (200, 255, 200))
        restart_rect = restart_text.get_rect(center=(self.game_state.width // 2,
            int(self.game_state.height * 0.70)))
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

        if self.game_state.state == "intro":
            self.draw_intro()
            return

        if self.game_state.state == "tutorial":
            self.draw_tutorial()
            return

        if self.game_state.state == "jumpscare":
            self.draw_jumpscare()
            return

        if self.game_state.state == "win":
            self.draw_win()
            return

        # Playing state
        self.draw_background()
        self.draw_anims()
        self.draw_hud()
        
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
        if self.office.cam_overload_timer > 0:
            self.set_status("Cameras overheated!")
            return
        self.office.cams_open = not self.office.cams_open
        if self.office.cams_open:
            self.office.cam_flash = 1.0
        else:
            pass  # No static loop needed in this version

    def switch_camera(self, index):
        """Switch to a specific camera"""
        if 0 <= index < len(self.cameras.cameras):
            self.cameras.switch(index)
            if self.office.cams_open:
                self.office.cam_flash = 1.0

    def handle_input(self):
        """Handle all input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Menu slider handling
                if self.game_state.state == "menu":
                    mx, my = event.pos
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

                # Handle minimap clicks when playing
                if self.game_state.state == "playing":
                    clicked_room = self.get_clicked_room(event.pos)
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
                    mx, my = event.pos
                    slider_width = 420
                    slider_x = (self.game_state.width - slider_width) // 2
                    t = (mx - slider_x) / slider_width
                    self.game_state.seconds_per_hour = self.clamp(self.slider_min + t * (self.slider_max - self.slider_min), self.slider_min, self.slider_max)
                if self.dragging_difficulty and self.game_state.state == "menu":
                    mx, my = event.pos
                    slider_width = 420
                    slider_x = (self.game_state.width - slider_width) // 2
                    t = (mx - slider_x) / slider_width
                    self.difficulty = self.clamp(self.difficulty_min + t * (self.difficulty_max - self.difficulty_min), self.difficulty_min, self.difficulty_max)
            elif event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)

                if key == "escape":
                    self.running = False

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
                    elif key in ("escape", "p"):
                        self.game_state.state = "paused"

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
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_input()
            self.update(dt)
            self.draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    game = Game()
    game.run()

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
            print(f"\n⏳ Installing {package}...")
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
import random
import time
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
        self.state = "menu"  # "menu", "playing", "jumpscare", "win"
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
        self.base_drain = 0.125  # 25% faster drain
        self.door_drain = 0.1875  # 25% faster drain
        self.light_drain = 0.1875  # 25% faster drain
        self.cam_drain = 0.25   # 25% faster drain
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
        self.door_left_uses = 3          # Limited door uses
        self.door_right_uses = 3

    def reset(self):
        self.door_left_closed = False
        self.door_right_closed = False
        self.light_on = True
        self.cams_open = False
        self.door_left_progress = 0.0
        self.door_right_progress = 0.0
        self.light_dim = 0.0
        self.cam_flash = 0.0
        self.door_left_uses = 3
        self.door_right_uses = 3


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

    def reset(self):
        self.active = False
        self.timer = 0


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
    """Animatronic character with advanced AI"""
    def __init__(self, name, start_room, base_aggro, base_interval, style="teleport"):
        self.name = name
        self.room = start_room
        self.base_aggro = base_aggro
        self.base_interval = base_interval
        self.aggro = base_aggro
        self.move_interval = base_interval
        self.timer = 0
        self.style = style
        self.x, self.y = room_position(start_room, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.target_x = self.x
        self.target_y = self.y
        self.visible_on_cam = True
        
        # Advanced AI features
        self.mood = "neutral"  # neutral, aggressive, cautious, hunting, retreating
        self.mood_timer = 0
        self.mood_duration = random.uniform(8, 15)
        self.player_action_memory = []  # remember recent player actions
        self.target_player_room = None  # predicted player location
        self.communication_cooldown = 0
        self.hunting_mode = False
        self.hunt_target_room = None
        self.adaptive_aggro = base_aggro  # adjusts based on learning
        self.last_blocked_time = 0
        self.block_count = 0
        self.preferred_path = []  # learns efficient routes

    def update(self, dt, game_state=None):
        """Update animatronic with advanced AI"""
        self.timer += dt
        self.mood_timer += dt
        
        # Update mood state (affects behavior)
        if self.mood_timer >= self.mood_duration:
            self.update_mood(game_state)
            self.mood_timer = 0
            self.mood_duration = random.uniform(8, 15)
        
        # Adaptive aggression based on learning
        self.adaptive_aggro = self.base_aggro + (self.block_count * 0.05)
        interval = self.move_interval / (1.0 + self.adaptive_aggro * 0.3)
        chance = self.adaptive_aggro * self.get_mood_multiplier()
        
        # Hunting mode AI
        if self.hunting_mode:
            if random.random() < 0.7:  # 70% chance to pursue target
                self.move_toward_target(self.hunt_target_room)
            else:
                self.move()  # occasional randomness
        else:
            # Standard movement with learning
            if self.timer >= interval:
                self.timer -= interval
                if random.random() < chance:
                    self.move()
        
        # Smooth position toward target
        speed = 4 * dt
        self.x += (self.target_x - self.x) * speed
        self.y += (self.target_y - self.y) * speed
        
        # Communication cooldown
        if self.communication_cooldown > 0:
            self.communication_cooldown -= dt
        
        # Hunting timeout
        if self.hunting_mode and time.time() - self.last_blocked_time > 20:
            self.hunting_mode = False
            self.hunt_target_room = None

    def update_mood(self, game_state=None):
        """Update mood based on situation"""
        if self.block_count > 5:
            self.mood = "aggressive"  # frustrated from being blocked
        elif self.block_count > 2:
            self.mood = random.choice(["aggressive", "hunting"])
        else:
            self.mood = random.choice(["neutral", "cautious"])

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

    def move(self):
        """Move to a random adjacent room or use learned paths"""
        neighbors = get_neighbors(self.room)
        if neighbors:
            # 60% chance to use learned optimal path, 40% random
            if self.preferred_path and random.random() < 0.6:
                self.room = self.preferred_path[0] if self.preferred_path else random.choice(neighbors)
            else:
                self.room = random.choice(neighbors)
                self.preferred_path = [self.room]
            
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
            # Vent crawler ignores doors
            if self.name == "Vent Crawler":
                return True
            # Other animatronics need doors open to attack
            if not office.door_left_closed and not office.door_right_closed:
                return True
        return False
    
    def get_blocked_side(self, office):
        """Check which door is blocking this animatronic (if any)"""
        if self.room == "Office" and self.name != "Vent Crawler":
            if office.door_left_closed:
                self.handle_blocked("left")
                return "left"
            elif office.door_right_closed:
                self.handle_blocked("right")
                return "right"
        return None

    def handle_blocked(self, side):
        """Handle being blocked - learning and mood change"""
        self.block_count += 1
        self.last_blocked_time = time.time()
        self.hunting_mode = True
        self.hunt_target_room = "Office"
        self.mood = "aggressive"
        # MUST leave the office - find a neighboring room and move there immediately
        if self.room == "Office":
            neighbors = get_neighbors(self.room)
            if neighbors:
                # Pick a random neighbor, don't stay in office
                self.room = random.choice(neighbors)
                self.target_x, self.target_y = room_position(self.room, 1280, 720)
                self.x = self.target_x
                self.y = self.target_y
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
        
        # Minimap data
        self.minimap_room_positions = {}

        # Menu slider (night length)
        self.slider_min = 15.0   # seconds per in-game hour (fast)
        self.slider_max = 180.0  # seconds per in-game hour (slow)
        self.dragging_slider = False
        self.slider_hover = False

        # Intro sequence (Night 1)
        self.intro_messages = []
        self.intro_index = 0
        self.intro_timer = 0.0
        self.intro_message_duration = 1.5  # seconds per message (incl fade in/out)
        
        # Tutorial slideshow (after intro)
        self.tutorial_index = 0
        self.tutorial_timer = 0.0
        self.tutorial_slide_duration = 4.0  # seconds per slide
        self.tutorial_slides = [
            {"title": "CONTROLS", "text": "Use Q and E to control the doors\nQ = LEFT DOOR  |  E = RIGHT DOOR"},
            {"title": "MANAGING POWER", "text": "F toggles the office light\nMonitor power usage carefully\nKeep an eye on the power bar"},
            {"title": "CAMERAS", "text": "Press TAB to open/close cameras\nPress 1-6 to switch camera feeds\nClick the minimap to jump to rooms"},
            {"title": "SURVIVAL", "text": "Block animatronics with doors\nManage your power wisely\nSurvive until 6 AM to win!"},
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
    
    def apply_creepy_static(self, intensity=0.3):
        """Apply creepy static/noise overlay"""
        static_surface = pygame.Surface((self.game_state.width, self.game_state.height))
        static_surface.set_alpha(int(255 * intensity * 0.4))
        for _ in range(int(100 * intensity)):
            x = random.randint(0, self.game_state.width)
            y = random.randint(0, self.game_state.height)
            color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
            pygame.draw.line(static_surface, color, (x, y), (x + random.randint(1, 3), y + random.randint(1, 3)), 1)
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
            except:
                self.game_state.max_night_unlocked = 1
        else:
            self.game_state.max_night_unlocked = 1

    def save_progress(self):
        """Save progress to file"""
        data = {"max_night": self.clamp(self.game_state.max_night_unlocked, 1, 5)}
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass

    def reset_animatronics(self):
        """Reset animatronics to starting positions"""
        self.animatronics = [
            Animatronic("Mr Ingles", "Cafeteria", 0.35, 6.0, "teleport"),
            Animatronic("Janitor Bot", "Bathrooms", 0.30, 7.0, "teleport"),
            Animatronic("Librarian", "Library", 0.25, 8.0, "teleport"),
            Animatronic("Vent Crawler", "Vent", 0.40, 5.0, "vent"),
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
            self.flicker_timer += dt
            if self.flicker_timer > 0.2:
                self.flicker_timer = 0
                self.office.light_dim += (random.random() - 0.5) * 0.3
                self.office.light_dim = self.clamp(self.office.light_dim, 0, 0.8)

        if self.power.current <= 0:
            self.power.current = 0
            if not self.power.outage:
                self.power.outage = True
                self.office.door_left_closed = False
                self.office.door_right_closed = False
                self.office.light_on = False
                self.office.cams_open = False
                self.set_status("POWER OUTAGE.")
                self.static_intensity = 0.8
                self.screen_shake = 3
            return

        # Scale drain based on night length - gentler scaling
        # Default is 60 seconds/hour, scale from 0.7 to 1.3 across the range
        speed_ratio = self.game_state.seconds_per_hour / 60.0
        speed_multiplier = 0.5 + (speed_ratio * 0.5)  # Ranges from 0.75 (at 15s) to 1.25 (at 180s)
        
        drain = self.power.base_drain * speed_multiplier
        if self.office.door_left_closed or self.office.door_right_closed:
            drain += self.power.door_drain * speed_multiplier
        if self.office.light_on:
            drain += self.power.light_drain * speed_multiplier
        if self.office.cams_open:
            drain += self.power.cam_drain * speed_multiplier

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
            anim.update(dt, self.game_state)
        
        # Second pass: AI coordination and communication
        self.coordinate_animatronics(dt)
        
        # Third pass: check for attacks and blocked behaviors
        for anim in self.animatronics:
            # Check if animatronic was blocked by a door
            blocked_side = anim.get_blocked_side(self.office)
            if blocked_side and anim.room == "Office":
                # Restore a door use when it blocks an attack
                if blocked_side == "left" and self.office.door_left_uses < 3:
                    self.office.door_left_uses += 1
                    self.set_status(f"Left door repaired! Uses: {self.office.door_left_uses}")
                elif blocked_side == "right" and self.office.door_right_uses < 3:
                    self.office.door_right_uses += 1
                    self.set_status(f"Right door repaired! Uses: {self.office.door_right_uses}")
            # Check if animatronic should attack
            if anim.try_attack(self.office):
                self.jumpscare.killer = anim.name
                self.jumpscare.active = True
                self.jumpscare.timer = 0
                self.game_state.state = "jumpscare"
                self.assets.play_sound("jumpscare")
                self.assets.stop_music()
                break

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
                    # Coordinate: 40% chance to join the hunt
                    if random.random() < 0.4:
                        anim.hunting_mode = True
                        anim.hunt_target_room = target_room
                        anim.mood = "hunting"
                        anim.communication_cooldown = random.uniform(5, 10)
        
        # Predict player door preference and adapt strategy
        for anim in self.animatronics:
            if anim.player_action_memory:
                recent_actions = [a for a in anim.player_action_memory if time.time() - a["time"] < 60]
                if len(recent_actions) > 2:
                    # Player is blocking a specific side repeatedly
                    blocked_sides = [a["side"] for a in recent_actions[-5:]]
                    if blocked_sides.count("left") > blocked_sides.count("right"):
                        anim.prefer_side = "right"  # Try to attack from other side
                    elif blocked_sides.count("right") > blocked_sides.count("left"):
                        anim.prefer_side = "left"
        
        # Pack hunting behavior: multiple animatronics moving together
        at_office = [a for a in self.animatronics if a.room == "Office"]
        if len(at_office) >= 2 and random.random() < 0.1:
            # Increase mood and aggression for coordinated attack
            for anim in at_office:
                anim.mood = "aggressive"
                anim.adaptive_aggro += 0.1
                anim.block_count += 1  # simulate frustration from failed attacks

    def update(self, dt):
        """Main update loop"""
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

        self.update_office_effects(dt)

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
            for _ in range(30):
                x = random.randint(0, self.game_state.width)
                y = random.randint(0, self.game_state.height)
                w = random.randint(4, 14)
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
        
        # Door uses indicator
        left_color = (255, 50, 50) if self.office.door_left_uses == 0 else (100, 200, 255)
        right_color = (255, 50, 50) if self.office.door_right_uses == 0 else (100, 200, 255)
        door_text = self.font_small.render(f"L-DOOR: {self.office.door_left_uses}  R-DOOR: {self.office.door_right_uses}", True, (200, 200, 200))
        self.screen.blit(door_text, (30, self.game_state.height - 25))

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

        # Controls help moved to above (door uses display replaced it)
        # Draw minimap when not using cameras
        if not self.office.cams_open:
            self.draw_minimap()

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
        hint_rect = hint_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.92)))
        self.screen.blit(hint_text, hint_rect)
        
        # Night length slider
        slider_width = 420
        slider_height = 8
        slider_x = (self.game_state.width - slider_width) // 2
        slider_y = int(self.game_state.height * 0.86)
        # Track
        pygame.draw.rect(self.screen, (60, 60, 90), (slider_x, slider_y, slider_width, slider_height))
        # Fill based on current value
        val = self.clamp(self.game_state.seconds_per_hour, self.slider_min, self.slider_max)
        t = (val - self.slider_min) / (self.slider_max - self.slider_min)
        fill_w = int(slider_width * t)
        pygame.draw.rect(self.screen, (20, 150, 220), (slider_x, slider_y, fill_w, slider_height))
        # Knob
        knob_x = slider_x + fill_w
        knob_rect = pygame.Rect(knob_x - 8, slider_y - 6, 16, 20)
        pygame.draw.rect(self.screen, (200, 200, 255), knob_rect)

        # Slider label and value
        night_seconds = int(self.game_state.seconds_per_hour)
        minutes_total = int((self.game_state.seconds_per_hour * 6) / 60)
        label = self.font_small.render(f"Night Length: {night_seconds}s/hour  (~{minutes_total} min/night)", True, (200, 255, 200))
        label_rect = label.get_rect(center=(self.game_state.width // 2, slider_y - 18))
        self.screen.blit(label, label_rect)

        # Slider hint
        slider_hint = self.font_small.render("Drag slider or use ← / → to adjust", True, (150, 180, 200))
        hint_rect2 = slider_hint.get_rect(center=(self.game_state.width // 2, slider_y + 30))
        self.screen.blit(slider_hint, hint_rect2)

        # Subtle static for creepy vibe
        self.apply_creepy_static(0.05)

    def draw_jumpscare(self):
        """Draw jumpscare screen"""
        # Intense red screen
        intensity = 0.7 + 0.3 * math.sin(self.jumpscare.timer * 15)
        self.screen.fill((int(100 * intensity), 0, 0))

        # Multiple pulsing overlays for intensity
        for i in range(3):
            alpha = int(255 * (0.3 + 0.4 * math.sin(self.jumpscare.timer * (20 + i * 5))))
            jumpscare_surface = pygame.Surface((self.game_state.width, self.game_state.height))
            jumpscare_surface.set_alpha(alpha)
            jumpscare_surface.fill((255, 20, 20))
            self.screen.blit(jumpscare_surface, (0, 0))

        # Jumpscare text with pulsing
        scale = 1.0 + 0.1 * math.sin(self.jumpscare.timer * 8)
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
                # Closing door - costs a use
                if self.office.door_left_uses > 0:
                    self.office.door_left_closed = True
                    self.office.door_left_uses -= 1
                    sound = "door_close"
                else:
                    self.set_status("Left door broken!")
                    return
            self.assets.play_sound(sound)
        elif side == "right":
            if self.office.door_right_closed:
                # Opening door
                self.office.door_right_closed = False
                sound = "door_open"
            else:
                # Closing door - costs a use
                if self.office.door_right_uses > 0:
                    self.office.door_right_closed = True
                    self.office.door_right_uses -= 1
                    sound = "door_close"
                else:
                    self.set_status("Right door broken!")
                    return
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
                    slider_y = int(self.game_state.height * 0.86)
                    if slider_x <= mx <= slider_x + slider_width and slider_y - 12 <= my <= slider_y + 24:
                        # start dragging and update value
                        self.dragging_slider = True
                        t = (mx - slider_x) / slider_width
                        self.game_state.seconds_per_hour = self.clamp(self.slider_min + t * (self.slider_max - self.slider_min), self.slider_min, self.slider_max)
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
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_slider and self.game_state.state == "menu":
                    mx, my = event.pos
                    slider_width = 420
                    slider_x = (self.game_state.width - slider_width) // 2
                    t = (mx - slider_x) / slider_width
                    self.game_state.seconds_per_hour = self.clamp(self.slider_min + t * (self.slider_max - self.slider_min), self.slider_min, self.slider_max)
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

                elif self.game_state.state == "playing":
                    if key == "q":
                        self.toggle_door("left")
                    elif key == "e":
                        self.toggle_door("right")
                    elif key == "f":
                        self.toggle_flashlight()
                    elif key == "tab":
                        self.toggle_cameras()
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

#!/usr/bin/env python3
"""
Five Nights at Mr Ingles's - Python Edition (Pygame)
Faithful port of the LOVE2D game to Python
"""

import pygame
import sys
import os
import json
import math
import random
import time

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
        self.base_drain = 0.35
        self.door_drain = 0.50
        self.light_drain = 0.50
        self.cam_drain = 0.60
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

    def reset(self):
        self.door_left_closed = False
        self.door_right_closed = False
        self.light_on = True
        self.cams_open = False
        self.door_left_progress = 0.0
        self.door_right_progress = 0.0
        self.light_dim = 0.0
        self.cam_flash = 0.0


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
    "Vent": ["Bathrooms", "Office"],
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
    """Animatronic character"""
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

    def update(self, dt):
        """Update animatronic position and behavior"""
        self.timer += dt
        interval = self.move_interval
        chance = self.aggro

        if self.timer >= interval:
            self.timer -= interval
            if random.random() < chance:
                self.move()

        # Smooth position toward target
        speed = 4 * dt
        self.x += (self.target_x - self.x) * speed
        self.y += (self.target_y - self.y) * speed

    def move(self):
        """Move to a random adjacent room"""
        neighbors = get_neighbors(self.room)
        if neighbors:
            self.room = random.choice(neighbors)
            self.target_x, self.target_y = room_position(self.room, WINDOW_WIDTH, WINDOW_HEIGHT)

    def try_attack(self, office):
        """Try to attack if in office"""
        if self.room == "Office":
            # Vent crawler ignores doors
            if self.name == "Vent Crawler":
                return True
            # Other animatronics need doors open
            if not office.door_left_closed or not office.door_right_closed:
                return True
        return False


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

        # Fonts
        self.font_small = pygame.font.Font(None, 14)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 40)

        # Load everything
        self.assets.load_all_assets()
        self.load_save()

        if self.game_state.state == "menu":
            self.play_menu_music()

    def clamp(self, x, a, b):
        """Clamp value between a and b"""
        return max(a, min(x, b))

    def set_status(self, msg):
        """Set status message"""
        self.game_state.status = msg or ""

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
        self.game_state.state = "playing"
        self.set_status("")
        self.power.reset()
        self.office.reset()
        self.reset_animatronics()
        self.jumpscare.reset()
        self.cameras.current_index = 0

        # Load and play night ambience
        ambience_key = f"ambience_n{self.game_state.night}"
        self.assets.play_music(ambience_key)

        self.game_state.start_time = time.time()

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

    def update_power(self, dt):
        """Update power drain"""
        if self.game_state.state != "playing":
            return

        if self.power.current <= 0:
            self.power.current = 0
            if not self.power.outage:
                self.power.outage = True
                self.office.door_left_closed = False
                self.office.door_right_closed = False
                self.office.light_on = False
                self.office.cams_open = False
                self.set_status("POWER OUTAGE.")
            return

        drain = self.power.base_drain
        if self.office.door_left_closed or self.office.door_right_closed:
            drain += self.power.door_drain
        if self.office.light_on:
            drain += self.power.light_drain
        if self.office.cams_open:
            drain += self.power.cam_drain

        self.power.current -= drain * dt
        if self.power.current < 0:
            self.power.current = 0

    def update_time(self, dt):
        """Update in-game time"""
        if self.game_state.state != "playing":
            return

        self.game_state.hour_timer += dt
        if self.game_state.hour_timer >= self.game_state.seconds_per_hour:
            self.game_state.hour_timer -= self.game_state.seconds_per_hour
            self.game_state.hour += 1

            if self.game_state.hour >= 6:
                self.game_state.state = "win"
                self.set_status(f"6 AM! You survived Night {self.game_state.night}!")
                self.assets.play_sound("bell_6am")
                self.assets.stop_music()

                if (self.game_state.night < 5 and
                    self.game_state.night + 1 > self.game_state.max_night_unlocked):
                    self.game_state.max_night_unlocked = self.game_state.night + 1
                    self.save_progress()

    def update_animatronics(self, dt):
        """Update all animatronics"""
        for anim in self.animatronics:
            anim.update(dt)
            # Check if animatronic should attack
            if anim.try_attack(self.office):
                self.jumpscare.killer = anim.name
                self.jumpscare.active = True
                self.jumpscare.timer = 0
                self.game_state.state = "jumpscare"
                self.assets.play_sound("jumpscare")
                self.assets.stop_music()

    def update(self, dt):
        """Main update loop"""
        if self.game_state.state == "menu":
            return

        if self.game_state.state == "playing":
            self.update_power(dt)
            self.update_time(dt)
            self.update_animatronics(dt)
        elif self.game_state.state == "jumpscare":
            self.jumpscare.timer += dt

        self.update_office_effects(dt)

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
        # Only draw if in visible rooms
        if anim.room not in ["Hallway", "Office"]:
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
                slide = 1 - self.office.door_left_progress
                x = -scaled.get_width() * (1 - slide)
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

        # Scanlines overlay
        for y in range(0, self.game_state.height, 8):
            pygame.draw.line(self.screen, (0, 255, 255), (0, y), (self.game_state.width, y))
            pygame.draw.line(self.screen, (0, 255, 255), (0, y), (self.game_state.width, y))

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

    def draw_anims(self):
        """Draw animatronics (office or camera view)"""
        if self.office.cams_open:
            self.draw_camera_feed()
        else:
            self.draw_office_view()

    def draw_hud(self):
        """Draw heads-up display"""
        # Power indicator
        power_val = int(self.power.current + 0.5)
        power_color = (255, 0, 0) if power_val <= 20 else (0, 255, 0)
        power_text = self.font_small.render(f"POWER: {power_val}%", True, power_color)
        self.screen.blit(power_text, (20, self.game_state.height - 40))

        # Time indicator
        hour = self.game_state.hour if self.game_state.hour != 0 else 12
        time_text = self.font_small.render(f"{hour} AM", True, (204, 204, 255))
        self.screen.blit(time_text, (self.game_state.width - 90, 20))

        # Night indicator
        night_text = self.font_small.render(f"Night {self.game_state.night}", True, (255, 255, 255))
        self.screen.blit(night_text, (20, 20))

        # Status message
        if self.game_state.status:
            status_text = self.font_medium.render(self.game_state.status, True, (255, 255, 128))
            text_rect = status_text.get_rect(center=(self.game_state.width // 2, 
                int(self.game_state.height * 0.08)))
            self.screen.blit(status_text, text_rect)

        # Controls help
        controls = "[Q] Left Door  [E] Right Door  [F] Light  [TAB] Cameras  [1-6] Switch Cams"
        controls_text = self.font_small.render(controls, True, (179, 179, 179))
        self.screen.blit(controls_text, (20, self.game_state.height - 20))

    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill((0, 0, 25))

        # Title
        title = self.font_large.render("FIVE NIGHTS AT MR INGLES'S", True, (0, 255, 255))
        title_rect = title.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.2)))
        self.screen.blit(title, title_rect)

        # Instructions
        inst_text = self.font_medium.render("Press 1-5 to start a night", True, (255, 255, 255))
        inst2_text = self.font_small.render("(locked nights are disabled)", True, (255, 255, 255))
        inst_rect = inst_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.4)))
        inst2_rect = inst2_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.45)))
        self.screen.blit(inst_text, inst_rect)
        self.screen.blit(inst2_text, inst2_rect)

        # Unlocked nights
        if self.game_state.max_night_unlocked == 1:
            unlocked_text = "Unlocked nights: 1"
        else:
            unlocked_text = f"Unlocked nights: 1-{self.game_state.max_night_unlocked}"
        unlocked = self.font_small.render(unlocked_text, True, (179, 179, 179))
        unlocked_rect = unlocked.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.55)))
        self.screen.blit(unlocked, unlocked_rect)

    def draw_jumpscare(self):
        """Draw jumpscare screen"""
        self.screen.fill((76, 0, 0))

        # Pulsing red overlay
        alpha = int(255 * (0.5 + 0.5 * math.sin(self.jumpscare.timer * 30)))
        jumpscare_surface = pygame.Surface((self.game_state.width, self.game_state.height))
        jumpscare_surface.set_alpha(alpha)
        jumpscare_surface.fill((255, 0, 0))
        self.screen.blit(jumpscare_surface, (0, 0))

        # Jumpscare text
        jumpscare_text = self.font_large.render(f"{self.jumpscare.killer} GOT YOU!", True, (255, 255, 255))
        jumpscare_rect = jumpscare_text.get_rect(center=(self.game_state.width // 2, 
            int(self.game_state.height * 0.3)))
        self.screen.blit(jumpscare_text, jumpscare_rect)

        # Restart instructions
        restart_text = self.font_medium.render("Press [R] to restart Night 1  |  [M] for Menu", 
            True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.game_state.width // 2,
            int(self.game_state.height * 0.6)))
        self.screen.blit(restart_text, restart_rect)

    def draw_win(self):
        """Draw win screen"""
        self.screen.fill((0, 25, 0))

        # Win text
        win_text = self.font_large.render("6 AM", True, (153, 255, 153))
        win_rect = win_text.get_rect(center=(self.game_state.width // 2, int(self.game_state.height * 0.3)))
        self.screen.blit(win_text, win_rect)

        # Survived message
        survived_text = self.font_medium.render(f"You survived Night {self.game_state.night}!", True, (255, 255, 255))
        survived_rect = survived_text.get_rect(center=(self.game_state.width // 2, 
            int(self.game_state.height * 0.4)))
        self.screen.blit(survived_text, survived_rect)

        # Restart instructions
        restart_text = self.font_medium.render("Press [R] to restart Night 1  |  [M] for Menu",
            True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.game_state.width // 2,
            int(self.game_state.height * 0.6)))
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        """Main draw loop"""
        if self.game_state.state == "menu":
            self.draw_menu()
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

    # =====================================================
    # INPUT HANDLING
    # =====================================================

    def toggle_door(self, side):
        """Toggle a door"""
        if self.power.outage:
            return

        if side == "left":
            self.office.door_left_closed = not self.office.door_left_closed
            sound = "door_close" if self.office.door_left_closed else "door_open"
            self.assets.play_sound(sound)
        elif side == "right":
            self.office.door_right_closed = not self.office.door_right_closed
            sound = "door_close" if self.office.door_right_closed else "door_open"
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

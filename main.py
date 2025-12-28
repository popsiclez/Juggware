import dearpygui.dearpygui as dpg
import urllib.request
import ctypes
import ctypes.wintypes
import win32gui
import win32api
import win32con
import winsound
import time
import psutil
import os
import shutil
import atexit
import subprocess
import threading
import json
import math
import pymem
import pymem.process
import struct
import numpy as np
import sys
import pyautogui
from PIL import ImageGrab
from scipy.signal import convolve2d
from pynput.mouse import Controller as MouseController, Button as MouseButton

# PyImGui imports for GPU-accelerated overlay
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *


# Skip loader flag - set to True to bypass loader and load cheat directly
SKIP_LOADER = True

# Graphics reset flag - set to True to reset graphics before starting cheat
RESET_GRAPHICS = False

# Delay in seconds before starting cheat after graphics reset
RESET_GRAPHICS_DELAY = 10


# =============================================================================
# CONSTANTS
# =============================================================================

# Remote configuration
TITLE_URL = "https://raw.githubusercontent.com/popsiclez/Juggware/refs/heads/main/title"
STATUS_URL = "https://raw.githubusercontent.com/popsiclez/Juggware/refs/heads/main/cheatstatus"
VERSION_URL = "https://raw.githubusercontent.com/popsiclez/Juggware/refs/heads/main/cheatversion"
FALLBACK_TITLE = "CS2 Cheat"

# Offsets download URL
OFFSETS_URL = "https://www.dropbox.com/scl/fi/3w66y2kzkbn3x8mjnsfkq/offsets.exe?rlkey=fd423j7k5ljbz913bp74f9jnr&st=l99v5czg&dl=1"

# GitHub offsets URLs
GITHUB_OFFSETS_URL = "https://raw.githubusercontent.com/popsiclez/offsets/refs/heads/main/output/offsets.json"
GITHUB_CLIENT_DLL_URL = "https://raw.githubusercontent.com/popsiclez/offsets/refs/heads/main/output/client_dll.json"

# Sound file URLs
HITMARKER_SOUND_URL = "https://www.dropbox.com/scl/fi/zculofdxbyhrw0ra39lz3/hitmarker.wav?rlkey=lnqoq2kqigujegqkn17ofwnc2&st=8pt44bmy&dl=1"
METALHIT_SOUND_URL = "https://www.dropbox.com/scl/fi/o0u1eum40x6plywnf3wd9/metal.wav?rlkey=df5lg3s2yxvsxrx1wj34ama5i&st=3uyrtqeu&dl=1"
CRITICALHIT_SOUND_URL = "https://www.dropbox.com/scl/fi/r3b55ge6sug7oeop6xnkr/criticalhit.wav?rlkey=7xu9h4j7kq70i0djcihkj9a13&st=t3ef4ihn&dl=1"

# Window dimensions
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
TITLEBAR_HEIGHT = 30

# UI Spacing Constants
UI_SPACING_SMALL = 5    # Small spacing between related elements
UI_SPACING_MEDIUM = 10  # Medium spacing between sections
UI_SPACING_LARGE = 15   # Large spacing between major sections

# Win32 extended window style constants
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080  # Hides window from taskbar and Alt+Tab
WS_EX_APPWINDOW = 0x00040000   # Forces window onto taskbar (we remove this)
WS_EX_LAYERED = 0x00080000     # Layered window (for transparency)
WS_EX_TRANSPARENT = 0x00000020  # Click-through window

# Windows 11 DWM (Desktop Window Manager) constants for rounded corners
# These only work on Windows 11 Build 22000+
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2  # Rounded corners preference

# Temporary folder path (created on startup, deleted on exit)
SCRIPT_DIR = os.getcwd()
TEMP_FOLDER = os.path.join(SCRIPT_DIR, "temp")

# Configuration folder paths
CONFIGS_FOLDER = os.path.join(SCRIPT_DIR, "configs")
SETTINGS_FOLDER = os.path.join(CONFIGS_FOLDER, "Settings")
KEYBINDS_FOLDER = os.path.join(CONFIGS_FOLDER, "Keybinds")
AUTOSAVE_PATH = os.path.join(SETTINGS_FOLDER, "autosave.json")
KEYBINDS_AUTOSAVE_PATH = os.path.join(KEYBINDS_FOLDER, "autosave.json")

# =============================================================================
# GAME CONSTANTS - Bone IDs and Targeting
# =============================================================================
BONE_IDS = {
    "head": 6,
    "neck": 5,
    "spine": 4,
    "pelvis": 0,
    "left_shoulder": 13,
    "left_elbow": 14,
    "left_wrist": 15,
    "right_shoulder": 9,
    "right_elbow": 10,
    "right_wrist": 11,
    "left_hip": 25,
    "left_knee": 26,
    "left_ankle": 27,
    "right_hip": 22,
    "right_knee": 23,
    "right_ankle": 24,
}

BONE_CONNECTIONS = [
    ("head", "neck"),
    ("neck", "spine"),
    ("spine", "pelvis"),
    ("pelvis", "left_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("pelvis", "right_hip"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
    ("neck", "left_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("neck", "right_shoulder"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
]

# Weapon ID to name mapping for ESP weapon labels
WEAPON_NAMES = {
    1: "Deagle",
    2: "Dual Berettas",
    3: "Five-SeveN",
    4: "Glock-18",
    7: "AK-47",
    8: "AUG",
    9: "AWP",
    10: "FAMAS",
    11: "G3SG1",
    13: "Galil AR",
    14: "M249",
    16: "M4A4",
    17: "MAC-10",
    19: "P90",
    24: "UMP-45",
    25: "XM1014",
    26: "PP-Bizon",
    27: "MAG-7",
    28: "Negev",
    29: "Sawed-Off",
    30: "Tec-9",
    31: "Zeus x27",
    32: "P2000",
    33: "MP7",
    34: "MP9",
    35: "Nova",
    36: "P250",
    38: "SCAR-20",
    39: "SG 553",
    40: "SSG 08",
    42: "Knife",
    43: "Flashbang",
    44: "HE Grenade",
    45: "Smoke",
    46: "Molotov",
    47: "Decoy",
    48: "Incendiary",
    49: "C4",
    59: "Knife",
    60: "M4A1-S",
    61: "USP-S",
    63: "CZ75-Auto",
    64: "R8 Revolver",
    500: "Bayonet",
    505: "Flip Knife",
    506: "Gut Knife",
    507: "Karambit",
    508: "M9 Bayonet",
    509: "Tactical",
    512: "Falchion",
    514: "Bowie",
    515: "Butterfly",
    516: "Push Dagger",
    526: "Kukri"
}

# =============================================================================
# CONFIGURATION SYSTEM
# =============================================================================
# Centralized configuration management for ESP settings and keybinds.
# Default_Config serves as the template, Active_Config stores runtime values.
# =============================================================================

# Default Configuration - Template for all settings
Default_Config = {
    "esp_enabled": True,
    "box_esp": True,
    "box_type": "2D",                   # "2D" or "3D"
    "line_esp": True,
    "skeleton_esp": True,
    "health_bar": True,
    "armor_bar": True,
    "healthbar_type": "Vertical Left",   # "Vertical Left", "Vertical Right", "Horizontal Above", "Horizontal Below"
    "name_esp": True,
    "distance_esp": True,
    "weapon_esp": True,
    "hide_unknown_weapons": False,
    "head_dot": True,
    "team_color": (71, 167, 106),      # Legacy - kept for compatibility
    "enemy_color": (196, 30, 58),      # Legacy - kept for compatibility
    "skeleton_color": (255, 255, 255),  # Legacy - kept for compatibility
    "lines_position": "Bottom",         # "Top" or "Bottom"
    "targeting_type": 0,                # 0 = enemies only, 1 = all players
    # ESP Colors - Boxes
    "enemy_box_color": (196, 30, 58),       # Red for enemy boxes
    "team_box_color": (71, 167, 106),       # Green for team boxes
    # ESP Colors - Snaplines
    "enemy_snapline_color": (196, 30, 58),  # Red for enemy snaplines
    "team_snapline_color": (71, 167, 106),  # Green for team snaplines
    # ESP Colors - Skeleton
    "enemy_skeleton_color": (255, 255, 255), # White for enemy skeleton
    "team_skeleton_color": (255, 255, 255),  # White for team skeleton
    # ESP Colors - Head Dot
    "enemy_head_dot_color": (255, 255, 0),   # Yellow for enemy head dot
    "team_head_dot_color": (255, 255, 0),    # Yellow for team head dot
    # Bomb ESP
    "bomb_esp": True,                        # Show planted bomb info
    # Footstep ESP
    "footstep_esp": False,                   # Show footstep rings around enemies making noise
    "footstep_esp_color": (255, 165, 0),     # Orange color for footstep rings
    "footstep_esp_duration": 1.0,            # Duration of ring animation in seconds
    # Antialiasing
    "antialiasing": "4x MSAA",              # "None", "2x MSAA", "4x MSAA", "8x MSAA"
    # Menu Colorway
    "menu_colorway": "Default",             # UI color theme preset
    # Menu Font
    "menu_font": "Default",                 # UI font
    # Window Size
    "window_width": 600,                   # Cheat window width
    "window_height": 400,                  # Cheat window height
    # Menu Transparency
    "menu_transparency": 255,              # Menu window transparency (0-255, 255 = opaque)
    # ESP Thickness
    "box_thickness": 1.5,                   # Box outline thickness (1.0 - 5.0)
    "snapline_thickness": 1.5,              # Snapline thickness (1.0 - 5.0)
    "skeleton_thickness": 1.5,              # Skeleton line thickness (1.0 - 5.0)
    # Radar
    "radar_enabled": False,                 # Enable radar overlay
    "radar_size": 200,                      # Radar diameter in pixels
    "radar_scale": 40.0,                     # Scale factor (higher = zoomed out)
    "radar_x": 0,                           # X offset from screen center (negative = left, positive = right)
    "radar_y": 0,                           # Y offset from screen center (negative = up, positive = down)
    "radar_opacity": 180,                   # Background opacity (0-255)
    "radar_overlap_game": False,            # Lock radar to overlap game radar position
    # Radar Colors
    "radar_bg_color": (0, 0, 0),            # Radar background color
    "radar_border_color": (128, 128, 128),  # Radar border color
    "radar_crosshair_color": (77, 77, 77),  # Radar crosshair color
    "radar_player_color": (255, 255, 255),  # Local player dot color
    "radar_enemy_color": (255, 0, 0),       # Enemy dot color
    "radar_team_color": (0, 255, 0),        # Team dot color
    # Aimbot
    "aimbot_enabled": False,                # Enable aimbot
    "aimbot_radius": 50,                    # Aimbot FOV radius (pixels)
    "aimbot_smoothness": 5.0,               # Aimbot smoothness (1-100)
    "aimbot_movement_type": "Linear",      # Movement type: "Linear" or "Dynamic"
    "aimbot_show_radius": True,             # Show aimbot radius circle
    "aimbot_spotted_check": False,          # Only aim at spotted enemies
    "aimbot_require_key": True,             # Require aimbot key to be held
    "aimbot_lock_target": False,            # Lock to one target per aimkey hold
    "aimbot_target_bone": "Head",           # Target bone for aimbot
    "aimbot_deadzone_enabled": False,       # Enable aimbot deadzone
    "aimbot_deadzone_radius": 10,           # Deadzone radius (pixels)
    "aimbot_show_deadzone": True,          # Show deadzone circle
    "aimbot_snaplines": False,              # Show snaplines to aimbot targets
    # Aimbot Colors
    "aimbot_radius_color": (255, 0, 0),     # Neutral State
    "aimbot_deadzone_color": (255, 255, 0), # Neutral State
    "aimbot_targeting_radius_color": (0, 255, 0),  # Targeting State
    "aimbot_targeting_deadzone_color": (0, 0, 255), # Targeting State
    "aimbot_snapline_color": (255, 255, 255), # Aimbot snapline color
    "aimbot_radius_transparency": 180,      # Aimbot radius circle transparency (0-255)
    "aimbot_deadzone_transparency": 180,    # Aimbot deadzone circle transparency (0-255)
    "aimbot_radius_thickness": 2.0,         # Aimbot radius circle thickness
    "aimbot_deadzone_thickness": 1.5,       # Aimbot deadzone circle thickness
    "aimbot_snapline_thickness": 2.0,       # Aimbot snapline thickness
    # Spotted ESP
    "spotted_esp": True,                    # Show spotted/visibility indicator
    "hide_spotted_players": False,          # Hide ESP elements for spotted players
    "custom_crosshair": False,              # Show custom crosshair at screen center
    "custom_crosshair_scale": 1.0,          # Scale multiplier for crosshair size
    "custom_crosshair_color": (255, 255, 255), # Crosshair color (RGB)
    "custom_crosshair_thickness": 2.0,      # Crosshair line thickness
    "custom_crosshair_shape": "Sus",        # Crosshair shape preset
    "spotted_color": (0, 255, 0),           # Color when spotted (green)
    "not_spotted_color": (255, 0, 0),       # Color when not spotted (red)
    "spotted_text_size": 12.0,              # Spotted text font size
    "name_text_size": 14.0,                 # Nickname text font size
    "weapon_text_size": 11.0,               # Weapon text font size
    # ESP Distance Filter
    "esp_distance_filter_enabled": False,   # Enable distance-based ESP filtering
    "esp_distance_filter_type": "Further than", # "Further than" or "Closer than"
    "esp_distance_filter_distance": 25.0,   # Distance threshold in meters (5-50)
    "esp_distance_filter_mode": "Only Show", # "Only Show" or "Hide"
    # FPS Cap
    "fps_cap_enabled": False,               # Enable FPS limiting
    "fps_cap_value": 144,                   # FPS cap value
    # Triggerbot
    "triggerbot_enabled": False,            # Enable triggerbot
    "triggerbot_first_shot_delay": 0,       # Delay before first shot (ms)
    "triggerbot_between_shots_delay": 30,   # Delay between shots (ms)
    "triggerbot_burst_mode": False,         # Enable burst fire mode
    "triggerbot_burst_shots": 3,            # Number of shots in burst
    "triggerbot_head_only": False,          # Only fire when crosshair is on head
    # Auto Crosshair Placement (ACS)
    "acs_enabled": False,                   # Enable auto crosshair placement
    "acs_target_bone": "Head",              # Target bone (Head, Neck, Chest, Pelvis)
    "acs_smoothness": 5,                    # Movement smoothness (1-50)
    "acs_deadzone": 5,                      # Deadzone in pixels
    "acs_draw_deadzone_lines": False,       # Draw deadzone visualization lines
    "acs_always_show_deadzone_lines": False, # Show deadzone lines without holding key
    "acs_line_width": 2,                    # Deadzone line width (1-10)
    "acs_line_transparency": 80,            # Deadzone line transparency (0-255)
    "acs_line_color": (255, 0, 0),           # Deadzone line color (RGB)
    # Misc Features
    "anti_flash_enabled": False,            # Prevent flashbang blindness
    "hide_on_tabout": True,                 # Hide overlay and menu when tabbing out of CS2
    "show_tooltips": True,                  # Show tooltips on hover
    "show_status_labels": True,             # Show feature status labels in overlay
    # Camera FOV Changer
    "fov_changer_enabled": False,           # Enable FOV modification
    "fov_value": 90,                        # Desired FOV value (68-140)
    # Recoil Control System (RCS)
    "rcs_enabled": False,                   # Enable recoil control
    "rcs_strength_x": 100,                  # Horizontal recoil compensation (0-100%)
    "rcs_strength_y": 100,                  # Vertical recoil compensation (0-100%)
    "rcs_smoothness": 1,                    # RCS smoothness (1-10, 1=instant, 10=very smooth)
    "rcs_multiplier": 2.0,                  # RCS multiplier for fine-tuning (1.8-2.2)
    "rcs_continuous_only": False,           # Only compensate continuous fire, not single shots
    # Hitsound
    "hitsound_enabled": False,              # Enable hitsound
    "hitsound_type": "hitmarker",           # Hitsound type ("hitmarker", "criticalhit", "metalhit")
    # Anti-AFK
    "anti_afk_enabled": False,              # Enable anti-AFK movement
}

# =============================================================================
# UI COLORWAY PRESETS
# =============================================================================
# Predefined color schemes for the cheat menu UI.
# Each colorway defines colors for various UI elements.
# Colors are in RGBA format (0-255).
# =============================================================================

# Available menu fonts (Windows system fonts)
MENU_FONTS = {
    "Default": None,  # Use DearPyGui default font
    "Segoe UI": "C:/Windows/Fonts/segoeui.ttf",
    "Arial": "C:/Windows/Fonts/arial.ttf",
    "Verdana": "C:/Windows/Fonts/verdana.ttf",
    "Tahoma": "C:/Windows/Fonts/tahoma.ttf",
    "Consolas": "C:/Windows/Fonts/consola.ttf",
    "Courier New": "C:/Windows/Fonts/cour.ttf",
    "Trebuchet MS": "C:/Windows/Fonts/trebuc.ttf",
    "Georgia": "C:/Windows/Fonts/georgia.ttf",
    "Comic Sans MS": "C:/Windows/Fonts/comic.ttf",
}

# Font registry tags (populated at runtime)
loaded_fonts = {}

UI_COLORWAYS = {
    "Default": {
        # ImGui default dark theme colors
        "window_bg": (15, 15, 15, 255),
        "title_bg": (10, 10, 10, 255),
        "title_bg_active": (41, 74, 122, 255),
        "frame_bg": (41, 74, 122, 255),
        "frame_bg_hovered": (66, 150, 250, 255),
        "frame_bg_active": (66, 150, 250, 255),
        "button": (66, 150, 250, 255),
        "button_hovered": (66, 150, 250, 255),
        "button_active": (15, 135, 250, 255),
        "tab": (46, 89, 148, 255),
        "tab_hovered": (66, 150, 250, 255),
        "tab_active": (51, 105, 173, 255),
        "text": (255, 255, 255, 255),
        "check_mark": (66, 150, 250, 255),
        "slider_grab": (66, 150, 250, 255),
        "header": (66, 150, 250, 255),
        "header_hovered": (66, 150, 250, 255),
        "header_active": (66, 150, 250, 255),
    },
    "Light Blue": {
        "window_bg": (35, 45, 55, 255),
        "title_bg": (28, 38, 48, 255),
        "title_bg_active": (60, 140, 200, 255),
        "frame_bg": (50, 90, 130, 255),
        "frame_bg_hovered": (70, 130, 180, 255),
        "frame_bg_active": (90, 160, 220, 255),
        "button": (70, 140, 200, 255),
        "button_hovered": (100, 170, 230, 255),
        "button_active": (50, 120, 180, 255),
        "tab": (50, 100, 150, 255),
        "tab_hovered": (80, 150, 210, 255),
        "tab_active": (70, 140, 200, 255),
        "text": (230, 245, 255, 255),
        "check_mark": (120, 200, 255, 255),
        "slider_grab": (100, 180, 250, 255),
        "header": (60, 120, 180, 255),
        "header_hovered": (80, 150, 210, 255),
        "header_active": (100, 170, 230, 255),
    },
    "Dark Blue": {
        "window_bg": (12, 18, 28, 255),
        "title_bg": (8, 12, 20, 255),
        "title_bg_active": (20, 50, 90, 255),
        "frame_bg": (18, 35, 60, 255),
        "frame_bg_hovered": (25, 50, 85, 255),
        "frame_bg_active": (35, 70, 115, 255),
        "button": (25, 55, 95, 255),
        "button_hovered": (35, 75, 125, 255),
        "button_active": (20, 45, 80, 255),
        "tab": (15, 35, 60, 255),
        "tab_hovered": (30, 60, 100, 255),
        "tab_active": (25, 55, 95, 255),
        "text": (180, 200, 230, 255),
        "check_mark": (70, 140, 220, 255),
        "slider_grab": (50, 110, 190, 255),
        "header": (20, 45, 80, 255),
        "header_hovered": (30, 60, 105, 255),
        "header_active": (40, 80, 130, 255),
    },
    "Light Red": {
        "window_bg": (55, 35, 38, 255),
        "title_bg": (45, 28, 30, 255),
        "title_bg_active": (180, 70, 80, 255),
        "frame_bg": (120, 55, 65, 255),
        "frame_bg_hovered": (160, 75, 85, 255),
        "frame_bg_active": (200, 95, 105, 255),
        "button": (180, 70, 80, 255),
        "button_hovered": (210, 100, 110, 255),
        "button_active": (150, 55, 65, 255),
        "tab": (130, 55, 65, 255),
        "tab_hovered": (180, 80, 90, 255),
        "tab_active": (160, 70, 80, 255),
        "text": (255, 230, 235, 255),
        "check_mark": (255, 140, 150, 255),
        "slider_grab": (230, 110, 120, 255),
        "header": (150, 60, 70, 255),
        "header_hovered": (180, 80, 90, 255),
        "header_active": (200, 100, 110, 255),
    },
    "Dark Red": {
        "window_bg": (28, 12, 15, 255),
        "title_bg": (20, 8, 10, 255),
        "title_bg_active": (80, 25, 35, 255),
        "frame_bg": (55, 18, 25, 255),
        "frame_bg_hovered": (80, 28, 38, 255),
        "frame_bg_active": (110, 40, 52, 255),
        "button": (90, 30, 40, 255),
        "button_hovered": (120, 45, 58, 255),
        "button_active": (70, 22, 32, 255),
        "tab": (60, 20, 28, 255),
        "tab_hovered": (95, 35, 48, 255),
        "tab_active": (80, 28, 38, 255),
        "text": (230, 180, 190, 255),
        "check_mark": (220, 80, 100, 255),
        "slider_grab": (180, 60, 80, 255),
        "header": (70, 25, 35, 255),
        "header_hovered": (100, 38, 50, 255),
        "header_active": (120, 50, 65, 255),
    },
    "Light Green": {
        "window_bg": (35, 55, 40, 255),
        "title_bg": (28, 45, 32, 255),
        "title_bg_active": (70, 170, 90, 255),
        "frame_bg": (55, 115, 70, 255),
        "frame_bg_hovered": (75, 155, 95, 255),
        "frame_bg_active": (95, 190, 115, 255),
        "button": (70, 160, 90, 255),
        "button_hovered": (100, 195, 120, 255),
        "button_active": (55, 130, 72, 255),
        "tab": (55, 120, 72, 255),
        "tab_hovered": (80, 170, 100, 255),
        "tab_active": (70, 155, 88, 255),
        "text": (230, 255, 235, 255),
        "check_mark": (140, 255, 165, 255),
        "slider_grab": (110, 220, 135, 255),
        "header": (60, 130, 78, 255),
        "header_hovered": (80, 165, 100, 255),
        "header_active": (100, 190, 120, 255),
    },
    "Dark Green": {
        "window_bg": (12, 25, 15, 255),
        "title_bg": (8, 18, 10, 255),
        "title_bg_active": (25, 75, 35, 255),
        "frame_bg": (18, 50, 25, 255),
        "frame_bg_hovered": (28, 75, 38, 255),
        "frame_bg_active": (40, 100, 52, 255),
        "button": (30, 85, 42, 255),
        "button_hovered": (45, 115, 58, 255),
        "button_active": (22, 65, 32, 255),
        "tab": (20, 55, 28, 255),
        "tab_hovered": (35, 90, 48, 255),
        "tab_active": (28, 75, 38, 255),
        "text": (180, 230, 190, 255),
        "check_mark": (80, 200, 105, 255),
        "slider_grab": (60, 160, 82, 255),
        "header": (25, 65, 35, 255),
        "header_hovered": (38, 95, 50, 255),
        "header_active": (50, 120, 65, 255),
    },
    "Light Purple": {
        "window_bg": (48, 38, 58, 255),
        "title_bg": (38, 30, 48, 255),
        "title_bg_active": (140, 100, 180, 255),
        "frame_bg": (95, 70, 125, 255),
        "frame_bg_hovered": (130, 95, 165, 255),
        "frame_bg_active": (165, 125, 200, 255),
        "button": (140, 100, 180, 255),
        "button_hovered": (175, 135, 215, 255),
        "button_active": (110, 78, 148, 255),
        "tab": (100, 72, 130, 255),
        "tab_hovered": (150, 110, 190, 255),
        "tab_active": (130, 95, 170, 255),
        "text": (240, 230, 255, 255),
        "check_mark": (200, 160, 255, 255),
        "slider_grab": (170, 130, 220, 255),
        "header": (115, 82, 150, 255),
        "header_hovered": (145, 108, 185, 255),
        "header_active": (170, 130, 210, 255),
    },
    "Dark Purple": {
        "window_bg": (20, 14, 28, 255),
        "title_bg": (14, 10, 20, 255),
        "title_bg_active": (55, 35, 80, 255),
        "frame_bg": (38, 25, 55, 255),
        "frame_bg_hovered": (55, 38, 80, 255),
        "frame_bg_active": (75, 52, 108, 255),
        "button": (65, 42, 95, 255),
        "button_hovered": (88, 60, 125, 255),
        "button_active": (50, 32, 75, 255),
        "tab": (42, 28, 62, 255),
        "tab_hovered": (68, 48, 100, 255),
        "tab_active": (55, 38, 82, 255),
        "text": (210, 195, 235, 255),
        "check_mark": (150, 110, 210, 255),
        "slider_grab": (120, 85, 175, 255),
        "header": (50, 35, 75, 255),
        "header_hovered": (72, 50, 105, 255),
        "header_active": (92, 65, 132, 255),
    },
    "Light Pink": {
        "window_bg": (55, 38, 50, 255),
        "title_bg": (45, 30, 42, 255),
        "title_bg_active": (200, 100, 160, 255),
        "frame_bg": (140, 70, 115, 255),
        "frame_bg_hovered": (180, 95, 150, 255),
        "frame_bg_active": (220, 120, 180, 255),
        "button": (200, 100, 160, 255),
        "button_hovered": (235, 135, 195, 255),
        "button_active": (165, 78, 130, 255),
        "tab": (145, 75, 120, 255),
        "tab_hovered": (205, 110, 170, 255),
        "tab_active": (185, 95, 152, 255),
        "text": (255, 235, 248, 255),
        "check_mark": (255, 160, 210, 255),
        "slider_grab": (235, 130, 190, 255),
        "header": (160, 85, 135, 255),
        "header_hovered": (195, 112, 165, 255),
        "header_active": (220, 135, 185, 255),
    },
    "Dark Pink": {
        "window_bg": (28, 14, 24, 255),
        "title_bg": (20, 10, 18, 255),
        "title_bg_active": (90, 35, 70, 255),
        "frame_bg": (60, 25, 48, 255),
        "frame_bg_hovered": (88, 38, 70, 255),
        "frame_bg_active": (118, 52, 95, 255),
        "button": (100, 40, 78, 255),
        "button_hovered": (132, 58, 105, 255),
        "button_active": (78, 30, 60, 255),
        "tab": (65, 28, 52, 255),
        "tab_hovered": (105, 45, 85, 255),
        "tab_active": (88, 38, 70, 255),
        "text": (235, 195, 220, 255),
        "check_mark": (230, 100, 175, 255),
        "slider_grab": (190, 75, 145, 255),
        "header": (78, 32, 62, 255),
        "header_hovered": (108, 48, 88, 255),
        "header_active": (135, 62, 108, 255),
    },
    "Light Gray": {
        "window_bg": (55, 55, 58, 255),
        "title_bg": (45, 45, 48, 255),
        "title_bg_active": (120, 120, 130, 255),
        "frame_bg": (85, 85, 92, 255),
        "frame_bg_hovered": (110, 110, 118, 255),
        "frame_bg_active": (135, 135, 145, 255),
        "button": (115, 115, 125, 255),
        "button_hovered": (145, 145, 155, 255),
        "button_active": (95, 95, 105, 255),
        "tab": (90, 90, 98, 255),
        "tab_hovered": (125, 125, 135, 255),
        "tab_active": (110, 110, 120, 255),
        "text": (245, 245, 248, 255),
        "check_mark": (180, 180, 195, 255),
        "slider_grab": (155, 155, 170, 255),
        "header": (100, 100, 110, 255),
        "header_hovered": (130, 130, 142, 255),
        "header_active": (155, 155, 168, 255),
    },
    "Dark Gray": {
        "window_bg": (22, 22, 25, 255),
        "title_bg": (15, 15, 18, 255),
        "title_bg_active": (45, 45, 52, 255),
        "frame_bg": (35, 35, 40, 255),
        "frame_bg_hovered": (48, 48, 55, 255),
        "frame_bg_active": (62, 62, 70, 255),
        "button": (45, 45, 52, 255),
        "button_hovered": (60, 60, 68, 255),
        "button_active": (35, 35, 42, 255),
        "tab": (32, 32, 38, 255),
        "tab_hovered": (52, 52, 60, 255),
        "tab_active": (42, 42, 50, 255),
        "text": (185, 185, 195, 255),
        "check_mark": (120, 120, 135, 255),
        "slider_grab": (95, 95, 108, 255),
        "header": (40, 40, 48, 255),
        "header_hovered": (55, 55, 65, 255),
        "header_active": (68, 68, 78, 255),
    },
    "Light Yellow": {
        "window_bg": (55, 52, 35, 255),
        "title_bg": (45, 42, 28, 255),
        "title_bg_active": (200, 180, 70, 255),
        "frame_bg": (140, 125, 55, 255),
        "frame_bg_hovered": (180, 160, 75, 255),
        "frame_bg_active": (220, 195, 95, 255),
        "button": (200, 180, 70, 255),
        "button_hovered": (235, 215, 100, 255),
        "button_active": (165, 148, 55, 255),
        "tab": (145, 130, 58, 255),
        "tab_hovered": (205, 185, 85, 255),
        "tab_active": (185, 165, 72, 255),
        "text": (255, 252, 230, 255),
        "check_mark": (255, 240, 140, 255),
        "slider_grab": (235, 215, 110, 255),
        "header": (160, 145, 62, 255),
        "header_hovered": (195, 175, 82, 255),
        "header_active": (220, 198, 100, 255),
    },
    "Dark Yellow": {
        "window_bg": (28, 26, 12, 255),
        "title_bg": (20, 18, 8, 255),
        "title_bg_active": (90, 80, 25, 255),
        "frame_bg": (60, 54, 18, 255),
        "frame_bg_hovered": (88, 78, 28, 255),
        "frame_bg_active": (118, 105, 38, 255),
        "button": (100, 90, 30, 255),
        "button_hovered": (132, 118, 45, 255),
        "button_active": (78, 70, 22, 255),
        "tab": (65, 58, 20, 255),
        "tab_hovered": (105, 94, 35, 255),
        "tab_active": (88, 78, 28, 255),
        "text": (235, 230, 180, 255),
        "check_mark": (230, 210, 80, 255),
        "slider_grab": (190, 170, 60, 255),
        "header": (78, 70, 25, 255),
        "header_hovered": (108, 96, 38, 255),
        "header_active": (135, 120, 50, 255),
    },
    "Light Orange": {
        "window_bg": (55, 42, 35, 255),
        "title_bg": (45, 34, 28, 255),
        "title_bg_active": (220, 140, 60, 255),
        "frame_bg": (155, 95, 50, 255),
        "frame_bg_hovered": (195, 125, 70, 255),
        "frame_bg_active": (235, 155, 90, 255),
        "button": (220, 140, 60, 255),
        "button_hovered": (250, 175, 95, 255),
        "button_active": (185, 115, 48, 255),
        "tab": (160, 100, 52, 255),
        "tab_hovered": (225, 150, 75, 255),
        "tab_active": (200, 128, 65, 255),
        "text": (255, 245, 230, 255),
        "check_mark": (255, 195, 120, 255),
        "slider_grab": (245, 165, 95, 255),
        "header": (175, 110, 58, 255),
        "header_hovered": (210, 140, 78, 255),
        "header_active": (240, 165, 98, 255),
    },
    "Dark Orange": {
        "window_bg": (28, 18, 12, 255),
        "title_bg": (20, 12, 8, 255),
        "title_bg_active": (100, 55, 20, 255),
        "frame_bg": (68, 38, 18, 255),
        "frame_bg_hovered": (98, 55, 28, 255),
        "frame_bg_active": (130, 75, 40, 255),
        "button": (115, 62, 25, 255),
        "button_hovered": (150, 85, 40, 255),
        "button_active": (88, 48, 18, 255),
        "tab": (72, 40, 18, 255),
        "tab_hovered": (120, 68, 32, 255),
        "tab_active": (98, 55, 25, 255),
        "text": (235, 210, 185, 255),
        "check_mark": (240, 150, 70, 255),
        "slider_grab": (200, 115, 50, 255),
        "header": (85, 48, 22, 255),
        "header_hovered": (118, 68, 35, 255),
        "header_active": (145, 85, 48, 255),
    },
    "Light Brown": {
        "window_bg": (52, 45, 38, 255),
        "title_bg": (42, 36, 30, 255),
        "title_bg_active": (165, 120, 80, 255),
        "frame_bg": (115, 85, 58, 255),
        "frame_bg_hovered": (150, 112, 78, 255),
        "frame_bg_active": (185, 140, 98, 255),
        "button": (165, 120, 80, 255),
        "button_hovered": (198, 155, 115, 255),
        "button_active": (138, 98, 65, 255),
        "tab": (120, 88, 60, 255),
        "tab_hovered": (170, 128, 90, 255),
        "tab_active": (150, 110, 75, 255),
        "text": (255, 248, 235, 255),
        "check_mark": (220, 180, 140, 255),
        "slider_grab": (195, 150, 110, 255),
        "header": (135, 100, 68, 255),
        "header_hovered": (165, 125, 88, 255),
        "header_active": (190, 148, 108, 255),
    },
    "Dark Brown": {
        "window_bg": (25, 20, 16, 255),
        "title_bg": (18, 14, 10, 255),
        "title_bg_active": (75, 52, 32, 255),
        "frame_bg": (52, 38, 25, 255),
        "frame_bg_hovered": (75, 55, 38, 255),
        "frame_bg_active": (100, 75, 52, 255),
        "button": (85, 60, 38, 255),
        "button_hovered": (115, 85, 58, 255),
        "button_active": (65, 45, 28, 255),
        "tab": (55, 40, 28, 255),
        "tab_hovered": (90, 65, 45, 255),
        "tab_active": (75, 55, 38, 255),
        "text": (225, 210, 190, 255),
        "check_mark": (185, 145, 100, 255),
        "slider_grab": (150, 115, 78, 255),
        "header": (65, 48, 32, 255),
        "header_hovered": (90, 68, 48, 255),
        "header_active": (112, 85, 60, 255),
    },
    "Light Cyan": {
        "window_bg": (35, 52, 55, 255),
        "title_bg": (28, 42, 45, 255),
        "title_bg_active": (60, 180, 190, 255),
        "frame_bg": (50, 125, 135, 255),
        "frame_bg_hovered": (70, 165, 175, 255),
        "frame_bg_active": (90, 200, 210, 255),
        "button": (60, 175, 185, 255),
        "button_hovered": (95, 210, 220, 255),
        "button_active": (48, 145, 155, 255),
        "tab": (52, 130, 140, 255),
        "tab_hovered": (75, 180, 190, 255),
        "tab_active": (65, 160, 170, 255),
        "text": (230, 255, 255, 255),
        "check_mark": (140, 255, 255, 255),
        "slider_grab": (110, 230, 240, 255),
        "header": (58, 140, 150, 255),
        "header_hovered": (78, 175, 185, 255),
        "header_active": (98, 200, 210, 255),
    },
    "Dark Cyan": {
        "window_bg": (12, 25, 28, 255),
        "title_bg": (8, 18, 20, 255),
        "title_bg_active": (20, 75, 85, 255),
        "frame_bg": (18, 52, 58, 255),
        "frame_bg_hovered": (28, 78, 88, 255),
        "frame_bg_active": (40, 105, 115, 255),
        "button": (28, 88, 98, 255),
        "button_hovered": (42, 118, 128, 255),
        "button_active": (20, 68, 78, 255),
        "tab": (20, 58, 65, 255),
        "tab_hovered": (35, 95, 105, 255),
        "tab_active": (28, 78, 88, 255),
        "text": (180, 230, 235, 255),
        "check_mark": (70, 210, 220, 255),
        "slider_grab": (50, 170, 180, 255),
        "header": (25, 68, 78, 255),
        "header_hovered": (38, 98, 108, 255),
        "header_active": (50, 125, 135, 255),
    },
    "Light Magenta": {
        "window_bg": (55, 38, 55, 255),
        "title_bg": (45, 30, 45, 255),
        "title_bg_active": (200, 80, 180, 255),
        "frame_bg": (140, 58, 130, 255),
        "frame_bg_hovered": (180, 78, 168, 255),
        "frame_bg_active": (220, 100, 205, 255),
        "button": (200, 80, 180, 255),
        "button_hovered": (235, 115, 218, 255),
        "button_active": (165, 62, 150, 255),
        "tab": (145, 62, 135, 255),
        "tab_hovered": (205, 90, 188, 255),
        "tab_active": (185, 78, 170, 255),
        "text": (255, 235, 252, 255),
        "check_mark": (255, 150, 240, 255),
        "slider_grab": (235, 118, 218, 255),
        "header": (160, 68, 148, 255),
        "header_hovered": (195, 92, 180, 255),
        "header_active": (220, 115, 205, 255),
    },
    "Dark Magenta": {
        "window_bg": (28, 14, 26, 255),
        "title_bg": (20, 10, 18, 255),
        "title_bg_active": (90, 30, 80, 255),
        "frame_bg": (60, 22, 55, 255),
        "frame_bg_hovered": (88, 35, 80, 255),
        "frame_bg_active": (118, 48, 108, 255),
        "button": (100, 35, 90, 255),
        "button_hovered": (132, 52, 120, 255),
        "button_active": (78, 26, 70, 255),
        "tab": (65, 25, 58, 255),
        "tab_hovered": (105, 42, 95, 255),
        "tab_active": (88, 35, 80, 255),
        "text": (235, 195, 228, 255),
        "check_mark": (230, 90, 210, 255),
        "slider_grab": (190, 68, 175, 255),
        "header": (78, 30, 70, 255),
        "header_hovered": (108, 45, 98, 255),
        "header_active": (135, 58, 122, 255),
    },
}

# Active Configuration - Currently applied settings (runtime)
Active_Config = {}

# Keybinds Configuration - Keyboard shortcuts
Keybinds_Config = {
    "menu_toggle_key": "f8",  # Key to show/hide cheat menu
    "esp_toggle_key": "capslock",  # Key to toggle ESP on/off
    "exit_key": "f7",  # Key to close the script
    "aimbot_key": "alt",  # Key to activate aimbot (hold)
    "triggerbot_key": "x",  # Key to activate triggerbot (hold)
    "acs_key": "v",  # Key to activate auto crosshair placement (hold)
    "aimbot_toggle_key": "",  # Key to toggle aimbot on/off
    "head_only_toggle_key": "",  # Key to toggle head-only mode for triggerbot
    "rcs_toggle_key": "",  # Key to toggle RCS on/off
    "anti_afk_toggle_key": "",  # Key to toggle anti-AFK on/off
}


# =============================================================================
# GLOBAL STATE
# =============================================================================
# Global state variables track window dragging, application state, ESP overlay,
# and keybind listening. These are modified throughout the application lifecycle.
# =============================================================================

# Window drag state - tracks mouse position and window position during drag
# Used by update_window_drag() to implement custom window dragging via titlebar
drag_state = {
    "is_dragging": False,   # Whether user is currently dragging the window
    "start_mouse_x": 0,     # Mouse X position when drag started
    "start_mouse_y": 0,     # Mouse Y position when drag started  
    "start_window_x": 0,    # Window X position when drag started
    "start_window_y": 0,    # Window Y position when drag started
    "hwnd": None            # Win32 window handle (HWND)
}

# Application state
app_state = {
    "current_window": "loader",  # "loader" or "cheat"
    "app_title": None,           # Cached app title
    "switch_to_cheat": False,    # Flag to trigger window switch
    "last_window_pos": None      # (x, y) position of last window for persistence
}

# Loader settings
loader_settings = {
    "ShowDebugTab": False,
    "UseLocalOffsets": False
}

# Game offsets - loaded at runtime
offsets = None
client_dll = None

# Commonly used offsets (initialized after loading)
dwEntityList = None
dwLocalPlayerPawn = None
dwLocalPlayerController = None
dwViewMatrix = None
dwPlantedC4 = None
dwViewAngles = None
dwSensitivity = None
dwSensitivity_sensitivity = None

# Entity field offsets
m_iTeamNum = None
m_lifeState = None
m_pGameSceneNode = None
m_iHealth = None
m_fFlags = None
m_vecVelocity = None

# Player controller offsets
m_hPlayerPawn = None
m_iszPlayerName = None
m_iDesiredFOV = None

# Player pawn offsets
m_iIDEntIndex = None
m_ArmorValue = None
m_entitySpottedState = None
m_angEyeAngles = None
m_aimPunchAngle = None
m_iShotsFired = None
m_bIsScoped = None
m_pCameraServices = None
m_vOldOrigin = None
m_pWeaponServices = None

# Scene node offsets
m_vecAbsOrigin = None
m_vecOrigin = None
m_modelState = None

# Weapon and item offsets
m_AttributeManager = None
m_Item = None
m_iItemDefinitionIndex = None
m_hActiveWeapon = None
m_iClip1 = None
pBulletServicesOffset = None
m_pClippingWeapon = None
m_iItemDefinitionIndex = None

# Bomb offsets
m_flTimerLength = None
m_flDefuseLength = None
m_bBeingDefused = None
m_nBombSite = None

# Spotted state offsets
m_bSpotted = None
m_bSpottedByMask = None

# Camera and visual offsets
m_iFOV = None
m_flFlashMaxAlpha = None

# ESP Overlay State
esp_overlay = {
    "running": False,           # Whether ESP overlay thread is running
    "thread": None,             # Reference to ESP thread
    "hwnd": None,               # Win32 window handle for overlay
    "pm": None,                 # pymem instance
    "client": None,             # client.dll base address
    "settings": None,           # Current ESP settings (copy of Default_Config)
    "window_width": 0,          # CS2 window width
    "window_height": 0,         # CS2 window height
    "window_x": 0,              # CS2 window X position
    "window_y": 0,              # CS2 window Y position
    "fps": 0,                   # Current FPS counter
    "last_fps_time": 0,         # Last FPS calculation time
    "frame_count": 0,           # Frames since last FPS calculation
}

# Aimbot State
aimbot_state = {
    "running": False,           # Whether aimbot thread is running
    "thread": None,             # Reference to aimbot thread
    "settings": None,           # Current aimbot settings
    "locked_entity": None,      # Currently locked target entity address
    "accum_x": 0.0,             # Accumulated fractional X movement
    "accum_y": 0.0,             # Accumulated fractional Y movement
    "is_targeting": False,      # Whether currently targeting a player
}

# Triggerbot State
triggerbot_state = {
    "running": False,           # Whether triggerbot thread is running
    "thread": None,             # Reference to triggerbot thread
    "settings": None,           # Current triggerbot settings
    "mouse": None,              # pynput mouse controller
}

# Anti Flash State
anti_flash_state = {
    "running": False,           # Whether anti-flash thread is running
    "thread": None,             # Reference to anti-flash thread
    "settings": None,           # Current anti-flash settings
    "last_enabled": False,      # Last state of anti_flash_enabled
}

# FOV Changer State
fov_changer_state = {
    "running": False,           # Whether FOV changer thread is running
    "thread": None,             # Reference to FOV changer thread
    "settings": None,           # Current FOV changer settings
}

# Recoil Control System (RCS) State
rcs_state = {
    "running": False,           # Whether RCS thread is running
    "thread": None,             # Reference to RCS thread
    "settings": None,           # Current RCS settings
    "prev_punch": (0.0, 0.0),   # Previous aim punch angle for delta calculation
}

# Auto Crosshair Placement (ACS) State
acs_state = {
    "running": False,           # Whether ACS thread is running
    "thread": None,             # Reference to ACS thread
    "settings": None,           # Current ACS settings
}

# Hitsound State
hitsound_state = {
    "running": False,           # Whether hitsound thread is running
    "thread": None,             # Reference to hitsound thread
    "settings": None,           # Current hitsound settings
    "previous_total_hits": 0,   # Previous total hits count
}

# Anti-AFK State
anti_afk_state = {
    "running": False,           # Whether anti-AFK thread is running
    "thread": None,             # Reference to anti-AFK thread
    "settings": None,           # Current anti-AFK settings
}

# Footstep ESP State - Tracks footstep rings for each player
# Based on velocity changes to detect footsteps/movement sounds
footstep_esp_cache = {
    "ring_cache": {},           # Dict[pawn_address] -> List of ring info dicts
    "last_velocity": {},        # Dict[pawn_address] -> (vx, vy, vz) last velocity
    "last_origin": {},          # Dict[pawn_address] -> (x, y, z) last origin
}

# Keybind listening state
keybind_listener = {
    "listening": False,         # Whether we're currently listening for a key press
    "target": None,             # Which keybind we're setting (e.g., "menu_toggle_key")
}

# Debug output system - stores messages for mini-terminal
debug_output = {
    "messages": [],            # List of (timestamp, message) tuples
    "max_messages": 100,       # Maximum messages to keep in memory
    "scroll_to_bottom": True,  # Auto-scroll to newest message
}

# Bomb ESP timing state
BombPlantedTime = 0
BombDefusedTime = 0

# =============================================================================
# KEYBIND SYSTEM - Virtual Key Code Mapping
# =============================================================================
# Complete Virtual Key (VK) code mapping for all supported keybinds.
# This centralized system enables consistent keybind handling across all features.
# VK codes are Windows API constants for keyboard input detection.
# =============================================================================

VK_CODE_MAP = {
    # Function keys
    0x70: "f1", 0x71: "f2", 0x72: "f3", 0x73: "f4",
    0x74: "f5", 0x75: "f6", 0x76: "f7", 0x77: "f8",
    0x78: "f9", 0x79: "f10", 0x7A: "f11", 0x7B: "f12",
    
    # Number keys
    0x30: "0", 0x31: "1", 0x32: "2", 0x33: "3", 0x34: "4",
    0x35: "5", 0x36: "6", 0x37: "7", 0x38: "8", 0x39: "9",
    
    # Letter keys
    0x41: "a", 0x42: "b", 0x43: "c", 0x44: "d", 0x45: "e",
    0x46: "f", 0x47: "g", 0x48: "h", 0x49: "i", 0x4A: "j",
    0x4B: "k", 0x4C: "l", 0x4D: "m", 0x4E: "n", 0x4F: "o",
    0x50: "p", 0x51: "q", 0x52: "r", 0x53: "s", 0x54: "t",
    0x55: "u", 0x56: "v", 0x57: "w", 0x58: "x", 0x59: "y",
    0x5A: "z",
    
    # Modifier keys
    0x10: "shift", 0x11: "ctrl", 0x12: "alt",
    
    # Special keys
    0x20: "space", 0x09: "tab", 0x0D: "enter", 0x1B: "esc",
    0x08: "backspace", 0x14: "capslock",
    
    # Navigation keys
    0x2D: "insert", 0x2E: "delete", 0x24: "home", 0x23: "end",
    0x21: "pageup", 0x22: "pagedown",
    0x25: "left", 0x26: "up", 0x27: "right", 0x28: "down",
    
    # Numpad keys
    0x60: "numpad0", 0x61: "numpad1", 0x62: "numpad2", 0x63: "numpad3",
    0x64: "numpad4", 0x65: "numpad5", 0x66: "numpad6", 0x67: "numpad7",
    0x68: "numpad8", 0x69: "numpad9",
    0x6A: "multiply", 0x6B: "add", 0x6D: "subtract",
    0x6E: "decimal", 0x6F: "divide",
    
    # Other keys
    0xBA: "semicolon", 0xBB: "equals", 0xBC: "comma", 0xBD: "minus",
    0xBE: "period", 0xBF: "slash", 0xC0: "tilde",
    0xDB: "leftbracket", 0xDC: "backslash", 0xDD: "rightbracket",
    0xDE: "quote",
    
    # Mouse buttons
    0x01: "mouse1", 0x02: "mouse2", 0x04: "mouse3",
    0x05: "mouse4", 0x06: "mouse5",
}

# Reverse mapping for quick lookups (key_name -> vk_code)
KEY_NAME_TO_VK = {v: k for k, v in VK_CODE_MAP.items()}


# =============================================================================
# CONFIGURATION SAVE/LOAD SYSTEM
# =============================================================================

def save_settings():
    """
    Save Active_Config to autosave.json in Settings folder.
    Called when settings change or on application exit.
    """
    try:
        with open(AUTOSAVE_PATH, 'w') as f:
            json.dump(Active_Config, f, indent=4)
        debug_log("Settings saved to autosave.json", "SUCCESS")
    except Exception as e:
        debug_log(f"Failed to save settings: {str(e)}", "ERROR")


def save_keybinds():
    """
    Save Keybinds_Config to autosave.json in Keybinds folder.
    Called when keybinds change or on application exit.
    """
    try:
        with open(KEYBINDS_AUTOSAVE_PATH, 'w') as f:
            json.dump(Keybinds_Config, f, indent=4)
        debug_log("Keybinds saved to autosave.json", "SUCCESS")
    except Exception as e:
        debug_log(f"Failed to save keybinds: {str(e)}", "ERROR")


def load_keybinds():
    """
    Load keybinds from autosave.json into Keybinds_Config.
    If file doesn't exist, keep default keybinds.
    Called at application startup.
    """
    global Keybinds_Config
    
    if os.path.exists(KEYBINDS_AUTOSAVE_PATH):
        try:
            with open(KEYBINDS_AUTOSAVE_PATH, 'r') as f:
                loaded_keybinds = json.load(f)
            
            # Update Keybinds_Config with loaded values
            Keybinds_Config.update(loaded_keybinds)
            debug_log("Keybinds loaded from autosave.json", "SUCCESS")
            return True
        except Exception as e:
            debug_log(f"Failed to load keybinds: {str(e)}", "ERROR")
            return False
    else:
        # No autosave file, use default keybinds
        debug_log("No keybinds autosave found, using defaults", "INFO")
        return False


def load_settings(file_path=None):
    """
    Load settings from specified file or autosave.json into Active_Config.
    If file doesn't exist, copy Default_Config to Active_Config.
    Called at application startup.
    """
    global Active_Config
    
    if file_path is None:
        file_path = AUTOSAVE_PATH
    
    # List of keys that should be tuples (colors)
    color_keys = [
        "team_color", "enemy_color", "skeleton_color",
        "enemy_box_color", "team_box_color",
        "enemy_snapline_color", "team_snapline_color",
        "enemy_skeleton_color", "team_skeleton_color",
        "enemy_head_dot_color", "team_head_dot_color",
        "footstep_esp_color", "aimbot_snapline_color",
        "aimbot_radius_color", "aimbot_deadzone_color",
        "aimbot_targeting_radius_color", "aimbot_targeting_deadzone_color"
    ]
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Convert color lists back to tuples (JSON converts tuples to lists)
            for key in color_keys:
                if key in loaded_config and isinstance(loaded_config[key], list):
                    loaded_config[key] = tuple(loaded_config[key])
            
            # Merge with Default_Config to ensure all keys exist
            Active_Config = Default_Config.copy()
            Active_Config.update(loaded_config)
            
            debug_log(f"Settings loaded from {os.path.basename(file_path)}", "SUCCESS")
            # Log loaded color values for debugging
            debug_log(f"Loaded enemy_box_color: {Active_Config.get('enemy_box_color')}", "INFO")
            return True
        except Exception as e:
            debug_log(f"Failed to load settings: {str(e)}", "ERROR")
            Active_Config = Default_Config.copy()
            return False
    else:
        # No autosave file, use default config
        Active_Config = Default_Config.copy()
        debug_log("No autosave found, using default config", "INFO")
        debug_log(f"Default enemy_box_color: {Active_Config.get('enemy_box_color')}", "INFO")
        return False


def apply_loaded_settings():
    """
    Apply loaded Active_Config settings to ESP overlay.
    Called after settings are loaded and ESP is started.
    """
    if esp_overlay["settings"]:
        esp_overlay["settings"].update(Active_Config)
        debug_log("Applied loaded settings to ESP overlay", "SUCCESS")


def get_available_configs():
    """
    Get list of all JSON config files in the Settings folder.
    Returns list of filenames (without extension) excluding autosave.
    """
    configs = []
    if os.path.exists(SETTINGS_FOLDER):
        for filename in os.listdir(SETTINGS_FOLDER):
            if filename.endswith('.json'):
                # Get name without extension
                name = os.path.splitext(filename)[0]
                configs.append(name)
    return sorted(configs)


def load_config_from_file(config_name):
    """
    Load a specific config file into Active_Config.
    
    Args:
        config_name: Name of config file (without .json extension)
    
    Returns:
        True on success, False on failure
    """
    global Active_Config
    
    config_path = os.path.join(SETTINGS_FOLDER, f"{config_name}.json")
    
    # List of keys that should be tuples (colors)
    color_keys = [
        "team_color", "enemy_color", "skeleton_color",
        "enemy_box_color", "team_box_color",
        "enemy_snapline_color", "team_snapline_color",
        "enemy_skeleton_color", "team_skeleton_color",
        "enemy_head_dot_color", "team_head_dot_color",
        "spotted_color", "not_spotted_color",
        "radar_bg_color", "radar_border_color", "radar_crosshair_color",
        "radar_player_color", "radar_enemy_color", "radar_team_color",
        "aimbot_radius_color", "acs_line_color", "footstep_esp_color"
    ]
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Convert color lists back to tuples
            for key in color_keys:
                if key in loaded_config and isinstance(loaded_config[key], list):
                    loaded_config[key] = tuple(loaded_config[key])
            
            # Merge with Default_Config to ensure all keys exist
            Active_Config = Default_Config.copy()
            Active_Config.update(loaded_config)
            
            debug_log(f"Config loaded: {config_name}.json", "SUCCESS")
            return True
        except Exception as e:
            debug_log(f"Failed to load config {config_name}: {str(e)}", "ERROR")
            return False
    else:
        debug_log(f"Config file not found: {config_name}.json", "ERROR")
        return False


def apply_config_to_ui():
    """
    Update all UI elements to reflect current Active_Config values.
    Called after loading a config to sync the UI.
    """
    try:
        # === CHECKBOX MAPPINGS ===
        checkbox_mappings = {
            "chk_esp_enabled": "esp_enabled",
            "chk_box_esp": "box_esp",
            "chk_line_esp": "line_esp",
            "chk_skeleton_esp": "skeleton_esp",
            "chk_name_esp": "name_esp",
            "chk_distance_esp": "distance_esp",
            "chk_weapon_esp": "weapon_esp",
            "chk_hide_unknown_weapons": "hide_unknown_weapons",
            "chk_health_bar": "health_bar",
            "chk_armor_bar": "armor_bar",
            "chk_head_dot": "head_dot",
            "chk_bomb_esp": "bomb_esp",
            "chk_footstep_esp": "footstep_esp",
            "chk_spotted_esp": "spotted_esp",
            "chk_hide_spotted_players": "hide_spotted_players",
            "chk_custom_crosshair": "custom_crosshair",
            "chk_radar_enabled": "radar_enabled",
            "chk_radar_overlap_game": "radar_overlap_game",
            "chk_aimbot_enabled": "aimbot_enabled",
            "chk_aimbot_require_key": "aimbot_require_key",
            "chk_aimbot_spotted_check": "aimbot_spotted_check",
            "chk_aimbot_lock_target": "aimbot_lock_target",
            "chk_aimbot_show_radius": "aimbot_show_radius",
            "chk_triggerbot_enabled": "triggerbot_enabled",
            "chk_triggerbot_burst_mode": "triggerbot_burst_mode",
            "chk_triggerbot_head_only": "triggerbot_head_only",
            "chk_acs_enabled": "acs_enabled",
            "chk_acs_draw_deadzone_lines": "acs_draw_deadzone_lines",
            "chk_acs_always_show_deadzone_lines": "acs_always_show_deadzone_lines",
            "chk_anti_flash_enabled": "anti_flash_enabled",
            "chk_fov_changer_enabled": "fov_changer_enabled",
            "chk_rcs_enabled": "rcs_enabled",
            "chk_rcs_continuous_only": "rcs_continuous_only",
            "chk_fps_cap_enabled": "fps_cap_enabled",
            "chk_hide_on_tabout": "hide_on_tabout",
            "chk_show_status_labels": "show_status_labels",
            "chk_anti_afk_enabled": "anti_afk_enabled",
        }
        
        for tag, config_key in checkbox_mappings.items():
            if dpg.does_item_exist(tag):
                value = Active_Config.get(config_key, False)
                dpg.set_value(tag, value)
        
        # === SLIDER MAPPINGS ===
        slider_mappings = {
            "slider_box_thickness": "box_thickness",
            "slider_snapline_thickness": "snapline_thickness",
            "slider_skeleton_thickness": "skeleton_thickness",
            "slider_custom_crosshair_scale": "custom_crosshair_scale",
            "slider_custom_crosshair_thickness": "custom_crosshair_thickness",
            "slider_spotted_text_size": "spotted_text_size",
            "slider_name_text_size": "name_text_size",
            "slider_weapon_text_size": "weapon_text_size",
            "slider_radar_size": "radar_size",
            "slider_radar_scale": "radar_scale",
            "slider_radar_opacity": "radar_opacity",
            "slider_aimbot_smoothness": "aimbot_smoothness",
            "slider_aimbot_radius": "aimbot_radius",
            "slider_aimbot_deadzone_radius": "aimbot_deadzone_radius",
            "slider_aimbot_radius_transparency": "aimbot_radius_transparency",
            "slider_aimbot_deadzone_transparency": "aimbot_deadzone_transparency",
            "slider_triggerbot_first_shot_delay": "triggerbot_first_shot_delay",
            "slider_triggerbot_between_shots_delay": "triggerbot_between_shots_delay",
            "slider_triggerbot_burst_shots": "triggerbot_burst_shots",
            "slider_acs_smoothness": "acs_smoothness",
            "slider_acs_deadzone": "acs_deadzone",
            "slider_acs_line_width": "acs_line_width",
            "slider_acs_line_transparency": "acs_line_transparency",
            "slider_fps_cap": "fps_cap_value",
            "slider_fov_value": "fov_value",
            "slider_rcs_strength_x": "rcs_strength_x",
            "slider_rcs_strength_y": "rcs_strength_y",
            "slider_rcs_smoothness": "rcs_smoothness",
            "slider_rcs_multiplier": "rcs_multiplier",
            "slider_window_width": "window_width",
            "slider_window_height": "window_height",
            "slider_menu_transparency": "menu_transparency",
        }
        
        for tag, config_key in slider_mappings.items():
            if dpg.does_item_exist(tag):
                value = Active_Config.get(config_key, 0)
                dpg.set_value(tag, value)
        
        # Configure deadzone slider max value based on aimbot radius
        if dpg.does_item_exist("slider_aimbot_deadzone_radius"):
            aimbot_radius = Active_Config.get("aimbot_radius", 50)
            deadzone_max = max(0, aimbot_radius - 1)
            dpg.configure_item("slider_aimbot_deadzone_radius", max_value=deadzone_max)
        
        # === COMBO/DROPDOWN MAPPINGS ===
        # Lines position combo (stored as string: "Bottom", "Top")
        if dpg.does_item_exist("combo_lines_pos"):
            lines_pos = Active_Config.get("lines_position", "Bottom")
            dpg.set_value("combo_lines_pos", lines_pos)
        
        # Anti-aliasing combo (stored as string: "None", "2x MSAA", etc.)
        if dpg.does_item_exist("combo_antialiasing"):
            aa_mode = Active_Config.get("antialiasing", "4x MSAA")
            dpg.set_value("combo_antialiasing", aa_mode)
        
        # Radar position combo (stored as string: "Top Left", "Top Right", etc.) - DEPRECATED
        # if dpg.does_item_exist("combo_radar_position"):
        #     radar_pos = Active_Config.get("radar_position", "Top Right")
        #     dpg.set_value("combo_radar_position", radar_pos)
        
        # Radar overlap game checkbox
        if dpg.does_item_exist("chk_radar_overlap_game"):
            overlap_game = Active_Config.get("radar_overlap_game", False)
            dpg.set_value("chk_radar_overlap_game", overlap_game)
        
        # Radar manual position sliders
        if dpg.does_item_exist("slider_radar_x"):
            radar_x = Active_Config.get("radar_x", 0)
            dpg.set_value("slider_radar_x", radar_x)
        if dpg.does_item_exist("slider_radar_y"):
            radar_y = Active_Config.get("radar_y", 0)
            dpg.set_value("slider_radar_y", radar_y)
        
        # Aimbot target bone combo (stored as string: "Head", "Neck", etc.)
        if dpg.does_item_exist("combo_aimbot_target_bone"):
            bone = Active_Config.get("aimbot_target_bone", "Head")
            dpg.set_value("combo_aimbot_target_bone", bone)
        
        # ACS target bone combo (stored as string: "Head", "Neck", etc.)
        if dpg.does_item_exist("combo_acs_target_bone"):
            bone = Active_Config.get("acs_target_bone", "Head")
            dpg.set_value("combo_acs_target_bone", bone)
        
        # Custom crosshair shape combo
        if dpg.does_item_exist("combo_custom_crosshair_shape"):
            shape = Active_Config.get("custom_crosshair_shape", "Sus")
            dpg.set_value("combo_custom_crosshair_shape", shape)
        
        # Targeting combo
        if dpg.does_item_exist("combo_targeting"):
            targeting = Active_Config.get("targeting_type", 0)
            targeting_options = ["Enemies Only", "All Players"]
            if 0 <= targeting < len(targeting_options):
                dpg.set_value("combo_targeting", targeting_options[targeting])
        
        # Colorway combo (stored as string: "Default", etc.)
        if dpg.does_item_exist("combo_colorway"):
            colorway = Active_Config.get("menu_colorway", "Default")
            dpg.set_value("combo_colorway", colorway)
        
        # Font combo (stored as string: "Default", "Segoe UI", etc.)
        if dpg.does_item_exist("combo_font"):
            font = Active_Config.get("menu_font", "Default")
            dpg.set_value("combo_font", font)
        
        # Healthbar type combo (stored as string: "Vertical Left", "Vertical Right", "Horizontal Above", "Horizontal Below")
        if dpg.does_item_exist("combo_healthbar_type"):
            hb_type = Active_Config.get("healthbar_type", "Vertical Left")
            dpg.set_value("combo_healthbar_type", hb_type)
        
        # Box type combo (stored as string: "2D", "3D")
        if dpg.does_item_exist("combo_box_type"):
            box_type = Active_Config.get("box_type", "2D")
            dpg.set_value("combo_box_type", box_type)
        
        # === COLOR MAPPINGS ===
        color_mappings = {
            "color_enemy_box": "enemy_box_color",
            "color_team_box": "team_box_color",
            "color_enemy_snapline": "enemy_snapline_color",
            "color_team_snapline": "team_snapline_color",
            "color_enemy_skeleton": "enemy_skeleton_color",
            "color_team_skeleton": "team_skeleton_color",
            "color_enemy_head_dot": "enemy_head_dot_color",
            "color_team_head_dot": "team_head_dot_color",
            "color_spotted": "spotted_color",
            "color_not_spotted": "not_spotted_color",
            "color_custom_crosshair_color": "custom_crosshair_color",
            "color_radar_bg": "radar_bg_color",
            "color_radar_border": "radar_border_color",
            "color_radar_crosshair": "radar_crosshair_color",
            "color_radar_player": "radar_player_color",
            "color_radar_enemy": "radar_enemy_color",
            "color_radar_team": "radar_team_color",
            "color_aimbot_radius": "aimbot_radius_color",
            "color_aimbot_deadzone": "aimbot_deadzone_color",
            "color_acs_line": "acs_line_color",
            "color_footstep_esp": "footstep_esp_color",
        }
        
        for tag, config_key in color_mappings.items():
            if dpg.does_item_exist(tag):
                color = Active_Config.get(config_key)
                if color:
                    # Convert tuple to list for dpg color edit
                    color_list = list(color) if isinstance(color, tuple) else color
                    # Ensure we have RGB values (some colors may have alpha)
                    if len(color_list) >= 3:
                        dpg.set_value(tag, color_list[:3])
        
        # Apply to all running overlay/cheat systems
        # ESP overlay
        if esp_overlay["settings"]:
            esp_overlay["settings"].update(Active_Config)
        
        # Aimbot
        if aimbot_state.get("settings"):
            aimbot_state["settings"].update(Active_Config)
        
        # Triggerbot
        if triggerbot_state.get("settings"):
            triggerbot_state["settings"].update(Active_Config)
        
        # ACS (Aim Correction System)
        if acs_state.get("settings"):
            acs_state["settings"].update(Active_Config)
        
        # === HANDLE CONDITIONAL UI VISIBILITY ===
        # FPS cap slider visibility depends on fps_cap_enabled
        if dpg.does_item_exist("slider_fps_cap"):
            fps_cap_enabled = Active_Config.get("fps_cap_enabled", False)
            dpg.configure_item("slider_fps_cap", show=fps_cap_enabled)
            # Also update tooltip visibility
            if dpg.does_item_exist("tooltip_fps_cap_slider"):
                dpg.configure_item("tooltip_fps_cap_slider", show=fps_cap_enabled)
        
        # Triggerbot burst shots slider visibility depends on burst mode
        if dpg.does_item_exist("slider_triggerbot_burst_shots"):
            burst_mode = Active_Config.get("triggerbot_burst_mode", False)
            dpg.configure_item("slider_triggerbot_burst_shots", show=burst_mode)
        
        # FOV slider visibility depends on fov_changer_enabled
        if dpg.does_item_exist("slider_fov_value"):
            fov_enabled = Active_Config.get("fov_changer_enabled", False)
            dpg.configure_item("slider_fov_value", show=fov_enabled)
            # Also update tooltip visibility
            if dpg.does_item_exist("tooltip_fov_value"):
                dpg.configure_item("tooltip_fov_value", show=fov_enabled)
            # Reset FOV to 90 if config has FOV disabled
            if not fov_enabled:
                reset_fov_to_default()
        
        # Update FOV changer state settings
        if fov_changer_state.get("settings"):
            fov_changer_state["settings"].update(Active_Config)
        
        # Update RCS state settings
        if rcs_state.get("settings"):
            rcs_state["settings"].update(Active_Config)
        
        debug_log("UI and all systems updated from config", "SUCCESS")
        
    except Exception as e:
        debug_log(f"Failed to apply config to UI: {str(e)}", "ERROR")


def on_config_selected(sender, app_data, user_data):
    """
    Callback when a config is selected from the dropdown.
    Loads the selected config and applies it to UI.
    """
    config_name = app_data
    if config_name and config_name != "Select Config...":
        if load_config_from_file(config_name):
            apply_config_to_ui()
            # Also save to autosave so it persists
            save_settings()


def save_config_to_file(config_name):
    """
    Save current Active_Config to a named config file.
    
    Args:
        config_name: Name for the config file (without .json extension)
    
    Returns:
        True on success, False on failure
    """
    if not config_name or config_name.strip() == "":
        debug_log("Cannot save config: name is empty", "ERROR")
        return False
    
    # Clean the filename (remove invalid characters)
    clean_name = "".join(c for c in config_name if c.isalnum() or c in (' ', '-', '_')).strip()
    if not clean_name:
        debug_log("Cannot save config: invalid name", "ERROR")
        return False
    
    config_path = os.path.join(SETTINGS_FOLDER, f"{clean_name}.json")
    
    try:
        with open(config_path, 'w') as f:
            json.dump(Active_Config, f, indent=4)
        debug_log(f"Config saved: {clean_name}.json", "SUCCESS")
        return True
    except Exception as e:
        debug_log(f"Failed to save config {clean_name}: {str(e)}", "ERROR")
        return False


def on_save_config_clicked():
    """
    Callback for the Save Config button.
    Gets the name from input and saves current settings.
    """
    if dpg.does_item_exist("input_config_name"):
        config_name = dpg.get_value("input_config_name")
        if save_config_to_file(config_name):
            # Clear the input field after successful save
            dpg.set_value("input_config_name", "")
            # Refresh the config list
            refresh_config_list()


def reset_to_default_config():
    """
    Reset Active_Config to Default_Config and update all UI elements.
    Uses the same system as config loading to ensure everything updates.
    """
    global Active_Config
    
    # Reset Active_Config to default values
    Active_Config = Default_Config.copy()
    
    # Apply to UI using the same function as config loading
    apply_config_to_ui()
    
    # Save the reset config to autosave
    save_settings()
    
    debug_log("Config reset to default", "SUCCESS")


def refresh_config_list():
    """
    Refresh the config dropdown with current files in Settings folder.
    """
    if dpg.does_item_exist("combo_config_select"):
        configs = get_available_configs()
        dpg.configure_item("combo_config_select", items=configs)
        debug_log(f"Config list refreshed: {len(configs)} configs found", "INFO")


# =============================================================================
# ANTI-AFK CALLBACKS
# =============================================================================

def on_anti_afk_toggle(sender, value):
    """Handle anti-AFK enable/disable toggle."""
    Active_Config["anti_afk_enabled"] = value
    save_settings()
    
    if value:
        start_anti_afk_thread()
    else:
        stop_anti_afk_thread()
    
    debug_log(f"Anti-AFK {'enabled' if value else 'disabled'}", "INFO")


def on_anti_afk_toggle_key_button():
    """Handle anti-AFK toggle key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "anti_afk_toggle_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_anti_afk_toggle_cheat", "Press any key...")
    except:
        pass


def anti_afk_loop():
    """Main anti-AFK loop that presses W,A,S,D keys in sequence."""
    global anti_afk_state
    
    keys = [0x57, 0x41, 0x53, 0x44]  # W, A, S, D virtual key codes
    key_names = ['W', 'A', 'S', 'D']
    
    while anti_afk_state["running"]:
        for i, key in enumerate(keys):
            if not anti_afk_state["running"]:
                break
                
            # Press key down
            win32api.keybd_event(key, 0, 0, 0)
            debug_log(f"Anti-AFK: Pressed {key_names[i]}", "INFO")
            
            # Wait 100ms
            time.sleep(0.1)
            
            # Release key
            win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # Wait 1 second before next key
            time.sleep(1.0)
        
        # Wait 5 seconds before starting the cycle again
        time.sleep(5.0)


def start_anti_afk_thread():
    """Start the anti-AFK thread."""
    global anti_afk_state
    
    if anti_afk_state["running"]:
        return  # Already running
    
    anti_afk_state["running"] = True
    anti_afk_state["thread"] = threading.Thread(target=anti_afk_loop, daemon=True)
    anti_afk_state["thread"].start()
    debug_log("Anti-AFK thread started", "SUCCESS")


def stop_anti_afk_thread():
    """Stop the anti-AFK thread."""
    global anti_afk_state
    
    if not anti_afk_state["running"]:
        return  # Not running
    
    anti_afk_state["running"] = False
    
    if anti_afk_state["thread"] and anti_afk_state["thread"].is_alive():
        anti_afk_state["thread"].join(timeout=2.0)
    
    anti_afk_state["thread"] = None
    debug_log("Anti-AFK thread stopped", "INFO")


# =============================================================================
# DEBUG OUTPUT SYSTEM
# =============================================================================

def debug_log(message, level="INFO"):
    """
    Add a message to the debug output terminal.
    
    Args:
        message: The message to log
        level: Log level (INFO, SUCCESS, WARNING, ERROR)
    """
    global debug_output
    
    timestamp = time.strftime("%H:%M:%S")
    
    debug_output["messages"].append((timestamp, level, message))
    
    # Keep only the last max_messages
    if len(debug_output["messages"]) > debug_output["max_messages"]:
        debug_output["messages"].pop(0)


# =============================================================================
# OFFSET LOADING
# =============================================================================

def load_offsets_from_github():
    """
    Load game offsets from GitHub repository.
    
    Fetches two JSON files containing CS2 memory offsets:
    - offsets.json: Core game offsets (entity list, local player, view matrix, etc.)
    - client_dll.json: Class field offsets (player health, team, position, etc.)
    
    Returns:
        tuple: (offsets_dict, client_dll_dict) or (None, None) on failure
    """
    try:
        debug_log("Downloading offsets...", "INFO")
        
        # Load offsets.json
        offsets_response = urllib.request.urlopen(GITHUB_OFFSETS_URL, timeout=10)
        offsets_data = json.loads(offsets_response.read().decode('utf-8'))
        debug_log("Downloaded offsets.json successfully", "SUCCESS")
        
        # Load client_dll.json
        client_dll_response = urllib.request.urlopen(GITHUB_CLIENT_DLL_URL, timeout=10)
        client_dll_data = json.loads(client_dll_response.read().decode('utf-8'))
        debug_log("Downloaded client_dll.json successfully", "SUCCESS")
        
        return offsets_data, client_dll_data
    except Exception as e:
        return None, None


def load_offsets_from_local():
    """
    Load offsets from local temp/offsets/output directory.
    
    Returns:
        tuple: (offsets_dict, client_dll_dict) or (None, None) on failure
    """
    try:
        debug_log("Loading offsets from local files...", "INFO")
        offsets_dir = os.path.join(TEMP_FOLDER, "offsets", "output")
        
        # Load offsets.json
        offsets_path = os.path.join(offsets_dir, "offsets.json")
        with open(offsets_path, 'r') as f:
            offsets_data = json.load(f)
        debug_log(f"Loaded {offsets_path}", "SUCCESS")
        
        # Load client_dll.json
        client_dll_path = os.path.join(offsets_dir, "client_dll.json")
        with open(client_dll_path, 'r') as f:
            client_dll_data = json.load(f)
        debug_log(f"Loaded {client_dll_path}", "SUCCESS")
        
        return offsets_data, client_dll_data
    except Exception as e:
        debug_log(f"Failed to load local offsets: {str(e)}", "ERROR")
        return None, None


def initialize_offset_globals():
    """
    Initialize all global offset variables from loaded offset data.
    
    Extracts numeric offsets from the loaded JSON data and assigns them to
    global variables for fast access during ESP rendering. This avoids repeated
    dictionary lookups in the hot path (render loop).
    
    Must be called after offsets and client_dll are loaded.
    
    Returns:
        bool: True if successful, False if offsets not loaded or error occurred
    """
    global dwEntityList, dwLocalPlayerPawn, dwLocalPlayerController, dwViewMatrix
    global dwPlantedC4, dwViewAngles, dwSensitivity, dwSensitivity_sensitivity
    global m_iTeamNum, m_lifeState, m_pGameSceneNode, m_iHealth, m_fFlags, m_vecVelocity
    global m_hPlayerPawn, m_iszPlayerName, m_iDesiredFOV
    global m_iIDEntIndex, m_ArmorValue, m_entitySpottedState, m_angEyeAngles
    global m_aimPunchAngle, m_iShotsFired, m_bIsScoped, m_pCameraServices
    global m_vOldOrigin, m_pWeaponServices
    global m_vecAbsOrigin, m_vecOrigin, m_modelState
    global m_AttributeManager, m_Item, m_iItemDefinitionIndex, m_hActiveWeapon, m_iClip1, m_pClippingWeapon, m_iItemDefinitionIndex
    global m_flTimerLength, m_flDefuseLength, m_bBeingDefused, m_nBombSite
    global m_bSpotted, m_bSpottedByMask
    global m_iFOV, m_flFlashMaxAlpha
    
    if not offsets or not client_dll:
        debug_log("Cannot initialize offsets: data not loaded", "ERROR")
        return False
    
    try:
        debug_log("Initializing offset globals...", "INFO")
        # Extract commonly used offsets
        dwEntityList = offsets['client.dll']['dwEntityList']
        dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
        dwLocalPlayerController = offsets['client.dll']['dwLocalPlayerController']
        dwViewMatrix = offsets['client.dll']['dwViewMatrix']
        dwPlantedC4 = offsets['client.dll']['dwPlantedC4']
        dwViewAngles = offsets['client.dll']['dwViewAngles']
        dwSensitivity = offsets['client.dll']['dwSensitivity']
        dwSensitivity_sensitivity = offsets['client.dll']['dwSensitivity_sensitivity']
        
        # Entity field offsets
        m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
        m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
        m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
        m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
        m_fFlags = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_fFlags']
        m_vecVelocity = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_vecVelocity']
        
        # Player controller offsets
        m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
        m_iszPlayerName = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iszPlayerName']
        m_iDesiredFOV = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iDesiredFOV']
        
        # Player pawn offsets
        m_iIDEntIndex = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_iIDEntIndex']
        m_ArmorValue = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_ArmorValue']
        m_entitySpottedState = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_entitySpottedState']
        m_angEyeAngles = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_angEyeAngles']
        m_aimPunchAngle = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_aimPunchAngle']
        m_iShotsFired = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_iShotsFired']
        m_bIsScoped = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_bIsScoped']
        m_pCameraServices = client_dll['client.dll']['classes']['C_BasePlayerPawn']['fields']['m_pCameraServices']
        m_vOldOrigin = client_dll['client.dll']['classes']['C_BasePlayerPawn']['fields']['m_vOldOrigin']
        m_pWeaponServices = client_dll['client.dll']['classes']['C_BasePlayerPawn']['fields']['m_pWeaponServices']
        
        # Scene node offsets
        m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
        m_vecOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecOrigin']
        m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
        
        # Weapon and item offsets
        m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
        m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
        m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
        m_hActiveWeapon = client_dll['client.dll']['classes']['CPlayer_WeaponServices']['fields']['m_hActiveWeapon']
        m_iClip1 = client_dll['client.dll']['classes']['C_BasePlayerWeapon']['fields']['m_iClip1']
        m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_pClippingWeapon']
        m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']

        # Bomb offsets
        m_flTimerLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flTimerLength']
        m_flDefuseLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flDefuseLength']
        m_bBeingDefused = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_bBeingDefused']
        m_nBombSite = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_nBombSite']
        
        # Spotted state offsets
        m_bSpotted = client_dll['client.dll']['classes']['EntitySpottedState_t']['fields']['m_bSpotted']
        m_bSpottedByMask = client_dll['client.dll']['classes']['EntitySpottedState_t']['fields']['m_bSpottedByMask']
        
        # Camera and visual offsets
        m_iFOV = client_dll['client.dll']['classes']['CCSPlayerBase_CameraServices']['fields']['m_iFOV']
        m_flFlashMaxAlpha = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_flFlashMaxAlpha']
        
        debug_log("Offset globals initialized successfully", "SUCCESS")
        offset_count = len([x for x in dir() if not x.startswith('_')])
        debug_log(f"Loaded {offset_count} offset variables", "INFO")
        return True
    except Exception as e:
        debug_log(f"Failed to initialize offsets: {str(e)}", "ERROR")
        return False


def load_and_initialize_offsets(use_local=False):
    """
    Load offsets from either GitHub or local files and initialize globals.
    
    Args:
        use_local: If True, load from local files. Otherwise load from GitHub.
    
    Returns:
        bool: True if successful, False otherwise
    """
    global offsets, client_dll
    
    if use_local:
        offsets, client_dll = load_offsets_from_local()
    else:
        offsets, client_dll = load_offsets_from_github()
    
    if offsets is None or client_dll is None:
        return False
    
    # Initialize global offset variables
    return initialize_offset_globals()


# =============================================================================
# ESP UTILITY FUNCTIONS
# =============================================================================
# Helper functions for ESP overlay: window detection, coordinate conversion,
# and process monitoring.
# =============================================================================

def get_cs2_window_rect():
    """
    Get the client area rectangle of the CS2 window.
    
    Returns:
        tuple: (x, y, width, height) or (None, None, None, None) if not found
    """
    try:
        hwnd = win32gui.FindWindow(None, "Counter-Strike 2")
        if not hwnd:
            return None, None, None, None
        
        # Get window rect
        window_left, window_top, window_right, window_bottom = win32gui.GetWindowRect(hwnd)
        
        # Get client rect (excludes title bar and borders)
        client_left, client_top, client_right, client_bottom = win32gui.GetClientRect(hwnd)
        
        # Convert client coordinates to screen coordinates
        client_point = win32gui.ClientToScreen(hwnd, (0, 0))
        client_screen_x, client_screen_y = client_point
        
        # Calculate dimensions
        client_width = client_right - client_left
        client_height = client_bottom - client_top
        
        return client_screen_x, client_screen_y, client_width, client_height
    except Exception:
        return None, None, None, None


def is_cs2_running():
    """Check if CS2 process is currently running."""
    try:
        pymem.Pymem("cs2.exe")
        return True
    except Exception:
        return False


def is_cs2_running_fast(pm):
    """Fast check if CS2 is still running using existing pymem handle."""
    try:
        # Just try to read something small - if process died, this will fail
        pm.read_int(pm.base_address)
        return True
    except Exception:
        return False


def is_cs2_foreground():
    """Check if CS2 or the cheat window is the foreground window."""
    try:
        foreground_hwnd = win32gui.GetForegroundWindow()
        if not foreground_hwnd:
            return False
        
        # Check if CS2 is foreground
        window_title = win32gui.GetWindowText(foreground_hwnd)
        if window_title == "Counter-Strike 2":
            return True
        
        # Also check if the cheat window is foreground (don't hide when using cheat menu)
        if drag_state.get("hwnd") and foreground_hwnd == drag_state["hwnd"]:
            return True
        
        return False
    except Exception:
        return False


def w2s(view_matrix, x, y, z, width, height):
    """
    World-to-screen coordinate conversion.
    
    Transforms 3D world coordinates to 2D screen coordinates using the view matrix.
    
    Args:
        view_matrix: 16-element view matrix from game memory
        x, y, z: World coordinates
        width, height: Screen dimensions
    
    Returns:
        tuple: (screen_x, screen_y) or (-999, -999) if behind camera
    """
    try:
        if not view_matrix or width is None or height is None:
            return -999, -999
        
        if hasattr(view_matrix, '__len__') and len(view_matrix) >= 16:
            m = view_matrix
            # Matrix multiplication for projection
            clip_x = m[0]*x + m[1]*y + m[2]*z + m[3]
            clip_y = m[4]*x + m[5]*y + m[6]*z + m[7]
            clip_w = m[12]*x + m[13]*y + m[14]*z + m[15]
        else:
            return -999, -999
        
        # Check if point is behind camera
        if clip_w < 0.1:
            return -999, -999
        
        # Normalize device coordinates
        ndc_x = clip_x / clip_w
        ndc_y = clip_y / clip_w
        
        # Convert to screen coordinates
        screen_x = int((width / 2.0) * (1.0 + ndc_x))
        screen_y = int((height / 2.0) * (1.0 - ndc_y))
        
        return screen_x, screen_y
    except Exception:
        return -999, -999


# =============================================================================
# ESP OVERLAY WINDOW (PyImGui + GLFW + OpenGL)
# =============================================================================

class ESPOverlay:
    """
    Transparent overlay window for ESP rendering using PyImGui + GLFW + OpenGL.
    
    Architecture:
    - GLFW: Cross-platform window creation and event handling
    - OpenGL: Hardware-accelerated graphics rendering
    - ImGui: Immediate-mode GUI for drawing primitives (lines, boxes, text)
    
    Features:
    - Transparent background (only ESP elements visible)
    - Click-through (mouse events pass to CS2 window)
    - Always-on-top positioning
    - 4x MSAA anti-aliasing for smooth edges
    - No vsync for maximum FPS
    
    The overlay matches CS2's window position and size, creating the illusion
    that ESP elements are drawn directly on the game.
    """
    
    def __init__(self):
        self.window = None
        self.impl = None
        self.running = False
        self.width = 0
        self.height = 0
        self.pos_x = 0
        self.pos_y = 0
        
        # Draw list reference (set each frame)
        self.draw_list = None
        
        # Performance tracking
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
        # Colors will be initialized after ImGui context is created
        self.colors = {}
        
        # Fonts for overlay (loaded after ImGui context)
        self.overlay_fonts = {}
        self.default_font = None
    
    def _load_fonts(self):
        """Load fonts for overlay text rendering."""
        io = imgui.get_io()
        
        # Store default font
        self.default_font = io.fonts.add_font_default()
        
        # Load each font from MENU_FONTS at various sizes
        font_sizes = [8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 24.0]
        
        # For "Default", use Segoe UI as a scalable fallback
        default_font_path = "C:/Windows/Fonts/segoeui.ttf"
        if os.path.exists(default_font_path):
            self.overlay_fonts["Default"] = {}
            for size in font_sizes:
                try:
                    font = io.fonts.add_font_from_file_ttf(default_font_path, size)
                    self.overlay_fonts["Default"][size] = font
                except Exception:
                    pass
        
        for font_name, font_path in MENU_FONTS.items():
            if font_path and os.path.exists(font_path):
                self.overlay_fonts[font_name] = {}
                for size in font_sizes:
                    try:
                        font = io.fonts.add_font_from_file_ttf(font_path, size)
                        self.overlay_fonts[font_name][size] = font
                    except Exception as e:
                        pass
        
        # Rebuild font atlas
        self.impl.refresh_font_texture()
    
    def _init_colors(self):
        """Initialize color constants after ImGui context exists."""
        self.colors = {
            'red': imgui.get_color_u32_rgba(0.77, 0.12, 0.23, 1.0),      # RGB(196, 30, 58)
            'green': imgui.get_color_u32_rgba(0.28, 0.65, 0.42, 1.0),    # RGB(71, 167, 106)
            'white': imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0),
            'yellow': imgui.get_color_u32_rgba(1.0, 1.0, 0.0, 1.0),
            'health_bg': imgui.get_color_u32_rgba(0.2, 0.2, 0.2, 1.0),   # Dark gray
            'health_green': imgui.get_color_u32_rgba(0.0, 1.0, 0.0, 1.0),
            'health_yellow': imgui.get_color_u32_rgba(1.0, 1.0, 0.0, 1.0),
            'health_red': imgui.get_color_u32_rgba(1.0, 0.0, 0.0, 1.0),
            'head_dot': imgui.get_color_u32_rgba(1.0, 1.0, 0.0, 1.0),
            'armor_blue': imgui.get_color_u32_rgba(0.39, 0.58, 0.93, 1.0),  # Cornflower blue for armor
        }
    
    def create_window(self, x, y, width, height):
        """Create the transparent overlay window using GLFW."""
        self.pos_x = x
        self.pos_y = y
        self.width = width
        self.height = height
        
        # Initialize GLFW
        if not glfw.init():
            print("[ESP] Failed to initialize GLFW")
            return None
        
        # Set window hints for transparent overlay
        glfw.window_hint(glfw.DECORATED, glfw.FALSE)           # No title bar/borders
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)             # Always on top
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)  # Transparent background
        glfw.window_hint(glfw.MOUSE_PASSTHROUGH, glfw.TRUE)    # Click-through (GLFW 3.4+)
        glfw.window_hint(glfw.FOCUSED, glfw.FALSE)             # Don't steal focus
        glfw.window_hint(glfw.FOCUS_ON_SHOW, glfw.FALSE)       # Don't focus when shown
        
        # Set MSAA samples based on antialiasing setting
        aa_mode = Active_Config.get("antialiasing", "4x MSAA")
        if aa_mode == "None":
            glfw.window_hint(glfw.SAMPLES, 0)
        elif aa_mode == "2x MSAA":
            glfw.window_hint(glfw.SAMPLES, 2)
        elif aa_mode == "8x MSAA":
            glfw.window_hint(glfw.SAMPLES, 8)
        else:  # "4x MSAA" default
            glfw.window_hint(glfw.SAMPLES, 4)
        
        # Create window
        self.window = glfw.create_window(width, height, "ESP Overlay", None, None)
        if not self.window:
            print("[ESP] Failed to create GLFW window")
            glfw.terminate()
            return None
        
        # Position the window
        glfw.set_window_pos(self.window, x, y)
        
        # Make context current
        glfw.make_context_current(self.window)
        
        # Disable vsync for max FPS (set to 1 for vsync)
        glfw.swap_interval(0)
        
        # Initialize ImGui
        imgui.create_context()
        self.impl = GlfwRenderer(self.window)
        
        # Load fonts for overlay
        self._load_fonts()
        
        # Initialize colors now that ImGui context exists
        self._init_colors()
        
        # Enable anti-aliasing flags
        style = imgui.get_style()
        style.anti_aliased_lines = True
        style.anti_aliased_fill = True
        
        # Enable OpenGL blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable multisampling
        glEnable(GL_MULTISAMPLE)
        
        # Set up Win32 extended styles for click-through on Windows
        self._setup_windows_transparency()
        
        self.running = True
        return self.window
    
    def _setup_windows_transparency(self):
        """Set up Windows-specific extended styles for click-through."""
        if not self.window:
            return
            
        # Get the Win32 HWND from GLFW
        hwnd = glfw.get_win32_window(self.window)
        if hwnd:
            # Set extended window styles for transparency and click-through
            ex_style = win32gui.GetWindowLong(hwnd, GWL_EXSTYLE)
            ex_style |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
            ex_style &= ~WS_EX_APPWINDOW  # Remove from taskbar
            win32gui.SetWindowLong(hwnd, GWL_EXSTYLE, ex_style)
            
            # Make it always on top
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
            )
    
    def update_position(self, x, y, width, height):
        """Update overlay position to match CS2 window."""
        if not self.window:
            return
            
        size_changed = (width != self.width or height != self.height)
        pos_changed = (x != self.pos_x or y != self.pos_y)
        
        if pos_changed or size_changed:
            self.pos_x = x
            self.pos_y = y
            
            if pos_changed:
                glfw.set_window_pos(self.window, x, y)
            
            if size_changed:
                self.width = width
                self.height = height
                glfw.set_window_size(self.window, width, height)
    
    def hide(self):
        """Hide the overlay window."""
        if self.window:
            glfw.hide_window(self.window)
    
    def show(self):
        """Show the overlay window."""
        if self.window:
            glfw.show_window(self.window)
    
    def begin_paint(self):
        """Begin a new frame - polls events and starts ImGui frame."""
        if not self.window or not self.running:
            return None
        
        # Check if window should close
        if glfw.window_should_close(self.window):
            self.running = False
            return None
        
        # Poll events
        glfw.poll_events()
        self.impl.process_inputs()
        
        # Start new ImGui frame
        imgui.new_frame()
        
        # Get background draw list for overlay rendering
        self.draw_list = imgui.get_background_draw_list()
        
        return self.draw_list
    
    def end_paint(self):
        """End frame - renders and swaps buffers."""
        if not self.window:
            return
        
        # Render ImGui
        imgui.render()
        
        # Clear with transparent black
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Render ImGui draw data
        self.impl.render(imgui.get_draw_data())
        
        # Swap buffers
        glfw.swap_buffers(self.window)
        
        self.draw_list = None
    
    def clear(self):
        """Clear is handled automatically by OpenGL clear in end_paint."""
        pass  # No-op - ImGui handles this
    
    def draw_line(self, x1, y1, x2, y2, color='red', thickness=1.5):
        """Draw an anti-aliased line."""
        if not self.draw_list:
            return
        
        col = self.colors.get(color, self.colors['red'])
        self.draw_list.add_line(float(x1), float(y1), float(x2), float(y2), col, thickness)
    
    def draw_rect(self, x, y, width, height, color='red', thickness=1.5):
        """Draw a rectangle outline with anti-aliasing."""
        if not self.draw_list:
            return
        
        col = self.colors.get(color, self.colors['red'])
        self.draw_list.add_rect(
            float(x), float(y), 
            float(x + width), float(y + height), 
            col, 
            rounding=0.0, 
            thickness=thickness
        )
    
    def draw_filled_rect(self, x, y, width, height, r, g, b):
        """Draw a filled rectangle."""
        if not self.draw_list:
            return
        
        col = imgui.get_color_u32_rgba(r/255.0, g/255.0, b/255.0, 1.0)
        self.draw_list.add_rect_filled(
            float(x), float(y),
            float(x + width), float(y + height),
            col
        )
    
    def draw_filled_rect_brush(self, x, y, width, height, brush_name):
        """Draw a filled rectangle using a named color."""
        if not self.draw_list:
            return
        
        col = self.colors.get(brush_name, self.colors.get('white'))
        self.draw_list.add_rect_filled(
            float(x), float(y),
            float(x + width), float(y + height),
            col
        )
    
    def draw_circle_filled(self, cx, cy, radius, color='head_dot', segments=12):
        """Draw a filled circle with anti-aliasing."""
        if not self.draw_list:
            return
        
        col = self.colors.get(color, self.colors['yellow'])
        self.draw_list.add_circle_filled(float(cx), float(cy), float(radius), col, segments)
    
    def draw_circle_filled_rgb(self, cx, cy, radius, rgb_tuple, segments=12):
        """Draw a filled circle with RGB color tuple (0-255 values)."""
        if not self.draw_list:
            return
        
        col = imgui.get_color_u32_rgba(rgb_tuple[0]/255.0, rgb_tuple[1]/255.0, rgb_tuple[2]/255.0, 1.0)
        self.draw_list.add_circle_filled(float(cx), float(cy), float(radius), col, segments)
    
    def draw_line_rgb(self, x1, y1, x2, y2, rgb_tuple, thickness=1.5):
        """Draw a line with RGB color tuple (0-255 values)."""
        if not self.draw_list:
            return
        
        col = imgui.get_color_u32_rgba(rgb_tuple[0]/255.0, rgb_tuple[1]/255.0, rgb_tuple[2]/255.0, 1.0)
        self.draw_list.add_line(float(x1), float(y1), float(x2), float(y2), col, thickness)
    
    def draw_rect_rgb(self, x, y, width, height, rgb_tuple, thickness=1.5):
        """Draw a rectangle outline with RGB color tuple (0-255 values)."""
        if not self.draw_list:
            return
        
        col = imgui.get_color_u32_rgba(rgb_tuple[0]/255.0, rgb_tuple[1]/255.0, rgb_tuple[2]/255.0, 1.0)
        self.draw_list.add_rect(
            float(x), float(y), 
            float(x + width), float(y + height), 
            col, 
            rounding=0.0, 
            thickness=thickness
        )
    
    def draw_circle_filled_rgb(self, cx, cy, radius, rgb_tuple, segments=12):
        """Draw a filled circle with RGB color tuple (0-255 values)."""
        if not self.draw_list:
            return
        
        col = imgui.get_color_u32_rgba(rgb_tuple[0]/255.0, rgb_tuple[1]/255.0, rgb_tuple[2]/255.0, 1.0)
        self.draw_list.add_circle_filled(float(cx), float(cy), float(radius), col, segments)

    def draw_text(self, x, y, text, r=255, g=255, b=255, size=13.0, stroke=False, font_name=None):
        """Draw text at position with optional stroke and custom font."""
        if not self.draw_list:
            return
        
        # Get font if specified
        font = None
        if font_name and font_name in self.overlay_fonts:
            # Find closest size
            available_sizes = list(self.overlay_fonts[font_name].keys())
            if available_sizes:
                closest_size = min(available_sizes, key=lambda s: abs(s - size))
                font = self.overlay_fonts[font_name].get(closest_size)
        
        # Push font if available
        if font:
            imgui.push_font(font)
        
        # Draw black stroke if requested (draws text offset in 8 directions)
        if stroke:
            black_col = imgui.get_color_u32_rgba(0.0, 0.0, 0.0, 1.0)
            stroke_offset = 1.0
            for dx in [-stroke_offset, 0, stroke_offset]:
                for dy in [-stroke_offset, 0, stroke_offset]:
                    if dx == 0 and dy == 0:
                        continue
                    self.draw_list.add_text(float(x + dx), float(y + dy), black_col, str(text))
        
        # Draw main text
        col = imgui.get_color_u32_rgba(r/255.0, g/255.0, b/255.0, 1.0)
        self.draw_list.add_text(float(x), float(y), col, str(text))
        
        # Pop font if we pushed one
        if font:
            imgui.pop_font()
    
    def calc_text_width(self, text, size=13.0, font_name=None):
        """Calculate text width for centering purposes."""
        # Get font if specified
        font = None
        if font_name and font_name in self.overlay_fonts:
            available_sizes = list(self.overlay_fonts[font_name].keys())
            if available_sizes:
                closest_size = min(available_sizes, key=lambda s: abs(s - size))
                font = self.overlay_fonts[font_name].get(closest_size)
        
        # Push font if available
        if font:
            imgui.push_font(font)
        
        text_size = imgui.calc_text_size(str(text))
        
        # Pop font if we pushed one
        if font:
            imgui.pop_font()
        
        return text_size.x
    
    def destroy(self):
        """Destroy the overlay window and cleanup."""
        self.running = False
        
        if self.impl:
            self.impl.shutdown()
            self.impl = None
        
        if self.window:
            glfw.destroy_window(self.window)
            self.window = None
        
        glfw.terminate()


# =============================================================================
# ESP RENDERING FUNCTIONS
# =============================================================================

def render_esp_frame(overlay, pm, client, settings):
    """
    Render a single ESP frame.
    
    Main ESP rendering pipeline:
    1. Read view matrix (transforms 3D world coords to 2D screen coords)
    2. Read local player info (team, position) for filtering
    3. Iterate through entity list (up to 64 players)
    4. For each valid player:
       - Check if alive and on correct team (based on targeting settings)
       - Read player data (position, health, team, bones)
       - Convert 3D positions to 2D screen coordinates
       - Draw ESP elements (box, skeleton, health bar, snap lines, head dot)
    
    Performance optimizations:
    - Batch memory reads where possible
    - Early exit for invalid/dead players
    - Skip world-to-screen conversion if player data invalid
    
    Args:
        overlay: ESPOverlay instance for drawing
        pm: pymem instance for memory reading
        client: client.dll base address
        settings: ESP settings dictionary (esp_enabled, box_esp, etc.)
    """
    if not overlay or not pm or not client:
        return
    
    width = overlay.width
    height = overlay.height
    
    # Read view matrix in one call (64 bytes = 16 floats)
    try:
        matrix_bytes = pm.read_bytes(client + dwViewMatrix, 64)
        view_matrix = struct.unpack('16f', matrix_bytes)
    except Exception:
        return
    
    # Read local player info
    try:
        local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
        local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
        # Read local player position for distance calculation
        local_game_scene = pm.read_longlong(local_player_pawn_addr + m_pGameSceneNode)
        local_origin_x = pm.read_float(local_game_scene + m_vecAbsOrigin)
        local_origin_y = pm.read_float(local_game_scene + m_vecAbsOrigin + 4)
        local_origin_z = pm.read_float(local_game_scene + m_vecAbsOrigin + 8)
    except Exception:
        return
    
    # Get center position for snap lines
    center_x = width // 2
    lines_position = settings.get('lines_position', 'Bottom')
    center_y = 0 if lines_position == 'Top' else height
    
    # Read entity list
    try:
        entity_list = pm.read_longlong(client + dwEntityList)
        list_entry = pm.read_longlong(entity_list + 0x10)
    except Exception:
        return
    
    targeting_type = settings.get('targeting_type', 0)
    
    # Loop through players
    for i in range(1, 64):
        try:
            if list_entry == 0:
                break
            
            # Read controller (Updated offset from 0x78 to 0x70 for CS2 update)
            current_controller = pm.read_longlong(list_entry + i * 0x70)
            if current_controller == 0:
                continue
            
            # Get pawn handle
            pawn_handle = pm.read_int(current_controller + m_hPlayerPawn)
            if pawn_handle == 0:
                continue
            
            # Get pawn address (Updated offset from 0x78 to 0x70 for CS2 update)
            list_entry2 = pm.read_longlong(entity_list + 0x8 * ((pawn_handle & 0x7FFF) >> 9) + 0x10)
            if list_entry2 == 0:
                continue
            
            entity_pawn_addr = pm.read_longlong(list_entry2 + 0x70 * (pawn_handle & 0x1FF))
            if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                continue
            
            # Check team
            entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
            if entity_team == local_player_team and targeting_type == 0:
                continue
            
            # Check health
            entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
            if entity_hp <= 0:
                continue
            
            # Read armor value (only if armor bar is enabled)
            entity_armor = 0
            if settings.get('armor_bar', True):
                try:
                    entity_armor = pm.read_int(entity_pawn_addr + m_ArmorValue)
                except:
                    entity_armor = 0
            
            # Check alive state
            entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
            if entity_alive != 256:
                continue
            
            # Check spotted state for hide spotted players feature
            is_spotted = False
            if settings.get('hide_spotted_players', False) or settings.get('spotted_esp', True):
                try:
                    spotted_flag = pm.read_int(entity_pawn_addr + m_entitySpottedState + m_bSpotted)
                    is_spotted = spotted_flag != 0
                except:
                    try:
                        is_spotted = pm.read_bool(entity_pawn_addr + m_entitySpottedState + m_bSpotted)
                    except:
                        is_spotted = False
            
            # Determine color based on team
            is_teammate = entity_team == local_player_team
            
            # Get custom colors from settings
            if is_teammate:
                box_color = settings.get('team_box_color', (71, 167, 106))
                snapline_color = settings.get('team_snapline_color', (71, 167, 106))
                skeleton_color = settings.get('team_skeleton_color', (255, 255, 255))
                head_dot_color = settings.get('team_head_dot_color', (255, 255, 0))
            else:
                box_color = settings.get('enemy_box_color', (196, 30, 58))
                snapline_color = settings.get('enemy_snapline_color', (196, 30, 58))
                skeleton_color = settings.get('enemy_skeleton_color', (255, 255, 255))
                head_dot_color = settings.get('enemy_head_dot_color', (255, 255, 0))
            
            # Get bone positions for ESP
            game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
            bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
            
            # Read entity position for distance calculation
            entity_origin_x = pm.read_float(game_scene + m_vecAbsOrigin)
            entity_origin_y = pm.read_float(game_scene + m_vecAbsOrigin + 4)
            entity_origin_z = pm.read_float(game_scene + m_vecAbsOrigin + 8)
            
            # Apply ESP distance filter if enabled
            if settings.get('esp_distance_filter_enabled', False):
                # Calculate 3D distance between local player and entity
                distance = math.sqrt(
                    (entity_origin_x - local_origin_x) ** 2 +
                    (entity_origin_y - local_origin_y) ** 2 +
                    (entity_origin_z - local_origin_z) ** 2
                )
                
                filter_type = settings.get('esp_distance_filter_type', 'Further than')
                filter_distance = settings.get('esp_distance_filter_distance', 25.0)
                filter_mode = settings.get('esp_distance_filter_mode', 'Only Show')
                
                # Calculate displayed distance in meters (same as ESP display)
                displayed_distance_m = int(distance / 100)
                
                # Check if entity matches the filter criteria using displayed distance
                matches_filter = False
                if filter_type == 'Further than':
                    matches_filter = displayed_distance_m > filter_distance
                elif filter_type == 'Closer than':
                    matches_filter = displayed_distance_m < filter_distance
                
                # Apply filter mode
                if filter_mode == 'Only Show':
                    if not matches_filter:
                        continue  # Skip this entity
                elif filter_mode == 'Hide':
                    if matches_filter:
                        continue  # Skip this entity
            
            # Update Footstep ESP tracking for this entity
            if settings.get('footstep_esp', False):
                update_footstep_esp(pm, entity_pawn_addr, game_scene, local_player_team, entity_team, settings)
            
            # Read head bone (bone 6) in one call - 12 bytes for X, Y, Z
            head_bytes = pm.read_bytes(bone_matrix + 6 * 0x20, 12)
            headX, headY, headZ = struct.unpack('3f', head_bytes)
            headZ += 8  # Offset for head height
            
            # Read leg bone Z (bone 28)
            legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
            
            # Convert to screen coordinates
            head_pos = w2s(view_matrix, headX, headY, headZ, width, height)
            if head_pos[0] == -999:
                continue
            
            leg_pos = w2s(view_matrix, headX, headY, legZ, width, height)
            
            # Calculate box dimensions
            deltaZ = abs(head_pos[1] - leg_pos[1])
            box_width = deltaZ // 2
            leftX = head_pos[0] - box_width // 2
            rightX = head_pos[0] + box_width // 2
            
            # Draw snap lines
            if settings.get('line_esp', True) and not (settings.get('hide_spotted_players', False) and is_spotted):
                snapline_thickness = settings.get('snapline_thickness', 1.5)
                if lines_position == 'Top':
                    line_end_x = head_pos[0]
                    line_end_y = head_pos[1]
                else:
                    line_end_x = head_pos[0]
                    line_end_y = leg_pos[1]
                overlay.draw_line_rgb(center_x, center_y, line_end_x, line_end_y, snapline_color, snapline_thickness)
            
            # Draw box ESP
            if settings.get('box_esp', True) and not (settings.get('hide_spotted_players', False) and is_spotted):
                box_thickness = settings.get('box_thickness', 1.5)
                box_type = settings.get('box_type', '2D')
                
                if box_type == '3D':
                    # 3D box - draw a rectangular prism around the player using fixed player dimensions
                    player_width = 32.0
                    player_length = 32.0
                    player_height = 72.0
                    
                    try:
                        # Get player's absolute origin
                        game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
                        origin_x = pm.read_float(game_scene + m_vecAbsOrigin)
                        origin_y = pm.read_float(game_scene + m_vecAbsOrigin + 4)
                        origin_z = pm.read_float(game_scene + m_vecAbsOrigin + 8)
                        
                        half_width = player_width / 2
                        half_length = player_length / 2
                        
                        # Define 8 corners of the 3D bounding box in world space
                        # Bottom 4 corners (at feet level)
                        bottom_corners = [
                            (origin_x - half_width, origin_y - half_length, origin_z),                    # back-left-bottom
                            (origin_x + half_width, origin_y - half_length, origin_z),                    # back-right-bottom
                            (origin_x + half_width, origin_y + half_length, origin_z),                    # front-right-bottom
                            (origin_x - half_width, origin_y + half_length, origin_z),                    # front-left-bottom
                        ]
                        
                        # Top 4 corners (at head level)
                        top_corners = [
                            (origin_x - half_width, origin_y - half_length, origin_z + player_height),    # back-left-top
                            (origin_x + half_width, origin_y - half_length, origin_z + player_height),    # back-right-top
                            (origin_x + half_width, origin_y + half_length, origin_z + player_height),    # front-right-top
                            (origin_x - half_width, origin_y + half_length, origin_z + player_height),    # front-left-top
                        ]
                        
                        # Convert all corners to screen space
                        bottom_screen = []
                        top_screen = []
                        
                        all_corners_valid = True
                        for corner in bottom_corners:
                            screen_pos = w2s(view_matrix, corner[0], corner[1], corner[2], width, height)
                            if screen_pos[0] == -999:
                                all_corners_valid = False
                                break
                            bottom_screen.append(screen_pos)
                            
                        if all_corners_valid:
                            for corner in top_corners:
                                screen_pos = w2s(view_matrix, corner[0], corner[1], corner[2], width, height)
                                if screen_pos[0] == -999:
                                    all_corners_valid = False
                                    break
                                top_screen.append(screen_pos)
                        
                        if all_corners_valid:
                            # Draw the 12 edges of the 3D box
                            # Bottom face (4 edges)
                            for i in range(4):
                                next_i = (i + 1) % 4
                                overlay.draw_line_rgb(bottom_screen[i][0], bottom_screen[i][1], 
                                                    bottom_screen[next_i][0], bottom_screen[next_i][1], box_color, box_thickness)
                            
                            # Top face (4 edges)
                            for i in range(4):
                                next_i = (i + 1) % 4
                                overlay.draw_line_rgb(top_screen[i][0], top_screen[i][1],
                                                    top_screen[next_i][0], top_screen[next_i][1], box_color, box_thickness)
                            
                            # Vertical edges connecting top and bottom (4 edges)
                            for i in range(4):
                                overlay.draw_line_rgb(bottom_screen[i][0], bottom_screen[i][1],
                                                    top_screen[i][0], top_screen[i][1], box_color, box_thickness)
                        else:
                            # Fallback to 2D box if 3D corners are not visible
                            overlay.draw_rect_rgb(leftX, head_pos[1], box_width, deltaZ, box_color, box_thickness)
                            
                    except Exception:
                        # Fallback to 2D box on error
                        overlay.draw_rect_rgb(leftX, head_pos[1], box_width, deltaZ, box_color, box_thickness)
                else:
                    # 2D box (default)
                    overlay.draw_rect_rgb(leftX, head_pos[1], box_width, deltaZ, box_color, box_thickness)
            if settings.get('health_bar', True) and not (settings.get('hide_spotted_players', False) and is_spotted):
                hp_percent = entity_hp / 100.0
                healthbar_type = settings.get('healthbar_type', 'Vertical Left')
                bar_thickness = 3
                
                if healthbar_type == 'Horizontal Below':
                    # Horizontal health bar below player
                    bar_y = head_pos[1] + deltaZ + 2
                    hp_width = int(box_width * hp_percent)
                    overlay.draw_filled_rect_brush(leftX, bar_y, box_width, bar_thickness, 'health_bg')
                    if hp_percent > 0.5:
                        overlay.draw_filled_rect_brush(leftX, bar_y, hp_width, bar_thickness, 'health_green')
                    elif hp_percent > 0.25:
                        overlay.draw_filled_rect_brush(leftX, bar_y, hp_width, bar_thickness, 'health_yellow')
                    else:
                        overlay.draw_filled_rect_brush(leftX, bar_y, hp_width, bar_thickness, 'health_red')
                elif healthbar_type == 'Horizontal Above':
                    # Horizontal health bar above player
                    bar_y = head_pos[1] - 7
                    hp_width = int(box_width * hp_percent)
                    overlay.draw_filled_rect_brush(leftX, bar_y, box_width, bar_thickness, 'health_bg')
                    if hp_percent > 0.5:
                        overlay.draw_filled_rect_brush(leftX, bar_y, hp_width, bar_thickness, 'health_green')
                    elif hp_percent > 0.25:
                        overlay.draw_filled_rect_brush(leftX, bar_y, hp_width, bar_thickness, 'health_yellow')
                    else:
                        overlay.draw_filled_rect_brush(leftX, bar_y, hp_width, bar_thickness, 'health_red')
                elif healthbar_type == 'Vertical Right':
                    # Vertical health bar on the right
                    hp_height = int(deltaZ * hp_percent)
                    bar_x = leftX + box_width + 2
                    overlay.draw_filled_rect_brush(bar_x, head_pos[1], bar_thickness, deltaZ, 'health_bg')
                    if hp_percent > 0.5:
                        overlay.draw_filled_rect_brush(bar_x, head_pos[1] + (deltaZ - hp_height), bar_thickness, hp_height, 'health_green')
                    elif hp_percent > 0.25:
                        overlay.draw_filled_rect_brush(bar_x, head_pos[1] + (deltaZ - hp_height), bar_thickness, hp_height, 'health_yellow')
                    else:
                        overlay.draw_filled_rect_brush(bar_x, head_pos[1] + (deltaZ - hp_height), bar_thickness, hp_height, 'health_red')
                else:
                    # Vertical Left (default)
                    hp_height = int(deltaZ * hp_percent)
                    bar_x = leftX - 5
                    overlay.draw_filled_rect_brush(bar_x, head_pos[1], bar_thickness, deltaZ, 'health_bg')
                    if hp_percent > 0.5:
                        overlay.draw_filled_rect_brush(bar_x, head_pos[1] + (deltaZ - hp_height), bar_thickness, hp_height, 'health_green')
                    elif hp_percent > 0.25:
                        overlay.draw_filled_rect_brush(bar_x, head_pos[1] + (deltaZ - hp_height), bar_thickness, hp_height, 'health_yellow')
                    else:
                        overlay.draw_filled_rect_brush(bar_x, head_pos[1] + (deltaZ - hp_height), bar_thickness, hp_height, 'health_red')
            
            # Draw armor bar
            if settings.get('armor_bar', True) and entity_armor > 0 and not (settings.get('hide_spotted_players', False) and is_spotted):
                armor_percent = min(1.0, entity_armor / 100.0)
                healthbar_type = settings.get('healthbar_type', 'Vertical Left')
                bar_thickness = 3
                
                if healthbar_type == 'Horizontal Below':
                    # Horizontal armor bar below health bar
                    bar_y = head_pos[1] + deltaZ + 6  # Below health bar (2 + 3 + 1)
                    armor_width = int(box_width * armor_percent)
                    overlay.draw_filled_rect_brush(leftX, bar_y, box_width, bar_thickness, 'health_bg')
                    overlay.draw_filled_rect_brush(leftX, bar_y, armor_width, bar_thickness, 'armor_blue')
                elif healthbar_type == 'Horizontal Above':
                    # Horizontal armor bar above health bar
                    bar_y = head_pos[1] - 11  # Above health bar (-7 - 3 - 1)
                    armor_width = int(box_width * armor_percent)
                    overlay.draw_filled_rect_brush(leftX, bar_y, box_width, bar_thickness, 'health_bg')
                    overlay.draw_filled_rect_brush(leftX, bar_y, armor_width, bar_thickness, 'armor_blue')
                elif healthbar_type == 'Vertical Right':
                    # Vertical armor bar to the right of health bar
                    armor_height = int(deltaZ * armor_percent)
                    armor_bar_x = leftX + box_width + 7  # Right of health bar (2 + 3 + 2)
                    overlay.draw_filled_rect_brush(armor_bar_x, head_pos[1], bar_thickness, deltaZ, 'health_bg')
                    overlay.draw_filled_rect_brush(armor_bar_x, head_pos[1] + (deltaZ - armor_height), bar_thickness, armor_height, 'armor_blue')
                else:
                    # Vertical Left (default) - armor to the left of health bar
                    armor_height = int(deltaZ * armor_percent)
                    armor_bar_x = leftX - 10
                    overlay.draw_filled_rect_brush(armor_bar_x, head_pos[1], bar_thickness, deltaZ, 'health_bg')
                    overlay.draw_filled_rect_brush(armor_bar_x, head_pos[1] + (deltaZ - armor_height), bar_thickness, armor_height, 'armor_blue')
            
            # Draw head dot (anti-aliased circle with ImGui)
            if settings.get('head_dot', True) and not (settings.get('hide_spotted_players', False) and is_spotted):
                head_screen = w2s(view_matrix, headX, headY, headZ - 8, width, height)
                if head_screen[0] != -999:
                    # Scale radius based on box dimensions (similar to script.pyw head hitbox)
                    head_dot_size = box_width / 5
                    head_dot_radius = max(2, head_dot_size * 1.414 / 2)  # sqrt(2) ≈ 1.414
                    overlay.draw_circle_filled_rgb(head_screen[0], head_screen[1], head_dot_radius, head_dot_color, 12)
            
            # Track vertical offset for text stacking above head
            # Adjust based on healthbar type to avoid overlapping with horizontal above bars
            healthbar_type = settings.get('healthbar_type', 'Vertical Left')
            if healthbar_type == 'Horizontal Above':
                # Account for both health bar (-7 to -4) and armor bar (-11 to -8) if armor is enabled
                if settings.get('armor_bar', True) and entity_armor > 0:
                    text_y_offset = head_pos[1] - 14  # Start above armor bar
                else:
                    text_y_offset = head_pos[1] - 10  # Start above health bar only
            else:
                text_y_offset = head_pos[1] - 5  # Start just above head
            
            # Draw player nickname above head
            if settings.get('name_esp', False) and not (settings.get('hide_spotted_players', False) and is_spotted):
                try:
                    player_name = pm.read_string(current_controller + m_iszPlayerName, 32)
                    if player_name:
                        # Use configurable font size
                        font_size = settings.get('name_text_size', 14.0)
                        selected_font = settings.get('menu_font', 'Default')
                        
                        # Calculate text width for centering
                        text_width = overlay.calc_text_width(player_name, font_size, selected_font)
                        text_x = head_pos[0] - (text_width / 2)  # Center horizontally
                        
                        # Draw with white color and shadow/stroke for visibility
                        overlay.draw_text(text_x, text_y_offset - font_size, player_name, 255, 255, 255, size=font_size, stroke=True, font_name=selected_font)
                        
                        # Move offset up for next text element (tighter spacing)
                        text_y_offset -= (font_size + 1)
                except:
                    pass
            
            # Draw spotted indicator (above head, or above nickname if enabled)
            if settings.get('spotted_esp', True):
                try:
                    # Read spotted state
                    spotted_flag = pm.read_int(entity_pawn_addr + m_entitySpottedState + m_bSpotted)
                    is_spotted = spotted_flag != 0
                except:
                    try:
                        is_spotted = pm.read_bool(entity_pawn_addr + m_entitySpottedState + m_bSpotted)
                    except:
                        is_spotted = False
                
                # Draw text indicator above head
                spotted_text = "(Spotted)" if is_spotted else "(Not Spotted)"
                spotted_color = settings.get('spotted_color', (0, 255, 0)) if is_spotted else settings.get('not_spotted_color', (255, 0, 0))
                
                text_size = settings.get('spotted_text_size', 12.0)
                selected_font = settings.get('menu_font', 'Default')
                
                # Calculate text width for centering
                text_width = overlay.calc_text_width(spotted_text, text_size, selected_font)
                text_x = head_pos[0] - (text_width / 2)  # Center horizontally
                
                overlay.draw_text(text_x, text_y_offset - text_size, spotted_text, spotted_color[0], spotted_color[1], spotted_color[2], size=text_size, stroke=True, font_name=selected_font)
            
            # Draw skeleton
            if settings.get('skeleton_esp', True) and not (settings.get('hide_spotted_players', False) and is_spotted):
                skeleton_thickness = settings.get('skeleton_thickness', 1.5)
                draw_skeleton(overlay, pm, bone_matrix, view_matrix, width, height, skeleton_color, skeleton_thickness)
            
            # Draw distance over the bones
            if settings.get('distance_esp', True) and not (settings.get('hide_spotted_players', False) and is_spotted):
                # Calculate distance from local player to this entity
                dx = entity_origin_x - local_origin_x
                dy = entity_origin_y - local_origin_y
                dz = entity_origin_z - local_origin_z
                distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                # Display distance in meters (assuming units are in game units, roughly 1 unit = 1 cm, so divide by 100)
                distance_m = int(distance / 100)
                distance_text = f"{distance_m}m"
                
                # Draw at center of player box (over bones)
                center_x = head_pos[0]
                center_y = (head_pos[1] + leg_pos[1]) / 2
                
                text_size = 12.0
                selected_font = settings.get('menu_font', 'Default')
                
                # Calculate text width for centering
                text_width = overlay.calc_text_width(distance_text, text_size, selected_font)
                text_x = center_x - (text_width / 2)
                
                # Draw with white color
                overlay.draw_text(text_x, center_y - text_size/2, distance_text, 255, 255, 255, size=text_size, stroke=True, font_name=selected_font)
            
            # Draw weapon name below the player
            if settings.get('weapon_esp', True) and not (settings.get('hide_spotted_players', False) and is_spotted):
                try:
                    # Get current weapon from pawn
                    current_weapon_addr = pm.read_longlong(entity_pawn_addr + m_pClippingWeapon)
                    if current_weapon_addr != 0:
                        # Get weapon definition index
                        weapon_def_index = pm.read_int(current_weapon_addr + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
                        
                        # Get weapon name from mapping
                        weapon_name = WEAPON_NAMES.get(weapon_def_index, f"Unknown ({weapon_def_index})")
                        
                        # Check if we should hide unknown weapons
                        if not settings.get('hide_unknown_weapons', False) or weapon_def_index in WEAPON_NAMES:
                            # Draw below the player box
                            weapon_text = weapon_name
                            weapon_text_size = settings.get('weapon_text_size', 11.0)
                            selected_font = settings.get('menu_font', 'Default')
                            
                            # Calculate text width for centering
                            weapon_text_width = overlay.calc_text_width(weapon_text, weapon_text_size, selected_font)
                            weapon_text_x = head_pos[0] - (weapon_text_width / 2)
                            
                            # Position weapon text below player, accounting for health/shield bars
                            healthbar_type = settings.get('healthbar_type', 'Vertical Left')
                            if healthbar_type == 'Horizontal Below':
                                # Position below health and armor bars when they are at the bottom
                                if settings.get('armor_bar', True) and entity_armor > 0:
                                    # Both health and armor bars are present: health at +2, armor at +6, each 3px high
                                    weapon_text_y = head_pos[1] + deltaZ + 11  # 2 + 3 + 1 + 3 + 2 = below both bars
                                else:
                                    # Only health bar present: at +2, 3px high
                                    weapon_text_y = head_pos[1] + deltaZ + 7  # 2 + 3 + 2 = below health bar
                            else:
                                # Health bars are vertical or above, so position just below feet
                                weapon_text_y = leg_pos[1] + 2
                            
                            # Draw with white color
                            overlay.draw_text(weapon_text_x, weapon_text_y, weapon_text, 255, 255, 255, size=weapon_text_size, stroke=True, font_name=selected_font)
                except Exception:
                    pass
                
        except Exception:
            continue
    
    # Render Footstep ESP rings (after all players processed)
    if settings.get('footstep_esp', False):
        render_footstep_esp(overlay, pm, client, view_matrix, settings, width, height)


def draw_skeleton(overlay, pm, bone_matrix, view_matrix, width, height, skeleton_color=(255, 255, 255), thickness=1.5):
    """
    Draw player skeleton by connecting bone positions.
    
    Process:
    1. Read all bone positions from bone matrix (head, neck, spine, limbs, etc.)
    2. Convert 3D bone positions to 2D screen coordinates
    3. Draw lines between connected bones (defined in BONE_CONNECTIONS)
    
    The bone matrix contains transformation data for each bone in the player's
    skeleton. Each bone has an ID (0-27) and stores X, Y, Z coordinates.
    
    Args:
        overlay: ESPOverlay instance for drawing
        pm: pymem instance for memory reading
        bone_matrix: Base address of bone matrix in memory
        view_matrix: View matrix for world-to-screen conversion
        width: Screen width
        height: Screen height
        skeleton_color: RGB tuple for skeleton line color
        thickness: Line thickness for skeleton
    """
    bone_positions = {}
    
    try:
        # Read bones more efficiently - batch read where possible
        # Each bone is at bone_id * 0x20, with X, Y, Z as first 12 bytes
        for bone_name, bone_id in BONE_IDS.items():
            try:
                # Read X, Y, Z in one call (12 bytes)
                bone_bytes = pm.read_bytes(bone_matrix + bone_id * 0x20, 12)
                boneX, boneY, boneZ = struct.unpack('3f', bone_bytes)
                bone_pos = w2s(view_matrix, boneX, boneY, boneZ, width, height)
                if bone_pos[0] != -999:
                    bone_positions[bone_name] = bone_pos
            except:
                continue
        
        # Draw bone connections
        for bone1, bone2 in BONE_CONNECTIONS:
            if bone1 in bone_positions and bone2 in bone_positions:
                pos1 = bone_positions[bone1]
                pos2 = bone_positions[bone2]
                overlay.draw_line_rgb(pos1[0], pos1[1], pos2[0], pos2[1], skeleton_color, thickness)
    except Exception:
        pass


def update_footstep_esp(pm, entity_pawn_addr, game_scene, local_player_team, entity_team, settings):
    """
    Update footstep ESP cache for an entity based on velocity changes.
    
    This function detects when a player makes noise (through velocity changes)
    and adds a ring to be rendered at their current position.
    
    Args:
        pm: pymem instance for memory reading
        entity_pawn_addr: Entity pawn memory address
        game_scene: Game scene node address
        local_player_team: Local player's team number
        entity_team: Entity's team number
        settings: ESP settings dictionary
    """
    global footstep_esp_cache
    
    # Check targeting type - skip teammates unless targeting all players
    targeting_type = settings.get('targeting_type', 0)
    if entity_team == local_player_team and targeting_type == 0:
        return
    
    try:
        # Read current velocity
        vel_bytes = pm.read_bytes(entity_pawn_addr + m_vecVelocity, 12)
        vel_x, vel_y, vel_z = struct.unpack('3f', vel_bytes)
        
        # Calculate velocity magnitude (horizontal movement for footsteps)
        velocity_mag = math.sqrt(vel_x * vel_x + vel_y * vel_y)
        
        # Read current origin
        origin_x = pm.read_float(game_scene + m_vecAbsOrigin)
        origin_y = pm.read_float(game_scene + m_vecAbsOrigin + 4)
        origin_z = pm.read_float(game_scene + m_vecAbsOrigin + 8)
        
        current_origin = (origin_x, origin_y, origin_z)
        current_velocity = (vel_x, vel_y, vel_z)
        
        # Initialize cache for this entity if needed
        if entity_pawn_addr not in footstep_esp_cache["ring_cache"]:
            footstep_esp_cache["ring_cache"][entity_pawn_addr] = []
            footstep_esp_cache["last_velocity"][entity_pawn_addr] = (0, 0, 0)
            footstep_esp_cache["last_origin"][entity_pawn_addr] = current_origin
        
        # Get last velocity
        last_vel = footstep_esp_cache["last_velocity"].get(entity_pawn_addr, (0, 0, 0))
        last_vel_mag = math.sqrt(last_vel[0] * last_vel[0] + last_vel[1] * last_vel[1])
        
        # Detect sound-producing movement (velocity threshold for footsteps)
        # Sound is produced when player is moving at walking/running speed
        footstep_threshold = 50.0  # Minimum velocity to produce footstep sounds
        
        # Add a ring if the player is making noise (moving above threshold)
        # We use a cooldown to prevent too many rings
        if velocity_mag > footstep_threshold:
            rings = footstep_esp_cache["ring_cache"][entity_pawn_addr]
            
            # Check if enough time passed since last ring (cooldown ~0.25 seconds)
            should_add_ring = True
            if len(rings) > 0:
                last_ring_time = rings[-1]["start_time"]
                if time.time() - last_ring_time < 0.25:
                    should_add_ring = False
            
            if should_add_ring:
                # Add new ring at current position
                footstep_esp_cache["ring_cache"][entity_pawn_addr].append({
                    "start_time": time.time(),
                    "origin": current_origin
                })
        
        # Update cached values
        footstep_esp_cache["last_velocity"][entity_pawn_addr] = current_velocity
        footstep_esp_cache["last_origin"][entity_pawn_addr] = current_origin
        
    except Exception:
        pass


def render_footstep_esp(overlay, pm, client, view_matrix, settings, width, height):
    """
    Render footstep ESP rings for all tracked enemies.
    
    Each ring expands outward from the point where the enemy made noise,
    shrinking in radius over time until it disappears.
    
    Args:
        overlay: ESPOverlay instance for drawing
        pm: pymem instance for memory reading
        client: client.dll base address
        view_matrix: Current view matrix
        settings: ESP settings dictionary
        width: Screen width
        height: Screen height
    """
    global footstep_esp_cache
    
    if not settings.get('footstep_esp', False):
        return
    
    sound_color = settings.get('footstep_esp_color', (255, 165, 0))  # Orange default
    duration = settings.get('footstep_esp_duration', 1.0)
    current_time = time.time()
    
    # Iterate through all tracked entities
    entities_to_clean = []
    
    for entity_addr, rings in footstep_esp_cache["ring_cache"].items():
        # Process rings in reverse order for safe removal
        for r in range(len(rings) - 1, -1, -1):
            ring = rings[r]
            
            elapsed = current_time - ring["start_time"]
            
            # Remove expired rings
            if elapsed >= duration:
                rings.pop(r)
                continue
            
            # Calculate ring radius (starts at 30, shrinks to 0)
            progress = elapsed / duration
            radius = 30.0 * (1.0 - progress)
            
            if radius < 1.0:
                continue
            
            # Get ring origin in world space
            origin = ring["origin"]
            
            # Draw the ring as a circle in world space
            # We'll draw multiple points and connect them
            segments = 36  # Number of segments for the circle
            points = []
            
            for i in range(segments + 1):
                angle = (2.0 * math.pi * i) / segments
                x_offset = radius * math.cos(angle)
                y_offset = radius * math.sin(angle)
                
                # World position of this point
                world_x = origin[0] + x_offset
                world_y = origin[1] + y_offset
                world_z = origin[2]  # Ring is at player's feet level
                
                # Convert to screen space
                screen_pos = w2s(view_matrix, world_x, world_y, world_z, width, height)
                
                if screen_pos[0] != -999:
                    points.append(screen_pos)
                else:
                    # If a point is off-screen, draw what we have and start fresh
                    if len(points) > 1:
                        for j in range(len(points) - 1):
                            overlay.draw_line_rgb(
                                points[j][0], points[j][1],
                                points[j+1][0], points[j+1][1],
                                sound_color, 2.0
                            )
                    points = []
            
            # Draw remaining connected points
            if len(points) > 1:
                for j in range(len(points) - 1):
                    overlay.draw_line_rgb(
                        points[j][0], points[j][1],
                        points[j+1][0], points[j+1][1],
                        sound_color, 2.0
                    )
        
        # Mark empty entity caches for cleanup
        if len(rings) == 0:
            entities_to_clean.append(entity_addr)
    
    # Clean up empty caches (don't remove to allow re-detection)
    # We keep the last_velocity cache to detect future sounds


def render_bomb_esp(overlay, pm, client, settings):
    """
    Render bomb ESP showing planted C4 location and timer.
    
    Features:
    - Shows bomb position with "BOMB: X.XX" timer
    - Shows defuse timer when bomb is being defused
    - Color coding: Red = can't defuse in time, Green = can defuse, White = not being defused
    
    Args:
        overlay: ESPOverlay instance for drawing
        pm: pymem instance for memory reading
        client: client.dll base address
        settings: ESP settings dictionary
    """
    global BombPlantedTime, BombDefusedTime
    
    try:
        if not settings or not isinstance(settings, dict):
            return
            
        # Check if bomb ESP is enabled
        if not settings.get('bomb_esp', True):
            return
        
        width = overlay.width
        height = overlay.height
        
        # Read view matrix
        matrix_bytes = pm.read_bytes(client + dwViewMatrix, 64)
        view_matrix = struct.unpack('16f', matrix_bytes)
        
        # Check if bomb is planted
        def bomb_is_planted():
            global BombPlantedTime
            try:
                is_planted = pm.read_bool(client + dwPlantedC4 - 0x8)
                if is_planted:
                    if BombPlantedTime == 0:
                        BombPlantedTime = time.time()
                else:
                    BombPlantedTime = 0
                return is_planted
            except:
                return False
        
        # Get C4 base class address
        def get_c4_base_class():
            try:
                planted_c4 = pm.read_longlong(client + dwPlantedC4)
                planted_c4_class = pm.read_longlong(planted_c4)
                return planted_c4_class
            except:
                return None
        
        # Get bomb world-to-screen position
        def get_bomb_position_wts():
            try:
                c4_base = get_c4_base_class()
                if not c4_base:
                    return None
                c4_node = pm.read_longlong(c4_base + m_pGameSceneNode)
                c4_pos_x = pm.read_float(c4_node + m_vecAbsOrigin)
                c4_pos_y = pm.read_float(c4_node + m_vecAbsOrigin + 0x4)
                c4_pos_z = pm.read_float(c4_node + m_vecAbsOrigin + 0x8)
                bomb_pos = w2s(view_matrix, c4_pos_x, c4_pos_y, c4_pos_z, width, height)
                return bomb_pos
            except:
                return None
        
        # Get remaining bomb time
        def get_bomb_time():
            try:
                c4_base = get_c4_base_class()
                if not c4_base:
                    return 0
                bomb_time = pm.read_float(c4_base + m_flTimerLength) - (time.time() - BombPlantedTime)
                return bomb_time if bomb_time >= 0 else 0
            except:
                return 0
        
        # Check if bomb is being defused
        def is_being_defused():
            global BombDefusedTime
            try:
                c4_base = get_c4_base_class()
                if not c4_base:
                    return False
                is_defused = pm.read_bool(c4_base + m_bBeingDefused)
                if is_defused:
                    if BombDefusedTime == 0:
                        BombDefusedTime = time.time()
                else:
                    BombDefusedTime = 0
                return is_defused
            except:
                return False
        
        # Get defuse time remaining
        def get_defuse_time():
            try:
                c4_base = get_c4_base_class()
                if not c4_base:
                    return 0
                if is_being_defused():
                    defuse_time = pm.read_float(c4_base + m_flDefuseLength) - (time.time() - BombDefusedTime)
                    return defuse_time if defuse_time >= 0 else 0
                return 0
            except:
                return 0
        
        # Render bomb info if planted
        if bomb_is_planted():
            bomb_position = get_bomb_position_wts()
            bomb_time = get_bomb_time()
            defuse_time = get_defuse_time()
            
            if bomb_position and bomb_position[0] > 0 and bomb_position[1] > 0:
                # Build bomb text and determine color
                if defuse_time > 0:
                    bomb_text = f"BOMB: {bomb_time:.2f} | DEFUSE: {defuse_time:.2f}"
                    if bomb_time < defuse_time:
                        # Can't defuse in time - red
                        text_color = (255, 0, 0)
                    elif bomb_time > defuse_time:
                        # Can defuse in time - green
                        text_color = (0, 255, 0)
                    else:
                        # Equal - yellow
                        text_color = (255, 255, 0)
                else:
                    bomb_text = f"BOMB: {bomb_time:.2f}"
                    text_color = (255, 255, 255)  # White when not being defused
                
                # Draw bomb text with stroke for visibility
                # Offset left and up a few pixels for better positioning
                bomb_x = bomb_position[0] - 40
                bomb_y = bomb_position[1] - 15
                
                overlay.draw_text(bomb_x, bomb_y, bomb_text, 
                                  text_color[0], text_color[1], text_color[2], 
                                  size=14.0, stroke=True)
                
    except Exception:
        pass


def render_radar(overlay, pm, client, settings):
    """
    Render a radar overlay showing enemy positions relative to local player.
    
    Features:
    - Circular radar with configurable size and position
    - Local player at center (white dot)
    - Enemies shown as red dots, teammates as green
    - Rotation based on player view angle
    - Height indicators (arrows up/down when enemies on different levels)
    
    Args:
        overlay: ESPOverlay instance for drawing
        pm: pymem instance for memory reading
        client: client.dll base address
        settings: ESP settings dictionary
    """
    try:
        if not settings or not isinstance(settings, dict):
            return
            
        if not settings.get('radar_enabled', False):
            return
        
        width = overlay.width
        height = overlay.height
        
        # Get radar settings
        radar_overlap_game = settings.get('radar_overlap_game', False)
        
        if radar_overlap_game:
            # Use locked values for game radar overlap
            radar_size = 250
            radar_scale = 15.0
            radar_x_offset = -810
            radar_y_offset = -390
            radar_opacity = 50
        else:
            # Use normal configurable values
            radar_size = settings.get('radar_size', 200)
            radar_scale = settings.get('radar_scale', 5.0)
            radar_x_offset = settings.get('radar_x', 0)
            radar_y_offset = settings.get('radar_y', 0)
            radar_opacity = settings.get('radar_opacity', 180)
        
        # Calculate radar position relative to screen center
        screen_center_x = width / 2
        screen_center_y = height / 2
        radar_x = screen_center_x + radar_x_offset - radar_size / 2
        radar_y = screen_center_y + radar_y_offset - radar_size / 2
        
        # Get radar colors from settings
        radar_bg = settings.get('radar_bg_color', (0, 0, 0))
        radar_border = settings.get('radar_border_color', (128, 128, 128))
        radar_crosshair = settings.get('radar_crosshair_color', (77, 77, 77))
        radar_player = settings.get('radar_player_color', (255, 255, 255))
        
        # Draw radar background (semi-transparent circle)
        bg_color = imgui.get_color_u32_rgba(radar_bg[0] / 255.0, radar_bg[1] / 255.0, radar_bg[2] / 255.0, radar_opacity / 255.0)
        border_color = imgui.get_color_u32_rgba(radar_border[0] / 255.0, radar_border[1] / 255.0, radar_border[2] / 255.0, 0.8)
        
        center_x = radar_x + radar_size / 2
        center_y = radar_y + radar_size / 2
        radar_radius = radar_size / 2
        
        # Draw background circle
        overlay.draw_list.add_circle_filled(center_x, center_y, radar_radius, bg_color, 32)
        # Draw border
        overlay.draw_list.add_circle(center_x, center_y, radar_radius, border_color, 32, 2.0)
        
        # Draw cross-hairs
        crosshair_color = imgui.get_color_u32_rgba(radar_crosshair[0] / 255.0, radar_crosshair[1] / 255.0, radar_crosshair[2] / 255.0, 0.5)
        overlay.draw_list.add_line(center_x - radar_radius + 5, center_y, center_x + radar_radius - 5, center_y, crosshair_color, 1.0)
        overlay.draw_list.add_line(center_x, center_y - radar_radius + 5, center_x, center_y + radar_radius - 5, crosshair_color, 1.0)
        
        # Draw local player dot
        player_color = imgui.get_color_u32_rgba(radar_player[0] / 255.0, radar_player[1] / 255.0, radar_player[2] / 255.0, 1.0)
        overlay.draw_list.add_circle_filled(center_x, center_y, 4, player_color, 8)
        
        # Read local player info
        try:
            local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
            if not local_player_pawn_addr:
                return
                
            local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
            local_game_scene = pm.read_longlong(local_player_pawn_addr + m_pGameSceneNode)
            local_x = pm.read_float(local_game_scene + m_vecAbsOrigin)
            local_y = pm.read_float(local_game_scene + m_vecAbsOrigin + 0x4)
            local_z = pm.read_float(local_game_scene + m_vecAbsOrigin + 0x8)
            
            # Get player view angle for rotation
            view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
            forward_x = view_matrix[8]
            forward_y = view_matrix[9]
            local_yaw = math.degrees(math.atan2(forward_x, -forward_y))
            
        except Exception:
            return
        
        # Read entity list
        try:
            entity_list = pm.read_longlong(client + dwEntityList)
            list_entry = pm.read_longlong(entity_list + 0x10)
        except Exception:
            return
        
        targeting_type = settings.get('targeting_type', 0)
        
        # Iterate through entities
        for i in range(1, 64):
            try:
                if list_entry == 0:
                    break
                
                current_controller = pm.read_longlong(list_entry + i * 0x70)
                if current_controller == 0:
                    continue
                
                pawn_handle = pm.read_int(current_controller + m_hPlayerPawn)
                if pawn_handle == 0:
                    continue
                
                list_entry2 = pm.read_longlong(entity_list + 0x8 * ((pawn_handle & 0x7FFF) >> 9) + 0x10)
                if list_entry2 == 0:
                    continue
                
                entity_pawn_addr = pm.read_longlong(list_entry2 + 0x70 * (pawn_handle & 0x1FF))
                if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                    continue
                
                # Check entity validity
                entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
                entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
                entity_health = pm.read_int(entity_pawn_addr + m_iHealth)
                
                if entity_alive != 256 or entity_health <= 0:
                    continue
                if entity_team < 2 or entity_team > 3:
                    continue
                if entity_team == local_player_team and targeting_type == 0:
                    continue
                
                # Get entity position
                entity_game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
                if entity_game_scene == 0:
                    continue
                    
                entity_x = pm.read_float(entity_game_scene + m_vecAbsOrigin)
                entity_y = pm.read_float(entity_game_scene + m_vecAbsOrigin + 0x4)
                entity_z = pm.read_float(entity_game_scene + m_vecAbsOrigin + 0x8)
                
                # Sanity check position
                if abs(entity_x) > 50000 or abs(entity_y) > 50000:
                    continue
                
                # Calculate relative position
                # Scale determines visible range (units per radar radius)
                # Size only affects visual size of the radar circle
                rel_x = (entity_x - local_x) / (radar_scale * 100) * radar_radius
                rel_y = (entity_y - local_y) / (radar_scale * 100) * radar_radius
                
                # Rotate based on player view angle
                rotation_angle = math.radians(-local_yaw + 180)
                cos_rot = math.cos(rotation_angle)
                sin_rot = math.sin(rotation_angle)
                
                rotated_x = rel_x * cos_rot - rel_y * sin_rot
                rotated_y = rel_x * sin_rot + rel_y * cos_rot
                
                # Convert to radar coordinates
                radar_entity_x = center_x + rotated_x
                radar_entity_y = center_y - rotated_y
                
                # Check if within radar bounds
                distance_from_center = math.sqrt((radar_entity_x - center_x) ** 2 + (radar_entity_y - center_y) ** 2)
                
                if distance_from_center <= radar_radius - 5:
                    # Get radar entity colors from settings
                    radar_enemy = settings.get('radar_enemy_color', (255, 0, 0))
                    radar_team = settings.get('radar_team_color', (0, 255, 0))
                    
                    # Determine color based on team
                    if entity_team == local_player_team:
                        entity_color = imgui.get_color_u32_rgba(radar_team[0] / 255.0, radar_team[1] / 255.0, radar_team[2] / 255.0, 1.0)
                    else:
                        entity_color = imgui.get_color_u32_rgba(radar_enemy[0] / 255.0, radar_enemy[1] / 255.0, radar_enemy[2] / 255.0, 1.0)
                    
                    # Check height difference for arrow indicators
                    height_diff = entity_z - local_z
                    height_threshold = 50.0
                    
                    if abs(height_diff) > height_threshold:
                        # Draw arrow indicating height
                        if height_diff > 0:
                            # Enemy is above - draw up arrow
                            overlay.draw_list.add_triangle_filled(
                                radar_entity_x, radar_entity_y - 4,
                                radar_entity_x - 3, radar_entity_y + 2,
                                radar_entity_x + 3, radar_entity_y + 2,
                                entity_color
                            )
                        else:
                            # Enemy is below - draw down arrow
                            overlay.draw_list.add_triangle_filled(
                                radar_entity_x, radar_entity_y + 4,
                                radar_entity_x - 3, radar_entity_y - 2,
                                radar_entity_x + 3, radar_entity_y - 2,
                                entity_color
                            )
                    else:
                        # Same level - draw dot
                        overlay.draw_list.add_circle_filled(radar_entity_x, radar_entity_y, 3, entity_color, 8)
                
            except Exception:
                continue
                
    except Exception:
        pass


def render_aimbot_circle(overlay, settings):
    """
    Render the aimbot FOV circle in the center of the screen.
    
    Args:
        overlay: ESPOverlay instance for drawing
        settings: ESP settings dictionary
    """
    try:
        if not settings or not isinstance(settings, dict):
            return
            
        # Check if aimbot is enabled and radius should be shown
        if not settings.get('aimbot_enabled', False):
            return
        if not settings.get('aimbot_show_radius', True):
            return
        
        # Get screen center
        center_x = overlay.width / 2
        center_y = overlay.height / 2
        
        # Get radius from settings
        radius = settings.get('aimbot_radius', 50)
        
        # Get color from settings - use targeting color if currently targeting
        is_targeting = aimbot_state.get("is_targeting", False)
        if is_targeting:
            color = settings.get('aimbot_targeting_radius_color', (0, 255, 0))
        else:
            color = settings.get('aimbot_radius_color', (255, 0, 0))
        if not color or len(color) < 3:
            color = (255, 0, 0)
        
        # Get transparency from settings (0-255, convert to 0-1)
        transparency = settings.get('aimbot_radius_transparency', 180) / 255.0
        
        # Convert to imgui color (0-1 range)
        circle_color = imgui.get_color_u32_rgba(
            color[0] / 255.0, 
            color[1] / 255.0, 
            color[2] / 255.0, 
            transparency
        )
        
        # Get thickness from settings
        thickness = settings.get('aimbot_radius_thickness', 2.0)
        
        # Draw the radius circle
        overlay.draw_list.add_circle(center_x, center_y, radius, circle_color, 64, thickness)
        
        # Draw deadzone circle if enabled
        if settings.get('aimbot_show_deadzone', False) and settings.get('aimbot_deadzone_enabled', False):
            deadzone_radius = settings.get('aimbot_deadzone_radius', 10)
            if is_targeting:
                deadzone_color = settings.get('aimbot_targeting_deadzone_color', (0, 0, 255))
            else:
                deadzone_color = settings.get('aimbot_deadzone_color', (255, 255, 0))
            if deadzone_color and len(deadzone_color) >= 3:
                # Get deadzone transparency from settings (0-255, convert to 0-1)
                dz_transparency = settings.get('aimbot_deadzone_transparency', 180) / 255.0
                
                # Convert to imgui color (0-1 range)
                dz_circle_color = imgui.get_color_u32_rgba(
                    deadzone_color[0] / 255.0, 
                    deadzone_color[1] / 255.0, 
                    deadzone_color[2] / 255.0, 
                    dz_transparency
                )
                # Get deadzone thickness from settings
                dz_thickness = settings.get('aimbot_deadzone_thickness', 1.5)
                
                # Draw the deadzone circle
                overlay.draw_list.add_circle(center_x, center_y, deadzone_radius, dz_circle_color, 32, dz_thickness)
        
    except Exception:
        pass


def get_crosshair_shape_lines(shape, center_x, center_y, length):
    """
    Get the line segments for a specific crosshair shape.
    
    Args:
        shape: Shape name (e.g., "Sus")
        center_x, center_y: Center coordinates
        length: Length of arms
    
    Returns:
        list: List of (x1, y1, x2, y2) tuples for line segments
    """
    lines = []
    
    if shape == "Sus":
        # Plus sign with clockwise extensions
        # Top arm
        lines.append((center_x, center_y - length, center_x, center_y))
        # Right arm
        lines.append((center_x, center_y, center_x + length, center_y))
        # Bottom arm
        lines.append((center_x, center_y, center_x, center_y + length))
        # Left arm
        lines.append((center_x - length, center_y, center_x, center_y))
        
        # Extensions (clockwise)
        # At end of top arm: horizontal right
        lines.append((center_x, center_y - length, center_x + length, center_y - length))
        # At end of right arm: vertical down
        lines.append((center_x + length, center_y, center_x + length, center_y + length))
        # At end of bottom arm: horizontal left
        lines.append((center_x, center_y + length, center_x - length, center_y + length))
        # At end of left arm: vertical up
        lines.append((center_x - length, center_y, center_x - length, center_y - length))
    
    elif shape == "Plus":
        # Simple plus sign (cross)
        # Top arm
        lines.append((center_x, center_y - length, center_x, center_y))
        # Right arm
        lines.append((center_x, center_y, center_x + length, center_y))
        # Bottom arm
        lines.append((center_x, center_y, center_x, center_y + length))
        # Left arm
        lines.append((center_x - length, center_y, center_x, center_y))
    
    elif shape == "X":
        # X shape (diagonal cross)
        # Top-left to bottom-right diagonal
        lines.append((center_x - length, center_y - length, center_x + length, center_y + length))
        # Top-right to bottom-left diagonal
        lines.append((center_x + length, center_y - length, center_x - length, center_y + length))
    
    # Future shapes can be added here with elif statements
    # elif shape == "NewShape":
    #     lines.append(...)
    
    return lines


def render_custom_crosshair(overlay, settings):
    """
    Render custom crosshair at the center of the screen.
    
    Supports different crosshair shapes defined in get_crosshair_shape_lines().
    
    Args:
        overlay: ESPOverlay instance for drawing
        settings: ESP settings dictionary
    """
    try:
        if not settings or not isinstance(settings, dict):
            return
            
        # Check if custom crosshair is enabled
        if not settings.get('custom_crosshair', False):
            return
        
        # Get screen center
        center_x = overlay.width / 2
        center_y = overlay.height / 2
        
        # Get crosshair settings
        scale = settings.get('custom_crosshair_scale', 1.0)
        thickness = settings.get('custom_crosshair_thickness', 2.0)
        color = settings.get('custom_crosshair_color', (255, 255, 255))
        shape = settings.get('custom_crosshair_shape', 'Sus')
        if not color or len(color) < 3:
            color = (255, 255, 255)
        
        # Calculate length based on scale (base length 10, scaled)
        length = int(10 * scale)
        
        # Get line segments for the selected shape
        lines = get_crosshair_shape_lines(shape, center_x, center_y, length)
        
        # Special handling for circle shape
        if shape == "Circle":
            # Draw actual circle outline
            if overlay.draw_list:
                col = imgui.get_color_u32_rgba(color[0]/255.0, color[1]/255.0, color[2]/255.0, 1.0)
                overlay.draw_list.add_circle(center_x, center_y, length, col, 32, thickness)
        elif shape == "Dot":
            # Draw filled circle (dot)
            overlay.draw_circle_filled_rgb(center_x, center_y, max(1, thickness), color, 12)
        else:
            # Draw all lines for other shapes
            for x1, y1, x2, y2 in lines:
                overlay.draw_line_rgb(x1, y1, x2, y2, color, thickness)
        
    except Exception:
        pass


def render_aimbot_snaplines(overlay, pm, client, settings):
    """
    Render aimbot snaplines to the closest available target.
    
    Finds the closest enemy that passes all aimbot targeting checks
    and draws a line from screen center to their target bone.
    
    Args:
        overlay: ESPOverlay instance for drawing
        pm: pymem instance for memory reading
        client: client.dll base address
        settings: ESP settings dictionary
    """
    try:
        if not settings or not isinstance(settings, dict):
            return
            
        # Check if aimbot snaplines are enabled
        if not settings.get('aimbot_snaplines', False):
            return
        
        # Check if aimbot is enabled (snaplines only show when aimbot is available)
        if not settings.get('aimbot_enabled', False):
            return
        
        # Check if ESP is enabled (snaplines should not show if ESP is disabled)
        if not settings.get('esp_enabled', False):
            return
        
        # Get screen dimensions
        width = overlay.width
        height = overlay.height
        center_x = width // 2
        center_y = height // 2
        
        # Read view matrix
        try:
            matrix_bytes = pm.read_bytes(client + dwViewMatrix, 64)
            view_matrix = struct.unpack('16f', matrix_bytes)
        except:
            return
        
        # Get local player
        try:
            local_player_pawn = pm.read_longlong(client + dwLocalPlayerPawn)
            if not local_player_pawn:
                return
            local_team = pm.read_int(local_player_pawn + m_iTeamNum)
        except:
            return
        
        # Get aimbot settings
        radius = settings.get('aimbot_radius', 50)
        targeting_type = settings.get('targeting_type', 0)
        spotted_check = settings.get('aimbot_spotted_check', False)
        deadzone_enabled = settings.get('aimbot_deadzone_enabled', False)
        deadzone_radius = settings.get('aimbot_deadzone_radius', 10)
        
        # Get target bone
        target_bone_name = settings.get('aimbot_target_bone', 'Head')
        bone_map = {'Head': 6, 'Neck': 5, 'Chest': 4, 'Pelvis': 0}
        target_bone_id = bone_map.get(target_bone_name, 6)
        
        # Build target list
        target_list = []
        
        try:
            entity_list = pm.read_longlong(client + dwEntityList)
            list_entry = pm.read_longlong(entity_list + 0x10)
            
            for i in range(1, 64):
                try:
                    if list_entry == 0:
                        break
                    
                    current_controller = pm.read_longlong(list_entry + i * 0x70)
                    if current_controller == 0:
                        continue
                    
                    pawn_handle = pm.read_int(current_controller + m_hPlayerPawn)
                    if pawn_handle == 0:
                        continue
                    
                    list_entry2 = pm.read_longlong(entity_list + 0x8 * ((pawn_handle & 0x7FFF) >> 9) + 0x10)
                    if list_entry2 == 0:
                        continue
                    
                    entity_pawn = pm.read_longlong(list_entry2 + 0x70 * (pawn_handle & 0x1FF))
                    if entity_pawn == 0 or entity_pawn == local_player_pawn:
                        continue
                    
                    # Check team
                    entity_team = pm.read_int(entity_pawn + m_iTeamNum)
                    if entity_team == local_team and targeting_type == 0:
                        continue
                    
                    # Check if alive
                    entity_alive = pm.read_int(entity_pawn + m_lifeState)
                    if entity_alive != 256:
                        continue
                    
                    entity_health = pm.read_int(entity_pawn + m_iHealth)
                    if entity_health <= 0:
                        continue
                    
                    # Check spotted state if enabled
                    if spotted_check:
                        try:
                            spotted_flag = pm.read_int(entity_pawn + m_entitySpottedState + m_bSpotted)
                            is_spotted = spotted_flag != 0
                        except:
                            try:
                                is_spotted = pm.read_bool(entity_pawn + m_entitySpottedState + m_bSpotted)
                            except:
                                is_spotted = False
                        
                        if not is_spotted:
                            continue
                    
                    # Get bone position
                    game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
                    if game_scene == 0:
                        continue
                    
                    bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                    if bone_matrix == 0:
                        continue
                    
                    # Read target bone position
                    head_x = pm.read_float(bone_matrix + target_bone_id * 0x20)
                    head_y = pm.read_float(bone_matrix + target_bone_id * 0x20 + 0x4)
                    head_z = pm.read_float(bone_matrix + target_bone_id * 0x20 + 0x8)
                    
                    # Convert to screen coordinates
                    screen_pos = w2s(view_matrix, head_x, head_y, head_z, width, height)
                    
                    if screen_pos[0] != -999 and screen_pos[1] != -999:
                        target_list.append({
                            'pos': screen_pos,
                            'entity': entity_pawn
                        })
                except:
                    continue
        except:
            return
        
        if not target_list:
            return
        
        # Find closest target within radius (but outside deadzone if enabled)
        closest_target = None
        closest_dist = float('inf')
        
        for target in target_list:
            pos = target['pos']
            dx = pos[0] - center_x
            dy = pos[1] - center_y
            dist = math.sqrt(dx * dx + dy * dy)
            
            # Check if target is within FOV radius
            if dist < radius:
                # If deadzone is enabled, check if target is outside deadzone
                if not deadzone_enabled or dist >= deadzone_radius:
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_target = target
        
        if not closest_target:
            return
        
        # Draw snapline from center to target
        target_pos = closest_target['pos']
        snapline_color = settings.get('aimbot_snapline_color', (255, 255, 255))
        snapline_thickness = settings.get('aimbot_snapline_thickness', 2.0)
        
        overlay.draw_line_rgb(
            center_x, center_y,
            target_pos[0], target_pos[1],
            snapline_color,
            snapline_thickness
        )
        
    except Exception:
        pass


def render_acs_deadzone_lines(overlay, pm, client, settings):
    """
    Render the Auto Crosshair Placement deadzone visualization lines.
    
    Shows three horizontal lines:
    - Center line (solid): At the target bone's Y position
    - Upper deadzone line (dotted): Above center by deadzone pixels
    - Lower deadzone line (dotted): Below center by deadzone pixels
    
    Args:
        overlay: ESPOverlay instance for drawing
        pm: pymem instance
        client: client.dll base address
        settings: ESP settings dictionary
    """
    try:
        if not settings or not isinstance(settings, dict):
            return
        
        # Check if ACS is enabled and lines should be drawn
        if not settings.get('acs_enabled', False):
            return
        if not settings.get('acs_draw_deadzone_lines', False):
            return
        
        # Check if always show is enabled, otherwise only show while key is held
        always_show = settings.get('acs_always_show_deadzone_lines', False)
        
        if not always_show:
            # Only show lines while ACS key is held
            acs_key = Keybinds_Config.get("acs_key", "v").lower()
            if acs_key == "none":
                return
            
            vk_code = KEY_NAME_TO_VK.get(acs_key, 0)
            if vk_code == 0:
                return
            
            key_held = (win32api.GetAsyncKeyState(vk_code) & 0x8000) != 0
            if not key_held:
                return
        
        # Get screen dimensions
        screen_width = overlay.width
        screen_height = overlay.height
        center_x = screen_width / 2
        center_y = screen_height / 2
        
        # Read view matrix
        try:
            view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
        except:
            return
        
        # Get local player
        try:
            local_player_pawn = pm.read_longlong(client + dwLocalPlayerPawn)
            if not local_player_pawn:
                return
            local_team = pm.read_int(local_player_pawn + m_iTeamNum)
        except:
            return
        
        # Find closest target
        closest_target = None
        min_distance = float('inf')
        
        try:
            entity_list = pm.read_longlong(client + dwEntityList)
            list_entry = pm.read_longlong(entity_list + 0x10)
            
            for i in range(1, 64):
                try:
                    if list_entry == 0:
                        break
                    
                    current_controller = pm.read_longlong(list_entry + i * 0x70)
                    if current_controller == 0:
                        continue
                    
                    pawn_handle = pm.read_int(current_controller + m_hPlayerPawn)
                    if pawn_handle == 0:
                        continue
                    
                    list_entry2 = pm.read_longlong(entity_list + 0x8 * ((pawn_handle & 0x7FFF) >> 9) + 0x10)
                    if list_entry2 == 0:
                        continue
                    
                    entity_pawn = pm.read_longlong(list_entry2 + 0x70 * (pawn_handle & 0x1FF))
                    if entity_pawn == 0 or entity_pawn == local_player_pawn:
                        continue
                    
                    # Check team (enemies only)
                    entity_team = pm.read_int(entity_pawn + m_iTeamNum)
                    if entity_team == local_team:
                        continue
                    
                    # Check if alive
                    entity_alive = pm.read_int(entity_pawn + m_lifeState)
                    if entity_alive != 256:
                        continue
                    
                    entity_health = pm.read_int(entity_pawn + m_iHealth)
                    if entity_health <= 0:
                        continue
                    
                    # Get bone position
                    game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
                    if game_scene == 0:
                        continue
                    
                    bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                    if bone_matrix == 0:
                        continue
                    
                    # Get target bone ID
                    target_bone_name = settings.get("acs_target_bone", "Head")
                    bone_map = {"Head": 6, "Neck": 5, "Chest": 4, "Pelvis": 0}
                    target_bone_id = bone_map.get(target_bone_name, 6)
                    
                    # Read bone position
                    bone_x = pm.read_float(bone_matrix + target_bone_id * 0x20)
                    bone_y = pm.read_float(bone_matrix + target_bone_id * 0x20 + 0x4)
                    bone_z = pm.read_float(bone_matrix + target_bone_id * 0x20 + 0x8)
                    
                    # Convert to screen coordinates
                    screen_pos = w2s_aimbot(view_matrix, bone_x, bone_y, bone_z, int(screen_width), int(screen_height))
                    
                    if screen_pos[0] != -999 and screen_pos[1] != -999:
                        if 0 <= screen_pos[0] <= screen_width and 0 <= screen_pos[1] <= screen_height:
                            dx = screen_pos[0] - center_x
                            dy = screen_pos[1] - center_y
                            dist = math.sqrt(dx * dx + dy * dy)
                            
                            if dist < min_distance:
                                min_distance = dist
                                closest_target = screen_pos
                except:
                    continue
        except:
            return
        
        if not closest_target:
            return
        
        target_y = closest_target[1]
        deadzone = settings.get("acs_deadzone", 5)
        
        # Calculate line positions
        upper_line_y = target_y - deadzone
        lower_line_y = target_y + deadzone
        
        # Get line settings
        line_width_setting = settings.get("acs_line_width", 2)
        line_transparency = settings.get("acs_line_transparency", 80)
        
        # Calculate line width as percentage of screen
        line_width_multiplier = line_width_setting / 10.0
        line_length = screen_width * (0.02 + line_width_multiplier * 0.33)  # 2% to 35% of screen
        line_start_x = (screen_width - line_length) / 2
        line_end_x = line_start_x + line_length
        
        # Get ACS line color from settings
        color = settings.get('acs_line_color', (255, 0, 0))
        if not color or len(color) < 3:
            color = (255, 0, 0)
        
        # Create colors with transparency
        alpha = line_transparency / 255.0
        line_color = imgui.get_color_u32_rgba(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, alpha)
        
        # Draw center line (solid) at target Y position
        if 0 <= target_y <= screen_height:
            overlay.draw_list.add_line(line_start_x, target_y, line_end_x, target_y, line_color, 1.0)
        
        # Draw dotted deadzone lines (upper and lower)
        if deadzone > 1:
            dot_length = 5
            gap_length = 5
            
            # Upper deadzone line (dotted)
            if 0 <= upper_line_y <= screen_height:
                x = line_start_x
                while x < line_end_x:
                    segment_end = min(x + dot_length, line_end_x)
                    overlay.draw_list.add_line(x, upper_line_y, segment_end, upper_line_y, line_color, 1.0)
                    x += dot_length + gap_length
            
            # Lower deadzone line (dotted)
            if 0 <= lower_line_y <= screen_height:
                x = line_start_x
                while x < line_end_x:
                    segment_end = min(x + dot_length, line_end_x)
                    overlay.draw_list.add_line(x, lower_line_y, segment_end, lower_line_y, line_color, 1.0)
                    x += dot_length + gap_length
        
    except Exception:
        pass


def esp_overlay_thread():
    """
    ESP overlay thread function (runs in background).
    
    Lifecycle:
    1. Connect to CS2 process (retry up to 50 times with 100ms delays)
    2. Create transparent overlay window matching CS2 window size/position
    3. Main render loop:
       - Check if CS2 is still running (every 30 frames)
       - Update overlay position to match CS2 window
       - Render ESP frame if CS2 is foreground window
       - Calculate and display FPS
    4. Cleanup on exit
    
    This runs in a separate thread to avoid blocking the DearPyGui UI.
    The overlay continues rendering even when the menu is hidden.
    
    Global state modified:
    - esp_overlay["running"]: Set to False on error or window close
    - esp_overlay["pm"]: pymem instance
    - esp_overlay["client"]: client.dll base address
    - esp_overlay["hwnd"]: GLFW window handle
    - esp_overlay["fps"]: Current frames per second
    """
    global esp_overlay
    
    # Initialize pymem connection
    pm = None
    client = None
    
    retry_count = 0
    max_retries = 50
    
    while retry_count < max_retries and esp_overlay["running"]:
        try:
            pm = pymem.Pymem("cs2.exe")
            client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
            break
        except Exception as e:
            retry_count += 1
            time.sleep(0.1)
    
    if not pm or not client:
        print("[ESP] Failed to connect to CS2")
        esp_overlay["running"] = False
        return
    
    print("[ESP] Connected to CS2")
    esp_overlay["pm"] = pm
    esp_overlay["client"] = client
    
    # Get initial window position
    x, y, width, height = get_cs2_window_rect()
    if width is None:
        esp_overlay["running"] = False
        return
    
    # Create overlay window
    overlay = ESPOverlay()
    overlay.create_window(x, y, width, height)
    esp_overlay["hwnd"] = overlay.window  # Store GLFW window reference
    esp_overlay["window_width"] = width
    esp_overlay["window_height"] = height
    
    # Initialize settings
    settings = esp_overlay["settings"] or Active_Config.copy()
    
    # FPS tracking
    last_time = time.time()
    frame_count = 0
    check_counter = 0  # Counter to reduce expensive checks
    frame_start_time = time.perf_counter()  # For FPS limiting
    overlay_visible = True  # Track overlay visibility state
    
    # Main render loop - also check overlay.running for GLFW window close
    while esp_overlay["running"] and overlay.running:
        try:
            frame_start_time = time.perf_counter()
            check_counter += 1
            
            # Check if CS2 is in foreground (every 10 frames for responsiveness)
            if check_counter % 10 == 0:
                cs2_in_foreground = is_cs2_foreground()
                hide_on_tabout = Active_Config.get("hide_on_tabout", True)
                if cs2_in_foreground and not overlay_visible:
                    overlay.show()
                    overlay_visible = True
                elif not cs2_in_foreground and overlay_visible and hide_on_tabout:
                    overlay.hide()
                    overlay_visible = False
                elif not hide_on_tabout and not overlay_visible:
                    # If hide_on_tabout was disabled while hidden, show again
                    overlay.show()
                    overlay_visible = True
            
            # Only check if CS2 is still running every 60 frames (~1 second)
            if check_counter >= 60:
                check_counter = 0
                if not is_cs2_running_fast(pm):
                    print("[ESP] CS2 closed, stopping overlay")
                    break
                
                # Update window position less frequently
                new_x, new_y, new_width, new_height = get_cs2_window_rect()
                if new_width and new_height:
                    overlay.update_position(new_x, new_y, new_width, new_height)
                    esp_overlay["window_width"] = new_width
                    esp_overlay["window_height"] = new_height
            
            # Skip rendering if overlay is hidden
            if not overlay_visible:
                time.sleep(0.016)  # ~60fps check rate when hidden
                continue
            
            # Begin rendering (returns None if window closed)
            if overlay.begin_paint() is None:
                break
            overlay.clear()
            
            # Render ESP
            if settings.get('esp_enabled', True):
                render_esp_frame(overlay, pm, client, settings)
            
            # Render Bomb ESP (independent of main ESP toggle)
            render_bomb_esp(overlay, pm, client, settings)
            
            # Render Radar (independent of main ESP toggle)
            render_radar(overlay, pm, client, settings)
            
            # Render Aimbot FOV circle (independent of main ESP toggle)
            render_aimbot_circle(overlay, settings)
            
            # Render Custom Crosshair (independent of main ESP toggle)
            render_custom_crosshair(overlay, settings)
            
            # Render Aimbot snaplines (dependent on ESP toggle)
            render_aimbot_snaplines(overlay, pm, client, settings)
            
            # Render ACS deadzone lines (independent of main ESP toggle)
            render_acs_deadzone_lines(overlay, pm, client, settings)
            
            # Draw FPS counter
            current_time = time.time()
            frame_count += 1
            if current_time - last_time >= 1.0:
                esp_overlay["fps"] = frame_count
                frame_count = 0
                last_time = current_time
            
            overlay.draw_text(5, 5, f"OVERLAY FPS: {esp_overlay['fps']}", 255, 255, 255, size=16.0, stroke=True)
            
            # Draw status labels if enabled
            if Active_Config.get("show_status_labels", True):
                esp_status = "ON" if Active_Config.get("esp_enabled", True) else "OFF"
                aimbot_status = "ON" if Active_Config.get("aimbot_enabled", False) else "OFF"
                triggerbot_status = "ON" if Active_Config.get("triggerbot_enabled", False) else "OFF"
                head_only_status = "ON" if Active_Config.get("triggerbot_head_only", False) else "OFF"
                rcs_status = "ON" if Active_Config.get("rcs_enabled", False) else "OFF"
                anti_afk_status = "ON" if Active_Config.get("anti_afk_enabled", False) else "OFF"
                
                # ESP status (green for ON, red for OFF)
                esp_keybind = Keybinds_Config.get("esp_toggle_key", "").upper()
                esp_label = f"({esp_keybind}) ESP: " if esp_keybind else "ESP: "
                esp_status_x = 120 if esp_keybind else 45
                overlay.draw_text(5, 25, esp_label, 255, 255, 255, size=12.0, stroke=True)
                status_color = (0, 255, 0) if esp_status == "ON" else (255, 0, 0)
                overlay.draw_text(esp_status_x, 25, esp_status, status_color[0], status_color[1], status_color[2], size=12.0, stroke=True)
                
                # Aimbot status
                aimbot_keybind = Keybinds_Config.get("aimbot_toggle_key", "").upper()
                aimbot_label = f"({aimbot_keybind}) Aimbot: " if aimbot_keybind else "Aimbot: "
                aimbot_status_x = 120 if aimbot_keybind else 75
                overlay.draw_text(5, 40, aimbot_label, 255, 255, 255, size=12.0, stroke=True)
                status_color = (0, 255, 0) if aimbot_status == "ON" else (255, 0, 0)
                overlay.draw_text(aimbot_status_x, 40, aimbot_status, status_color[0], status_color[1], status_color[2], size=12.0, stroke=True)
                
                # Triggerbot status
                triggerbot_keybind = Keybinds_Config.get("triggerbot_toggle_key", "").upper()
                triggerbot_label = f"({triggerbot_keybind}) Triggerbot: " if triggerbot_keybind else "Triggerbot: "
                triggerbot_status_x = 120 if triggerbot_keybind else 105
                overlay.draw_text(5, 55, triggerbot_label, 255, 255, 255, size=12.0, stroke=True)
                status_color = (0, 255, 0) if triggerbot_status == "ON" else (255, 0, 0)
                overlay.draw_text(triggerbot_status_x, 55, triggerbot_status, status_color[0], status_color[1], status_color[2], size=12.0, stroke=True)
                
                # Triggerbot Head-Only status
                head_only_keybind = Keybinds_Config.get("head_only_toggle_key", "").upper()
                head_only_label = f"({head_only_keybind}) Triggerbot Head-Only: " if head_only_keybind else "Triggerbot Head-Only: "
                head_only_status_x = 240 if head_only_keybind else 185
                overlay.draw_text(5, 70, head_only_label, 255, 255, 255, size=12.0, stroke=True)
                status_color = (0, 255, 0) if head_only_status == "ON" else (255, 0, 0)
                overlay.draw_text(head_only_status_x, 70, head_only_status, status_color[0], status_color[1], status_color[2], size=12.0, stroke=True)
                
                # RCS status
                rcs_keybind = Keybinds_Config.get("rcs_toggle_key", "").upper()
                rcs_label = f"({rcs_keybind}) RCS: " if rcs_keybind else "RCS: "
                rcs_status_x = 110 if rcs_keybind else 50
                overlay.draw_text(5, 85, rcs_label, 255, 255, 255, size=12.0, stroke=True)
                status_color = (0, 255, 0) if rcs_status == "ON" else (255, 0, 0)
                overlay.draw_text(rcs_status_x, 85, rcs_status, status_color[0], status_color[1], status_color[2], size=12.0, stroke=True)
                
                # Anti-AFK status
                anti_afk_keybind = Keybinds_Config.get("anti_afk_toggle_key", "").upper()
                anti_afk_label = f"({anti_afk_keybind}) Anti-AFK: " if anti_afk_keybind else "Anti-AFK: "
                anti_afk_status_x = 140 if anti_afk_keybind else 85
                overlay.draw_text(5, 100, anti_afk_label, 255, 255, 255, size=12.0, stroke=True)
                status_color = (0, 255, 0) if anti_afk_status == "ON" else (255, 0, 0)
                overlay.draw_text(anti_afk_status_x, 100, anti_afk_status, status_color[0], status_color[1], status_color[2], size=12.0, stroke=True)
            
            overlay.end_paint()
            
            # FPS limiting
            if settings.get('fps_cap_enabled', False):
                fps_cap = settings.get('fps_cap_value', 144)
                if fps_cap > 0:
                    target_frame_time = 1.0 / fps_cap
                    elapsed = time.perf_counter() - frame_start_time
                    if elapsed < target_frame_time:
                        time.sleep(target_frame_time - elapsed)
            
        except Exception as e:
            # Don't print every error or sleep - just continue
            pass
    
    # Cleanup
    print("[ESP] Cleaning up overlay...")
    overlay.destroy()
    esp_overlay["hwnd"] = None
    esp_overlay["pm"] = None
    esp_overlay["client"] = None
    print("[ESP] Overlay thread stopped")


def start_esp_overlay():
    """Start the ESP overlay thread."""
    global esp_overlay
    
    if esp_overlay["running"]:
        debug_log("ESP overlay already running", "WARNING")
        return
    
    debug_log("Starting ESP overlay thread...", "INFO")
    
    # Initialize settings from Active_Config (which may have loaded settings)
    esp_overlay["settings"] = Active_Config.copy()
    esp_overlay["running"] = True
    
    # Start thread
    esp_overlay["thread"] = threading.Thread(target=esp_overlay_thread, daemon=True)
    esp_overlay["thread"].start()
    
    debug_log("ESP overlay thread started", "SUCCESS")


def stop_esp_overlay():
    """Stop the ESP overlay thread."""
    global esp_overlay
    
    if not esp_overlay["running"]:
        return
    
    debug_log("Stopping ESP overlay...", "INFO")
    esp_overlay["running"] = False
    
    # Wait for thread to finish
    if esp_overlay["thread"]:
        esp_overlay["thread"].join(timeout=2.0)
        esp_overlay["thread"] = None
    
    debug_log("ESP overlay stopped", "SUCCESS")


# =============================================================================
# AIMBOT THREAD
# =============================================================================
# Background thread for aimbot functionality.
# Runs independently of ESP overlay, scanning for targets and moving mouse.
# =============================================================================

def w2s_aimbot(view_matrix, x, y, z, width, height):
    """
    World to Screen transformation for aimbot.
    Converts 3D world coordinates to 2D screen coordinates.
    """
    clip_x = x * view_matrix[0] + y * view_matrix[1] + z * view_matrix[2] + view_matrix[3]
    clip_y = x * view_matrix[4] + y * view_matrix[5] + z * view_matrix[6] + view_matrix[7]
    clip_w = x * view_matrix[12] + y * view_matrix[13] + z * view_matrix[14] + view_matrix[15]
    
    if clip_w < 0.1:
        return (-999, -999)
    
    ndc_x = clip_x / clip_w
    ndc_y = clip_y / clip_w
    
    screen_x = (width / 2) * (1 + ndc_x)
    screen_y = (height / 2) * (1 - ndc_y)
    
    return (screen_x, screen_y)


def aimbot_thread():
    """
    Aimbot thread function - runs in background.
    
    Functionality:
    1. Check if aimbot is enabled
    2. Check if aimbot key is held
    3. Scan for enemy targets
    4. Find closest target within FOV radius
    5. Move mouse towards target with smoothing
    """
    global aimbot_state
    
    print("[AIMBOT] Thread starting...")
    
    # Wait for ESP overlay to connect to CS2 and provide pm/client
    max_wait = 100  # 10 seconds max wait
    wait_count = 0
    while wait_count < max_wait:
        if esp_overlay.get("pm") and esp_overlay.get("client"):
            break
        time.sleep(0.1)
        wait_count += 1
    
    if not esp_overlay.get("pm") or not esp_overlay.get("client"):
        print("[AIMBOT] Failed to get pm/client from ESP overlay")
        return
    
    print("[AIMBOT] Connected to CS2 via ESP overlay")
    
    while aimbot_state["running"]:
        try:
            # Get settings from aimbot_state (updated by main thread)
            settings = aimbot_state.get("settings", {})
            if not settings:
                settings = Active_Config.copy()
            
            # Check if aimbot is enabled
            if not settings.get("aimbot_enabled", False):
                time.sleep(0.01)
                continue
            
            # Check if aimbot key is required
            require_key = settings.get("aimbot_require_key", True)
            key_held = False
            
            if require_key:
                # Get aimbot key and check if it's held
                aimbot_key = Keybinds_Config.get("aimbot_key", "alt").lower()
                if aimbot_key == "none":
                    time.sleep(0.01)
                    continue
                
                # Get VK code for aimbot key
                vk_code = KEY_NAME_TO_VK.get(aimbot_key, 0)
                if vk_code == 0:
                    time.sleep(0.01)
                    continue
                
                # Check if key is held
                key_held = (win32api.GetAsyncKeyState(vk_code) & 0x8000) != 0
                if not key_held:
                    # Reset locked entity and accumulators when key is released
                    aimbot_state["locked_entity"] = None
                    aimbot_state["accum_x"] = 0.0
                    aimbot_state["accum_y"] = 0.0
                    aimbot_state["is_targeting"] = False
                    time.sleep(0.002)
                    continue
            
            # Get pm and client from ESP overlay
            pm = esp_overlay.get("pm")
            client = esp_overlay.get("client")
            
            if not pm or not client:
                time.sleep(0.01)
                continue
            
            # Get screen dimensions
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            # Get aimbot settings
            radius = settings.get("aimbot_radius", 50)
            smoothness = settings.get("aimbot_smoothness", 5.0)
            targeting_type = settings.get("targeting_type", 0)  # 0 = enemies only
            
            # Read view matrix
            try:
                view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
            except:
                time.sleep(0.002)
                continue
            
            # Get local player
            try:
                local_player_pawn = pm.read_longlong(client + dwLocalPlayerPawn)
                if not local_player_pawn:
                    time.sleep(0.002)
                    continue
                local_team = pm.read_int(local_player_pawn + m_iTeamNum)
            except:
                time.sleep(0.002)
                continue
            
            # Build target list
            target_list = []
            
            try:
                entity_list = pm.read_longlong(client + dwEntityList)
                list_entry = pm.read_longlong(entity_list + 0x10)
                
                for i in range(1, 64):
                    try:
                        if list_entry == 0:
                            break
                        
                        current_controller = pm.read_longlong(list_entry + i * 0x70)
                        if current_controller == 0:
                            continue
                        
                        pawn_handle = pm.read_int(current_controller + m_hPlayerPawn)
                        if pawn_handle == 0:
                            continue
                        
                        list_entry2 = pm.read_longlong(entity_list + 0x8 * ((pawn_handle & 0x7FFF) >> 9) + 0x10)
                        if list_entry2 == 0:
                            continue
                        
                        entity_pawn = pm.read_longlong(list_entry2 + 0x70 * (pawn_handle & 0x1FF))
                        if entity_pawn == 0 or entity_pawn == local_player_pawn:
                            continue
                        
                        # Check team
                        entity_team = pm.read_int(entity_pawn + m_iTeamNum)
                        if entity_team == local_team and targeting_type == 0:
                            continue
                        
                        # Check if alive
                        entity_alive = pm.read_int(entity_pawn + m_lifeState)
                        if entity_alive != 256:
                            continue
                        
                        entity_health = pm.read_int(entity_pawn + m_iHealth)
                        if entity_health <= 0:
                            continue
                        
                        # Check spotted state if enabled
                        if settings.get("aimbot_spotted_check", False):
                            try:
                                spotted_flag = pm.read_int(entity_pawn + m_entitySpottedState + m_bSpotted)
                                is_spotted = spotted_flag != 0
                            except:
                                try:
                                    is_spotted = pm.read_bool(entity_pawn + m_entitySpottedState + m_bSpotted)
                                except:
                                    is_spotted = False
                            
                            if not is_spotted:
                                continue
                        
                        # Get bone position based on target bone setting
                        game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
                        if game_scene == 0:
                            continue
                        
                        bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                        if bone_matrix == 0:
                            continue
                        
                        # Get target bone ID based on setting
                        target_bone_name = settings.get("aimbot_target_bone", "Head")
                        bone_map = {"Head": 6, "Neck": 5, "Chest": 4, "Pelvis": 0}
                        target_bone_id = bone_map.get(target_bone_name, 6)
                        
                        # Read target bone position
                        head_x = pm.read_float(bone_matrix + target_bone_id * 0x20)
                        head_y = pm.read_float(bone_matrix + target_bone_id * 0x20 + 0x4)
                        head_z = pm.read_float(bone_matrix + target_bone_id * 0x20 + 0x8)
                        
                        # Convert to screen coordinates
                        screen_pos = w2s_aimbot(view_matrix, head_x, head_y, head_z, screen_width, screen_height)
                        
                        if screen_pos[0] != -999 and screen_pos[1] != -999:
                            target_list.append({
                                "pos": screen_pos,
                                "entity": entity_pawn
                            })
                    except:
                        continue
            except:
                time.sleep(0.002)
                continue
            
            if not target_list:
                aimbot_state["is_targeting"] = False
                time.sleep(0.002)
                continue
            
            # Find closest target within radius (but outside deadzone if enabled)
            closest_target = None
            closest_dist = float('inf')
            
            # Get deadzone settings
            deadzone_enabled = settings.get("aimbot_deadzone_enabled", False)
            deadzone_radius = settings.get("aimbot_deadzone_radius", 10)
            
            for target in target_list:
                pos = target["pos"]
                dx = pos[0] - center_x
                dy = pos[1] - center_y
                dist = math.sqrt(dx * dx + dy * dy)
                
                # Check if target is within FOV radius
                if dist < radius:
                    # If deadzone is enabled, check if target is outside deadzone
                    if not deadzone_enabled or dist >= deadzone_radius:
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_target = target
            
            if not closest_target:
                aimbot_state["is_targeting"] = False
                time.sleep(0.002)
                continue
            
            # Lock target logic - keep same target while aimkey is held
            lock_target_enabled = settings.get("aimbot_lock_target", False)
            
            if lock_target_enabled:
                locked_entity = aimbot_state.get("locked_entity")
                
                if locked_entity is not None:
                    # Try to find our locked entity in the target list
                    found_locked = None
                    for target in target_list:
                        if target["entity"] == locked_entity:
                            found_locked = target
                            break
                    
                    if found_locked:
                        # Use the locked target instead of closest
                        closest_target = found_locked
                    else:
                        # Locked target is no longer valid (dead, out of sight, etc.)
                        aimbot_state["locked_entity"] = None
                
                # Lock to current target if not already locked
                if aimbot_state.get("locked_entity") is None:
                    aimbot_state["locked_entity"] = closest_target["entity"]
            
            # We have a valid target, set targeting state
            aimbot_state["is_targeting"] = True
            
            # Calculate mouse movement
            target_x, target_y = closest_target["pos"]
            dx = target_x - center_x
            dy = target_y - center_y
            
            # Get movement type setting
            movement_type = settings.get("aimbot_movement_type", "Dynamic")
            
            # Apply smoothing based on movement type
            if movement_type == "Linear":
                # Linear: constant speed regardless of distance
                # Calculate direction and move at fixed speed based on smoothness
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    # Speed is inversely proportional to smoothness (higher smoothness = slower)
                    # At smoothness 1, move ~10 pixels/frame; at smoothness 100, move ~0.1 pixels/frame
                    speed = max(0.1, 10.0 / max(smoothness, 1.0))
                    # Normalize direction and apply speed
                    frac_x = (dx / dist) * speed
                    frac_y = (dy / dist) * speed
                    # Cap movement to not overshoot target
                    if abs(frac_x) > abs(dx):
                        frac_x = dx
                    if abs(frac_y) > abs(dy):
                        frac_y = dy
                else:
                    frac_x = 0
                    frac_y = 0
            else:
                # Dynamic: speed based on distance percentage (original behavior)
                if smoothness <= 1:
                    alpha = 1.0
                else:
                    alpha = 1.0 / smoothness
                frac_x = dx * alpha
                frac_y = dy * alpha
            
            aimbot_state["accum_x"] += frac_x
            aimbot_state["accum_y"] += frac_y
            
            # Extract integer pixels from accumulators
            move_x = int(aimbot_state["accum_x"])
            move_y = int(aimbot_state["accum_y"])
            
            # Subtract the moved amount from accumulators (keep fractional remainder)
            aimbot_state["accum_x"] -= move_x
            aimbot_state["accum_y"] -= move_y
            
            # Only move if we have at least 1 pixel to move
            if move_x != 0 or move_y != 0:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.002)
            
        except Exception as e:
            time.sleep(0.01)
    
    print("[AIMBOT] Thread stopped")


def start_aimbot_thread():
    """Start the aimbot background thread."""
    global aimbot_state
    
    if aimbot_state["running"]:
        return
    
    debug_log("Starting aimbot thread...", "INFO")
    
    # Initialize settings from Active_Config
    aimbot_state["settings"] = Active_Config.copy()
    aimbot_state["running"] = True
    aimbot_state["locked_entity"] = None
    aimbot_state["accum_x"] = 0.0
    aimbot_state["accum_y"] = 0.0
    aimbot_state["is_targeting"] = False
    
    # Start thread
    aimbot_state["thread"] = threading.Thread(target=aimbot_thread, daemon=True)
    aimbot_state["thread"].start()
    
    debug_log("Aimbot thread started", "SUCCESS")


def stop_aimbot_thread():
    """Stop the aimbot background thread."""
    global aimbot_state
    
    if not aimbot_state["running"]:
        return
    
    debug_log("Stopping aimbot thread...", "INFO")
    aimbot_state["running"] = False
    
    # Wait for thread to finish
    if aimbot_state["thread"]:
        aimbot_state["thread"].join(timeout=2.0)
        aimbot_state["thread"] = None
    
    debug_log("Aimbot thread stopped", "SUCCESS")


# =============================================================================
# TRIGGERBOT THREAD
# =============================================================================
# Background thread that handles automatic firing when crosshair is on enemy.
# =============================================================================

def triggerbot_thread():
    """
    Triggerbot background thread.
    
    Runs continuously while enabled:
    1. Check if triggerbot key is held
    2. Read m_iIDEntIndex to check if crosshair is on an entity
    3. Validate the entity is an enemy and alive
    4. Fire shots with configurable delays and burst mode
    """
    global triggerbot_state
    
    print("[TRIGGERBOT] Thread starting...")
    
    # Wait for ESP overlay to connect to CS2 and provide pm/client
    max_wait = 100  # 10 seconds max wait
    wait_count = 0
    while wait_count < max_wait:
        if esp_overlay.get("pm") and esp_overlay.get("client"):
            break
        time.sleep(0.1)
        wait_count += 1
    
    if not esp_overlay.get("pm") or not esp_overlay.get("client"):
        print("[TRIGGERBOT] Failed to get pm/client from ESP overlay")
        return
    
    print("[TRIGGERBOT] Connected to CS2 via ESP overlay")
    
    # Initialize mouse controller
    mouse = MouseController()
    triggerbot_state["mouse"] = mouse
    
    # Track if we just started shooting (for first shot delay)
    first_shot_pending = True
    
    while triggerbot_state["running"]:
        try:
            # Get settings from triggerbot_state (updated by main thread)
            settings = triggerbot_state.get("settings", {})
            if not settings:
                settings = Active_Config.copy()
            
            # Check if triggerbot is enabled
            if not settings.get("triggerbot_enabled", False):
                first_shot_pending = True
                time.sleep(0.01)
                continue
            
            # Get triggerbot key and check if it's held
            triggerbot_key = Keybinds_Config.get("triggerbot_key", "x").lower()
            if triggerbot_key == "none":
                first_shot_pending = True
                time.sleep(0.01)
                continue
            
            # Get VK code for triggerbot key
            vk_code = KEY_NAME_TO_VK.get(triggerbot_key, 0)
            if vk_code == 0:
                first_shot_pending = True
                time.sleep(0.01)
                continue
            
            # Check if key is held
            key_held = (win32api.GetAsyncKeyState(vk_code) & 0x8000) != 0
            if not key_held:
                first_shot_pending = True
                time.sleep(0.001)
                continue
            
            # Get pm and client from ESP overlay
            pm = esp_overlay.get("pm")
            client = esp_overlay.get("client")
            
            if not pm or not client:
                time.sleep(0.01)
                continue
            
            # Get local player pawn
            try:
                local_player_pawn = pm.read_longlong(client + dwLocalPlayerPawn)
                if not local_player_pawn:
                    time.sleep(0.001)
                    continue
                local_team = pm.read_int(local_player_pawn + m_iTeamNum)
            except:
                time.sleep(0.001)
                continue
            
            # Read entity ID under crosshair
            try:
                entity_id = pm.read_int(local_player_pawn + m_iIDEntIndex)
            except:
                first_shot_pending = True
                time.sleep(0.001)
                continue
            
            # If no entity under crosshair, reset first shot flag and continue
            if entity_id <= 0:
                first_shot_pending = True
                time.sleep(0.001)
                continue
            
            # Get entity from entity list
            try:
                entity_list = pm.read_longlong(client + dwEntityList)
                if not entity_list:
                    first_shot_pending = True
                    time.sleep(0.001)
                    continue
                
                # Calculate entity address from ID
                list_entry = pm.read_longlong(entity_list + 0x8 * ((entity_id & 0x7FFF) >> 9) + 0x10)
                if not list_entry:
                    first_shot_pending = True
                    time.sleep(0.001)
                    continue
                
                entity_pawn = pm.read_longlong(list_entry + 0x70 * (entity_id & 0x1FF))
                if not entity_pawn:
                    first_shot_pending = True
                    time.sleep(0.001)
                    continue
                
                # Check if it's an enemy
                entity_team = pm.read_int(entity_pawn + m_iTeamNum)
                if entity_team == local_team:
                    first_shot_pending = True
                    time.sleep(0.001)
                    continue
                
                # Check if alive
                entity_health = pm.read_int(entity_pawn + m_iHealth)
                if entity_health <= 0:
                    first_shot_pending = True
                    time.sleep(0.001)
                    continue
                
                # Head-only mode check
                head_only_mode = settings.get("triggerbot_head_only", False)
                if head_only_mode:
                    try:
                        # Get screen dimensions
                        screen_width = win32api.GetSystemMetrics(0)
                        screen_height = win32api.GetSystemMetrics(1)
                        crosshair_x = screen_width // 2
                        crosshair_y = screen_height // 2
                        
                        # Read view matrix
                        view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
                        
                        # Get entity bone data
                        game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
                        if not game_scene:
                            first_shot_pending = True
                            time.sleep(0.001)
                            continue
                        
                        bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                        if not bone_matrix:
                            first_shot_pending = True
                            time.sleep(0.001)
                            continue
                        
                        # Read head bone position (bone 6)
                        head_x = pm.read_float(bone_matrix + 6 * 0x20)
                        head_y = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
                        head_z = pm.read_float(bone_matrix + 6 * 0x20 + 0x8)
                        
                        # Read leg position for bounding box calculation (bone 28)
                        leg_z = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                        
                        # Convert to screen coordinates
                        head_pos = w2s_aimbot(view_matrix, head_x, head_y, head_z, screen_width, screen_height)
                        leg_pos = w2s_aimbot(view_matrix, head_x, head_y, leg_z, screen_width, screen_height)
                        
                        if head_pos[0] == -999 or leg_pos[0] == -999:
                            first_shot_pending = True
                            time.sleep(0.001)
                            continue
                        
                        # Calculate bounding box (same as ESP)
                        deltaZ = abs(head_pos[1] - leg_pos[1])
                        leftX = head_pos[0] - deltaZ // 4
                        rightX = head_pos[0] + deltaZ // 4
                        
                        # Calculate head hitbox (same as ESP head_dot)
                        box_width = rightX - leftX
                        head_dot_size = box_width / 5
                        head_dot_radius = max(2, head_dot_size * 1.414 / 2)  # sqrt(2) ≈ 1.414
                        
                        # Head position on screen (same calculation as ESP)
                        head_screen_x = head_pos[0]
                        head_screen_y = head_pos[1]
                        
                        # Check if crosshair is within head hitbox circle
                        distance_to_head = math.sqrt((crosshair_x - head_screen_x) ** 2 + (crosshair_y - head_screen_y) ** 2)
                        
                        if distance_to_head > head_dot_radius:
                            # Crosshair not on head, skip
                            first_shot_pending = True
                            time.sleep(0.001)
                            continue
                    except:
                        first_shot_pending = True
                        time.sleep(0.001)
                        continue
            except:
                first_shot_pending = True
                time.sleep(0.001)
                continue
            
            # Valid enemy target under crosshair - fire!
            
            # Get timing settings
            first_shot_delay = settings.get("triggerbot_first_shot_delay", 0)
            between_shots_delay = settings.get("triggerbot_between_shots_delay", 30)
            burst_mode = settings.get("triggerbot_burst_mode", False)
            burst_shots = settings.get("triggerbot_burst_shots", 3)
            
            # Apply first shot delay if needed
            if first_shot_pending and first_shot_delay > 0:
                time.sleep(first_shot_delay / 1000.0)
                # Re-check if key still held and target still valid
                key_held = (win32api.GetAsyncKeyState(vk_code) & 0x8000) != 0
                if not key_held:
                    first_shot_pending = True
                    continue
                try:
                    entity_id = pm.read_int(local_player_pawn + m_iIDEntIndex)
                    if entity_id <= 0:
                        first_shot_pending = True
                        continue
                except:
                    first_shot_pending = True
                    continue
            
            first_shot_pending = False
            
            if burst_mode:
                # Burst fire mode - fire burst_shots times
                # Complete the entire burst even if target becomes invalid or key released
                for _ in range(burst_shots):
                    mouse.click(MouseButton.left)
                    time.sleep(0.05)  # Small delay between burst shots
                
                # Reset for next burst and wait between bursts
                first_shot_pending = True
                time.sleep(between_shots_delay / 1000.0)
            else:
                # Non-burst mode - single shots with delay between each
                # Fire one shot
                mouse.click(MouseButton.left)
                
                # Wait between shots delay before allowing next shot
                time.sleep(between_shots_delay / 1000.0)
            
            time.sleep(0.001)
            
        except Exception as e:
            time.sleep(0.01)
    
    print("[TRIGGERBOT] Thread stopped")


def start_triggerbot_thread():
    """Start the triggerbot background thread."""
    global triggerbot_state
    
    if triggerbot_state["running"]:
        return
    
    debug_log("Starting triggerbot thread...", "INFO")
    
    # Initialize settings from Active_Config
    triggerbot_state["settings"] = Active_Config.copy()
    triggerbot_state["running"] = True
    
    # Start thread
    triggerbot_state["thread"] = threading.Thread(target=triggerbot_thread, daemon=True)
    triggerbot_state["thread"].start()
    
    debug_log("Triggerbot thread started", "SUCCESS")


def stop_triggerbot_thread():
    """Stop the triggerbot background thread."""
    global triggerbot_state
    
    if not triggerbot_state["running"]:
        return
    
    debug_log("Stopping triggerbot thread...", "INFO")
    triggerbot_state["running"] = False
    
    # Wait for thread to finish
    if triggerbot_state["thread"]:
        triggerbot_state["thread"].join(timeout=2.0)
        triggerbot_state["thread"] = None
    
    debug_log("Triggerbot thread stopped", "SUCCESS")


# =============================================================================
# AUTO ACCEPT THREAD
# =============================================================================
# Background thread that automatically accepts CS2 matches when found.
# =============================================================================

# =============================================================================
# ANTI FLASH THREAD
# =============================================================================
# Background thread that prevents flashbang effects by writing to memory.
# =============================================================================

def anti_flash_thread():
    """
    Anti-flash background thread.
    
    Runs continuously:
    - When enabled: sets m_flFlashMaxAlpha to 0.0 repeatedly
    - When disabled: sets m_flFlashMaxAlpha to 255.0 once, then stops writing
    """
    global anti_flash_state
    
    print("[ANTI FLASH] Thread starting...")
    
    # Wait for ESP overlay to connect to CS2 and provide pm/client
    max_wait = 100  # 10 seconds max wait
    wait_count = 0
    while wait_count < max_wait:
        if esp_overlay.get("pm") and esp_overlay.get("client"):
            break
        time.sleep(0.1)
        wait_count += 1
    
    if not esp_overlay.get("pm") or not esp_overlay.get("client"):
        print("[ANTI FLASH] Failed to get pm/client from ESP overlay")
        return
    
    print("[ANTI FLASH] Connected to CS2 via ESP overlay")
    
    while anti_flash_state["running"]:
        try:
            # Get settings from anti_flash_state
            settings = anti_flash_state.get("settings", {})
            if not settings:
                settings = Active_Config.copy()
            
            current_enabled = settings.get("anti_flash_enabled", False)
            last_enabled = anti_flash_state.get("last_enabled", False)
            
            # Check if m_flFlashMaxAlpha offset is available
            if not m_flFlashMaxAlpha:
                time.sleep(0.1)
                continue
            
            # Get pm and client from ESP overlay
            pm = esp_overlay.get("pm")
            client = esp_overlay.get("client")
            
            if not pm or not client:
                time.sleep(0.1)
                continue
            
            # Get local player pawn
            try:
                local_player_pawn = pm.read_longlong(client + dwLocalPlayerPawn)
                if local_player_pawn:
                    if current_enabled != last_enabled:
                        if not current_enabled:
                            # Just disabled, set to 255 once
                            pm.write_float(local_player_pawn + m_flFlashMaxAlpha, 255.0)
                    elif current_enabled:
                        # Enabled, set to 0.0
                        pm.write_float(local_player_pawn + m_flFlashMaxAlpha, 0.0)
            except:
                pass
            
            anti_flash_state["last_enabled"] = current_enabled
            
            # Check frequently for responsive anti-flash
            time.sleep(0.02)  # 20ms interval
            
        except Exception as e:
            time.sleep(0.1)
    
    print("[ANTI FLASH] Thread stopped")


def start_anti_flash_thread():
    """Start the anti-flash background thread."""
    global anti_flash_state
    
    if anti_flash_state["running"]:
        return
    
    debug_log("Starting anti-flash thread...", "INFO")
    
    # Initialize settings from Active_Config
    anti_flash_state["settings"] = Active_Config.copy()
    anti_flash_state["running"] = True
    
    # Start thread
    anti_flash_state["thread"] = threading.Thread(target=anti_flash_thread, daemon=True)
    anti_flash_state["thread"].start()
    
    debug_log("Anti-flash thread started", "SUCCESS")


def stop_anti_flash_thread():
    """Stop the anti-flash background thread."""
    global anti_flash_state
    
    if not anti_flash_state["running"]:
        return
    
    debug_log("Stopping anti-flash thread...", "INFO")
    anti_flash_state["running"] = False
    
    # Wait for thread to finish
    if anti_flash_state["thread"]:
        anti_flash_state["thread"].join(timeout=2.0)
        anti_flash_state["thread"] = None
    
    debug_log("Anti-flash thread stopped", "SUCCESS")


# =============================================================================
# HITSOUND THREAD
# =============================================================================
# Background thread that plays hitsound when total hits changes.
# =============================================================================

def hitsound_thread():
    """
    Hitsound background thread.
    
    Runs continuously while enabled:
    1. Check if hitsound is enabled
    2. Get local player pawn
    3. Read total hits from bullet services
    4. Play sound when hits change
    """
    global hitsound_state
    
    print("[HITSOUND] Thread starting...")
    
    # Wait for ESP overlay to connect to CS2 and provide pm/client
    max_wait = 100  # 10 seconds max wait
    wait_count = 0
    while wait_count < max_wait:
        if esp_overlay.get("pm") and esp_overlay.get("client"):
            break
        time.sleep(0.1)
        wait_count += 1
    
    if not esp_overlay.get("pm") or not esp_overlay.get("client"):
        print("[HITSOUND] Failed to get pm/client from ESP overlay")
        return
    
    print("[HITSOUND] Connected to CS2 via ESP overlay")
    
    while hitsound_state["running"]:
        try:
            # Get settings from hitsound_state
            settings = hitsound_state.get("settings", {})
            if not settings:
                settings = Active_Config.copy()
            
            # Check if hitsound is enabled
            if not settings.get("hitsound_enabled", False):
                time.sleep(0.1)
                continue
            
            # Get pm and client from ESP overlay
            pm = esp_overlay.get("pm")
            client = esp_overlay.get("client")
            
            if not pm or not client:
                time.sleep(0.1)
                continue
            
            # Get local player pawn
            try:
                local_player_pawn = pm.read_longlong(client + dwLocalPlayerPawn)
                if local_player_pawn:
                    # Get bullet services
                    pBulletServices = pm.read_longlong(local_player_pawn + 0x1678) #change this one
                    if pBulletServices:
                        total_hits = pm.read_int(pBulletServices + 0x40)
                        
                        if total_hits != hitsound_state["previous_total_hits"]:
                            if total_hits == 0 and hitsound_state["previous_total_hits"] != 0:
                                # totalHits changed from non-zero to zero, do not play hitsound
                                pass
                            else:
                                # Play the hitsound
                                try:
                                    # Get selected hitsound type
                                    hitsound_type = settings.get("hitsound_type", "hitmarker")
                                    # Map to filename
                                    filename_map = {
                                        "hitmarker": "hitmarker.wav",
                                        "criticalhit": "criticalhit.wav",
                                        "metalhit": "metal.wav"
                                    }
                                    filename = filename_map.get(hitsound_type, "hitmarker.wav")
                                    sound_path = os.path.join(TEMP_FOLDER, filename)
                                    winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                                except:
                                    pass  # Silently fail if sound file not found
                            
                            hitsound_state["previous_total_hits"] = total_hits
            except:
                pass
            
            # Check frequently
            time.sleep(0.02)  # 20ms interval
            
        except Exception as e:
            time.sleep(0.1)
    
    print("[HITSOUND] Thread stopped")


def start_hitsound_thread():
    """Start the hitsound background thread."""
    global hitsound_state
    
    if hitsound_state["running"]:
        return
    
    debug_log("Starting hitsound thread...", "INFO")
    hitsound_state["settings"] = Active_Config.copy()
    hitsound_state["running"] = True
    hitsound_state["previous_total_hits"] = 0  # Reset
    hitsound_state["thread"] = threading.Thread(target=hitsound_thread, daemon=True)
    hitsound_state["thread"].start()
    
    debug_log("Hitsound thread started", "SUCCESS")


def stop_hitsound_thread():
    """Stop the hitsound background thread."""
    global hitsound_state
    
    if not hitsound_state["running"]:
        return
    
    debug_log("Stopping hitsound thread...", "INFO")
    hitsound_state["running"] = False
    
    # Wait for thread to finish
    if hitsound_state["thread"]:
        hitsound_state["thread"].join(timeout=2.0)
        hitsound_state["thread"] = None
    
    debug_log("Hitsound thread stopped", "SUCCESS")


# =============================================================================
# FOV CHANGER THREAD
# =============================================================================
# Background thread for camera FOV modification.
# Continuously writes desired FOV value to game memory when enabled.
# =============================================================================

def fov_changer_thread():
    """
    FOV changer thread function - runs in background.
    
    Functionality:
    1. Check if FOV changer is enabled
    2. Get desired FOV value from settings
    3. Write FOV value to game memory via m_iDesiredFOV
    
    Note: FOV is written via CBasePlayerController::m_iDesiredFOV which
    modifies the player's camera field of view. Default FOV is 90.
    """
    global fov_changer_state
    
    print("[FOV CHANGER] Thread starting...")
    
    # Wait for ESP overlay to connect to CS2 and provide pm/client
    max_wait = 100  # 10 seconds max wait
    wait_count = 0
    while wait_count < max_wait:
        if esp_overlay.get("pm") and esp_overlay.get("client"):
            break
        time.sleep(0.1)
        wait_count += 1
    
    if not esp_overlay.get("pm") or not esp_overlay.get("client"):
        print("[FOV CHANGER] Failed to get pm/client from ESP overlay")
        return
    
    print("[FOV CHANGER] Connected to CS2 via ESP overlay")
    
    while fov_changer_state["running"]:
        try:
            # Get settings from fov_changer_state (updated by main thread)
            settings = fov_changer_state.get("settings", {})
            if not settings:
                settings = Active_Config.copy()
            
            # Check if FOV changer is enabled
            if not settings.get("fov_changer_enabled", False):
                time.sleep(0.1)
                continue
            
            # Check if m_iDesiredFOV offset is available
            if not m_iDesiredFOV:
                time.sleep(0.1)
                continue
            
            # Get pm and client from ESP overlay
            pm = esp_overlay.get("pm")
            client = esp_overlay.get("client")
            
            if not pm or not client:
                time.sleep(0.1)
                continue
            
            # Get local player controller
            try:
                local_player_controller = pm.read_longlong(client + dwLocalPlayerController)
                if local_player_controller:
                    # Get desired FOV value from settings
                    fov_value = settings.get("fov_value", 90)
                    
                    # Write FOV value to player controller
                    pm.write_uint(local_player_controller + m_iDesiredFOV, fov_value)
            except:
                pass
            
            # Check frequently for responsive FOV updates
            time.sleep(0.02)  # 20ms interval
            
        except Exception as e:
            time.sleep(0.1)
    
    print("[FOV CHANGER] Thread stopped")


def start_fov_changer_thread():
    """Start the FOV changer background thread."""
    global fov_changer_state
    
    if fov_changer_state["running"]:
        return
    
    debug_log("Starting FOV changer thread...", "INFO")
    
    # Initialize settings from Active_Config
    fov_changer_state["settings"] = Active_Config.copy()
    fov_changer_state["running"] = True
    
    # Start thread
    fov_changer_state["thread"] = threading.Thread(target=fov_changer_thread, daemon=True)
    fov_changer_state["thread"].start()
    
    debug_log("FOV changer thread started", "SUCCESS")


def stop_fov_changer_thread():
    """Stop the FOV changer background thread."""
    global fov_changer_state
    
    if not fov_changer_state["running"]:
        return
    
    debug_log("Stopping FOV changer thread...", "INFO")
    fov_changer_state["running"] = False
    
    # Wait for thread to finish
    if fov_changer_state["thread"]:
        fov_changer_state["thread"].join(timeout=2.0)
        fov_changer_state["thread"] = None
    
    debug_log("FOV changer thread stopped", "SUCCESS")


def update_fov_changer_settings():
    """Update FOV changer thread settings from Active_Config."""
    global fov_changer_state
    if fov_changer_state["running"]:
        fov_changer_state["settings"] = Active_Config.copy()


# =============================================================================
# RECOIL CONTROL SYSTEM (RCS) THREAD
# =============================================================================
# Background thread for recoil control functionality.
# Compensates for weapon recoil by adjusting view angles based on aim punch.
# =============================================================================

def rcs_thread():
    """
    Recoil Control System thread function - runs in background.
    
    Functionality:
    1. Read m_iShotsFired to detect when player is shooting
    2. Read m_aimPunchAngle to get current recoil offset
    3. Calculate delta from previous punch and apply compensation
    4. Write adjusted view angles to dwViewAngles
    
    The RCS works by counteracting the aim punch that CS2 applies when shooting.
    It reads the punch angle delta (change from last frame) and subtracts it
    from the current view angles, effectively negating recoil.
    """
    global rcs_state
    
    print("[RCS] Thread starting...")
    
    # Wait for ESP overlay to connect to CS2 and provide pm/client
    max_wait = 100  # 10 seconds max wait
    wait_count = 0
    while wait_count < max_wait:
        if esp_overlay.get("pm") and esp_overlay.get("client"):
            break
        time.sleep(0.1)
        wait_count += 1
    
    if not esp_overlay.get("pm") or not esp_overlay.get("client"):
        print("[RCS] Failed to get pm/client from ESP overlay")
        return
    
    print("[RCS] Connected to CS2 via ESP overlay")
    
    # Store previous punch angle for delta calculation
    prev_punch_x = 0.0
    prev_punch_y = 0.0
    
    # Accumulator for remaining compensation (smoothing)
    remaining_comp_x = 0.0
    remaining_comp_y = 0.0
    
    # Continuous fire detection
    shot_timestamps = []  # List of (timestamp, shots_fired) tuples
    continuous_fire_window = 0.3  # 300ms window for continuous fire detection
    min_continuous_shots = 2  # Need at least 2 shots in window to be continuous
    
    while rcs_state["running"]:
        try:
            # Get settings from rcs_state (updated by main thread)
            settings = rcs_state.get("settings", {})
            if not settings:
                settings = Active_Config.copy()
            
            # Check if RCS is enabled
            if not settings.get("rcs_enabled", False):
                # Reset previous punch and accumulator when disabled
                prev_punch_x = 0.0
                prev_punch_y = 0.0
                remaining_comp_x = 0.0
                remaining_comp_y = 0.0
                time.sleep(0.05)
                continue
            
            # Check if required offsets are available
            if not m_aimPunchAngle or not m_iShotsFired or not dwViewAngles:
                time.sleep(0.1)
                continue
            
            # Get pm and client from ESP overlay
            pm = esp_overlay.get("pm")
            client = esp_overlay.get("client")
            
            if not pm or not client:
                time.sleep(0.1)
                continue
            
            # Get local player pawn
            try:
                local_player_controller = pm.read_longlong(client + dwLocalPlayerController)
                if not local_player_controller:
                    prev_punch_x = 0.0
                    prev_punch_y = 0.0
                    remaining_comp_x = 0.0
                    remaining_comp_y = 0.0
                    time.sleep(0.05)
                    continue
                
                local_player_pawn = pm.read_longlong(local_player_controller + m_hPlayerPawn)
                if not local_player_pawn:
                    prev_punch_x = 0.0
                    prev_punch_y = 0.0
                    remaining_comp_x = 0.0
                    remaining_comp_y = 0.0
                    time.sleep(0.05)
                    continue
                
                # Resolve entity from handle
                entity_list = pm.read_longlong(client + dwEntityList)
                if not entity_list:
                    time.sleep(0.05)
                    continue
                
                # Get list entry for local pawn
                list_entry = pm.read_longlong(entity_list + 0x8 * ((local_player_pawn & 0x7FFF) >> 9) + 0x10)
                if not list_entry:
                    time.sleep(0.05)
                    continue
                
                pawn_address = pm.read_longlong(list_entry + 0x70 * (local_player_pawn & 0x1FF))
                if not pawn_address:
                    prev_punch_x = 0.0
                    prev_punch_y = 0.0
                    remaining_comp_x = 0.0
                    remaining_comp_y = 0.0
                    time.sleep(0.05)
                    continue
                
                # Read shots fired count
                shots_fired = pm.read_int(pawn_address + m_iShotsFired)
                current_time = time.time()
                
                # Check if continuous fire only mode is enabled
                continuous_only = settings.get("rcs_continuous_only", False)
                
                # Only apply RCS when shooting (shots_fired > 0)
                if shots_fired <= 0:
                    prev_punch_x = 0.0
                    prev_punch_y = 0.0
                    remaining_comp_x = 0.0
                    remaining_comp_y = 0.0
                    shot_timestamps.clear()  # Clear timestamps when not shooting
                    time.sleep(0.01)
                    continue
                
                # If continuous fire only is enabled, check if this is continuous fire
                if continuous_only:
                    # Update shot timestamps
                    if len(shot_timestamps) == 0 or shots_fired > shot_timestamps[-1][1]:
                        # New shot fired, add timestamp
                        shot_timestamps.append((current_time, shots_fired))
                    
                    # Remove old timestamps outside the window
                    shot_timestamps[:] = [
                        (ts, sf) for ts, sf in shot_timestamps 
                        if current_time - ts <= continuous_fire_window
                    ]
                    
                    # Check if we have enough shots in the window to consider it continuous fire
                    is_continuous = len(shot_timestamps) >= min_continuous_shots
                    
                    # Skip if not continuous fire
                    if not is_continuous:
                        prev_punch_x = 0.0
                        prev_punch_y = 0.0
                        remaining_comp_x = 0.0
                        remaining_comp_y = 0.0
                        time.sleep(0.01)
                        continue
                
                # Read current aim punch angle as bytes for more atomic read (12 bytes = 3 floats: X, Y, Z)
                # X = pitch (vertical), Y = yaw (horizontal)
                try:
                    punch_bytes = pm.read_bytes(pawn_address + m_aimPunchAngle, 8)
                    punch_x = struct.unpack('f', punch_bytes[0:4])[0]  # Pitch (vertical)
                    punch_y = struct.unpack('f', punch_bytes[4:8])[0]  # Yaw (horizontal)
                except:
                    punch_x = pm.read_float(pawn_address + m_aimPunchAngle)
                    punch_y = pm.read_float(pawn_address + m_aimPunchAngle + 4)
                
                # Calculate delta (change since last frame)
                delta_x = punch_x - prev_punch_x
                delta_y = punch_y - prev_punch_y
                
                # Update previous punch for next iteration
                prev_punch_x = punch_x
                prev_punch_y = punch_y
                
                # Get strength settings (0-100%)
                strength_x = settings.get("rcs_strength_x", 100) / 100.0
                strength_y = settings.get("rcs_strength_y", 100) / 100.0
                smoothness = settings.get("rcs_smoothness", 1)
                recoil_scale = settings.get("rcs_multiplier", 2.0)
                
                # Add new compensation to the accumulator
                # recoil_scale (default 2.0) is the CS2 weapon_recoil_scale factor
                remaining_comp_x += delta_x * recoil_scale * strength_y  # Y strength for vertical
                remaining_comp_y += delta_y * recoil_scale * strength_x  # X strength for horizontal
                
                # Skip only if there's truly nothing to apply (very small threshold)
                if abs(remaining_comp_x) < 0.00001 and abs(remaining_comp_y) < 0.00001:
                    time.sleep(0.001)
                    continue
                
                # Calculate how much to apply this frame based on smoothness
                # Smoothness 1 = apply all at once, Smoothness 10 = apply 10% per frame
                smooth_factor = 1.0 / max(1, smoothness)
                
                # Calculate this frame's compensation amount
                apply_x = remaining_comp_x * smooth_factor
                apply_y = remaining_comp_y * smooth_factor
                
                # For smoothness 1 (instant), apply everything and clear accumulator
                if smoothness <= 1:
                    apply_x = remaining_comp_x
                    apply_y = remaining_comp_y
                    remaining_comp_x = 0.0
                    remaining_comp_y = 0.0
                else:
                    # Subtract from accumulator (what we're about to apply)
                    remaining_comp_x -= apply_x
                    remaining_comp_y -= apply_y
                
                # Skip if the amount to apply is negligible
                if abs(apply_x) < 0.00001 and abs(apply_y) < 0.00001:
                    time.sleep(0.001)
                    continue
                
                # Read current view angles as bytes for more atomic read
                try:
                    view_bytes = pm.read_bytes(client + dwViewAngles, 8)
                    view_angle_x = struct.unpack('f', view_bytes[0:4])[0]  # Pitch
                    view_angle_y = struct.unpack('f', view_bytes[4:8])[0]  # Yaw
                except:
                    view_angle_x = pm.read_float(client + dwViewAngles)
                    view_angle_y = pm.read_float(client + dwViewAngles + 4)
                
                # Apply compensation
                new_view_x = view_angle_x - apply_x
                new_view_y = view_angle_y - apply_y
                
                # Clamp pitch to valid range (-89 to 89)
                new_view_x = max(-89.0, min(89.0, new_view_x))
                
                # Normalize yaw to -180 to 180
                while new_view_y > 180.0:
                    new_view_y -= 360.0
                while new_view_y < -180.0:
                    new_view_y += 360.0
                
                # Write both view angles together for more atomic write
                try:
                    new_view_bytes = struct.pack('ff', new_view_x, new_view_y)
                    pm.write_bytes(client + dwViewAngles, new_view_bytes, 8)
                except:
                    pm.write_float(client + dwViewAngles, new_view_x)
                    pm.write_float(client + dwViewAngles + 4, new_view_y)
                
            except Exception as e:
                prev_punch_x = 0.0
                prev_punch_y = 0.0
                remaining_comp_x = 0.0
                remaining_comp_y = 0.0
            
            # Run at high frequency for responsive recoil control
            time.sleep(0.001)  # 1ms interval
            
        except Exception as e:
            time.sleep(0.05)
    
    print("[RCS] Thread stopped")


def start_rcs_thread():
    """Start the Recoil Control System background thread."""
    global rcs_state
    
    if rcs_state["running"]:
        return
    
    debug_log("Starting RCS thread...", "INFO")
    
    # Initialize settings from Active_Config
    rcs_state["settings"] = Active_Config.copy()
    rcs_state["running"] = True
    rcs_state["prev_punch"] = (0.0, 0.0)
    
    # Start thread
    rcs_state["thread"] = threading.Thread(target=rcs_thread, daemon=True)
    rcs_state["thread"].start()
    
    debug_log("RCS thread started", "SUCCESS")


def stop_rcs_thread():
    """Stop the Recoil Control System background thread."""
    global rcs_state
    
    if not rcs_state["running"]:
        return
    
    debug_log("Stopping RCS thread...", "INFO")
    rcs_state["running"] = False
    
    # Wait for thread to finish
    if rcs_state["thread"]:
        rcs_state["thread"].join(timeout=2.0)
        rcs_state["thread"] = None
    
    debug_log("RCS thread stopped", "SUCCESS")


def update_rcs_settings():
    """Update RCS thread settings from Active_Config."""
    global rcs_state
    if rcs_state["running"]:
        rcs_state["settings"] = Active_Config.copy()


# =============================================================================
# AUTO CROSSHAIR PLACEMENT (ACS) THREAD
# =============================================================================
# Background thread for auto crosshair placement functionality.
# Automatically adjusts vertical aim to target bone level when key is held.
# =============================================================================

def acs_thread():
    """
    Auto Crosshair Placement thread function - runs in background.
    
    Functionality:
    1. Check if ACS is enabled
    2. Check if ACS key is held
    3. Find closest enemy target
    4. Adjust vertical aim to match target bone level with smoothing
    5. Respects deadzone - won't adjust if already within deadzone
    """
    global acs_state
    
    print("[ACS] Thread starting...")
    
    # Wait for ESP overlay to connect to CS2 and provide pm/client
    max_wait = 100  # 10 seconds max wait
    wait_count = 0
    while wait_count < max_wait:
        if esp_overlay.get("pm") and esp_overlay.get("client"):
            break
        time.sleep(0.1)
        wait_count += 1
    
    if not esp_overlay.get("pm") or not esp_overlay.get("client"):
        print("[ACS] Failed to get pm/client from ESP overlay")
        return
    
    print("[ACS] Connected to CS2 via ESP overlay")
    
    while acs_state["running"]:
        try:
            # Get settings from acs_state (updated by main thread)
            settings = acs_state.get("settings", {})
            if not settings:
                settings = Active_Config.copy()
            
            # Check if ACS is enabled
            if not settings.get("acs_enabled", False):
                time.sleep(0.01)
                continue
            
            # Get ACS key and check if it's held
            acs_key = Keybinds_Config.get("acs_key", "v").lower()
            if acs_key == "none":
                time.sleep(0.01)
                continue
            
            # Get VK code for ACS key
            vk_code = KEY_NAME_TO_VK.get(acs_key, 0)
            if vk_code == 0:
                time.sleep(0.01)
                continue
            
            # Check if key is held
            key_held = (win32api.GetAsyncKeyState(vk_code) & 0x8000) != 0
            if not key_held:
                time.sleep(0.005)
                continue
            
            # Get pm and client from ESP overlay
            pm = esp_overlay.get("pm")
            client = esp_overlay.get("client")
            
            if not pm or not client:
                time.sleep(0.01)
                continue
            
            # Get screen dimensions
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            # Read view matrix
            try:
                view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
            except:
                time.sleep(0.005)
                continue
            
            # Get local player
            try:
                local_player_pawn = pm.read_longlong(client + dwLocalPlayerPawn)
                if not local_player_pawn:
                    time.sleep(0.005)
                    continue
                local_team = pm.read_int(local_player_pawn + m_iTeamNum)
            except:
                time.sleep(0.005)
                continue
            
            # Build target list and find closest
            closest_target = None
            min_distance = float('inf')
            
            try:
                entity_list = pm.read_longlong(client + dwEntityList)
                list_entry = pm.read_longlong(entity_list + 0x10)
                
                for i in range(1, 64):
                    try:
                        if list_entry == 0:
                            break
                        
                        current_controller = pm.read_longlong(list_entry + i * 0x70)
                        if current_controller == 0:
                            continue
                        
                        pawn_handle = pm.read_int(current_controller + m_hPlayerPawn)
                        if pawn_handle == 0:
                            continue
                        
                        list_entry2 = pm.read_longlong(entity_list + 0x8 * ((pawn_handle & 0x7FFF) >> 9) + 0x10)
                        if list_entry2 == 0:
                            continue
                        
                        entity_pawn = pm.read_longlong(list_entry2 + 0x70 * (pawn_handle & 0x1FF))
                        if entity_pawn == 0 or entity_pawn == local_player_pawn:
                            continue
                        
                        # Check team (enemies only)
                        entity_team = pm.read_int(entity_pawn + m_iTeamNum)
                        if entity_team == local_team:
                            continue
                        
                        # Check if alive
                        entity_alive = pm.read_int(entity_pawn + m_lifeState)
                        if entity_alive != 256:
                            continue
                        
                        entity_health = pm.read_int(entity_pawn + m_iHealth)
                        if entity_health <= 0:
                            continue
                        
                        # Get bone position based on target bone setting
                        game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
                        if game_scene == 0:
                            continue
                        
                        bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                        if bone_matrix == 0:
                            continue
                        
                        # Get target bone ID based on setting
                        target_bone_name = settings.get("acs_target_bone", "Head")
                        bone_map = {"Head": 6, "Neck": 5, "Chest": 4, "Pelvis": 0}
                        target_bone_id = bone_map.get(target_bone_name, 6)
                        
                        # Read target bone position
                        bone_x = pm.read_float(bone_matrix + target_bone_id * 0x20)
                        bone_y = pm.read_float(bone_matrix + target_bone_id * 0x20 + 0x4)
                        bone_z = pm.read_float(bone_matrix + target_bone_id * 0x20 + 0x8)
                        
                        # Convert to screen coordinates
                        screen_pos = w2s_aimbot(view_matrix, bone_x, bone_y, bone_z, screen_width, screen_height)
                        
                        if screen_pos[0] != -999 and screen_pos[1] != -999:
                            # Check if on screen
                            if 0 <= screen_pos[0] <= screen_width and 0 <= screen_pos[1] <= screen_height:
                                dx = screen_pos[0] - center_x
                                dy = screen_pos[1] - center_y
                                dist = math.sqrt(dx * dx + dy * dy)
                                
                                if dist < min_distance:
                                    min_distance = dist
                                    closest_target = screen_pos
                    except:
                        continue
            except:
                time.sleep(0.005)
                continue
            
            if not closest_target:
                time.sleep(0.005)
                continue
            
            # Calculate vertical adjustment
            target_y = closest_target[1]
            dy = target_y - center_y
            
            # Check if within deadzone
            deadzone = settings.get("acs_deadzone", 5)
            if abs(dy) <= deadzone:
                time.sleep(0.005)
                continue
            
            # Apply linear movement (constant speed regardless of distance)
            smoothness = settings.get("acs_smoothness", 5)
            if smoothness <= 0:
                smoothness = 1
            smoothness = max(1, min(50, smoothness))
            
            if smoothness == 1:
                move_y = int(dy)
            else:
                # Linear: constant speed based on smoothness
                # Speed is inversely proportional to smoothness
                speed = max(1, 10.0 / smoothness)
                # Move in the direction of target at constant speed
                if dy > 0:
                    move_y = int(min(speed, dy))  # Don't overshoot
                else:
                    move_y = int(max(-speed, dy))  # Don't overshoot
            
            # Move mouse (vertical only)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, move_y, 0, 0)
            
            # Small delay
            time.sleep(0.005)
            
        except Exception as e:
            time.sleep(0.01)
    
    print("[ACS] Thread stopped")


def start_acs_thread():
    """Start the ACS background thread."""
    global acs_state
    
    if acs_state["running"]:
        return
    
    debug_log("Starting ACS thread...", "INFO")
    
    # Initialize settings from Active_Config
    acs_state["settings"] = Active_Config.copy()
    acs_state["running"] = True
    
    # Start thread
    acs_state["thread"] = threading.Thread(target=acs_thread, daemon=True)
    acs_state["thread"].start()
    
    debug_log("ACS thread started", "SUCCESS")


def stop_acs_thread():
    """Stop the ACS background thread."""
    global acs_state
    
    if not acs_state["running"]:
        return
    
    debug_log("Stopping ACS thread...", "INFO")
    acs_state["running"] = False
    
    # Wait for thread to finish
    if acs_state["thread"]:
        acs_state["thread"].join(timeout=2.0)
        acs_state["thread"] = None
    
    debug_log("ACS thread stopped", "SUCCESS")


# =============================================================================
# UI CALLBACKS
# =============================================================================
# Event handlers for UI interactions: button clicks, checkbox toggles, etc.
# These functions are called by DearPyGui when users interact with widgets.
# =============================================================================

def on_bypass_password_entered():
    """
    Handle bypass password Enter button click.
    Checks if password is correct and shows Launch button if valid.
    """
    password = dpg.get_value("txt_bypass_password")
    
    if password == "israel":
        # Correct password - show Launch button and update offline message
        dpg.configure_item("btn_launch", show=True)
        dpg.configure_item("txt_bypass_password", show=False)
        dpg.configure_item("btn_bypass_enter", show=False)
        dpg.configure_item("txt_offline_message", default_value="Correct Password!", color=(0, 255, 0))
        dpg.configure_item("txt_bypass_label", show=False)
        debug_log("Bypass password accepted", "SUCCESS")
    else:
        # Incorrect password - show error
        debug_log("Invalid bypass password entered", "WARNING")
        # Flash the input box by briefly changing its hint
        dpg.configure_item("txt_bypass_password", hint="Incorrect password")


def restore_loader_ui():
    """
    Restore the loader UI elements after a failed launch attempt.
    Shows all hidden elements including tooltips.
    """
    show_tips = Active_Config.get("show_tooltips", True)
    
    # Hide progress elements
    dpg.configure_item("progress_status_text", show=False)
    dpg.configure_item("progress_launch", show=False)
    dpg.set_value("progress_launch", 0.0)
    
    # Show launch button
    dpg.configure_item("btn_launch", show=True)
    
    # Show hidden UI elements
    dpg.configure_item("chk_show_debug_tab", show=True)
    dpg.configure_item("tooltip_show_debug_tab", show=show_tips)
    dpg.configure_item("chk_show_tooltips", show=True)
    dpg.configure_item("tooltip_show_tooltips", show=show_tips)
    dpg.configure_item("chk_use_local_offsets", show=True)
    dpg.configure_item("tooltip_use_local_offsets", show=show_tips)
    dpg.configure_item("close_btn", show=True)
    
    # Show create offsets button if use local offsets is checked
    if dpg.get_value("chk_use_local_offsets"):
        dpg.configure_item("btn_create_offsets", show=True)


def on_test_clicked():
    """
    Handle Launch button click.
    
    Loading sequence (5 stages):
    1. Apply loader settings (console visibility, offset source)
    2. Wait for CS2.exe to be running
    3. Load offsets (from GitHub or local files)
       - If local: Check if offsets exist, show error if missing
       - If GitHub: Download from remote repository
    4. Initialize offset globals (extract values from JSON)
    5. Switch to cheat window
    
    Progress bar updates after each stage with status text.
    Errors are shown via Win32 MessageBox (always on top).
    """
    # Hide launch button and show progress bar + status text
    dpg.configure_item("btn_launch", show=False)
    dpg.configure_item("progress_status_text", show=True)
    dpg.configure_item("progress_launch", show=True)
    
    # Hide additional UI elements during loading (including their tooltips)
    dpg.configure_item("chk_show_debug_tab", show=False)
    dpg.configure_item("tooltip_show_debug_tab", show=False)
    dpg.configure_item("chk_show_tooltips", show=False)
    dpg.configure_item("tooltip_show_tooltips", show=False)
    dpg.configure_item("chk_use_local_offsets", show=False)
    dpg.configure_item("tooltip_use_local_offsets", show=False)
    dpg.configure_item("btn_create_offsets", show=False)
    dpg.configure_item("close_btn", show=False)
    
    # Save current window position for the cheat window
    if drag_state["hwnd"]:
        try:
            rect = win32gui.GetWindowRect(drag_state["hwnd"])
            app_state["last_window_pos"] = (rect[0], rect[1])
        except Exception:
            pass
    
    # Stage 1: Applying loader settings
    dpg.set_value("progress_launch", 0.20)
    dpg.set_value("progress_status_text", "Applying loader settings...")
    dpg.render_dearpygui_frame()  # Force UI update
    
    # Read checkbox values and store in loader_settings
    loader_settings["ShowDebugTab"] = dpg.get_value("chk_show_debug_tab")
    loader_settings["UseLocalOffsets"] = dpg.get_value("chk_use_local_offsets")
    
    time.sleep(1.0)
    
    # Stage 2: Wait for CS2 to be running
    dpg.set_value("progress_launch", 0.40)
    dpg.set_value("progress_status_text", "Waiting for CS2...")
    dpg.render_dearpygui_frame()  # Force UI update
    
    # Wait for CS2 to be running (check every 500ms)
    while not is_cs2_running():
        dpg.render_dearpygui_frame()  # Keep UI responsive
        time.sleep(0.5)
    
    time.sleep(0.5)  # Brief pause after CS2 detected
    
    # Stage 3: Installing Sounds
    dpg.set_value("progress_launch", 0.50)
    dpg.set_value("progress_status_text", "Installing Sounds...")
    dpg.render_dearpygui_frame()  # Force UI update
    
    # Download sound files to temp folder
    sound_files = [
        (HITMARKER_SOUND_URL, "hitmarker.wav"),
        (METALHIT_SOUND_URL, "metalhit.wav"),
        (CRITICALHIT_SOUND_URL, "criticalhit.wav")
    ]
    
    for url, filename in sound_files:
        try:
            filepath = os.path.join(TEMP_FOLDER, filename)
            urllib.request.urlretrieve(url, filepath)
            print(f"[SOUNDS] Downloaded {filename}")
        except Exception as e:
            print(f"[SOUNDS] Failed to download {filename}: {e}")
    
    time.sleep(1.0)
    
    # Stage 4: Check manual offsets if enabled
    if loader_settings["UseLocalOffsets"]:
        dpg.set_value("progress_launch", 0.70)
        dpg.set_value("progress_status_text", "Checking manual offsets...")
        dpg.render_dearpygui_frame()  # Force UI update
        
        # Check if output folder exists
        output_folder = os.path.join(TEMP_FOLDER, "offsets", "output")
        if not os.path.exists(output_folder):
            # Show error message
            hwnd = drag_state["hwnd"] if drag_state["hwnd"] else 0
            title = app_state["app_title"] if app_state["app_title"] else FALLBACK_TITLE
            ctypes.windll.user32.MessageBoxW(
                hwnd,
                "Manual offsets not found. Please create offsets first.",
                title,
                0x00000010 | 0x00040000  # MB_ICONERROR | MB_TOPMOST
            )
            
            # Reset UI - restore all hidden elements
            restore_loader_ui()
            return
        
        # Load local offsets
        if not load_and_initialize_offsets(use_local=True):
            hwnd = drag_state["hwnd"] if drag_state["hwnd"] else 0
            title = app_state["app_title"] if app_state["app_title"] else FALLBACK_TITLE
            ctypes.windll.user32.MessageBoxW(
                hwnd,
                "Failed to load manual offsets. Files may be corrupted.",
                title,
                0x00000010 | 0x00040000  # MB_ICONERROR | MB_TOPMOST
            )
            
            # Reset UI - restore all hidden elements
            restore_loader_ui()
            return
        
        time.sleep(1.5)
    else:
        # Load offsets from GitHub
        dpg.set_value("progress_launch", 0.70)
        dpg.set_value("progress_status_text", "Fetching offsets...")
        dpg.render_dearpygui_frame()  # Force UI update
        
        if not load_and_initialize_offsets(use_local=False):
            hwnd = drag_state["hwnd"] if drag_state["hwnd"] else 0
            title = app_state["app_title"] if app_state["app_title"] else FALLBACK_TITLE
            ctypes.windll.user32.MessageBoxW(
                hwnd,
                "Failed to load offsets. Check your internet connection.",
                title,
                0x00000010 | 0x00040000  # MB_ICONERROR | MB_TOPMOST
            )
            
            # Reset UI - restore all hidden elements
            restore_loader_ui()
            return
        
        time.sleep(1.5)
    
    # Stage 5: Starting cheat
    dpg.set_value("progress_launch", 0.90)
    dpg.set_value("progress_status_text", "Starting cheat...")
    dpg.render_dearpygui_frame()  # Force UI update
    time.sleep(1.5)
    
    # Stage 5: Switch to cheat window
    dpg.set_value("progress_launch", 1.0)
    dpg.render_dearpygui_frame()  # Force UI update
    time.sleep(0.5)  # Brief pause before switching
    
    app_state["switch_to_cheat"] = True
    dpg.stop_dearpygui()


def on_close_clicked():
    """
    Handle close button click.
    Stops the DearPyGui render loop, triggering application shutdown.
    """
    dpg.stop_dearpygui()


def on_rounded_corners_changed(sender, value):
    """
    Handle Rounded Window Corners checkbox toggle.
    Applies or removes rounded corners immediately.
    """
    if drag_state["hwnd"]:
        if value:
            enable_rounded_corners(drag_state["hwnd"])
        else:
            disable_rounded_corners(drag_state["hwnd"])


def on_fps_cap_toggle(sender, value):
    """Handle FPS cap toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["fps_cap_enabled"] = value
    Active_Config["fps_cap_enabled"] = value
    save_settings()
    
    # Show/hide the FPS slider based on toggle state
    if dpg.does_item_exist("slider_fps_cap"):
        dpg.configure_item("slider_fps_cap", show=value)
    # Also show/hide the tooltip
    show_tips = Active_Config.get("show_tooltips", True)
    if dpg.does_item_exist("tooltip_fps_cap_slider"):
        dpg.configure_item("tooltip_fps_cap_slider", show=value and show_tips)
    
    debug_log(f"FPS Cap {'enabled' if value else 'disabled'}", "INFO")


def on_fps_cap_change(sender, value):
    """Handle FPS cap slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["fps_cap_value"] = value
    Active_Config["fps_cap_value"] = value
    save_settings()
    debug_log(f"FPS Cap set to: {value}", "INFO")


def on_anti_flash_toggle(sender, value):
    """Handle anti-flash toggle."""
    if anti_flash_state["settings"]:
        anti_flash_state["settings"]["anti_flash_enabled"] = value
    Active_Config["anti_flash_enabled"] = value
    save_settings()
    debug_log(f"Anti-Flash {'enabled' if value else 'disabled'}", "INFO")


def on_hitsound_toggle(sender, value):
    """Handle hitsound toggle."""
    if hitsound_state["settings"]:
        hitsound_state["settings"]["hitsound_enabled"] = value
    Active_Config["hitsound_enabled"] = value
    save_settings()
    
    # Show/hide hitsound dropdown based on toggle
    if dpg.does_item_exist("combo_hitsound_type"):
        dpg.configure_item("combo_hitsound_type", show=value)
    if dpg.does_item_exist("tooltip_hitsound_type"):
        show_tips = Active_Config.get("show_tooltips", True)
        dpg.configure_item("tooltip_hitsound_type", show=value and show_tips)
    
    if value:
        start_hitsound_thread()
    else:
        stop_hitsound_thread()
    
    debug_log(f"Hitsound {'enabled' if value else 'disabled'}", "INFO")


def on_hitsound_type_change(sender, value):
    """Handle hitsound type dropdown change."""
    if hitsound_state["settings"]:
        hitsound_state["settings"]["hitsound_type"] = value
    Active_Config["hitsound_type"] = value
    save_settings()
    debug_log(f"Hitsound type set to: {value}", "INFO")


def reset_fov_to_default():
    """Reset FOV to default value (90) by writing to game memory."""
    try:
        # Check if m_iDesiredFOV offset is available
        if not m_iDesiredFOV:
            return
        
        # Get pm and client from ESP overlay
        pm = esp_overlay.get("pm")
        client = esp_overlay.get("client")
        
        if not pm or not client:
            return
        
        # Get local player controller and reset FOV to 90
        local_player_controller = pm.read_longlong(client + dwLocalPlayerController)
        if local_player_controller:
            pm.write_uint(local_player_controller + m_iDesiredFOV, 90)
            debug_log("FOV reset to default (90)", "INFO")
    except Exception as e:
        pass  # Silently fail if reset fails


def on_fov_changer_toggle(sender, value):
    """Handle FOV changer toggle."""
    if fov_changer_state["settings"]:
        fov_changer_state["settings"]["fov_changer_enabled"] = value
    Active_Config["fov_changer_enabled"] = value
    save_settings()
    
    # Show/hide FOV slider based on toggle
    if dpg.does_item_exist("slider_fov_value"):
        dpg.configure_item("slider_fov_value", show=value)
    if dpg.does_item_exist("tooltip_fov_value"):
        dpg.configure_item("tooltip_fov_value", show=value)
    
    # Reset FOV to 90 when disabled
    if not value:
        reset_fov_to_default()
    
    debug_log(f"FOV Changer {'enabled' if value else 'disabled'}", "INFO")


def on_fov_value_change(sender, value):
    """Handle FOV value slider change."""
    if fov_changer_state["settings"]:
        fov_changer_state["settings"]["fov_value"] = value
    Active_Config["fov_value"] = value
    save_settings()
    debug_log(f"FOV value set to {value}", "INFO")


def on_rcs_toggle(sender, value):
    """Handle RCS toggle."""
    if rcs_state["settings"]:
        rcs_state["settings"]["rcs_enabled"] = value
    Active_Config["rcs_enabled"] = value
    save_settings()
    debug_log(f"RCS {'enabled' if value else 'disabled'}", "INFO")


def on_rcs_strength_x_change(sender, value):
    """Handle RCS horizontal strength slider change."""
    if rcs_state["settings"]:
        rcs_state["settings"]["rcs_strength_x"] = value
    Active_Config["rcs_strength_x"] = value
    save_settings()
    debug_log(f"RCS horizontal strength set to {value}%", "INFO")


def on_rcs_strength_y_change(sender, value):
    """Handle RCS vertical strength slider change."""
    if rcs_state["settings"]:
        rcs_state["settings"]["rcs_strength_y"] = value
    Active_Config["rcs_strength_y"] = value
    save_settings()
    debug_log(f"RCS vertical strength set to {value}%", "INFO")


def on_rcs_smoothness_change(sender, value):
    """Handle RCS smoothness slider change."""
    if rcs_state["settings"]:
        rcs_state["settings"]["rcs_smoothness"] = value
    Active_Config["rcs_smoothness"] = value
    save_settings()
    debug_log(f"RCS smoothness set to {value}", "INFO")


def on_rcs_multiplier_change(sender, value):
    """Handle RCS multiplier slider change."""
    if rcs_state["settings"]:
        rcs_state["settings"]["rcs_multiplier"] = value
    Active_Config["rcs_multiplier"] = value
    save_settings()
    debug_log(f"RCS multiplier set to {value}", "INFO")


def on_rcs_continuous_only_toggle(sender, value):
    """Handle RCS continuous fire only toggle."""
    if rcs_state["settings"]:
        rcs_state["settings"]["rcs_continuous_only"] = value
    Active_Config["rcs_continuous_only"] = value
    save_settings()
    debug_log(f"RCS continuous fire only {'enabled' if value else 'disabled'}", "INFO")


def on_hide_on_tabout_toggle(sender, value):
    """Handle hide on tab-out toggle."""
    Active_Config["hide_on_tabout"] = value
    save_settings()
    debug_log(f"Hide on Tab-Out {'enabled' if value else 'disabled'}", "INFO")


def on_show_status_labels_toggle(sender, value):
    """Handle show status labels toggle."""
    Active_Config["show_status_labels"] = value
    save_settings()
    debug_log(f"Status labels {'enabled' if value else 'disabled'}", "INFO")


# List of all tooltip tags for show/hide functionality
ALL_TOOLTIP_TAGS = []

def on_show_tooltips_toggle(sender, value):
    """Handle show tooltips toggle - shows/hides all tooltips."""
    Active_Config["show_tooltips"] = value
    save_settings()
    # Show/hide all registered tooltips
    for tag in ALL_TOOLTIP_TAGS:
        try:
            dpg.configure_item(tag, show=value)
        except:
            pass
    debug_log(f"Tooltips {'enabled' if value else 'disabled'}", "INFO")


def on_use_local_offsets_changed(sender, value):
    """
    Handle Use Local Offsets checkbox toggle.
    Shows/hides the Create Offsets button based on checkbox state.
    """
    dpg.configure_item("btn_create_offsets", show=value)


def on_create_offsets_clicked():
    """
    Handle Create Offsets button click.
    Checks if CS2 is running before proceeding.
    """
    # Check if cs2.exe is running
    cs2_running = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == 'cs2.exe':
                cs2_running = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if not cs2_running:
        # Show topmost message box using the loader window as parent
        hwnd = drag_state["hwnd"] if drag_state["hwnd"] else 0
        title = app_state["app_title"] if app_state["app_title"] else FALLBACK_TITLE
        ctypes.windll.user32.MessageBoxW(
            hwnd,
            "Launch cs2.exe first",
            title,
            0x00000010 | 0x00040000  # MB_ICONERROR | MB_TOPMOST
        )
        return
    
    # CS2 is running - start offset creation in background thread
    def create_offsets_thread():
        process = None
        try:
            # Step 0: Disable button and update text
            dpg.configure_item("btn_create_offsets", enabled=False, label="Creating Offsets...")
            dpg.render_dearpygui_frame()
            
            # Step 1: Create offsets folder inside temp
            offsets_folder = os.path.join(TEMP_FOLDER, "offsets")
            os.makedirs(offsets_folder, exist_ok=True)
            
            # Step 2: Download offsets.exe with error handling
            offsets_exe_path = os.path.join(offsets_folder, "offsets.exe")
            try:
                urllib.request.urlretrieve(OFFSETS_URL, offsets_exe_path)
            except Exception as download_error:
                hwnd = drag_state["hwnd"] if drag_state["hwnd"] else 0
                title = app_state["app_title"] if app_state["app_title"] else FALLBACK_TITLE
                ctypes.windll.user32.MessageBoxW(
                    hwnd,
                    f"Failed to download offsets.exe: {str(download_error)}",
                    title,
                    0x00000010 | 0x00040000  # MB_ICONERROR | MB_TOPMOST
                )
                raise
            
            # Step 3: Run offsets.exe and wait for output folder
            # Use CREATE_NO_WINDOW flag to prevent console window
            CREATE_NO_WINDOW = 0x08000000
            process = subprocess.Popen(
                [offsets_exe_path], 
                cwd=offsets_folder,
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for output folder to be created (check every 0.5 seconds, max 60 seconds)
            output_folder = os.path.join(offsets_folder, "output")
            max_wait_time = 60
            elapsed_time = 0
            while not os.path.exists(output_folder) and elapsed_time < max_wait_time:
                # Check if process is still running
                if process.poll() is not None:
                    # Process ended, wait a bit more for files to be written
                    time.sleep(1)
                    break
                time.sleep(0.5)
                elapsed_time += 0.5
            
            # Give the process a moment to finish writing files
            time.sleep(1)
            
            # Terminate process if still running
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except Exception:
                    try:
                        process.kill()
                    except Exception:
                        pass
            
            # Step 4: Delete cs2-dumper.log and offsets.exe
            try:
                log_file = os.path.join(offsets_folder, "cs2-dumper.log")
                if os.path.exists(log_file):
                    os.remove(log_file)
            except Exception:
                pass  # Ignore if file is locked or doesn't exist
            
            try:
                if os.path.exists(offsets_exe_path):
                    # Wait a bit to ensure process has released the file
                    time.sleep(0.5)
                    os.remove(offsets_exe_path)
            except Exception:
                pass  # Ignore if file is locked
            
            # Step 5: Update button to show success
            dpg.configure_item("btn_create_offsets", label="Offsets Created!")
            dpg.render_dearpygui_frame()
            time.sleep(2)
            
            # Step 6: Reset button to original state
            dpg.configure_item("btn_create_offsets", enabled=True, label="Create Offsets")
            dpg.render_dearpygui_frame()
            
        except Exception as e:
            # Ensure process is terminated on any error
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except Exception:
                    try:
                        process.kill()
                    except Exception:
                        pass
            
            # On error, reset button
            try:
                dpg.configure_item("btn_create_offsets", enabled=True, label="Create Offsets")
                dpg.render_dearpygui_frame()
            except Exception:
                pass  # Ignore if UI is no longer available
    
    # Run in background thread to avoid blocking UI
    thread = threading.Thread(target=create_offsets_thread, daemon=True)
    thread.start()


# =============================================================================
# WINDOW DRAGGING
# =============================================================================
# Custom window dragging implementation using Win32 API.
# Allows users to drag the borderless window by clicking the titlebar.
# Called every frame in the main render loop.
# =============================================================================

def update_window_drag():
    """
    Update window position while dragging.
    
    Drag state machine:
    - Not dragging + mouse down → Check if cursor in titlebar, start drag if yes
    - Dragging + mouse down → Calculate delta, move window to new position
    - Mouse up → Stop dragging
    
    This function is called every frame in the main loop. It:
    1. Checks if left mouse button is held down (Win32 GetAsyncKeyState)
    2. If starting a drag, checks if cursor is in the titlebar area
       - Titlebar: Full width minus 35px (close button), top 30px height
    3. If dragging, moves the window to follow the cursor
       - Calculates delta from drag start position
       - Applies delta to window's original position
    
    Uses Win32 API for reliable cursor position and window movement.
    """
    # Skip if we don't have a valid window handle
    if not drag_state["hwnd"]:
        return
    
    # Check if left mouse button is currently held down
    is_mouse_down = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000
    
    if is_mouse_down:
        # Get current cursor position (screen coordinates)
        cursor_x, cursor_y = win32api.GetCursorPos()
        
        if not drag_state["is_dragging"]:
            # Not currently dragging - check if we should start
            _try_start_drag(cursor_x, cursor_y)
        else:
            # Currently dragging - update window position
            _continue_drag(cursor_x, cursor_y)
    else:
        # Mouse released - stop dragging
        drag_state["is_dragging"] = False


def _try_start_drag(cursor_x, cursor_y):
    """
    Check if cursor is in titlebar and start dragging if so.
    
    Args:
        cursor_x: Current cursor X position (screen coordinates)
        cursor_y: Current cursor Y position (screen coordinates)
    """
    # Get current window rectangle
    window_rect = win32gui.GetWindowRect(drag_state["hwnd"])
    win_left, win_top, win_right, win_bottom = window_rect
    
    # Define titlebar hit area:
    # - Full width minus 35px on right (to exclude close button)
    # - Only top TITLEBAR_HEIGHT pixels
    is_in_titlebar_x = win_left <= cursor_x <= win_right - 35
    is_in_titlebar_y = win_top <= cursor_y <= win_top + TITLEBAR_HEIGHT
    
    if is_in_titlebar_x and is_in_titlebar_y:
        # Start dragging - save initial positions
        drag_state["is_dragging"] = True
        drag_state["start_mouse_x"] = cursor_x
        drag_state["start_mouse_y"] = cursor_y
        drag_state["start_window_x"] = win_left
        drag_state["start_window_y"] = win_top


def _continue_drag(cursor_x, cursor_y):
    """
    Move window to follow cursor during drag, constrained to CS2 window bounds (cheat only).
    
    Args:
        cursor_x: Current cursor X position (screen coordinates)
        cursor_y: Current cursor Y position (screen coordinates)
    """
    # Calculate how far the mouse has moved since drag started
    delta_x = cursor_x - drag_state["start_mouse_x"]
    delta_y = cursor_y - drag_state["start_mouse_y"]
    
    # Calculate new window position
    new_x = drag_state["start_window_x"] + delta_x
    new_y = drag_state["start_window_y"] + delta_y
    
    # Only constrain to CS2 bounds for cheat window, not loader
    if app_state.get("current_window") == "cheat":
        # Get screen bounds to constrain window position
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        # Get current window dimensions
        current_width = Active_Config.get("window_width", WINDOW_WIDTH)
        current_height = Active_Config.get("window_height", WINDOW_HEIGHT)
        
        # Clamp the window position within screen bounds
        new_x = max(0, min(new_x, screen_width - current_width))
        new_y = max(0, min(new_y, screen_height - current_height))
    
    # Move window (SWP_NOSIZE = don't change size, SWP_NOZORDER = don't change Z-order)
    win32gui.SetWindowPos(
        drag_state["hwnd"], 
        None, 
        new_x, new_y, 
        0, 0,
        win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
    )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
# General-purpose helper functions: remote data fetching, window styling,
# and Win32 API wrappers.
# =============================================================================

def get_app_title():
    """
    Fetch application title from remote GitHub source.
    
    Returns:
        str: The fetched title, or FALLBACK_TITLE if fetch fails
    """
    try:
        response = urllib.request.urlopen(TITLE_URL, timeout=5)
        return response.read().decode('utf-8').strip()
    except Exception:
        # Network error, timeout, or invalid response - use fallback
        return FALLBACK_TITLE


def get_cheat_status():
    """
    Fetch cheat status from remote GitHub source.
    
    Returns:
        str: The fetched status text, or error message if fetch fails
    """
    try:
        response = urllib.request.urlopen(STATUS_URL, timeout=5)
        return response.read().decode('utf-8').strip()
    except Exception as e:
        return f"Error loading status: {str(e)}"


def get_cheat_version():
    """
    Fetch cheat version from remote GitHub source.
    
    Returns:
        str: The fetched version text, or error message if fetch fails
    """
    try:
        response = urllib.request.urlopen(VERSION_URL, timeout=5)
        return response.read().decode('utf-8').strip()
    except Exception as e:
        return f"Error loading version: {str(e)}"


def get_offsets_last_update():
    """
    Fetch the last update time of the offsets GitHub repository.
    
    Returns:
        str: Formatted date/time string, or error message if fetch fails
    """
    try:
        # GitHub API endpoint for repository commits
        api_url = "https://api.github.com/repos/popsiclez/offsets/commits?per_page=1"
        
        # Create request with User-Agent header (required by GitHub API)
        req = urllib.request.Request(api_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if data and len(data) > 0:
            # Get commit date from first (most recent) commit
            commit_date_str = data[0]['commit']['committer']['date']
            # Parse ISO 8601 format: 2025-12-08T10:30:45Z
            from datetime import datetime
            commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ')
            # Format as readable string
            return commit_date.strftime('%B %d, %Y at %I:%M %p UTC')
        else:
            return "Unknown"
    except Exception as e:
        return f"Error: {str(e)}"


def hide_from_taskbar(hwnd):
    """
    Hide window from taskbar and Alt+Tab using Win32 extended styles.
    
    This modifies the window's extended style flags:
    - Add WS_EX_TOOLWINDOW (0x00000080): Marks as "tool window"
      Tool windows don't appear in taskbar or Alt+Tab switcher
    - Remove WS_EX_APPWINDOW (0x00040000): Prevents forcing onto taskbar
      Normal windows with this flag always appear in taskbar
    
    Use case: Keep cheat window hidden from casual observation.
    User can still access it via the menu toggle keybind.
    
    Args:
        hwnd: Win32 window handle (HWND)
    """
    try:
        # Get current extended style
        current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        
        # Modify style: add TOOLWINDOW, remove APPWINDOW
        new_style = (current_style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
        
        # Apply new style
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
    except Exception:
        pass  # Silently fail - window will just appear in taskbar


def enable_rounded_corners(hwnd):
    """
    Enable rounded corners on Windows 11+.
    
    Uses the DWM (Desktop Window Manager) API to request rounded corners.
    This API only exists on Windows 11 Build 22000+, so we silently fail
    on older Windows versions.
    
    Args:
        hwnd: Win32 window handle
    """
    try:
        preference = ctypes.c_int(DWMWCP_ROUND)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(preference),
            ctypes.sizeof(preference)
        )
    except Exception:
        # Silently fail on Windows 10 or if DWM API is unavailable
        # Window will simply have square corners
        pass


def disable_rounded_corners(hwnd):
    """
    Disable rounded corners (use default square corners).
    
    Sets the corner preference to default/square corners.
    
    Args:
        hwnd: Win32 window handle
    """
    try:
        # DWMWCP_DEFAULT (0) = let system decide (usually square)
        # DWMWCP_DONOTROUND (1) = explicitly square corners
        preference = ctypes.c_int(1)  # Force square corners
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(preference),
            ctypes.sizeof(preference)
        )
    except Exception:
        # Silently fail on Windows 10 or if DWM API is unavailable
        pass


def apply_menu_transparency(alpha):
    """
    Apply transparency to the menu window.
    
    Uses Win32 layered window API to set the window alpha.
    The window must already have WS_EX_LAYERED style applied.
    
    Args:
        alpha: Transparency value (0-255, 255 = opaque)
    """
    try:
        # Use stored window handle if available
        hwnd = drag_state.get("hwnd")
        if not hwnd:
            # Fallback: find the cheat window by title
            hwnd = win32gui.FindWindow(None, FALLBACK_TITLE)
            if not hwnd:
                # Try alternative titles
                for title in [TITLE_URL, "CS2 Cheat"]:
                    hwnd = win32gui.FindWindow(None, title)
                    if hwnd:
                        break
        
        if hwnd:
            # Ensure window has layered style
            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            if not (current_style & WS_EX_LAYERED):
                new_style = current_style | WS_EX_LAYERED
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            
            # Set layered window attributes for transparency
            # LWA_ALPHA = 0x2 (use alpha for entire window)
            ctypes.windll.user32.SetLayeredWindowAttributes(
                hwnd,
                0,  # crKey (not used when LWA_ALPHA)
                alpha,  # bAlpha (0-255)
                0x2  # dwFlags (LWA_ALPHA)
            )
    except Exception as e:
        debug_log(f"Failed to apply menu transparency: {e}", "ERROR")


# =============================================================================
# UI COMPONENTS
# =============================================================================
# DearPyGui UI component creation functions.
# Each function creates a tab or window section with widgets (buttons, checkboxes, etc.)
# =============================================================================

def create_titlebar(title, window_type="loader"):
    """
    Create custom draggable titlebar with title text and optional close button.
    
    Layout uses a table for reliable positioning:
    - Column 1 (stretch): Title text, takes remaining space
    - Column 2 (fixed): Close button, fixed width (only for loader)
    
    Args:
        title: Text to display in the titlebar
        window_type: "loader" or "cheat" - cheat window has no close button
    """
    with dpg.child_window(
        height=TITLEBAR_HEIGHT, 
        no_scrollbar=True, 
        tag="titlebar", 
        border=False
    ):
        # Use table for layout - more reliable than spacers
        with dpg.table(
            header_row=False, 
            borders_innerH=False, 
            borders_innerV=False,
            borders_outerH=False, 
            borders_outerV=False, 
            pad_outerX=False
        ):
            # Define columns
            dpg.add_table_column(width_stretch=True)   # Title (flexible width)
            if window_type == "loader":
                dpg.add_table_column(width_fixed=True, init_width_or_weight=28)  # Button (fixed)
            
            with dpg.table_row():
                # Title text
                dpg.add_text(title, color=(255, 255, 255))
                
                # Close button (only for loader window)
                if window_type == "loader":
                    dpg.add_button(
                        label="X", 
                        width=25, 
                        height=TITLEBAR_HEIGHT - 6,
                        callback=on_close_clicked, 
                        tag="close_btn"
                    )


def create_settings_tab():
    """
    Create the Loader tab content.
    """
    with dpg.tab(label="Loader"):
        # Get show_tooltips setting
        show_tips = Active_Config.get("show_tooltips", True)
        
        # Debug tab visibility option
        dpg.add_checkbox(label="Show Debug Tab", tag="chk_show_debug_tab", default_value=True)
        with dpg.tooltip("chk_show_debug_tab", tag="tooltip_show_debug_tab", show=show_tips):
            dpg.add_text("If enabled, Debug tab will be visible in the cheat menu")
        ALL_TOOLTIP_TAGS.append("tooltip_show_debug_tab")
        
        # Show tooltips option
        dpg.add_checkbox(
            label="Show Tooltips",
            tag="chk_show_tooltips",
            default_value=show_tips,
            callback=on_show_tooltips_toggle
        )
        with dpg.tooltip("chk_show_tooltips", tag="tooltip_show_tooltips", show=show_tips):
            dpg.add_text("Show helpful tooltips when hovering over options")
        ALL_TOOLTIP_TAGS.append("tooltip_show_tooltips")
        
        # Local offsets options
        dpg.add_checkbox(
            label="Use Local Offsets", 
            tag="chk_use_local_offsets",
            callback=on_use_local_offsets_changed
        )
        with dpg.tooltip("chk_use_local_offsets", tag="tooltip_use_local_offsets", show=show_tips):
            dpg.add_text("-Creates offsets in local temp directory")
            dpg.add_text("-Allows cheat to genuinely function without updating")
        ALL_TOOLTIP_TAGS.append("tooltip_use_local_offsets")
        
        dpg.add_button(
            label="Create Offsets", 
            tag="btn_create_offsets",
            callback=on_create_offsets_clicked,
            show=False  # Hidden by default
        )
        
        dpg.add_separator()
        
        # Check cheat status and show appropriate UI
        status_text = get_cheat_status()
        if status_text.lower() == "offline":
            # Show offline message instead of Launch button
            dpg.add_text("Cheat is currently offline, try again later.", color=(255, 0, 0), tag="txt_offline_message")
            
            # Bypass password system
            dpg.add_spacer(height=UI_SPACING_SMALL)
            dpg.add_text("Enter bypass password:", color=(255, 255, 255), tag="txt_bypass_label")
            dpg.add_input_text(tag="txt_bypass_password", password=True, width=200, hint="Password")
            dpg.add_button(label="Enter", callback=on_bypass_password_entered, tag="btn_bypass_enter")
            
            # Hidden launch button (shown when password is correct)
            dpg.add_button(label="Launch", callback=on_test_clicked, tag="btn_launch", show=False)
        else:
            # Launch button (only shown if cheat is online)
            dpg.add_button(label="Launch", callback=on_test_clicked, tag="btn_launch")
        
        # Progress status text (hidden by default)
        dpg.add_text("", tag="progress_status_text", show=False)
        
        # Progress bar (hidden by default)
        dpg.add_progress_bar(
            default_value=0.0,
            width=400,
            tag="progress_launch",
            show=False
        )


def create_info_tab():
    """
    Create the Info tab content.
    """
    with dpg.tab(label="Info"):
        # Fetch and display cheat status
        status_text = get_cheat_status()
        dpg.add_text(f"Cheat Status: {status_text}")
        
        # Fetch and display cheat version
        version_text = get_cheat_version()
        dpg.add_text(f"Cheat Version: V{version_text}")
        
        # Fetch and display offsets last update time
        last_update = get_offsets_last_update()
        dpg.add_text(f"Offsets Last Updated: {last_update}")


def on_esp_toggle(sender, value):
    """Handle ESP enable/disable toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["esp_enabled"] = value
        Active_Config["esp_enabled"] = value
        save_settings()
        debug_log(f"ESP {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_box_esp_toggle(sender, value):
    """Handle Box ESP toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["box_esp"] = value
        Active_Config["box_esp"] = value
        save_settings()
        debug_log(f"Box ESP {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_line_esp_toggle(sender, value):
    """Handle Line ESP toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["line_esp"] = value
        Active_Config["line_esp"] = value
        save_settings()
        debug_log(f"Line ESP {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_skeleton_esp_toggle(sender, value):
    """Handle Skeleton ESP toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["skeleton_esp"] = value
        Active_Config["skeleton_esp"] = value
        save_settings()
        debug_log(f"Skeleton ESP {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_name_esp_toggle(sender, value):
    """Handle Name ESP toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["name_esp"] = value
        Active_Config["name_esp"] = value
        save_settings()
        debug_log(f"Name ESP {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_distance_esp_toggle(sender, value):
    """Handle Distance ESP toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["distance_esp"] = value
        Active_Config["distance_esp"] = value
        save_settings()
        debug_log(f"Distance ESP {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_weapon_esp_toggle(sender, value):
    """Handle Weapon ESP toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["weapon_esp"] = value
        Active_Config["weapon_esp"] = value
        save_settings()
        debug_log(f"Weapon ESP {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_hide_unknown_weapons_toggle(sender, value):
    """Handle Hide Unknown Weapons toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["hide_unknown_weapons"] = value
        Active_Config["hide_unknown_weapons"] = value
        save_settings()
        debug_log(f"Hide unknown weapons {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_health_bar_toggle(sender, value):
    """Handle Health Bar toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["health_bar"] = value
        Active_Config["health_bar"] = value
        save_settings()
        debug_log(f"Health Bar {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_armor_bar_toggle(sender, value):
    """Handle Armor Bar toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["armor_bar"] = value
        Active_Config["armor_bar"] = value
        save_settings()
        debug_log(f"Armor Bar {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_head_dot_toggle(sender, value):
    """Handle Head Dot toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["head_dot"] = value
        Active_Config["head_dot"] = value
        save_settings()
        debug_log(f"Head Dot {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_bomb_esp_toggle(sender, value):
    """Handle Bomb ESP toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["bomb_esp"] = value
        Active_Config["bomb_esp"] = value
        save_settings()
        debug_log(f"Bomb ESP {'enabled' if value else 'disabled'}", "INFO")


def on_footstep_esp_toggle(sender, value):
    """Handle Footstep ESP toggle."""
    global footstep_esp_cache
    if esp_overlay["settings"]:
        esp_overlay["settings"]["footstep_esp"] = value
        Active_Config["footstep_esp"] = value
        save_settings()
        # Clear footstep ESP cache when toggling off
        if not value:
            footstep_esp_cache["ring_cache"].clear()
            footstep_esp_cache["last_velocity"].clear()
            footstep_esp_cache["last_origin"].clear()
        debug_log(f"Footstep ESP {'enabled' if value else 'disabled'}", "INFO")


def on_spotted_esp_toggle(sender, value):
    """Handle Spotted ESP toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["spotted_esp"] = value
        Active_Config["spotted_esp"] = value
        save_settings()
        debug_log(f"Spotted ESP {'enabled' if value else 'disabled'}", "INFO")


def on_hide_spotted_players_toggle(sender, value):
    """Handle Hide Spotted Players toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["hide_spotted_players"] = value
        Active_Config["hide_spotted_players"] = value
        save_settings()
        debug_log(f"Hide spotted players {'enabled' if value else 'disabled'}", "INFO")


def on_custom_crosshair_toggle(sender, value):
    """Handle Custom Crosshair toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["custom_crosshair"] = value
        Active_Config["custom_crosshair"] = value
        save_settings()
        debug_log(f"Custom Crosshair {'enabled' if value else 'disabled'}", "INFO")


def on_targeting_type_change(sender, value):
    """Handle targeting type dropdown change."""
    if esp_overlay["settings"]:
        # "Enemies Only" = 0, "All Players" = 1
        targeting_type = 0 if value == "Enemies Only" else 1
        esp_overlay["settings"]["targeting_type"] = targeting_type
        Active_Config["targeting_type"] = targeting_type
        save_settings()
        debug_log(f"Targeting type changed to: {value}", "INFO")


def on_lines_position_change(sender, value):
    """Handle snap lines position change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["lines_position"] = value
    Active_Config["lines_position"] = value
    save_settings()
    debug_log(f"Lines position changed to: {value}", "INFO")
    update_esp_preview()


def on_antialiasing_change(sender, value):
    """Handle antialiasing mode change."""
    Active_Config["antialiasing"] = value
    save_settings()
    debug_log(f"Antialiasing changed to: {value}", "INFO")
    
    # Auto-restart ESP overlay to apply new antialiasing setting
    if esp_overlay["running"]:
        debug_log("Restarting ESP overlay to apply antialiasing...", "INFO")
        stop_esp_overlay()
        time.sleep(0.5)  # Brief delay to ensure clean shutdown
        start_esp_overlay()
        debug_log("ESP overlay restarted with new antialiasing", "SUCCESS")


def on_healthbar_type_change(sender, value):
    """Handle healthbar type change (Vertical/Horizontal)."""
    Active_Config["healthbar_type"] = value
    if esp_overlay["settings"]:
        esp_overlay["settings"]["healthbar_type"] = value
    save_settings()
    debug_log(f"Healthbar type changed to: {value}", "INFO")
    update_esp_preview()


def on_box_type_change(sender, value):
    """Handle box type change (2D/3D)."""
    Active_Config["box_type"] = value
    if esp_overlay["settings"]:
        esp_overlay["settings"]["box_type"] = value
    save_settings()
    debug_log(f"Box type changed to: {value}", "INFO")
    update_esp_preview()


def on_box_thickness_change(sender, value):
    """Handle box thickness slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["box_thickness"] = value
    Active_Config["box_thickness"] = value
    save_settings()
    debug_log(f"Box thickness changed to: {value}", "INFO")
    update_esp_preview()


def on_snapline_thickness_change(sender, value):
    """Handle snapline thickness slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["snapline_thickness"] = value
    Active_Config["snapline_thickness"] = value
    save_settings()
    debug_log(f"Snapline thickness changed to: {value}", "INFO")
    update_esp_preview()


def on_skeleton_thickness_change(sender, value):
    """Handle skeleton thickness slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["skeleton_thickness"] = value
    Active_Config["skeleton_thickness"] = value
    save_settings()
    debug_log(f"Skeleton thickness changed to: {value}", "INFO")
    update_esp_preview()


def on_custom_crosshair_scale_change(sender, value):
    """Handle custom crosshair scale slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["custom_crosshair_scale"] = value
    Active_Config["custom_crosshair_scale"] = value
    save_settings()
    debug_log(f"Custom crosshair scale changed to: {value}", "INFO")


def on_custom_crosshair_thickness_change(sender, value):
    """Handle custom crosshair thickness slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["custom_crosshair_thickness"] = value
    Active_Config["custom_crosshair_thickness"] = value
    save_settings()
    debug_log(f"Custom crosshair thickness changed to: {value}", "INFO")


def on_custom_crosshair_color_change(sender, value):
    """Handle custom crosshair color picker change."""
    # Convert DearPyGui color format to RGB tuple
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        rgb_color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    else:
        rgb_color = (255, 255, 255)  # Default to white
    
    if esp_overlay["settings"]:
        esp_overlay["settings"]["custom_crosshair_color"] = rgb_color
    Active_Config["custom_crosshair_color"] = rgb_color
    save_settings()
    debug_log(f"Custom crosshair color changed to: {rgb_color}", "INFO")


def on_custom_crosshair_shape_change(sender, value):
    """Handle custom crosshair shape dropdown change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["custom_crosshair_shape"] = value
    Active_Config["custom_crosshair_shape"] = value
    save_settings()
    debug_log(f"Custom crosshair shape changed to: {value}", "INFO")


def on_esp_distance_filter_toggle(sender, value):
    """Handle ESP distance filter toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["esp_distance_filter_enabled"] = value
    Active_Config["esp_distance_filter_enabled"] = value
    save_settings()
    
    # Show/hide the filter controls based on toggle state
    dpg.configure_item("combo_esp_distance_filter_type", show=value)
    dpg.configure_item("slider_esp_distance_filter_distance", show=value)
    dpg.configure_item("combo_esp_distance_filter_mode", show=value)
    
    debug_log(f"ESP distance filter {'enabled' if value else 'disabled'}", "INFO")


def on_esp_distance_filter_type_change(sender, value):
    """Handle ESP distance filter type dropdown change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["esp_distance_filter_type"] = value
    Active_Config["esp_distance_filter_type"] = value
    save_settings()
    debug_log(f"ESP distance filter type changed to: {value}", "INFO")


def on_esp_distance_filter_distance_change(sender, value):
    """Handle ESP distance filter distance slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["esp_distance_filter_distance"] = value
    Active_Config["esp_distance_filter_distance"] = value
    save_settings()
    debug_log(f"ESP distance filter distance changed to: {value}", "INFO")


def on_esp_distance_filter_mode_change(sender, value):
    """Handle ESP distance filter mode dropdown change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["esp_distance_filter_mode"] = value
    Active_Config["esp_distance_filter_mode"] = value
    save_settings()
    debug_log(f"ESP distance filter mode changed to: {value}", "INFO")


# =============================================================================
# RADAR CALLBACKS
# =============================================================================

def on_radar_enabled_toggle(sender, value):
    """Handle radar enabled toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_enabled"] = value
    Active_Config["radar_enabled"] = value
    save_settings()
    debug_log(f"Radar {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_radar_size_change(sender, value):
    """Handle radar size slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_size"] = value
    Active_Config["radar_size"] = value
    save_settings()
    debug_log(f"Radar size changed to: {value}", "INFO")


def on_radar_scale_change(sender, value):
    """Handle radar scale slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_scale"] = value
    Active_Config["radar_scale"] = value
    save_settings()
    debug_log(f"Radar scale changed to: {value}", "INFO")


def on_radar_opacity_change(sender, value):
    """Handle radar opacity slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_opacity"] = value
    Active_Config["radar_opacity"] = value
    save_settings()
    debug_log(f"Radar opacity changed to: {value}", "INFO")


def on_radar_position_change(sender, value):
    """Handle radar position dropdown change (deprecated)."""
    pass  # No longer used


def on_radar_x_change(sender, value):
    """Handle radar X position slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_x"] = value
    Active_Config["radar_x"] = value
    save_settings()
    debug_log(f"Radar X position changed to: {value}", "INFO")


def on_radar_y_change(sender, value):
    """Handle radar Y position slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_y"] = value
    Active_Config["radar_y"] = value
    save_settings()
    debug_log(f"Radar Y position changed to: {value}", "INFO")


def on_radar_overlap_game_toggle(sender, value):
    """Handle radar overlap game toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_overlap_game"] = value
    Active_Config["radar_overlap_game"] = value
    
    # When enabling overlap mode, set the locked values
    if value:
        # Lock to game radar position values
        locked_values = {
            "radar_size": 250,
            "radar_opacity": 50,
            "radar_x": -810,
            "radar_y": -390,
            "radar_scale": 15.0
        }
        
        # Update both active config and overlay settings
        for key, locked_value in locked_values.items():
            Active_Config[key] = locked_value
            if esp_overlay["settings"]:
                esp_overlay["settings"][key] = locked_value
        
        # Update UI sliders to show locked values
        if dpg.does_item_exist("slider_radar_size"):
            dpg.set_value("slider_radar_size", 250)
        if dpg.does_item_exist("slider_radar_opacity"):
            dpg.set_value("slider_radar_opacity", 50)
        if dpg.does_item_exist("slider_radar_x"):
            dpg.set_value("slider_radar_x", -810)
        if dpg.does_item_exist("slider_radar_y"):
            dpg.set_value("slider_radar_y", -390)
        if dpg.does_item_exist("slider_radar_scale"):
            dpg.set_value("slider_radar_scale", 15.0)
    
    save_settings()
    debug_log(f"Radar overlap game mode: {'enabled' if value else 'disabled'}", "INFO")


# =============================================================================
# COLOR PICKER CALLBACKS
# =============================================================================

def on_enemy_box_color_change(sender, value):
    """Handle enemy box color change."""
    # Convert from 0-1 float to 0-255 int tuple
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["enemy_box_color"] = color
    Active_Config["enemy_box_color"] = color
    save_settings()
    debug_log(f"Enemy box color changed to: {color}", "INFO")
    update_esp_preview()


def on_team_box_color_change(sender, value):
    """Handle team box color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["team_box_color"] = color
    Active_Config["team_box_color"] = color
    save_settings()
    debug_log(f"Team box color changed to: {color}", "INFO")
    update_esp_preview()


def on_enemy_snapline_color_change(sender, value):
    """Handle enemy snapline color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["enemy_snapline_color"] = color
    Active_Config["enemy_snapline_color"] = color
    save_settings()
    debug_log(f"Enemy snapline color changed to: {color}", "INFO")


def on_team_snapline_color_change(sender, value):
    """Handle team snapline color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["team_snapline_color"] = color
    Active_Config["team_snapline_color"] = color
    save_settings()
    debug_log(f"Team snapline color changed to: {color}", "INFO")


def on_enemy_skeleton_color_change(sender, value):
    """Handle enemy skeleton color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["enemy_skeleton_color"] = color
    Active_Config["enemy_skeleton_color"] = color
    save_settings()
    debug_log(f"Enemy skeleton color changed to: {color}", "INFO")


def on_team_skeleton_color_change(sender, value):
    """Handle team skeleton color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["team_skeleton_color"] = color
    Active_Config["team_skeleton_color"] = color
    save_settings()
    debug_log(f"Team skeleton color changed to: {color}", "INFO")


def on_enemy_head_dot_color_change(sender, value):
    """Handle enemy head dot color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["enemy_head_dot_color"] = color
    Active_Config["enemy_head_dot_color"] = color
    save_settings()
    debug_log(f"Enemy head dot color changed to: {color}", "INFO")


def on_team_head_dot_color_change(sender, value):
    """Handle team head dot color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["team_head_dot_color"] = color
    Active_Config["team_head_dot_color"] = color
    save_settings()
    debug_log(f"Team head dot color changed to: {color}", "INFO")


def on_spotted_color_change(sender, value):
    """Handle spotted indicator color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["spotted_color"] = color
    Active_Config["spotted_color"] = color
    save_settings()
    debug_log(f"Spotted color changed to: {color}", "INFO")


def on_not_spotted_color_change(sender, value):
    """Handle not spotted indicator color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["not_spotted_color"] = color
    Active_Config["not_spotted_color"] = color
    save_settings()
    debug_log(f"Not spotted color changed to: {color}", "INFO")


def on_spotted_text_size_change(sender, value):
    """Handle spotted text size slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["spotted_text_size"] = value
    Active_Config["spotted_text_size"] = value
    save_settings()
    update_esp_preview()  # Update the preview with new text size
    debug_log(f"Spotted text size changed to: {value}", "INFO")


def on_name_text_size_change(sender, value):
    """Handle nickname text size slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["name_text_size"] = value
    Active_Config["name_text_size"] = value
    save_settings()
    update_esp_preview()  # Update the preview with new text size
    debug_log(f"Nickname text size changed to: {value}", "INFO")


def on_weapon_text_size_change(sender, value):
    """Handle weapon text size slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["weapon_text_size"] = value
    Active_Config["weapon_text_size"] = value
    save_settings()
    update_esp_preview()  # Update the preview with new text size
    debug_log(f"Weapon text size changed to: {value}", "INFO")


def on_radar_bg_color_change(sender, value):
    """Handle radar background color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_bg_color"] = color
    Active_Config["radar_bg_color"] = color
    save_settings()
    debug_log(f"Radar background color changed to: {color}", "INFO")


def on_radar_border_color_change(sender, value):
    """Handle radar border color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_border_color"] = color
    Active_Config["radar_border_color"] = color
    save_settings()
    debug_log(f"Radar border color changed to: {color}", "INFO")


def on_radar_crosshair_color_change(sender, value):
    """Handle radar crosshair color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_crosshair_color"] = color
    Active_Config["radar_crosshair_color"] = color
    save_settings()
    debug_log(f"Radar crosshair color changed to: {color}", "INFO")


def on_radar_player_color_change(sender, value):
    """Handle radar player dot color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_player_color"] = color
    Active_Config["radar_player_color"] = color
    save_settings()
    debug_log(f"Radar player color changed to: {color}", "INFO")


def on_radar_enemy_color_change(sender, value):
    """Handle radar enemy dot color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_enemy_color"] = color
    Active_Config["radar_enemy_color"] = color
    save_settings()
    debug_log(f"Radar enemy color changed to: {color}", "INFO")


def on_radar_team_color_change(sender, value):
    """Handle radar team dot color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["radar_team_color"] = color
    Active_Config["radar_team_color"] = color
    save_settings()
    debug_log(f"Radar team color changed to: {color}", "INFO")


# =============================================================================
# AIMBOT CALLBACKS
# =============================================================================

def on_aimbot_toggle(sender, value):
    """Handle aimbot enable/disable toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_enabled"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_enabled"] = value
    Active_Config["aimbot_enabled"] = value
    save_settings()
    debug_log(f"Aimbot {'enabled' if value else 'disabled'}", "INFO")
    update_esp_preview()


def on_aimbot_require_key_toggle(sender, value):
    """Handle aimbot require key toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_require_key"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_require_key"] = value
    Active_Config["aimbot_require_key"] = value
    save_settings()
    debug_log(f"Aimbot require key {'enabled' if value else 'disabled'}", "INFO")
    
    # Show/hide lock target checkbox based on require key setting
    show_tips = Active_Config.get("show_tooltips", True)
    try:
        if value:
            dpg.show_item("chk_aimbot_lock_target")
            if show_tips:
                dpg.show_item("tooltip_aimbot_lock_target")
        else:
            # Hide and disable lock target when require_key is off
            dpg.hide_item("chk_aimbot_lock_target")
            dpg.hide_item("tooltip_aimbot_lock_target")
            dpg.set_value("chk_aimbot_lock_target", False)
            # Also update the settings
            if esp_overlay["settings"]:
                esp_overlay["settings"]["aimbot_lock_target"] = False
            if aimbot_state["settings"]:
                aimbot_state["settings"]["aimbot_lock_target"] = False
            Active_Config["aimbot_lock_target"] = False
    except:
        pass


def on_aimbot_lock_target_toggle(sender, value):
    """Handle aimbot lock target toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_lock_target"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_lock_target"] = value
    Active_Config["aimbot_lock_target"] = value
    # Reset locked entity when setting changes
    aimbot_state["locked_entity"] = None
    save_settings()
    debug_log(f"Aimbot lock target {'enabled' if value else 'disabled'}", "INFO")


def on_aimbot_radius_change(sender, value):
    """Handle aimbot radius change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_radius"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_radius"] = value
    Active_Config["aimbot_radius"] = value
    
    # Update deadzone radius slider max value (must be less than aimbot radius)
    try:
        current_deadzone = Active_Config.get("aimbot_deadzone_radius", 10)
        new_max = max(0, value - 1)  # Deadzone can't be equal to or larger than radius
        dpg.configure_item("slider_aimbot_deadzone_radius", max_value=new_max)
        
        # If current deadzone is now too large, adjust it
        if current_deadzone >= value:
            new_deadzone = min(current_deadzone, new_max)
            Active_Config["aimbot_deadzone_radius"] = new_deadzone
            if esp_overlay["settings"]:
                esp_overlay["settings"]["aimbot_deadzone_radius"] = new_deadzone
            if aimbot_state["settings"]:
                aimbot_state["settings"]["aimbot_deadzone_radius"] = new_deadzone
            dpg.set_value("slider_aimbot_deadzone_radius", new_deadzone)
    except:
        pass
    
    save_settings()
    debug_log(f"Aimbot radius changed to: {value}", "INFO")


def on_aimbot_smoothness_change(sender, value):
    """Handle aimbot smoothness change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_smoothness"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_smoothness"] = value
    Active_Config["aimbot_smoothness"] = value
    save_settings()
    debug_log(f"Aimbot smoothness changed to: {value}", "INFO")


def on_aimbot_show_radius_toggle(sender, value):
    """Handle aimbot show radius toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_show_radius"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_show_radius"] = value
    Active_Config["aimbot_show_radius"] = value
    save_settings()
    debug_log(f"Aimbot radius visibility {'enabled' if value else 'disabled'}", "INFO")


def on_aimbot_spotted_check_toggle(sender, value):
    """Handle aimbot spotted check toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_spotted_check"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_spotted_check"] = value
    Active_Config["aimbot_spotted_check"] = value
    save_settings()
    debug_log(f"Aimbot spotted check {'enabled' if value else 'disabled'}", "INFO")


def on_aimbot_target_bone_change(sender, value):
    """Handle aimbot target bone change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_target_bone"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_target_bone"] = value
    Active_Config["aimbot_target_bone"] = value
    save_settings()
    debug_log(f"Aimbot target bone changed to: {value}", "INFO")


def on_aimbot_movement_type_change(sender, value):
    """Handle aimbot movement type change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_movement_type"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_movement_type"] = value
    Active_Config["aimbot_movement_type"] = value
    save_settings()
    debug_log(f"Aimbot movement type changed to: {value}", "INFO")


def on_aimbot_radius_color_change(sender, value):
    """Handle aimbot radius color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_radius_color"] = color
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_radius_color"] = color
    Active_Config["aimbot_radius_color"] = color
    save_settings()
    debug_log(f"Aimbot radius color changed to: {color}", "INFO")


def on_aimbot_deadzone_color_change(sender, value):
    """Handle aimbot deadzone color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_deadzone_color"] = color
    Active_Config["aimbot_deadzone_color"] = color
    save_settings()
    debug_log(f"Aimbot deadzone color changed to: {color}", "INFO")


def on_aimbot_targeting_radius_color_change(sender, value):
    """Handle aimbot targeting radius color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_targeting_radius_color"] = color
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_targeting_radius_color"] = color
    Active_Config["aimbot_targeting_radius_color"] = color
    save_settings()
    debug_log(f"Aimbot targeting radius color changed to: {color}", "INFO")


def on_aimbot_targeting_deadzone_color_change(sender, value):
    """Handle aimbot targeting deadzone color change."""
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_targeting_deadzone_color"] = color
    Active_Config["aimbot_targeting_deadzone_color"] = color
    save_settings()
    debug_log(f"Aimbot targeting deadzone color changed to: {color}", "INFO")


def on_aimbot_key_button():
    """Handle aimbot key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "aimbot_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_aimbot_cheat", "Press any key...")
    except:
        pass


def on_aimbot_deadzone_toggle(sender, value):
    """Handle aimbot deadzone toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_deadzone_enabled"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_deadzone_enabled"] = value
    Active_Config["aimbot_deadzone_enabled"] = value
    save_settings()
    debug_log(f"Aimbot deadzone {'enabled' if value else 'disabled'}", "INFO")


def on_aimbot_show_deadzone_toggle(sender, value):
    """Handle aimbot show deadzone toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_show_deadzone"] = value
    Active_Config["aimbot_show_deadzone"] = value
    save_settings()
    debug_log(f"Aimbot show deadzone {'enabled' if value else 'disabled'}", "INFO")


def on_aimbot_deadzone_radius_change(sender, value):
    """Handle aimbot deadzone radius change."""
    # Ensure deadzone radius doesn't exceed aimbot radius - 1
    aimbot_radius = Active_Config.get("aimbot_radius", 50)
    if value >= aimbot_radius:
        value = aimbot_radius - 1
        # Update the slider value
        try:
            dpg.set_value("slider_aimbot_deadzone_radius", value)
        except:
            pass
    
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_deadzone_radius"] = value
    if aimbot_state["settings"]:
        aimbot_state["settings"]["aimbot_deadzone_radius"] = value
    Active_Config["aimbot_deadzone_radius"] = value
    save_settings()
    debug_log(f"Aimbot deadzone radius changed to: {value}", "INFO")


def on_aimbot_radius_transparency_change(sender, value):
    """Handle aimbot radius transparency change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_radius_transparency"] = value
    Active_Config["aimbot_radius_transparency"] = value
    save_settings()
    debug_log(f"Aimbot radius transparency changed to: {value}", "INFO")


def on_aimbot_deadzone_transparency_change(sender, value):
    """Handle aimbot deadzone transparency change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_deadzone_transparency"] = value
    Active_Config["aimbot_deadzone_transparency"] = value
    save_settings()
    debug_log(f"Aimbot deadzone transparency changed to: {value}", "INFO")


def on_menu_transparency_change(sender, value):
    """Handle menu transparency change."""
    Active_Config["menu_transparency"] = value
    save_settings()
    apply_menu_transparency(value)
    debug_log(f"Menu transparency changed to: {value}", "INFO")


def on_aimbot_radius_thickness_change(sender, value):
    """Handle aimbot radius thickness change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_radius_thickness"] = value
    Active_Config["aimbot_radius_thickness"] = value
    save_settings()
    debug_log(f"Aimbot radius thickness changed to: {value}", "INFO")


def on_aimbot_deadzone_thickness_change(sender, value):
    """Handle aimbot deadzone thickness change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_deadzone_thickness"] = value
    Active_Config["aimbot_deadzone_thickness"] = value
    save_settings()
    debug_log(f"Aimbot deadzone thickness changed to: {value}", "INFO")


def on_aimbot_snapline_thickness_change(sender, value):
    """Handle aimbot snapline thickness change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_snapline_thickness"] = value
    Active_Config["aimbot_snapline_thickness"] = value
    save_settings()
    debug_log(f"Aimbot snapline thickness changed to: {value}", "INFO")


def on_aimbot_snaplines_toggle(sender, value):
    """Handle aimbot snaplines toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_snaplines"] = value
    Active_Config["aimbot_snaplines"] = value
    save_settings()
    debug_log(f"Aimbot snaplines {'enabled' if value else 'disabled'}", "INFO")


def on_aimbot_snapline_color_change(sender, value):
    """Handle aimbot snapline color change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["aimbot_snapline_color"] = value
    Active_Config["aimbot_snapline_color"] = value
    save_settings()
    debug_log(f"Aimbot snapline color changed to: {value}", "INFO")


# =============================================================================
# TRIGGERBOT CALLBACKS
# =============================================================================

def on_triggerbot_toggle(sender, value):
    """Handle triggerbot enable/disable toggle."""
    if triggerbot_state["settings"]:
        triggerbot_state["settings"]["triggerbot_enabled"] = value
    Active_Config["triggerbot_enabled"] = value
    save_settings()
    debug_log(f"Triggerbot {'enabled' if value else 'disabled'}", "INFO")


def on_triggerbot_first_shot_delay_change(sender, value):
    """Handle triggerbot first shot delay change."""
    if triggerbot_state["settings"]:
        triggerbot_state["settings"]["triggerbot_first_shot_delay"] = value
    Active_Config["triggerbot_first_shot_delay"] = value
    save_settings()
    debug_log(f"Triggerbot first shot delay changed to: {value}ms", "INFO")


def on_triggerbot_between_shots_delay_change(sender, value):
    """Handle triggerbot between shots delay change."""
    if triggerbot_state["settings"]:
        triggerbot_state["settings"]["triggerbot_between_shots_delay"] = value
    Active_Config["triggerbot_between_shots_delay"] = value
    save_settings()
    debug_log(f"Triggerbot between shots delay changed to: {value}ms", "INFO")


def on_triggerbot_burst_mode_toggle(sender, value):
    """Handle triggerbot burst mode toggle."""
    if triggerbot_state["settings"]:
        triggerbot_state["settings"]["triggerbot_burst_mode"] = value
    Active_Config["triggerbot_burst_mode"] = value
    save_settings()
    # Show/hide burst shots slider and tooltip
    show_tips = Active_Config.get("show_tooltips", True)
    try:
        dpg.configure_item("slider_triggerbot_burst_shots", show=value)
        dpg.configure_item("tooltip_triggerbot_burst_shots", show=value and show_tips)
    except:
        pass
    debug_log(f"Triggerbot burst mode {'enabled' if value else 'disabled'}", "INFO")


def on_triggerbot_burst_shots_change(sender, value):
    """Handle triggerbot burst shots change."""
    if triggerbot_state["settings"]:
        triggerbot_state["settings"]["triggerbot_burst_shots"] = value
    Active_Config["triggerbot_burst_shots"] = value
    save_settings()
    debug_log(f"Triggerbot burst shots changed to: {value}", "INFO")


def on_triggerbot_head_only_toggle(sender, value):
    """Handle triggerbot head-only mode toggle."""
    if triggerbot_state["settings"]:
        triggerbot_state["settings"]["triggerbot_head_only"] = value
    Active_Config["triggerbot_head_only"] = value
    save_settings()
    debug_log(f"Triggerbot head-only mode {'enabled' if value else 'disabled'}", "INFO")


def on_triggerbot_key_button():
    """Handle triggerbot key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "triggerbot_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_triggerbot_cheat", "Press any key...")
    except:
        pass


# =============================================================================
# ACS (AUTO CROSSHAIR PLACEMENT) CALLBACKS
# =============================================================================

def on_acs_toggle(sender, value):
    """Handle ACS enable/disable toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["acs_enabled"] = value
    if acs_state["settings"]:
        acs_state["settings"]["acs_enabled"] = value
    Active_Config["acs_enabled"] = value
    save_settings()
    debug_log(f"ACS {'enabled' if value else 'disabled'}", "INFO")


def on_acs_target_bone_change(sender, value):
    """Handle ACS target bone dropdown change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["acs_target_bone"] = value
    if acs_state["settings"]:
        acs_state["settings"]["acs_target_bone"] = value
    Active_Config["acs_target_bone"] = value
    save_settings()
    debug_log(f"ACS target bone changed to: {value}", "INFO")


def on_acs_smoothness_change(sender, value):
    """Handle ACS smoothness slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["acs_smoothness"] = value
    if acs_state["settings"]:
        acs_state["settings"]["acs_smoothness"] = value
    Active_Config["acs_smoothness"] = value
    save_settings()
    debug_log(f"ACS smoothness changed to: {value}", "INFO")


def on_acs_deadzone_change(sender, value):
    """Handle ACS deadzone slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["acs_deadzone"] = value
    if acs_state["settings"]:
        acs_state["settings"]["acs_deadzone"] = value
    Active_Config["acs_deadzone"] = value
    save_settings()
    debug_log(f"ACS deadzone changed to: {value}", "INFO")


def on_acs_draw_deadzone_lines_toggle(sender, value):
    """Handle ACS draw deadzone lines toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["acs_draw_deadzone_lines"] = value
    if acs_state["settings"]:
        acs_state["settings"]["acs_draw_deadzone_lines"] = value
    Active_Config["acs_draw_deadzone_lines"] = value
    save_settings()
    # Show/hide line settings and tooltips based on toggle
    show_tips = Active_Config.get("show_tooltips", True)
    try:
        dpg.configure_item("chk_acs_always_show_deadzone_lines", show=value)
        dpg.configure_item("tooltip_acs_always_show_deadzone_lines", show=value and show_tips)
        # Note: Line width and transparency sliders are now in Appearance tab and always visible
    except:
        pass
    debug_log(f"ACS draw deadzone lines {'enabled' if value else 'disabled'}", "INFO")


def on_acs_always_show_deadzone_lines_toggle(sender, value):
    """Handle ACS always show deadzone lines toggle."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["acs_always_show_deadzone_lines"] = value
    if acs_state["settings"]:
        acs_state["settings"]["acs_always_show_deadzone_lines"] = value
    Active_Config["acs_always_show_deadzone_lines"] = value
    save_settings()
    debug_log(f"ACS always show deadzone lines {'enabled' if value else 'disabled'}", "INFO")


def on_acs_line_width_change(sender, value):
    """Handle ACS line width slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["acs_line_width"] = value
    if acs_state["settings"]:
        acs_state["settings"]["acs_line_width"] = value
    Active_Config["acs_line_width"] = value
    save_settings()
    debug_log(f"ACS line width changed to: {value}", "INFO")


def on_acs_line_transparency_change(sender, value):
    """Handle ACS line transparency slider change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["acs_line_transparency"] = value
    if acs_state["settings"]:
        acs_state["settings"]["acs_line_transparency"] = value
    Active_Config["acs_line_transparency"] = value
    save_settings()
    debug_log(f"ACS line transparency changed to: {value}", "INFO")


def on_acs_line_color_change(sender, value):
    """Handle ACS line color change."""
    # Convert from 0-255 list to tuple
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["acs_line_color"] = color
    if acs_state["settings"]:
        acs_state["settings"]["acs_line_color"] = color
    Active_Config["acs_line_color"] = color
    save_settings()
    debug_log(f"ACS line color changed to: {color}", "INFO")


def on_footstep_esp_color_change(sender, value):
    """Handle footstep ESP color change."""
    # Convert from 0-1 float to 0-255 int tuple
    color = (int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
    if esp_overlay["settings"]:
        esp_overlay["settings"]["footstep_esp_color"] = color
    Active_Config["footstep_esp_color"] = color
    save_settings()
    debug_log(f"Footstep ESP color changed to: {color}", "INFO")
    update_esp_preview()


def on_acs_key_button():
    """Handle ACS key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "acs_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_acs_cheat", "Press any key...")
    except:
        pass


def on_colorway_change(sender, value):
    """Handle colorway dropdown change."""
    Active_Config["menu_colorway"] = value
    save_settings()
    apply_colorway(value)
    debug_log(f"Menu colorway changed to: {value}", "INFO")


def on_font_change(sender, value):
    """Handle font dropdown change."""
    if esp_overlay["settings"]:
        esp_overlay["settings"]["menu_font"] = value
    Active_Config["menu_font"] = value
    save_settings()
    apply_font(value)
    debug_log(f"Menu font changed to: {value}", "INFO")


def on_window_width_change(sender, value):
    """Handle window width slider change."""
    Active_Config["window_width"] = value
    save_settings()
    dpg.configure_viewport(0, width=value)
    
    # Ensure window stays within screen bounds after resize
    import ctypes
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    
    current_pos = dpg.get_viewport_pos()
    current_x, current_y = current_pos
    current_height = Active_Config.get("window_height", WINDOW_HEIGHT)
    
    # Clamp position
    new_x = max(0, min(current_x, screen_width - value))
    new_y = max(0, min(current_y, screen_height - current_height))
    
    if new_x != current_x or new_y != current_y:
        dpg.set_viewport_pos([new_x, new_y])
    
    debug_log(f"Window width changed to: {value}", "INFO")


def on_window_height_change(sender, value):
    """Handle window height slider change."""
    Active_Config["window_height"] = value
    save_settings()
    dpg.configure_viewport(0, height=value)
    
    # Ensure window stays within screen bounds after resize
    import ctypes
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    
    current_pos = dpg.get_viewport_pos()
    current_x, current_y = current_pos
    current_width = Active_Config.get("window_width", WINDOW_WIDTH)
    
    # Clamp position
    new_x = max(0, min(current_x, screen_width - current_width))
    new_y = max(0, min(current_y, screen_height - value))
    
    if new_x != current_x or new_y != current_y:
        dpg.set_viewport_pos([new_x, new_y])
    
    debug_log(f"Window height changed to: {value}", "INFO")


def setup_fonts():
    """
    Set up font registry with available fonts.
    Must be called after dpg.create_context() and before dpg.setup_dearpygui().
    """
    global loaded_fonts
    
    with dpg.font_registry():
        # Load each available font
        for font_name, font_path in MENU_FONTS.items():
            if font_path is None:
                # Default font - use DearPyGui's built-in
                continue
            
            try:
                if os.path.exists(font_path):
                    font_tag = f"font_{font_name.replace(' ', '_').lower()}"
                    loaded_fonts[font_name] = dpg.add_font(font_path, 16, tag=font_tag)
                    debug_log(f"Loaded font: {font_name}", "INFO")
                else:
                    debug_log(f"Font file not found: {font_path}", "WARNING")
            except Exception as e:
                debug_log(f"Failed to load font {font_name}: {e}", "WARNING")


def apply_font(font_name):
    """
    Apply a font to the DearPyGui interface.
    
    Args:
        font_name: Name of the font from MENU_FONTS
    """
    try:
        # First unbind any current font to reset
        dpg.bind_font(0)
    except:
        pass
    
    if font_name == "Default" or font_name not in loaded_fonts:
        # Keep default font (already unbound above)
        debug_log(f"Applied default font", "INFO")
    else:
        try:
            # Now bind the new font
            dpg.bind_font(loaded_fonts[font_name])
            debug_log(f"Applied font: {font_name}", "INFO")
        except Exception as e:
            debug_log(f"Failed to apply font {font_name}: {e}", "WARNING")


def apply_colorway(colorway_name):
    """
    Apply a colorway preset to the DearPyGui theme.
    
    Args:
        colorway_name: Name of the colorway from UI_COLORWAYS
    """
    if colorway_name not in UI_COLORWAYS:
        debug_log(f"Colorway '{colorway_name}' not found, using Default", "WARNING")
        colorway_name = "Default"
    
    colors = UI_COLORWAYS[colorway_name]
    
    # Delete existing theme if it exists
    try:
        if dpg.does_item_exist("global_theme"):
            dpg.delete_item("global_theme")
    except:
        pass
    
    # Create new theme with colorway colors
    with dpg.theme(tag="global_theme"):
        with dpg.theme_component(dpg.mvAll):
            # Window background
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, colors["window_bg"])
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, colors["window_bg"])
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, colors["window_bg"])
            
            # Title bar
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, colors["title_bg"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, colors["title_bg_active"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, colors["title_bg"])
            
            # Frame (input boxes, etc.)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, colors["frame_bg"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, colors["frame_bg_hovered"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, colors["frame_bg_active"])
            
            # Buttons
            dpg.add_theme_color(dpg.mvThemeCol_Button, colors["button"])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, colors["button_hovered"])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, colors["button_active"])
            
            # Tabs
            dpg.add_theme_color(dpg.mvThemeCol_Tab, colors["tab"])
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, colors["tab_hovered"])
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, colors["tab_active"])
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, colors["tab"])
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, colors["tab_active"])
            
            # Text
            dpg.add_theme_color(dpg.mvThemeCol_Text, colors["text"])
            
            # Checkmark
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, colors["check_mark"])
            
            # Sliders
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, colors["slider_grab"])
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, colors["slider_grab"])
            
            # Headers (collapsing headers, tree nodes)
            dpg.add_theme_color(dpg.mvThemeCol_Header, colors["header"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, colors["header_hovered"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, colors["header_active"])
            
            # Separator
            dpg.add_theme_color(dpg.mvThemeCol_Separator, colors["frame_bg"])
            
            # Scrollbar
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, colors["window_bg"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, colors["button"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, colors["button_hovered"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, colors["button_active"])
            
            # Border
            dpg.add_theme_color(dpg.mvThemeCol_Border, colors["frame_bg"])
    
    # Bind the theme globally
    dpg.bind_theme("global_theme")


def apply_loader_theme():
    """
    Apply a fixed dark gray + white theme for the loader window.
    This theme cannot be changed by the user.
    """
    # Dark gray background with white elements
    dark_gray = (25, 25, 25, 255)
    medium_gray = (50, 50, 50, 255)
    light_gray = (60, 60, 60, 255)
    highlight_gray = (100, 100, 100, 255)
    white = (255, 255, 255, 255)
    white_dim = (200, 200, 200, 255)
    
    # Delete existing theme if it exists
    try:
        if dpg.does_item_exist("loader_theme"):
            dpg.delete_item("loader_theme")
    except:
        pass
    
    # Create the loader theme
    with dpg.theme(tag="loader_theme"):
        with dpg.theme_component(dpg.mvAll):
            # Window background
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, dark_gray)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, dark_gray)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, dark_gray)
            
            # Title bar
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, medium_gray)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, light_gray)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, medium_gray)
            
            # Frame (input boxes, etc.)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, medium_gray)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, light_gray)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, highlight_gray)
            
            # Buttons
            dpg.add_theme_color(dpg.mvThemeCol_Button, medium_gray)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, light_gray)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, highlight_gray)
            
            # Tabs
            dpg.add_theme_color(dpg.mvThemeCol_Tab, medium_gray)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, light_gray)
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, highlight_gray)
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, medium_gray)
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, highlight_gray)
            
            # Text - white
            dpg.add_theme_color(dpg.mvThemeCol_Text, white)
            
            # Checkmark - white
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, white)
            
            # Sliders - white
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, white_dim)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, white)
            
            # Headers (collapsing headers, tree nodes)
            dpg.add_theme_color(dpg.mvThemeCol_Header, medium_gray)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, light_gray)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, highlight_gray)
            
            # Separator
            dpg.add_theme_color(dpg.mvThemeCol_Separator, light_gray)
            
            # Scrollbar
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, dark_gray)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, medium_gray)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, light_gray)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, highlight_gray)
            
            # Border
            dpg.add_theme_color(dpg.mvThemeCol_Border, light_gray)
            
            # Progress bar - white fill
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, white)
    
    # Bind the theme globally
    dpg.bind_theme("loader_theme")


def on_menu_toggle_key_button():
    """Handle menu toggle key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "menu_toggle_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_menu_toggle_cheat", "Press any key...")
    except:
        pass


def on_esp_toggle_key_button():
    """Handle ESP toggle key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "esp_toggle_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_esp_toggle_cheat", "Press any key...")
    except:
        pass


def on_exit_key_button():
    """Handle exit key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "exit_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_exit_cheat", "Press any key...")
    except:
        pass


def on_aimbot_toggle_key_button():
    """Handle aimbot toggle key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "aimbot_toggle_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_aimbot_toggle_cheat", "Press any key...")
    except:
        pass


def on_head_only_toggle_key_button():
    """Handle head-only toggle key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "head_only_toggle_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_head_only_toggle_cheat", "Press any key...")
    except:
        pass


def on_rcs_toggle_key_button():
    """Handle RCS toggle key bind button click."""
    global keybind_listener
    keybind_listener["listening"] = True
    keybind_listener["target"] = "rcs_toggle_key"
    # Update button text to show we're listening
    try:
        dpg.set_item_label("btn_bind_rcs_toggle_cheat", "Press any key...")
    except:
        pass


def update_esp_preview():
    """
    Update the ESP preview canvas with current settings.
    Draws simplified ESP elements to show what they look like.
    """
    try:
        # Clear the canvas
        dpg.delete_item("esp_preview_canvas", children_only=True)
        
        # Get current ESP settings
        settings = Active_Config.copy()
        
        # Only draw if ESP is enabled
        if not settings.get("esp_enabled", True):
            # Draw disabled message
            dpg.draw_text((200, 150), "ESP Disabled", color=(128, 128, 128), size=20, parent="esp_preview_canvas")
            return
        
        canvas_width = 400
        canvas_height = 300
        
        # Draw background
        dpg.draw_rectangle((0, 0), (canvas_width, canvas_height), color=(20, 20, 20), fill=True, parent="esp_preview_canvas")
        
        # Draw some sample ESP elements
        # Sample enemy player (red) - positioned more realistically
        enemy_x, enemy_y = 120, 100  # Left side, aligned
        draw_preview_player(enemy_x, enemy_y, "Enemy", settings, is_enemy=True)
        
        # Sample team player (green) - positioned on right side, aligned
        team_x, team_y = 280, 100  # Right side, same height as enemy
        draw_preview_player(team_x, team_y, "Teammate", settings, is_enemy=False)
        
        # Draw radar preview if enabled (top-right corner)
        if settings.get("radar_enabled", False):
            draw_preview_radar(settings)
            
        # Aimbot FOV preview removed - only shown in actual game overlay
            
    except Exception as e:
        debug_log(f"Error updating ESP preview: {str(e)}", "ERROR")


def draw_preview_player(x, y, name, settings, is_enemy=True):
    """
    Draw a preview ESP player at the given position.
    More accurate to real ESP rendering.
    """
    try:
        # Get colors based on team
        if is_enemy:
            box_color = settings.get('enemy_box_color', (196, 30, 58))
            snapline_color = settings.get('enemy_snapline_color', (196, 30, 58))
            skeleton_color = settings.get('enemy_skeleton_color', (255, 255, 255))
            head_dot_color = settings.get('enemy_head_dot_color', (255, 255, 0))
        else:
            box_color = settings.get('team_box_color', (71, 167, 106))
            snapline_color = settings.get('team_snapline_color', (71, 167, 106))
            skeleton_color = settings.get('team_skeleton_color', (255, 255, 255))
            head_dot_color = settings.get('team_head_dot_color', (255, 255, 0))
        
        # Convert colors to Dear PyGui format (0-255)
        box_color = tuple(int(c) for c in box_color)
        snapline_color = tuple(int(c) for c in snapline_color)
        skeleton_color = tuple(int(c) for c in skeleton_color)
        head_dot_color = tuple(int(c) for c in head_dot_color)
        
        # Realistic player proportions (based on real ESP calculations)
        # deltaZ represents the screen space distance from head to feet
        deltaZ = 120  # Fixed for preview - represents player height in screen pixels (increased for bigger preview)
        box_width = deltaZ // 2  # Real ESP calculation: box_width = deltaZ // 2
        
        # Player positions (head at top, feet at bottom)
        head_y = y
        feet_y = y + deltaZ
        
        # Box boundaries
        leftX = x - box_width // 2
        rightX = x + box_width // 2
        
        # Draw snaplines first (behind everything else)
        if settings.get('line_esp', True):
            thickness = settings.get('snapline_thickness', 1.5)
            lines_position = settings.get('lines_position', 'Bottom')
            
            if lines_position == 'Top':
                # Line from top center to head
                dpg.draw_line((200, 0), (x, head_y), color=snapline_color, thickness=thickness, parent="esp_preview_canvas")
            else:
                # Line from bottom center to feet
                dpg.draw_line((200, 300), (x, feet_y), color=snapline_color, thickness=thickness, parent="esp_preview_canvas")
        
        # Draw box ESP
        if settings.get('box_esp', True):
            thickness = settings.get('box_thickness', 1.5)
            box_type = settings.get('box_type', '2D')
            
            if box_type == '2D':
                # 2D box - simple rectangle
                dpg.draw_rectangle((leftX, head_y), (rightX, feet_y), 
                                 color=box_color, thickness=thickness, parent="esp_preview_canvas")
            else:
                # 3D box - with depth lines (simplified)
                dpg.draw_rectangle((leftX, head_y), (rightX, feet_y), 
                                 color=box_color, thickness=thickness, parent="esp_preview_canvas")
                # Add depth lines
                depth_offset = 8
                dpg.draw_line((leftX, head_y), (leftX - depth_offset//2, head_y - depth_offset), 
                             color=box_color, thickness=thickness, parent="esp_preview_canvas")
                dpg.draw_line((rightX, head_y), (rightX - depth_offset//2, head_y - depth_offset), 
                             color=box_color, thickness=thickness, parent="esp_preview_canvas")
        
        # Draw health and armor bars
        healthbar_type = settings.get('healthbar_type', 'Vertical Left')
        bar_thickness = 3
        
        # Sample values
        health = 85 if is_enemy else 100
        armor = 50 if is_enemy else 100
        hp_percent = health / 100.0
        armor_percent = armor / 100.0
        
        if settings.get('health_bar', True):
            if healthbar_type == 'Vertical Left':
                # Health bar on the left
                hp_height = int(deltaZ * hp_percent)
                hp_bar_x = leftX - 6
                # Background
                dpg.draw_rectangle((hp_bar_x, head_y), (hp_bar_x + bar_thickness, feet_y), 
                                 color=(64, 64, 64), fill=True, parent="esp_preview_canvas")
                # Health fill
                health_color = (0, 255, 0) if hp_percent > 0.5 else (255, 255, 0) if hp_percent > 0.25 else (255, 0, 0)
                dpg.draw_rectangle((hp_bar_x, feet_y - hp_height), (hp_bar_x + bar_thickness, feet_y), 
                                 color=health_color, fill=True, parent="esp_preview_canvas")
                
                # Armor bar on the right of health bar
                if settings.get('armor_bar', True) and armor > 0:
                    armor_height = int(deltaZ * armor_percent)
                    armor_bar_x = hp_bar_x - 5
                    dpg.draw_rectangle((armor_bar_x, head_y), (armor_bar_x + bar_thickness, feet_y), 
                                     color=(64, 64, 64), fill=True, parent="esp_preview_canvas")
                    dpg.draw_rectangle((armor_bar_x, feet_y - armor_height), (armor_bar_x + bar_thickness, feet_y), 
                                     color=(0, 100, 255), fill=True, parent="esp_preview_canvas")
                                     
            elif healthbar_type == 'Vertical Right':
                # Health bar on the right
                hp_height = int(deltaZ * hp_percent)
                hp_bar_x = rightX + 3
                dpg.draw_rectangle((hp_bar_x, head_y), (hp_bar_x + bar_thickness, feet_y), 
                                 color=(64, 64, 64), fill=True, parent="esp_preview_canvas")
                health_color = (0, 255, 0) if hp_percent > 0.5 else (255, 255, 0) if hp_percent > 0.25 else (255, 0, 0)
                dpg.draw_rectangle((hp_bar_x, feet_y - hp_height), (hp_bar_x + bar_thickness, feet_y), 
                                 color=health_color, fill=True, parent="esp_preview_canvas")
                
                # Armor bar to the right of health bar
                if settings.get('armor_bar', True) and armor > 0:
                    armor_height = int(deltaZ * armor_percent)
                    armor_bar_x = hp_bar_x + 4
                    dpg.draw_rectangle((armor_bar_x, head_y), (armor_bar_x + bar_thickness, feet_y), 
                                     color=(64, 64, 64), fill=True, parent="esp_preview_canvas")
                    dpg.draw_rectangle((armor_bar_x, feet_y - armor_height), (armor_bar_x + bar_thickness, feet_y), 
                                     color=(0, 100, 255), fill=True, parent="esp_preview_canvas")
                                     
            elif healthbar_type == 'Horizontal Above':
                # Health bar above head
                hp_width = int(box_width * hp_percent)
                bar_y = head_y - 7
                dpg.draw_rectangle((leftX, bar_y), (rightX, bar_y + bar_thickness), 
                                 color=(64, 64, 64), fill=True, parent="esp_preview_canvas")
                health_color = (0, 255, 0) if hp_percent > 0.5 else (255, 255, 0) if hp_percent > 0.25 else (255, 0, 0)
                dpg.draw_rectangle((leftX, bar_y), (leftX + hp_width, bar_y + bar_thickness), 
                                 color=health_color, fill=True, parent="esp_preview_canvas")
                
                # Armor bar above health bar
                if settings.get('armor_bar', True) and armor > 0:
                    armor_width = int(box_width * armor_percent)
                    armor_bar_y = bar_y - 4
                    dpg.draw_rectangle((leftX, armor_bar_y), (rightX, armor_bar_y + bar_thickness), 
                                     color=(64, 64, 64), fill=True, parent="esp_preview_canvas")
                    dpg.draw_rectangle((leftX, armor_bar_y), (leftX + armor_width, armor_bar_y + bar_thickness), 
                                     color=(0, 100, 255), fill=True, parent="esp_preview_canvas")
                                     
            elif healthbar_type == 'Horizontal Below':
                # Health bar below feet
                hp_width = int(box_width * hp_percent)
                bar_y = feet_y + 3
                dpg.draw_rectangle((leftX, bar_y), (rightX, bar_y + bar_thickness), 
                                 color=(64, 64, 64), fill=True, parent="esp_preview_canvas")
                health_color = (0, 255, 0) if hp_percent > 0.5 else (255, 255, 0) if hp_percent > 0.25 else (255, 0, 0)
                dpg.draw_rectangle((leftX, bar_y), (leftX + hp_width, bar_y + bar_thickness), 
                                 color=health_color, fill=True, parent="esp_preview_canvas")
                
                # Armor bar below health bar
                if settings.get('armor_bar', True) and armor > 0:
                    armor_width = int(box_width * armor_percent)
                    armor_bar_y = bar_y + 4
                    dpg.draw_rectangle((leftX, armor_bar_y), (rightX, armor_bar_y + bar_thickness), 
                                     color=(64, 64, 64), fill=True, parent="esp_preview_canvas")
                    dpg.draw_rectangle((leftX, armor_bar_y), (leftX + armor_width, armor_bar_y + bar_thickness), 
                                     color=(0, 100, 255), fill=True, parent="esp_preview_canvas")
        
        # Draw skeleton if enabled
        if settings.get('skeleton_esp', True):
            thickness = settings.get('skeleton_thickness', 1.5)
            # More realistic skeleton proportions based on actual bone positions (scaled for bigger preview)
            scale_factor = deltaZ / 80.0  # Scale based on deltaZ
            
            # Head
            head_center = (x, head_y + int(8 * scale_factor))
            dpg.draw_circle(head_center, 6, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            
            # Neck to shoulders
            neck = (x, head_y + int(16 * scale_factor))
            shoulders_left = (x - 12, head_y + int(24 * scale_factor))
            shoulders_right = (x + 12, head_y + int(24 * scale_factor))
            
            # Arms
            elbows_left = (x - 18, head_y + int(40 * scale_factor))
            elbows_right = (x + 18, head_y + int(40 * scale_factor))
            hands_left = (x - 24, head_y + int(56 * scale_factor))
            hands_right = (x + 24, head_y + int(56 * scale_factor))
            
            # Body
            hips_left = (x - 8, head_y + int(56 * scale_factor))
            hips_right = (x + 8, head_y + int(56 * scale_factor))
            
            # Legs
            knees_left = (x - 8, head_y + int(72 * scale_factor))
            knees_right = (x + 8, head_y + int(72 * scale_factor))
            feet_left = (x - 8, feet_y)
            feet_right = (x + 8, feet_y)
            
            # Draw skeleton lines
            # Head to neck
            dpg.draw_line(head_center, neck, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            
            # Neck to shoulders
            dpg.draw_line(neck, shoulders_left, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            dpg.draw_line(neck, shoulders_right, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            
            # Shoulders to elbows
            dpg.draw_line(shoulders_left, elbows_left, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            dpg.draw_line(shoulders_right, elbows_right, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            
            # Elbows to hands
            dpg.draw_line(elbows_left, hands_left, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            dpg.draw_line(elbows_right, hands_right, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            
            # Body - single vertical line for torso
            torso_bottom = (x, head_y + int(56 * scale_factor))  # Center of hips
            dpg.draw_line(neck, torso_bottom, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            dpg.draw_line(hips_left, hips_right, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            
            # Legs
            dpg.draw_line(hips_left, knees_left, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            dpg.draw_line(hips_right, knees_right, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            dpg.draw_line(knees_left, feet_left, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
            dpg.draw_line(knees_right, feet_right, color=skeleton_color, thickness=thickness, parent="esp_preview_canvas")
        
        # Draw head dot if enabled
        if settings.get('head_dot', True):
            # Position at head center
            dpg.draw_circle((x, head_y + int(8 * scale_factor)), 4, color=head_dot_color, fill=True, parent="esp_preview_canvas")
        
        # Calculate text Y offset based on healthbar type (like real ESP)
        healthbar_type = settings.get('healthbar_type', 'Vertical Left')
        scale_factor = deltaZ / 80.0  # Scale factor for bigger preview
        
        # Get text sizes for positioning calculations
        spotted_enabled = settings.get('spotted_esp', True)
        name_enabled = settings.get('name_esp', True)
        distance_enabled = settings.get('distance_esp', True)
        spotted_size = settings.get('spotted_text_size', 12.0) if spotted_enabled else 0
        name_size = settings.get('name_text_size', 14.0) if name_enabled else 0
        weapon_enabled = settings.get('weapon_esp', True)
        weapon_size = settings.get('weapon_text_size', 11.0) if weapon_enabled else 0
        
        # Calculate total height needed for text stack
        text_stack_height = 0
        if spotted_enabled:
            text_stack_height += spotted_size
        if name_enabled:
            text_stack_height += name_size
        if spotted_enabled and name_enabled:
            text_stack_height += int(max(spotted_size, name_size, 12) * 0.8)  # Add spacing between texts
        
        # Add padding above text stack
        text_padding = int(8 * scale_factor)
        total_text_height = text_stack_height + text_padding
        
        # Base offset depends on healthbar type
        if healthbar_type == 'Horizontal Above':
            if settings.get('armor_bar', True) and armor > 0:
                base_y_offset = head_y - int(20 * scale_factor) - total_text_height  # Above armor bar
            else:
                base_y_offset = head_y - int(12 * scale_factor) - total_text_height  # Above health bar
        else:
            base_y_offset = head_y - int(8 * scale_factor) - total_text_height  # Just above head
        
        # Draw spotted indicator first (above name)
        spotted_y = base_y_offset
        if settings.get('spotted_esp', True):
            spotted_color = settings.get('spotted_color', (0, 255, 0))
            spotted_text = "SPOTTED"
            # Center the spotted text
            text_width_factor = len(spotted_text) * 3.0 * (spotted_size / 14.0)
            dpg.draw_text((x - text_width_factor, spotted_y), spotted_text, color=spotted_color, size=spotted_size, parent="esp_preview_canvas")
        
        # Draw player name below spotted with dynamic spacing
        spacing = int(max(spotted_size, name_size, 12) * 0.8)  # Dynamic spacing based on text sizes
        name_y = spotted_y + spacing
        if settings.get('name_esp', True):
            # Center the text based on name length and font size
            text_width_factor = len(name) * 3.5 * (name_size / 14.0)
            dpg.draw_text((x - text_width_factor, name_y), name, color=(255, 255, 255), size=name_size, parent="esp_preview_canvas")
        
        # Draw distance at center of player
        if settings.get('distance_esp', True):
            distance_text = "25m"  # Sample distance
            center_y = (head_y + feet_y) / 2
            text_width_factor = len(distance_text) * 2.5 * (12.0 / 14.0)  # Approximate width
            dpg.draw_text((x - text_width_factor, center_y - 6), distance_text, color=(255, 255, 255), size=12.0, parent="esp_preview_canvas")
            
    except Exception as e:
        debug_log(f"Error drawing preview player: {str(e)}", "ERROR")


def draw_preview_radar(settings):
    """
    Draw a preview radar in the corner.
    """
    try:
        radar_size = min(80, settings.get('radar_size', 200) // 3)  # Scale down for preview
        radar_x = 320
        radar_y = 20
        
        # Radar background
        opacity = settings.get('radar_opacity', 180)
        bg_color = settings.get('radar_bg_color', (0, 0, 0))
        bg_color = tuple(list(bg_color) + [opacity])
        
        dpg.draw_rectangle((radar_x - radar_size//2, radar_y - radar_size//2), 
                          (radar_x + radar_size//2, radar_y + radar_size//2), 
                          color=bg_color, fill=True, parent="esp_preview_canvas")
        
        # Radar border
        border_color = settings.get('radar_border_color', (128, 128, 128))
        dpg.draw_rectangle((radar_x - radar_size//2, radar_y - radar_size//2), 
                          (radar_x + radar_size//2, radar_y + radar_size//2), 
                          color=border_color, thickness=1, parent="esp_preview_canvas")
        
        # Radar crosshair
        crosshair_color = settings.get('radar_crosshair_color', (77, 77, 77))
        dpg.draw_line((radar_x - radar_size//4, radar_y), (radar_x + radar_size//4, radar_y), 
                     color=crosshair_color, thickness=1, parent="esp_preview_canvas")
        dpg.draw_line((radar_x, radar_y - radar_size//4), (radar_x, radar_y + radar_size//4), 
                     color=crosshair_color, thickness=1, parent="esp_preview_canvas")
        
        # Sample player dots
        player_color = settings.get('radar_player_color', (255, 255, 255))
        enemy_color = settings.get('radar_enemy_color', (255, 0, 0))
        team_color = settings.get('radar_team_color', (0, 255, 0))
        
        # Local player (center)
        dpg.draw_circle((radar_x, radar_y), 2, color=player_color, fill=True, parent="esp_preview_canvas")
        
        # Enemy
        dpg.draw_circle((radar_x + 15, radar_y - 10), 2, color=enemy_color, fill=True, parent="esp_preview_canvas")
        
        # Team
        dpg.draw_circle((radar_x - 12, radar_y + 8), 2, color=team_color, fill=True, parent="esp_preview_canvas")
        
    except Exception as e:
        debug_log(f"Error drawing preview radar: {str(e)}", "ERROR")


def draw_preview_aimbot_fov(settings):
    """
    Draw aimbot FOV circle preview.
    """
    try:
        radius = settings.get('aimbot_radius', 50) // 2  # Scale down for preview
        center_x, center_y = 200, 200  # Moved down to avoid player overlap
        
        color = settings.get('aimbot_radius_color', (255, 0, 0))
        color = tuple(int(c) for c in color)
        
        # Draw FOV circle
        dpg.draw_circle((center_x, center_y), radius, color=color, thickness=2, parent="esp_preview_canvas")
        
        # Draw deadzone if enabled
        if settings.get('aimbot_deadzone_enabled', False) and settings.get('aimbot_show_deadzone', False):
            deadzone_radius = settings.get('aimbot_deadzone_radius', 10) // 2
            deadzone_color = settings.get('aimbot_deadzone_color', (255, 255, 0))
            deadzone_color = tuple(int(c) for c in deadzone_color)
            
            dpg.draw_circle((center_x, center_y), deadzone_radius, color=deadzone_color, thickness=1, parent="esp_preview_canvas")
            
    except Exception as e:
        debug_log(f"Error drawing preview aimbot FOV: {str(e)}", "ERROR")


def create_esp_tab():
    """
    Create the ESP settings tab content with Toggles and Options subtabs.
    """
    with dpg.tab(label="ESP"):
        with dpg.tab_bar():
            # =========== TOGGLES SUBTAB ===========
            with dpg.tab(label="Toggles"):
                # Get show_tooltips setting
                show_tips = Active_Config.get("show_tooltips", True)
                
                # Master ESP toggle - load from Active_Config
                dpg.add_checkbox(
                    label="Enable ESP", 
                    default_value=Active_Config.get("esp_enabled", True),
                    tag="chk_esp_enabled",
                    callback=on_esp_toggle
                )
                with dpg.tooltip("chk_esp_enabled", tag="tooltip_esp_enabled", show=show_tips):
                    dpg.add_text("Master toggle for all ESP features")
                ALL_TOOLTIP_TAGS.append("tooltip_esp_enabled")
                
                dpg.add_separator()
                
                # Individual feature toggles - load from Active_Config
                dpg.add_checkbox(
                    label="Box ESP", 
                    default_value=Active_Config.get("box_esp", True),
                    tag="chk_box_esp",
                    callback=on_box_esp_toggle
                )
                with dpg.tooltip("chk_box_esp", tag="tooltip_box_esp", show=show_tips):
                    dpg.add_text("Draw boxes around players")
                ALL_TOOLTIP_TAGS.append("tooltip_box_esp")
                
                dpg.add_checkbox(
                    label="Snap Lines", 
                    default_value=Active_Config.get("line_esp", True),
                    tag="chk_line_esp",
                    callback=on_line_esp_toggle
                )
                with dpg.tooltip("chk_line_esp", tag="tooltip_line_esp", show=show_tips):
                    dpg.add_text("Draw lines from screen edge to players")
                ALL_TOOLTIP_TAGS.append("tooltip_line_esp")
                
                dpg.add_checkbox(
                    label="Skeleton", 
                    default_value=Active_Config.get("skeleton_esp", True),
                    tag="chk_skeleton_esp",
                    callback=on_skeleton_esp_toggle
                )
                with dpg.tooltip("chk_skeleton_esp", tag="tooltip_skeleton_esp", show=show_tips):
                    dpg.add_text("Draw player skeleton bones")
                ALL_TOOLTIP_TAGS.append("tooltip_skeleton_esp")
                
                dpg.add_checkbox(
                    label="Show Nickname", 
                    default_value=Active_Config.get("name_esp", False),
                    tag="chk_name_esp",
                    callback=on_name_esp_toggle
                )
                with dpg.tooltip("chk_name_esp", tag="tooltip_name_esp", show=show_tips):
                    dpg.add_text("Display player names above boxes")
                ALL_TOOLTIP_TAGS.append("tooltip_name_esp")
                
                dpg.add_checkbox(
                    label="Show Distance", 
                    default_value=Active_Config.get("distance_esp", True),
                    tag="chk_distance_esp",
                    callback=on_distance_esp_toggle
                )
                with dpg.tooltip("chk_distance_esp", tag="tooltip_distance_esp", show=show_tips):
                    dpg.add_text("Display distance to players at center of boxes")
                ALL_TOOLTIP_TAGS.append("tooltip_distance_esp")
                
                dpg.add_checkbox(
                    label="Show Weapon", 
                    default_value=Active_Config.get("weapon_esp", True),
                    tag="chk_weapon_esp",
                    callback=on_weapon_esp_toggle
                )
                with dpg.tooltip("chk_weapon_esp", tag="tooltip_weapon_esp", show=show_tips):
                    dpg.add_text("Display current weapon name below player")
                ALL_TOOLTIP_TAGS.append("tooltip_weapon_esp")
                
                dpg.add_checkbox(
                    label="Hide Unknown Weapons", 
                    default_value=Active_Config.get("hide_unknown_weapons", False),
                    tag="chk_hide_unknown_weapons",
                    callback=on_hide_unknown_weapons_toggle
                )
                with dpg.tooltip("chk_hide_unknown_weapons", tag="tooltip_hide_unknown_weapons", show=show_tips):
                    dpg.add_text("Hide weapon names for unknown weapon IDs")
                ALL_TOOLTIP_TAGS.append("tooltip_hide_unknown_weapons")
                
                dpg.add_checkbox(
                    label="Health Bar", 
                    default_value=Active_Config.get("health_bar", True),
                    tag="chk_health_bar",
                    callback=on_health_bar_toggle
                )
                with dpg.tooltip("chk_health_bar", tag="tooltip_health_bar", show=show_tips):
                    dpg.add_text("Show health bar on left side of box")
                ALL_TOOLTIP_TAGS.append("tooltip_health_bar")
                
                dpg.add_checkbox(
                    label="Armor Bar", 
                    default_value=Active_Config.get("armor_bar", True),
                    tag="chk_armor_bar",
                    callback=on_armor_bar_toggle
                )
                with dpg.tooltip("chk_armor_bar", tag="tooltip_armor_bar", show=show_tips):
                    dpg.add_text("Show armor bar on right side of box")
                ALL_TOOLTIP_TAGS.append("tooltip_armor_bar")
                
                dpg.add_checkbox(
                    label="Head Dot", 
                    default_value=Active_Config.get("head_dot", True),
                    tag="chk_head_dot",
                    callback=on_head_dot_toggle
                )
                with dpg.tooltip("chk_head_dot", tag="tooltip_head_dot", show=show_tips):
                    dpg.add_text("Draw a dot at player's head position")
                ALL_TOOLTIP_TAGS.append("tooltip_head_dot")
                
                dpg.add_checkbox(
                    label="Bomb ESP", 
                    default_value=Active_Config.get("bomb_esp", True),
                    tag="chk_bomb_esp",
                    callback=on_bomb_esp_toggle
                )
                with dpg.tooltip("chk_bomb_esp", tag="tooltip_bomb_esp", show=show_tips):
                    dpg.add_text("Show bomb location when planted")
                ALL_TOOLTIP_TAGS.append("tooltip_bomb_esp")
                
                dpg.add_checkbox(
                    label="Footstep ESP", 
                    default_value=Active_Config.get("footstep_esp", False),
                    tag="chk_footstep_esp",
                    callback=on_footstep_esp_toggle
                )
                with dpg.tooltip("chk_footstep_esp", tag="tooltip_footstep_esp", show=show_tips):
                    dpg.add_text("Show expanding rings when enemies make noise")
                ALL_TOOLTIP_TAGS.append("tooltip_footstep_esp")
                
                dpg.add_checkbox(
                    label="Spotted Status", 
                    default_value=Active_Config.get("spotted_esp", True),
                    tag="chk_spotted_esp",
                    callback=on_spotted_esp_toggle
                )
                with dpg.tooltip("chk_spotted_esp", tag="tooltip_spotted_esp", show=show_tips):
                    dpg.add_text("Show if player is visible to your team")
                ALL_TOOLTIP_TAGS.append("tooltip_spotted_esp")
                
                dpg.add_checkbox(
                    label="Hide Spotted Players", 
                    default_value=Active_Config.get("hide_spotted_players", False),
                    tag="chk_hide_spotted_players",
                    callback=on_hide_spotted_players_toggle
                )
                with dpg.tooltip("chk_hide_spotted_players", tag="tooltip_hide_spotted_players", show=show_tips):
                    dpg.add_text("Hide ESP elements (boxes, lines, skeleton, name, bars, dot) for spotted players")
                ALL_TOOLTIP_TAGS.append("tooltip_hide_spotted_players")
                
                dpg.add_checkbox(
                    label="Custom Crosshair", 
                    default_value=Active_Config.get("custom_crosshair", False),
                    tag="chk_custom_crosshair",
                    callback=on_custom_crosshair_toggle
                )
                with dpg.tooltip("chk_custom_crosshair", tag="tooltip_custom_crosshair", show=show_tips):
                    dpg.add_text("Show custom crosshair at screen center")
                ALL_TOOLTIP_TAGS.append("tooltip_custom_crosshair")
            
            # =========== OPTIONS SUBTAB ===========
            with dpg.tab(label="Options"):
                dpg.add_text("ESP Options", color=(255, 255, 255))
                dpg.add_separator()
                
                # Snap lines position - load from Active_Config
                dpg.add_combo(
                    items=["Bottom", "Top"],
                    default_value=Active_Config.get("lines_position", "Bottom"),
                    label="Snaplines Position",
                    tag="combo_lines_pos",
                    callback=on_lines_position_change
                )
                with dpg.tooltip("combo_lines_pos", tag="tooltip_lines_pos", show=show_tips):
                    dpg.add_text("Where snaplines originate from")
                ALL_TOOLTIP_TAGS.append("tooltip_lines_pos")
                
                # Antialiasing mode - load from Active_Config
                dpg.add_combo(
                    items=["None", "2x MSAA", "4x MSAA", "8x MSAA"],
                    default_value=Active_Config.get("antialiasing", "4x MSAA"),
                    label="Antialiasing",
                    tag="combo_antialiasing",
                    callback=on_antialiasing_change
                )
                with dpg.tooltip("combo_antialiasing", tag="tooltip_antialiasing", show=show_tips):
                    dpg.add_text("Smooth edges (higher = better quality)")
                    dpg.add_text("Change causes overlay to refresh")
                ALL_TOOLTIP_TAGS.append("tooltip_antialiasing")
                
                # Healthbar type dropdown
                dpg.add_combo(
                    items=["Vertical Left", "Vertical Right", "Horizontal Above", "Horizontal Below"],
                    default_value=Active_Config.get("healthbar_type", "Vertical Left"),
                    label="Healthbar Type",
                    tag="combo_healthbar_type",
                    callback=on_healthbar_type_change
                )
                with dpg.tooltip("combo_healthbar_type", tag="tooltip_healthbar_type", show=show_tips):
                    dpg.add_text("Position of health/armor bars relative to player box")
                ALL_TOOLTIP_TAGS.append("tooltip_healthbar_type")
                
                # Box type dropdown (2D/3D)
                dpg.add_combo(
                    items=["2D", "3D"],
                    default_value=Active_Config.get("box_type", "2D"),
                    label="Box Type",
                    tag="combo_box_type",
                    callback=on_box_type_change
                )
                with dpg.tooltip("combo_box_type", tag="tooltip_box_type", show=show_tips):
                    dpg.add_text("2D: Flat rectangle around player")
                    dpg.add_text("3D: 3D box that rotates with player view")
                ALL_TOOLTIP_TAGS.append("tooltip_box_type")
                
                dpg.add_separator()
                dpg.add_text("Line Thickness")
                
                dpg.add_slider_float(
                    label="Box",
                    default_value=Active_Config.get("box_thickness", 1.5),
                    min_value=1.0,
                    max_value=5.0,
                    tag="slider_box_thickness",
                    callback=on_box_thickness_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_box_thickness", tag="tooltip_box_thickness", show=show_tips):
                    dpg.add_text("Thickness of ESP box outlines")
                ALL_TOOLTIP_TAGS.append("tooltip_box_thickness")
                
                dpg.add_slider_float(
                    label="Snaplines",
                    default_value=Active_Config.get("snapline_thickness", 1.5),
                    min_value=1.0,
                    max_value=5.0,
                    tag="slider_snapline_thickness",
                    callback=on_snapline_thickness_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_snapline_thickness", tag="tooltip_snapline_thickness", show=show_tips):
                    dpg.add_text("Thickness of snap lines to players")
                ALL_TOOLTIP_TAGS.append("tooltip_snapline_thickness")
                
                dpg.add_slider_float(
                    label="Skeleton",
                    default_value=Active_Config.get("skeleton_thickness", 1.5),
                    min_value=1.0,
                    max_value=5.0,
                    tag="slider_skeleton_thickness",
                    callback=on_skeleton_thickness_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_skeleton_thickness", tag="tooltip_skeleton_thickness", show=show_tips):
                    dpg.add_text("Thickness of skeleton bone lines")
                ALL_TOOLTIP_TAGS.append("tooltip_skeleton_thickness")
                
                dpg.add_separator()
                dpg.add_text("Text Size")
                
                dpg.add_slider_float(
                    label="Spotted Status",
                    default_value=Active_Config.get("spotted_text_size", 12.0),
                    min_value=8.0,
                    max_value=24.0,
                    tag="slider_spotted_text_size",
                    callback=on_spotted_text_size_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_spotted_text_size", tag="tooltip_spotted_text_size", show=show_tips):
                    dpg.add_text("Font size for spotted status text")
                ALL_TOOLTIP_TAGS.append("tooltip_spotted_text_size")
                
                dpg.add_slider_float(
                    label="Nickname",
                    default_value=Active_Config.get("name_text_size", 14.0),
                    min_value=8.0,
                    max_value=24.0,
                    tag="slider_name_text_size",
                    callback=on_name_text_size_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_name_text_size", tag="tooltip_name_text_size", show=show_tips):
                    dpg.add_text("Font size for player nickname text")
                ALL_TOOLTIP_TAGS.append("tooltip_name_text_size")
                
                dpg.add_slider_float(
                    label="Weapon",
                    default_value=Active_Config.get("weapon_text_size", 11.0),
                    min_value=8.0,
                    max_value=24.0,
                    tag="slider_weapon_text_size",
                    callback=on_weapon_text_size_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_weapon_text_size", tag="tooltip_weapon_text_size", show=show_tips):
                    dpg.add_text("Font size for weapon name text")
                ALL_TOOLTIP_TAGS.append("tooltip_weapon_text_size")
                
                dpg.add_separator()
                dpg.add_text("Crosshair Options")
                
                dpg.add_slider_float(
                    label="Scale",
                    default_value=Active_Config.get("custom_crosshair_scale", 1.0),
                    min_value=0.5,
                    max_value=3.0,
                    tag="slider_custom_crosshair_scale",
                    callback=on_custom_crosshair_scale_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_custom_crosshair_scale", tag="tooltip_custom_crosshair_scale", show=show_tips):
                    dpg.add_text("Size multiplier for custom crosshair")
                ALL_TOOLTIP_TAGS.append("tooltip_custom_crosshair_scale")
                
                dpg.add_slider_float(
                    label="Thickness",
                    default_value=Active_Config.get("custom_crosshair_thickness", 2.0),
                    min_value=1.0,
                    max_value=5.0,
                    tag="slider_custom_crosshair_thickness",
                    callback=on_custom_crosshair_thickness_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_custom_crosshair_thickness", tag="tooltip_custom_crosshair_thickness", show=show_tips):
                    dpg.add_text("Line thickness for custom crosshair")
                ALL_TOOLTIP_TAGS.append("tooltip_custom_crosshair_thickness")
                
                dpg.add_combo(
                    items=["Sus", "Plus", "X", "Circle", "Dot"],
                    default_value=Active_Config.get("custom_crosshair_shape", "Sus"),
                    label="Shape",
                    tag="combo_custom_crosshair_shape",
                    callback=on_custom_crosshair_shape_change
                )
                with dpg.tooltip("combo_custom_crosshair_shape", tag="tooltip_custom_crosshair_shape", show=show_tips):
                    dpg.add_text("Crosshair shape preset")
                ALL_TOOLTIP_TAGS.append("tooltip_custom_crosshair_shape")
                
                dpg.add_separator()
                dpg.add_text("ESP Distance Filter")
                
                # ESP Distance Filter toggle
                dpg.add_checkbox(
                    label="ESP Distance Filter",
                    default_value=Active_Config.get("esp_distance_filter_enabled", False),
                    tag="chk_esp_distance_filter_enabled",
                    callback=on_esp_distance_filter_toggle
                )
                with dpg.tooltip("chk_esp_distance_filter_enabled", tag="tooltip_esp_distance_filter_enabled", show=show_tips):
                    dpg.add_text("Filter ESP based on player distance")
                ALL_TOOLTIP_TAGS.append("tooltip_esp_distance_filter_enabled")
                
                # Distance Filter Type dropdown (shown when enabled)
                dpg.add_combo(
                    items=["Further than", "Closer than"],
                    default_value=Active_Config.get("esp_distance_filter_type", "Further than"),
                    label="Distance Filter",
                    tag="combo_esp_distance_filter_type",
                    callback=on_esp_distance_filter_type_change,
                    show=Active_Config.get("esp_distance_filter_enabled", False)
                )
                with dpg.tooltip("combo_esp_distance_filter_type", tag="tooltip_esp_distance_filter_type", show=show_tips):
                    dpg.add_text("Filter direction: show players further/closer than distance")
                ALL_TOOLTIP_TAGS.append("tooltip_esp_distance_filter_type")
                
                # Distance slider (shown when enabled)
                dpg.add_slider_float(
                    label="Distance (m)",
                    default_value=Active_Config.get("esp_distance_filter_distance", 25.0),
                    min_value=5.0,
                    max_value=50.0,
                    tag="slider_esp_distance_filter_distance",
                    callback=on_esp_distance_filter_distance_change,
                    format="%.1f",
                    show=Active_Config.get("esp_distance_filter_enabled", False)
                )
                with dpg.tooltip("slider_esp_distance_filter_distance", tag="tooltip_esp_distance_filter_distance", show=show_tips):
                    dpg.add_text("Distance threshold in meters (5-50)")
                ALL_TOOLTIP_TAGS.append("tooltip_esp_distance_filter_distance")
                
                # Filter Mode dropdown (shown when enabled)
                dpg.add_combo(
                    items=["Only Show", "Hide"],
                    default_value=Active_Config.get("esp_distance_filter_mode", "Only Show"),
                    label="Filter Type",
                    tag="combo_esp_distance_filter_mode",
                    callback=on_esp_distance_filter_mode_change,
                    show=Active_Config.get("esp_distance_filter_enabled", False)
                )
                with dpg.tooltip("combo_esp_distance_filter_mode", tag="tooltip_esp_distance_filter_mode", show=show_tips):
                    dpg.add_text("Only Show: display only matching players")
                    dpg.add_text("Hide: hide matching players")
                ALL_TOOLTIP_TAGS.append("tooltip_esp_distance_filter_mode")
            
            # =========== RADAR SUBTAB ===========
            with dpg.tab(label="Radar"):
                dpg.add_checkbox(
                    label="Enable Radar",
                    default_value=Active_Config.get("radar_enabled", False),
                    tag="chk_radar_enabled",
                    callback=on_radar_enabled_toggle
                )
                with dpg.tooltip("chk_radar_enabled", tag="tooltip_radar_enabled", show=show_tips):
                    dpg.add_text("Show minimap radar overlay")
                ALL_TOOLTIP_TAGS.append("tooltip_radar_enabled")
                
                dpg.add_checkbox(
                    label="Overlap Game Radar (Lock Settings)",
                    default_value=Active_Config.get("radar_overlap_game", False),
                    tag="chk_radar_overlap_game",
                    callback=on_radar_overlap_game_toggle
                )
                with dpg.tooltip("chk_radar_overlap_game", tag="tooltip_radar_overlap_game", show=show_tips):
                    dpg.add_text("CS2 RADAR SETTINS REQUIRED:\n-CENTER PLAYER = YES\n-RADAR ROTATING = YES\n-RADAR HUD SIZE = 1.0\n-RADAR MAP ZOM = 0.7\n-FORCE SQUARE SHAPE = NO\n-RADAR ZOOMING DYNAMICALLY  = NO")
                ALL_TOOLTIP_TAGS.append("tooltip_radar_overlap_game")
                
                dpg.add_separator()
                
                dpg.add_slider_int(
                    label="Size",
                    default_value=Active_Config.get("radar_size", 200),
                    min_value=100,
                    max_value=400,
                    tag="slider_radar_size",
                    callback=on_radar_size_change
                )
                with dpg.tooltip("slider_radar_size", tag="tooltip_radar_size", show=show_tips):
                    dpg.add_text("Radar display size in pixels")
                ALL_TOOLTIP_TAGS.append("tooltip_radar_size")
                
                dpg.add_slider_float(
                    label="Scale",
                    default_value=Active_Config.get("radar_scale", 5.0),
                    min_value=1.0,
                    max_value=80.0,
                    tag="slider_radar_scale",
                    callback=on_radar_scale_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_radar_scale", tag="tooltip_radar_scale", show=show_tips):
                    dpg.add_text("Higher = more zoomed out")
                ALL_TOOLTIP_TAGS.append("tooltip_radar_scale")
                
                dpg.add_slider_int(
                    label="Opacity",
                    default_value=Active_Config.get("radar_opacity", 180),
                    min_value=50,
                    max_value=255,
                    tag="slider_radar_opacity",
                    callback=on_radar_opacity_change
                )
                with dpg.tooltip("slider_radar_opacity", tag="tooltip_radar_opacity", show=show_tips):
                    dpg.add_text("Background transparency (higher = more visible)")
                ALL_TOOLTIP_TAGS.append("tooltip_radar_opacity")
                
                dpg.add_slider_int(
                    label="X Offset",
                    default_value=Active_Config.get("radar_x", 0),
                    min_value=-860,  # Keep radar fully visible on 1920x1080
                    max_value=860,
                    tag="slider_radar_x",
                    callback=on_radar_x_change
                )
                with dpg.tooltip("slider_radar_x", tag="tooltip_radar_x", show=show_tips):
                    dpg.add_text("X offset from screen center (negative = left, positive = right). Range keeps radar fully visible.")
                ALL_TOOLTIP_TAGS.append("tooltip_radar_x")
                
                dpg.add_slider_int(
                    label="Y Offset",
                    default_value=Active_Config.get("radar_y", 0),
                    min_value=-440,  # Keep radar fully visible on 1920x1080
                    max_value=440,
                    tag="slider_radar_y",
                    callback=on_radar_y_change
                )
                with dpg.tooltip("slider_radar_y", tag="tooltip_radar_y", show=show_tips):
                    dpg.add_text("Y offset from screen center (negative = up, positive = down). Range keeps radar fully visible.")
                ALL_TOOLTIP_TAGS.append("tooltip_radar_y")
            
            # =========== PREVIEW SUBTAB ===========
            with dpg.tab(label="Preview"):
                dpg.add_text("ESP Preview", color=(255, 255, 255))
                dpg.add_separator()
                
                # Create a drawing canvas for ESP preview
                with dpg.drawlist(width=400, height=300, tag="esp_preview_canvas"):
                    # Background
                    dpg.draw_rectangle((0, 0), (400, 300), color=(20, 20, 20), fill=True)
                    
                    # Draw initial preview
                    update_esp_preview()


def get_color_for_picker(key, default):
    """
    Get a color value from Active_Config and convert for color picker.
    
    Args:
        key: The config key (e.g., "enemy_box_color")
        default: Default RGB tuple (e.g., (196, 30, 58))
    
    Returns:
        list: [r, g, b] with values in 0-255 range
    """
    color = Active_Config.get(key, default)
    # Ensure color is a valid tuple/list with 3 elements
    if not color or len(color) < 3:
        color = default
    # Return as LIST with 0-255 integer values
    return [int(color[0]), int(color[1]), int(color[2])]


def create_aimbot_tab():
    """
    Create the Aimbot settings tab content.
    """
    with dpg.tab(label="Aim"):
        # Create sub-tabs for organization
        with dpg.tab_bar():
            # Toggles sub-tab
            with dpg.tab(label="Aimbot"):
                # Get show_tooltips setting
                show_tips = Active_Config.get("show_tooltips", True)
                
                dpg.add_text("Aimbot Settings", color=(255, 255, 255))
                dpg.add_separator()
                
                # Enable aimbot
                dpg.add_checkbox(
                    label="Enable Aimbot",
                    default_value=Active_Config.get("aimbot_enabled", False),
                    callback=on_aimbot_toggle,
                    tag="chk_aimbot_enabled"
                )
                with dpg.tooltip("chk_aimbot_enabled", tag="tooltip_aimbot_enabled", show=show_tips):
                    dpg.add_text("Automatically aim at enemies")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_enabled")
                
                # Aimbot deadzone toggle
                dpg.add_checkbox(
                    label="Aimbot Deadzone",
                    default_value=Active_Config.get("aimbot_deadzone_enabled", False),
                    callback=on_aimbot_deadzone_toggle,
                    tag="chk_aimbot_deadzone_enabled"
                )
                with dpg.tooltip("chk_aimbot_deadzone_enabled", tag="tooltip_aimbot_deadzone_enabled", show=show_tips):
                    dpg.add_text("Create a deadzone where enemies won't be targeted")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_deadzone_enabled")
                
                # Require aimbot key
                dpg.add_checkbox(
                    label="Require Aimkey",
                    default_value=Active_Config.get("aimbot_require_key", True),
                    callback=on_aimbot_require_key_toggle,
                    tag="chk_aimbot_require_key"
                )
                with dpg.tooltip("chk_aimbot_require_key", tag="tooltip_aimbot_require_key", show=show_tips):
                    dpg.add_text("Require holding aimbot key to activate")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_require_key")
                
                dpg.add_spacer(height=UI_SPACING_SMALL)
                dpg.add_text("Targeting", color=(255, 255, 255))
                dpg.add_separator()
                
                # Spotted check toggle
                dpg.add_checkbox(
                    label="Spotted Check",
                    default_value=Active_Config.get("aimbot_spotted_check", False),
                    callback=on_aimbot_spotted_check_toggle,
                    tag="chk_aimbot_spotted_check"
                )
                with dpg.tooltip("chk_aimbot_spotted_check", tag="tooltip_aimbot_spotted_check", show=show_tips):
                    dpg.add_text("Only aim at enemies that are spotted")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_spotted_check")
                
                # Lock target toggle (only visible when require aimkey is on)
                require_key_enabled = Active_Config.get("aimbot_require_key", True)
                lock_target_show = show_tips and require_key_enabled
                dpg.add_checkbox(
                    label="Lock Target",
                    default_value=Active_Config.get("aimbot_lock_target", False),
                    callback=on_aimbot_lock_target_toggle,
                    tag="chk_aimbot_lock_target",
                    show=require_key_enabled
                )
                with dpg.tooltip("chk_aimbot_lock_target", tag="tooltip_aimbot_lock_target", show=lock_target_show):
                    dpg.add_text("Keep targeting the same enemy until aimkey is released")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_lock_target")
                
                # Target bone dropdown
                dpg.add_combo(
                    items=["Head", "Neck", "Chest", "Pelvis"],
                    default_value=Active_Config.get("aimbot_target_bone", "Head"),
                    label="Target Bone",
                    tag="combo_aimbot_target_bone",
                    callback=on_aimbot_target_bone_change
                )
                with dpg.tooltip("combo_aimbot_target_bone", tag="tooltip_aimbot_target_bone", show=show_tips):
                    dpg.add_text("Body part to aim at")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_target_bone")
                
                # Movement type dropdown
                dpg.add_combo(
                    items=["Dynamic", "Linear"],
                    default_value=Active_Config.get("aimbot_movement_type", "Dynamic"),
                    label="Movement Type",
                    tag="combo_aimbot_movement_type",
                    callback=on_aimbot_movement_type_change
                )
                with dpg.tooltip("combo_aimbot_movement_type", tag="tooltip_aimbot_movement_type", show=show_tips):
                    dpg.add_text("Dynamic: Speed based on distance (fast far, slow close)")
                    dpg.add_text("Linear: Constant speed regardless of distance")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_movement_type")
                
                # Aimbot smoothness
                dpg.add_slider_float(
                    label="Smoothness",
                    default_value=Active_Config.get("aimbot_smoothness", 5.0),
                    min_value=0.0,
                    max_value=100.0,
                    tag="slider_aimbot_smoothness",
                    callback=on_aimbot_smoothness_change,
                    format="%.1f"
                )
                with dpg.tooltip("slider_aimbot_smoothness", tag="tooltip_aimbot_smoothness", show=show_tips):
                    dpg.add_text("Higher = smoother aim movement")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_smoothness")
                
                dpg.add_spacer(height=UI_SPACING_SMALL)
                dpg.add_text("Visuals", color=(255, 255, 255))
                dpg.add_separator()
                
                # Show radius toggle
                dpg.add_checkbox(
                    label="Show Radius Circle",
                    default_value=Active_Config.get("aimbot_show_radius", True),
                    callback=on_aimbot_show_radius_toggle,
                    tag="chk_aimbot_show_radius"
                )
                with dpg.tooltip("chk_aimbot_show_radius", tag="tooltip_aimbot_show_radius", show=show_tips):
                    dpg.add_text("Display FOV circle on screen")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_show_radius")
                
                # Aimbot radius
                dpg.add_slider_int(
                    label="Radius",
                    default_value=Active_Config.get("aimbot_radius", 50),
                    min_value=10,
                    max_value=500,
                    tag="slider_aimbot_radius",
                    callback=on_aimbot_radius_change
                )
                with dpg.tooltip("slider_aimbot_radius", tag="tooltip_aimbot_radius", show=show_tips):
                    dpg.add_text("FOV radius in pixels")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_radius")
                
                # Show deadzone circle toggle
                dpg.add_checkbox(
                    label="Show Deadzone Circle",
                    default_value=Active_Config.get("aimbot_show_deadzone", False),
                    callback=on_aimbot_show_deadzone_toggle,
                    tag="chk_aimbot_show_deadzone"
                )
                with dpg.tooltip("chk_aimbot_show_deadzone", tag="tooltip_aimbot_show_deadzone", show=show_tips):
                    dpg.add_text("Display deadzone circle on screen")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_show_deadzone")
                
                # Deadzone radius slider
                dpg.add_slider_int(
                    label="Deadzone Radius",
                    default_value=Active_Config.get("aimbot_deadzone_radius", 10),
                    min_value=0,
                    max_value=Active_Config.get("aimbot_radius", 50) - 1,  # Max is always 1 less than aimbot radius
                    tag="slider_aimbot_deadzone_radius",
                    callback=on_aimbot_deadzone_radius_change
                )
                with dpg.tooltip("slider_aimbot_deadzone_radius", tag="tooltip_aimbot_deadzone_radius", show=show_tips):
                    dpg.add_text("Deadzone radius (must be smaller than FOV radius)")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_deadzone_radius")
                
                # Aimbot snaplines toggle
                dpg.add_checkbox(
                    label="Aimbot Snaplines",
                    default_value=Active_Config.get("aimbot_snaplines", False),
                    callback=on_aimbot_snaplines_toggle,
                    tag="chk_aimbot_snaplines"
                )
                with dpg.tooltip("chk_aimbot_snaplines", tag="tooltip_aimbot_snaplines", show=show_tips):
                    dpg.add_text("Draw lines from center of screen to aimbot targets")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_snaplines")
            
            # Triggerbot sub-tab
            with dpg.tab(label="Triggerbot"):
                dpg.add_text("Triggerbot Settings", color=(255, 255, 255))
                dpg.add_separator()
                
                # Enable triggerbot
                dpg.add_checkbox(
                    label="Enable Triggerbot",
                    default_value=Active_Config.get("triggerbot_enabled", False),
                    callback=on_triggerbot_toggle,
                    tag="chk_triggerbot_enabled"
                )
                with dpg.tooltip("chk_triggerbot_enabled", tag="tooltip_triggerbot_enabled", show=show_tips):
                    dpg.add_text("Auto-fire when crosshair is on enemy")
                ALL_TOOLTIP_TAGS.append("tooltip_triggerbot_enabled")
                
                dpg.add_spacer(height=UI_SPACING_SMALL)
                dpg.add_text("Timing", color=(255, 255, 255))
                dpg.add_separator()
                
                # First shot delay
                dpg.add_slider_int(
                    label="First Shot Delay (ms)",
                    default_value=Active_Config.get("triggerbot_first_shot_delay", 0),
                    min_value=0,
                    max_value=1000,
                    tag="slider_triggerbot_first_shot_delay",
                    callback=on_triggerbot_first_shot_delay_change
                )
                with dpg.tooltip("slider_triggerbot_first_shot_delay", tag="tooltip_triggerbot_first_shot_delay", show=show_tips):
                    dpg.add_text("Delay before first shot fires")
                ALL_TOOLTIP_TAGS.append("tooltip_triggerbot_first_shot_delay")
                
                # Between shots delay
                dpg.add_slider_int(
                    label="Between Shots Delay (ms)",
                    default_value=Active_Config.get("triggerbot_between_shots_delay", 30),
                    min_value=0,
                    max_value=1000,
                    tag="slider_triggerbot_between_shots_delay",
                    callback=on_triggerbot_between_shots_delay_change
                )
                with dpg.tooltip("slider_triggerbot_between_shots_delay", tag="tooltip_triggerbot_between_shots_delay", show=show_tips):
                    dpg.add_text("Delay between consecutive shots")
                ALL_TOOLTIP_TAGS.append("tooltip_triggerbot_between_shots_delay")
                
                dpg.add_spacer(height=UI_SPACING_SMALL)
                dpg.add_text("Burst Mode", color=(255, 255, 255))
                dpg.add_separator()
                
                # Burst mode toggle
                dpg.add_checkbox(
                    label="Enable Burst Mode",
                    default_value=Active_Config.get("triggerbot_burst_mode", False),
                    callback=on_triggerbot_burst_mode_toggle,
                    tag="chk_triggerbot_burst_mode"
                )
                with dpg.tooltip("chk_triggerbot_burst_mode", tag="tooltip_triggerbot_burst_mode", show=show_tips):
                    dpg.add_text("Fire multiple shots in bursts")
                ALL_TOOLTIP_TAGS.append("tooltip_triggerbot_burst_mode")
                
                # Burst shots amount
                burst_mode_enabled = Active_Config.get("triggerbot_burst_mode", False)
                burst_shots_show = show_tips and burst_mode_enabled
                dpg.add_slider_int(
                    label="Burst Shots",
                    default_value=Active_Config.get("triggerbot_burst_shots", 3),
                    min_value=1,
                    max_value=10,
                    tag="slider_triggerbot_burst_shots",
                    callback=on_triggerbot_burst_shots_change,
                    show=burst_mode_enabled
                )
                with dpg.tooltip("slider_triggerbot_burst_shots", tag="tooltip_triggerbot_burst_shots", show=burst_shots_show):
                    dpg.add_text("Number of shots per burst")
                ALL_TOOLTIP_TAGS.append("tooltip_triggerbot_burst_shots")
                
                dpg.add_spacer(height=UI_SPACING_SMALL)
                dpg.add_text("Targeting", color=(255, 255, 255))
                dpg.add_separator()
                
                # Head-only mode toggle
                dpg.add_checkbox(
                    label="Head-Only Mode",
                    default_value=Active_Config.get("triggerbot_head_only", False),
                    callback=on_triggerbot_head_only_toggle,
                    tag="chk_triggerbot_head_only"
                )
                with dpg.tooltip("chk_triggerbot_head_only", tag="tooltip_triggerbot_head_only", show=show_tips):
                    dpg.add_text("Only fire when crosshair is on enemy's head")
                ALL_TOOLTIP_TAGS.append("tooltip_triggerbot_head_only")
            
            # ACP (Auto Crosshair Placement) sub-tab
            with dpg.tab(label="Auto Crosshair Placement"):
                dpg.add_text("Auto Crosshair Placement", color=(255, 255, 255))
                dpg.add_separator()
                
                # Enable ACS
                dpg.add_checkbox(
                    label="Enable ACP",
                    default_value=Active_Config.get("acs_enabled", False),
                    callback=on_acs_toggle,
                    tag="chk_acs_enabled"
                )
                with dpg.tooltip("chk_acs_enabled", tag="tooltip_acs_enabled", show=show_tips):
                    dpg.add_text("Auto vertical crosshair adjustment when key held")
                ALL_TOOLTIP_TAGS.append("tooltip_acs_enabled")
                
                dpg.add_spacer(height=UI_SPACING_SMALL)
                dpg.add_text("Targeting", color=(255, 255, 255))
                dpg.add_separator()
                
                # Target bone dropdown
                dpg.add_combo(
                    items=["Head", "Neck", "Chest", "Pelvis"],
                    default_value=Active_Config.get("acs_target_bone", "Head"),
                    label="Target Bone",
                    tag="combo_acs_target_bone",
                    callback=on_acs_target_bone_change
                )
                with dpg.tooltip("combo_acs_target_bone", tag="tooltip_acs_target_bone", show=show_tips):
                    dpg.add_text("Body part to align crosshair to")
                ALL_TOOLTIP_TAGS.append("tooltip_acs_target_bone")
                
                # Smoothness slider
                dpg.add_slider_int(
                    label="Smoothness",
                    default_value=Active_Config.get("acs_smoothness", 5),
                    min_value=1,
                    max_value=50,
                    tag="slider_acs_smoothness",
                    callback=on_acs_smoothness_change
                )
                with dpg.tooltip("slider_acs_smoothness", tag="tooltip_acs_smoothness", show=show_tips):
                    dpg.add_text("Higher = slower/smoother adjustment")
                ALL_TOOLTIP_TAGS.append("tooltip_acs_smoothness")
                
                # Deadzone slider
                dpg.add_slider_int(
                    label="Deadzone (px)",
                    default_value=Active_Config.get("acs_deadzone", 5),
                    min_value=0,
                    max_value=100,
                    tag="slider_acs_deadzone",
                    callback=on_acs_deadzone_change
                )
                with dpg.tooltip("slider_acs_deadzone", tag="tooltip_acs_deadzone", show=show_tips):
                    dpg.add_text("Pixels around target where no adjustment occurs")
                ALL_TOOLTIP_TAGS.append("tooltip_acs_deadzone")
                
                dpg.add_spacer(height=UI_SPACING_SMALL)
                dpg.add_text("Visuals", color=(255, 255, 255))
                dpg.add_separator()
                
                # Draw deadzone lines toggle
                dpg.add_checkbox(
                    label="Draw Deadzone Lines",
                    default_value=Active_Config.get("acs_draw_deadzone_lines", False),
                    callback=on_acs_draw_deadzone_lines_toggle,
                    tag="chk_acs_draw_deadzone_lines"
                )
                with dpg.tooltip("chk_acs_draw_deadzone_lines", tag="tooltip_acs_draw_deadzone_lines", show=show_tips):
                    dpg.add_text("Show visual lines indicating target and deadzone")
                ALL_TOOLTIP_TAGS.append("tooltip_acs_draw_deadzone_lines")
                
                # Always show deadzone lines toggle (only visible when draw lines is enabled)
                draw_lines_enabled = Active_Config.get("acs_draw_deadzone_lines", False)
                always_show_tips = show_tips and draw_lines_enabled
                dpg.add_checkbox(
                    label="Always Show Deadzone Lines",
                    default_value=Active_Config.get("acs_always_show_deadzone_lines", False),
                    callback=on_acs_always_show_deadzone_lines_toggle,
                    tag="chk_acs_always_show_deadzone_lines",
                    show=draw_lines_enabled
                )
                with dpg.tooltip("chk_acs_always_show_deadzone_lines", tag="tooltip_acs_always_show_deadzone_lines", show=always_show_tips):
                    dpg.add_text("Show lines without holding ACS key")
                ALL_TOOLTIP_TAGS.append("tooltip_acs_always_show_deadzone_lines")
            
            # Recoil Control sub-tab
            with dpg.tab(label="Recoil Control"):
                dpg.add_text("Recoil Control", color=(255, 255, 255))
                dpg.add_separator()
                
                # Enable RCS
                rcs_enabled = Active_Config.get("rcs_enabled", False)
                dpg.add_checkbox(
                    label="Enable RCS",
                    default_value=rcs_enabled,
                    tag="chk_rcs_enabled",
                    callback=on_rcs_toggle
                )
                with dpg.tooltip("chk_rcs_enabled", tag="tooltip_rcs", show=show_tips):
                    dpg.add_text("Automatically compensates for weapon recoil")
                    dpg.add_text("Adjusts view angles based on aim punch")
                ALL_TOOLTIP_TAGS.append("tooltip_rcs")
                
                # RCS horizontal strength slider
                dpg.add_slider_int(
                    label="Horizontal %",
                    default_value=Active_Config.get("rcs_strength_x", 100),
                    min_value=0,
                    max_value=100,
                    tag="slider_rcs_strength_x",
                    callback=on_rcs_strength_x_change
                )
                with dpg.tooltip("slider_rcs_strength_x", tag="tooltip_rcs_strength_x", show=show_tips):
                    dpg.add_text("Horizontal recoil compensation strength")
                    dpg.add_text("100% = Full compensation, 0% = None")
                ALL_TOOLTIP_TAGS.append("tooltip_rcs_strength_x")
                
                # RCS vertical strength slider
                dpg.add_slider_int(
                    label="Vertical %",
                    default_value=Active_Config.get("rcs_strength_y", 100),
                    min_value=0,
                    max_value=100,
                    tag="slider_rcs_strength_y",
                    callback=on_rcs_strength_y_change
                )
                with dpg.tooltip("slider_rcs_strength_y", tag="tooltip_rcs_strength_y", show=show_tips):
                    dpg.add_text("Vertical recoil compensation strength")
                    dpg.add_text("100% = Full compensation, 0% = None")
                ALL_TOOLTIP_TAGS.append("tooltip_rcs_strength_y")
                
                # RCS smoothness slider
                dpg.add_slider_int(
                    label="Smoothness",
                    default_value=Active_Config.get("rcs_smoothness", 1),
                    min_value=1,
                    max_value=10,
                    tag="slider_rcs_smoothness",
                    callback=on_rcs_smoothness_change
                )
                with dpg.tooltip("slider_rcs_smoothness", tag="tooltip_rcs_smoothness", show=show_tips):
                    dpg.add_text("How smoothly recoil compensation is applied")
                    dpg.add_text("1 = Instant, 10 = Very Smooth")
                ALL_TOOLTIP_TAGS.append("tooltip_rcs_smoothness")
                
                # RCS multiplier slider
                dpg.add_slider_float(
                    label="Multiplier",
                    default_value=Active_Config.get("rcs_multiplier", 2.0),
                    min_value=1.8,
                    max_value=2.2,
                    format="%.2f",
                    tag="slider_rcs_multiplier",
                    callback=on_rcs_multiplier_change
                )
                with dpg.tooltip("slider_rcs_multiplier", tag="tooltip_rcs_multiplier", show=show_tips):
                    dpg.add_text("Increase if crosshair drifts up, decrease if down")
                    dpg.add_text("Default: 2.0")
                ALL_TOOLTIP_TAGS.append("tooltip_rcs_multiplier")
                
                # RCS continuous fire only toggle
                rcs_continuous_only = Active_Config.get("rcs_continuous_only", False)
                dpg.add_checkbox(
                    label="Continuous Fire Only",
                    default_value=rcs_continuous_only,
                    tag="chk_rcs_continuous_only",
                    callback=on_rcs_continuous_only_toggle
                )
                with dpg.tooltip("chk_rcs_continuous_only", tag="tooltip_rcs_continuous_only", show=show_tips):
                    dpg.add_text("Only compensate recoil during continuous fire")
                    dpg.add_text("Activates after 2+ shots in 300ms window")
                    dpg.add_text("Ignores isolated single shots")
                ALL_TOOLTIP_TAGS.append("tooltip_rcs_continuous_only")


def create_colors_tab():
    """
    Create the Appearance tab content.
    """
    show_tips = Active_Config.get("show_tooltips", True)
    
    with dpg.tab(label="Appearance"):
        # Nested tab bar for color sub-categories
        with dpg.tab_bar():
            # ESP Colors sub-tab
            with dpg.tab(label="ESP"):
                dpg.add_text("Box Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Enemy Box Color
                dpg.add_color_edit(
                    label="Enemy Boxes",
                    default_value=get_color_for_picker("enemy_box_color", (196, 30, 58)),
                    no_alpha=True,
                    callback=on_enemy_box_color_change,
                    tag="color_enemy_box"
                )
                
                # Team Box Color
                dpg.add_color_edit(
                    label="Team Boxes",
                    default_value=get_color_for_picker("team_box_color", (71, 167, 106)),
                    no_alpha=True,
                    callback=on_team_box_color_change,
                    tag="color_team_box"
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Snapline Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Enemy Snapline Color
                dpg.add_color_edit(
                    label="Enemy Snaplines",
                    default_value=get_color_for_picker("enemy_snapline_color", (196, 30, 58)),
                    no_alpha=True,
                    callback=on_enemy_snapline_color_change,
                    tag="color_enemy_snapline"
                )
                
                # Team Snapline Color
                dpg.add_color_edit(
                    label="Team Snaplines",
                    default_value=get_color_for_picker("team_snapline_color", (71, 167, 106)),
                    no_alpha=True,
                    callback=on_team_snapline_color_change,
                    tag="color_team_snapline"
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Skeleton Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Enemy Skeleton Color
                dpg.add_color_edit(
                    label="Enemy Skeleton",
                    default_value=get_color_for_picker("enemy_skeleton_color", (255, 255, 255)),
                    no_alpha=True,
                    callback=on_enemy_skeleton_color_change,
                    tag="color_enemy_skeleton"
                )
                
                # Team Skeleton Color
                dpg.add_color_edit(
                    label="Team Skeleton",
                    default_value=get_color_for_picker("team_skeleton_color", (255, 255, 255)),
                    no_alpha=True,
                    callback=on_team_skeleton_color_change,
                    tag="color_team_skeleton"
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Head Dot Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Enemy Head Dot Color
                dpg.add_color_edit(
                    label="Enemy Head Dot",
                    default_value=get_color_for_picker("enemy_head_dot_color", (255, 255, 0)),
                    no_alpha=True,
                    callback=on_enemy_head_dot_color_change,
                    tag="color_enemy_head_dot"
                )
                
                # Team Head Dot Color
                dpg.add_color_edit(
                    label="Team Head Dot",
                    default_value=get_color_for_picker("team_head_dot_color", (255, 255, 0)),
                    no_alpha=True,
                    callback=on_team_head_dot_color_change,
                    tag="color_team_head_dot"
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Spotted Status Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Spotted Color (when visible)
                dpg.add_color_edit(
                    label="Spotted",
                    default_value=get_color_for_picker("spotted_color", (0, 255, 0)),
                    no_alpha=True,
                    callback=on_spotted_color_change,
                    tag="color_spotted"
                )
                
                # Not Spotted Color
                dpg.add_color_edit(
                    label="Not Spotted",
                    default_value=get_color_for_picker("not_spotted_color", (255, 0, 0)),
                    no_alpha=True,
                    callback=on_not_spotted_color_change,
                    tag="color_not_spotted"
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Footstep ESP Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Footstep ESP Color
                dpg.add_color_edit(
                    label="Footstep ESP",
                    default_value=get_color_for_picker("footstep_esp_color", (255, 165, 0)),
                    no_alpha=True,
                    callback=on_footstep_esp_color_change,
                    tag="color_footstep_esp"
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Crosshair Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Custom Crosshair Color
                dpg.add_color_edit(
                    label="Custom Crosshair",
                    default_value=get_color_for_picker("custom_crosshair_color", (255, 255, 255)),
                    no_alpha=True,
                    callback=on_custom_crosshair_color_change,
                    tag="color_custom_crosshair_color"
                )
            
            # Menu Colors sub-tab
            with dpg.tab(label="Menu"):
                dpg.add_text("UI Theme", color=(255, 255, 255))
                dpg.add_separator()
                
                # Get list of colorway names
                colorway_names = list(UI_COLORWAYS.keys())
                current_colorway = Active_Config.get("menu_colorway", "Default")
                
                dpg.add_combo(
                    label="Colorway",
                    items=colorway_names,
                    default_value=current_colorway,
                    callback=on_colorway_change,
                    tag="combo_colorway",
                    width=200
                )
                
                dpg.add_spacer(height=UI_SPACING_SMALL)
                
                # Font selection dropdown
                font_names = list(MENU_FONTS.keys())
                current_font = Active_Config.get("menu_font", "Default")
                
                dpg.add_combo(
                    label="Font",
                    items=font_names,
                    default_value=current_font,
                    callback=on_font_change,
                    tag="combo_font",
                    width=200
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Window Size", color=(255, 255, 255))
                dpg.add_separator()
                
                # Window Width Slider
                current_width = Active_Config.get("window_width", 600)
                dpg.add_slider_int(
                    label="Width",
                    default_value=current_width,
                    min_value=400,
                    max_value=1200,
                    callback=on_window_width_change,
                    tag="slider_window_width",
                    width=200
                )
                
                # Window Height Slider
                current_height = Active_Config.get("window_height", 400)
                dpg.add_slider_int(
                    label="Height",
                    default_value=current_height,
                    min_value=300,
                    max_value=800,
                    callback=on_window_height_change,
                    tag="slider_window_height",
                    width=200
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Window Transparency", color=(255, 255, 255))
                dpg.add_separator()
                
                # Menu Transparency Slider
                current_transparency = Active_Config.get("menu_transparency", 255)
                dpg.add_slider_int(
                    label="Menu Transparency",
                    default_value=current_transparency,
                    min_value=50,
                    max_value=255,
                    callback=on_menu_transparency_change,
                    tag="slider_menu_transparency",
                    width=200
                )
                with dpg.tooltip("slider_menu_transparency", tag="tooltip_menu_transparency", show=show_tips):
                    dpg.add_text("Menu window transparency (50 = very transparent, 255 = opaque)")
                ALL_TOOLTIP_TAGS.append("tooltip_menu_transparency")
            
            # Radar Colors sub-tab
            with dpg.tab(label="Radar"):
                dpg.add_text("Radar Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Radar Background Color
                dpg.add_color_edit(
                    label="Background",
                    default_value=get_color_for_picker("radar_bg_color", (0, 0, 0)),
                    no_alpha=True,
                    callback=on_radar_bg_color_change,
                    tag="color_radar_bg"
                )
                
                # Radar Border Color
                dpg.add_color_edit(
                    label="Border",
                    default_value=get_color_for_picker("radar_border_color", (128, 128, 128)),
                    no_alpha=True,
                    callback=on_radar_border_color_change,
                    tag="color_radar_border"
                )
                
                # Radar Crosshair Color
                dpg.add_color_edit(
                    label="Crosshair",
                    default_value=get_color_for_picker("radar_crosshair_color", (77, 77, 77)),
                    no_alpha=True,
                    callback=on_radar_crosshair_color_change,
                    tag="color_radar_crosshair"
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Entity Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Radar Player Color
                dpg.add_color_edit(
                    label="Player Dot",
                    default_value=get_color_for_picker("radar_player_color", (255, 255, 255)),
                    no_alpha=True,
                    callback=on_radar_player_color_change,
                    tag="color_radar_player"
                )
                
                # Radar Enemy Color
                dpg.add_color_edit(
                    label="Enemy Dots",
                    default_value=get_color_for_picker("radar_enemy_color", (255, 0, 0)),
                    no_alpha=True,
                    callback=on_radar_enemy_color_change,
                    tag="color_radar_enemy"
                )
                
                # Radar Team Color
                dpg.add_color_edit(
                    label="Team Dots",
                    default_value=get_color_for_picker("radar_team_color", (0, 255, 0)),
                    no_alpha=True,
                    callback=on_radar_team_color_change,
                    tag="color_radar_team"
                )
            
            # Aimbot Colors sub-tab
            with dpg.tab(label="Aimbot"):
                dpg.add_text("Aimbot Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # Aimbot Radius Color
                dpg.add_color_edit(
                    label="Radius Circle",
                    default_value=get_color_for_picker("aimbot_radius_color", (255, 0, 0)),
                    no_alpha=True,
                    callback=on_aimbot_radius_color_change,
                    tag="color_aimbot_radius"
                )
                
                # Aimbot Deadzone Color
                dpg.add_color_edit(
                    label="Deadzone Circle",
                    default_value=get_color_for_picker("aimbot_deadzone_color", (255, 255, 0)),
                    no_alpha=True,
                    callback=on_aimbot_deadzone_color_change,
                    tag="color_aimbot_deadzone"
                )
                
                # Aimbot Targeting Radius Color
                dpg.add_color_edit(
                    label="Targeting Radius Circle",
                    default_value=get_color_for_picker("aimbot_targeting_radius_color", (0, 255, 0)),
                    no_alpha=True,
                    callback=on_aimbot_targeting_radius_color_change,
                    tag="color_aimbot_targeting_radius"
                )
                
                # Aimbot Targeting Deadzone Color
                dpg.add_color_edit(
                    label="Targeting Deadzone Circle",
                    default_value=get_color_for_picker("aimbot_targeting_deadzone_color", (0, 0, 255)),
                    no_alpha=True,
                    callback=on_aimbot_targeting_deadzone_color_change,
                    tag="color_aimbot_targeting_deadzone"
                )
                
                # Aimbot Snapline Color
                dpg.add_color_edit(
                    label="Aimbot Snaplines",
                    default_value=get_color_for_picker("aimbot_snapline_color", (255, 255, 255)),
                    no_alpha=True,
                    callback=on_aimbot_snapline_color_change,
                    tag="color_aimbot_snapline"
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Transparency", color=(255, 255, 255))
                dpg.add_separator()
                
                # Aimbot radius transparency
                dpg.add_slider_int(
                    label="Radius Transparency",
                    default_value=Active_Config.get("aimbot_radius_transparency", 180),
                    min_value=0,
                    max_value=255,
                    tag="slider_aimbot_radius_transparency",
                    callback=on_aimbot_radius_transparency_change
                )
                with dpg.tooltip("slider_aimbot_radius_transparency", tag="tooltip_aimbot_radius_transparency", show=show_tips):
                    dpg.add_text("Transparency of the FOV radius circle (0 = invisible, 255 = solid)")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_radius_transparency")
                
                # Aimbot deadzone transparency
                dpg.add_slider_int(
                    label="Deadzone Transparency",
                    default_value=Active_Config.get("aimbot_deadzone_transparency", 180),
                    min_value=0,
                    max_value=255,
                    tag="slider_aimbot_deadzone_transparency",
                    callback=on_aimbot_deadzone_transparency_change
                )
                with dpg.tooltip("slider_aimbot_deadzone_transparency", tag="tooltip_aimbot_deadzone_transparency", show=show_tips):
                    dpg.add_text("Transparency of the deadzone circle (0 = invisible, 255 = solid)")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_deadzone_transparency")
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Thickness", color=(255, 255, 255))
                dpg.add_separator()
                
                # Aimbot radius thickness
                dpg.add_slider_float(
                    label="Radius Thickness",
                    default_value=Active_Config.get("aimbot_radius_thickness", 2.0),
                    min_value=0.5,
                    max_value=10.0,
                    tag="slider_aimbot_radius_thickness",
                    callback=on_aimbot_radius_thickness_change
                )
                with dpg.tooltip("slider_aimbot_radius_thickness", tag="tooltip_aimbot_radius_thickness", show=show_tips):
                    dpg.add_text("Thickness of the FOV radius circle outline")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_radius_thickness")
                
                # Aimbot deadzone thickness
                dpg.add_slider_float(
                    label="Deadzone Thickness",
                    default_value=Active_Config.get("aimbot_deadzone_thickness", 1.5),
                    min_value=0.5,
                    max_value=10.0,
                    tag="slider_aimbot_deadzone_thickness",
                    callback=on_aimbot_deadzone_thickness_change
                )
                with dpg.tooltip("slider_aimbot_deadzone_thickness", tag="tooltip_aimbot_deadzone_thickness", show=show_tips):
                    dpg.add_text("Thickness of the deadzone circle outline")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_deadzone_thickness")
                
                # Aimbot snapline thickness
                dpg.add_slider_float(
                    label="Snapline Thickness",
                    default_value=Active_Config.get("aimbot_snapline_thickness", 2.0),
                    min_value=0.5,
                    max_value=10.0,
                    tag="slider_aimbot_snapline_thickness",
                    callback=on_aimbot_snapline_thickness_change
                )
                with dpg.tooltip("slider_aimbot_snapline_thickness", tag="tooltip_aimbot_snapline_thickness", show=show_tips):
                    dpg.add_text("Thickness of the aimbot snapline")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_snapline_thickness")
            
            # ACP Colors sub-tab
            with dpg.tab(label="Auto Crosshair Placement"):
                dpg.add_text("ACP Colors", color=(255, 255, 255))
                dpg.add_separator()
                
                # ACS Deadzone Line Color
                dpg.add_color_edit(
                    label="Deadzone Lines",
                    default_value=get_color_for_picker("acs_line_color", (255, 0, 0)),
                    no_alpha=True,
                    callback=on_acs_line_color_change,
                    tag="color_acs_line"
                )
                
                dpg.add_spacer(height=UI_SPACING_MEDIUM)
                dpg.add_text("Deadzone Line Appearance", color=(255, 255, 255))
                dpg.add_separator()
                
                # Line width slider
                dpg.add_slider_int(
                    label="Line Width",
                    default_value=Active_Config.get("acs_line_width", 2),
                    min_value=1,
                    max_value=10,
                    tag="slider_acs_line_width",
                    callback=on_acs_line_width_change
                )
                with dpg.tooltip("slider_acs_line_width", tag="tooltip_acs_line_width", show=show_tips):
                    dpg.add_text("Width of deadzone visualization lines")
                ALL_TOOLTIP_TAGS.append("tooltip_acs_line_width")
                
                # Line transparency slider
                dpg.add_slider_int(
                    label="Line Transparency",
                    default_value=Active_Config.get("acs_line_transparency", 80),
                    min_value=10,
                    max_value=255,
                    tag="slider_acs_line_transparency",
                    callback=on_acs_line_transparency_change
                )
                with dpg.tooltip("slider_acs_line_transparency", tag="tooltip_acs_line_transparency", show=show_tips):
                    dpg.add_text("Transparency of deadzone lines (higher = more visible)")
                ALL_TOOLTIP_TAGS.append("tooltip_acs_line_transparency")


def initialize_color_pickers():
    """
    Initialize color picker values from Active_Config after UI is created.
    
    DearPyGui's default_value for color_edit doesn't always work correctly,
    so we explicitly set the values after the widgets are created and rendered.
    """
    color_picker_mappings = [
        ("color_enemy_box", "enemy_box_color", (196, 30, 58)),
        ("color_team_box", "team_box_color", (71, 167, 106)),
        ("color_enemy_snapline", "enemy_snapline_color", (196, 30, 58)),
        ("color_team_snapline", "team_snapline_color", (71, 167, 106)),
        ("color_enemy_skeleton", "enemy_skeleton_color", (255, 255, 255)),
        ("color_team_skeleton", "team_skeleton_color", (255, 255, 255)),
        ("color_enemy_head_dot", "enemy_head_dot_color", (255, 255, 0)),
        ("color_team_head_dot", "team_head_dot_color", (255, 255, 0)),
        # Spotted colors
        ("color_spotted", "spotted_color", (0, 255, 0)),
        ("color_not_spotted", "not_spotted_color", (255, 0, 0)),
        # Footstep ESP color
        ("color_footstep_esp", "footstep_esp_color", (255, 165, 0)),
        # Radar colors
        ("color_radar_bg", "radar_bg_color", (0, 0, 0)),
        ("color_radar_border", "radar_border_color", (128, 128, 128)),
        ("color_radar_crosshair", "radar_crosshair_color", (77, 77, 77)),
        ("color_radar_player", "radar_player_color", (255, 255, 255)),
        ("color_radar_enemy", "radar_enemy_color", (255, 0, 0)),
        ("color_radar_team", "radar_team_color", (0, 255, 0)),
        # Aimbot colors
        ("color_aimbot_radius", "aimbot_radius_color", (255, 0, 0)),
        ("color_aimbot_deadzone", "aimbot_deadzone_color", (255, 255, 0)),
        ("color_aimbot_targeting_radius", "aimbot_targeting_radius_color", (0, 255, 0)),
        ("color_aimbot_targeting_deadzone", "aimbot_targeting_deadzone_color", (0, 0, 255)),
        ("color_aimbot_snapline", "aimbot_snapline_color", (255, 255, 255)),
    ]
    
    for tag, config_key, default in color_picker_mappings:
        try:
            # Get color from config
            color = Active_Config.get(config_key, default)
            if not color or len(color) < 3:
                color = default
            # Use 0-255 integer values
            color_int = [int(color[0]), int(color[1]), int(color[2])]
            dpg.set_value(tag, color_int)
            dpg.configure_item(tag, default_value=color_int)
        except Exception as e:
            debug_log(f"Failed to initialize {tag}: {str(e)}", "WARNING")


def create_config_tab():
    """
    Create the Config tab for configuration management.
    """
    with dpg.tab(label="Config"):
        # Get tooltip visibility setting
        show_tips = Active_Config.get("show_tooltips", True)
        
        dpg.add_text("Configuration", color=(255, 255, 255))
        dpg.add_separator()
        
        # Config selection dropdown (auto-refreshes every ~2 seconds)
        dpg.add_text("Load Config:", color=(200, 200, 200))
        configs = get_available_configs()
        dpg.add_combo(
            items=configs,
            default_value=configs[0] if configs else "",
            callback=on_config_selected,
            tag="combo_config_select",
            width=200
        )
        with dpg.tooltip("combo_config_select", tag="tooltip_config_select", show=show_tips):
            dpg.add_text("Select a config to load")
            dpg.add_text("List auto-refreshes every 2 seconds")
        ALL_TOOLTIP_TAGS.append("tooltip_config_select")
        
        dpg.add_spacer(height=UI_SPACING_LARGE)
        dpg.add_separator()
        dpg.add_spacer(height=UI_SPACING_MEDIUM)
        
        # Save config section
        dpg.add_text("Save Config:", color=(200, 200, 200))
        dpg.add_input_text(
            hint="Enter config name...",
            tag="input_config_name",
            width=200
        )
        with dpg.tooltip("input_config_name", tag="tooltip_config_name_input", show=show_tips):
            dpg.add_text("Enter a name for your config")
            dpg.add_text("Saved to configs/Settings/")
        ALL_TOOLTIP_TAGS.append("tooltip_config_name_input")
        
        dpg.add_spacer(height=UI_SPACING_SMALL)
        dpg.add_button(
            label="Save Current Settings",
            callback=lambda: on_save_config_clicked(),
            width=150,
            tag="btn_save_config"
        )
        with dpg.tooltip("btn_save_config", tag="tooltip_save_config", show=show_tips):
            dpg.add_text("Save all current settings to a new config file")
        ALL_TOOLTIP_TAGS.append("tooltip_save_config")
        
        dpg.add_spacer(height=UI_SPACING_LARGE)
        dpg.add_separator()
        dpg.add_spacer(height=UI_SPACING_MEDIUM)
        
        # Reset to default section
        dpg.add_button(
            label="Reset to Default",
            callback=lambda: reset_to_default_config(),
            width=150,
            tag="btn_reset_config"
        )
        with dpg.tooltip("btn_reset_config", tag="tooltip_reset_config", show=show_tips):
            dpg.add_text("Reset all settings to default values")
        ALL_TOOLTIP_TAGS.append("tooltip_reset_config")


def create_debug_tab():
    """
    Create the Debug tab with nested sub-tabs.
    """
    with dpg.tab(label="Debug"):
        # Nested tab bar for sub-tabs
        with dpg.tab_bar():
            # Output sub-tab with mini-terminal
            with dpg.tab(label="Output"):
                # Mini-terminal for debug output
                dpg.add_text("Debug Terminal", color=(255, 255, 255))
                dpg.add_separator()
                
                # Scrollable child window for debug output
                with dpg.child_window(tag="debug_output_window", height=-35, border=True, horizontal_scrollbar=True):
                    # Container for debug text lines
                    dpg.add_text("Waiting for events...", tag="debug_terminal_text", wrap=0)
                
                # Bottom controls
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Clear", callback=lambda: clear_debug_terminal())
                    dpg.add_button(label="Print Config", callback=lambda: print_active_config())
                    dpg.add_button(label="Dump Output", callback=lambda: dump_debug_output())
                    dpg.add_button(label="Copy Output", callback=lambda: copy_debug_output())
                    dpg.add_checkbox(label="Auto-scroll", default_value=True, tag="debug_autoscroll")
            
            # Offsets sub-tab
            with dpg.tab(label="Offsets"):
                create_offsets_content()
            
            # Performance sub-tab
            with dpg.tab(label="Performance", tag="tab_performance"):
                create_performance_content()


def clear_debug_terminal():
    """Clear all messages from the debug terminal."""
    global debug_output
    debug_output["messages"].clear()
    try:
        dpg.set_value("debug_terminal_text", "Terminal cleared.")
    except:
        pass


def dump_debug_output():
    """
    Dump the debug terminal output to a text file.
    Creates output.txt in the script's directory.
    """
    try:
        output_path = os.path.join(SCRIPT_DIR, "output.txt")
        
        # Get current terminal text
        terminal_text = dpg.get_value("debug_terminal_text")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Debug Output - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(terminal_text)
        
        debug_log(f"Output dumped to: {output_path}", "SUCCESS")
    except Exception as e:
        debug_log(f"Failed to dump output: {str(e)}", "ERROR")


def copy_debug_output():
    """
    Copy the debug terminal output to clipboard using Windows clip command.
    """
    try:
        # Get current terminal text
        terminal_text = dpg.get_value("debug_terminal_text")
        
        if not terminal_text:
            debug_log("Nothing to copy - output is empty", "WARNING")
            return
        
        # Use Windows clip command via subprocess (simple and reliable)
        import subprocess
        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
        process.communicate(input=terminal_text.encode('utf-16le'))
        
        debug_log("Output copied to clipboard", "SUCCESS")
            
    except Exception as e:
        debug_log(f"Failed to copy output: {str(e)}", "ERROR")


def print_active_config():
    """Print the Active_Config dictionary to the debug terminal."""
    debug_log("=== Active Configuration ===", "INFO")
    if Active_Config:
        for key, value in Active_Config.items():
            debug_log(f"  {key}: {value}", "INFO")
    else:
        debug_log("Active_Config is empty", "WARNING")
    debug_log("===========================", "INFO")


def update_debug_terminal():
    """Update the debug terminal display with latest messages."""
    global debug_output
    
    try:
        if not dpg.does_item_exist("debug_terminal_text"):
            return
        
        if not debug_output["messages"]:
            dpg.set_value("debug_terminal_text", "No messages yet...")
            return
        
        # Build output text with color codes
        lines = []
        for timestamp, level, message in debug_output["messages"]:
            # Format with color indicators
            if level == "ERROR":
                prefix = "[!]"
            elif level == "SUCCESS":
                prefix = "[✓]"
            elif level == "WARNING":
                prefix = "[?]"
            else:
                prefix = "[i]"
            
            lines.append(f"{prefix} [{timestamp}] {message}")
        
        output_text = "\n".join(lines)
        dpg.set_value("debug_terminal_text", output_text)
        
        # Auto-scroll to bottom if enabled
        try:
            if dpg.does_item_exist("debug_autoscroll") and dpg.get_value("debug_autoscroll"):
                if dpg.does_item_exist("debug_output_window"):
                    # Force a frame render first so content size is updated
                    dpg.render_dearpygui_frame()
                    # Then scroll to bottom
                    max_scroll = dpg.get_y_scroll_max("debug_output_window")
                    dpg.set_y_scroll("debug_output_window", max_scroll)
        except:
            pass
    except Exception as e:
        pass


def create_offsets_content():
    """
    Create the offset display content (used in Debug > Offsets sub-tab).
    """
    if offsets and client_dll:
        # Display main offsets
        dpg.add_text("=== Main Offsets ===", color=(255, 255, 255))
        dpg.add_separator()
        
        for key, value in offsets.get('client.dll', {}).items():
            dpg.add_text(f"{key}: 0x{value:X}" if isinstance(value, int) else f"{key}: {value}")
        
        dpg.add_spacer(height=UI_SPACING_MEDIUM)
        
        # Display client_dll class offsets
        dpg.add_text("=== Client DLL Classes ===", color=(255, 255, 255))
        dpg.add_separator()
        
        classes = client_dll.get('client.dll', {}).get('classes', {})
        for class_name, class_data in classes.items():
            dpg.add_text(f"\n{class_name}:", color=(255, 255, 255))
            
            fields = class_data.get('fields', {})
            if fields:
                for field_name, field_value in fields.items():
                    dpg.add_text(f"  {field_name}: 0x{field_value:X}" if isinstance(field_value, int) else f"  {field_name}: {field_value}")
    else:
        dpg.add_text("Offsets not loaded yet. Launch the cheat first.", color=(255, 100, 100))


def create_performance_content():
    """
    Create the performance monitoring content (used in Debug > Performance sub-tab).
    """
    # Performance Metrics Section
    dpg.add_text("Performance Metrics", color=(255, 255, 255))
    dpg.add_separator()
    
    # CPU and Memory
    with dpg.group(horizontal=True):
        dpg.add_text("CPU Usage:")
        dpg.add_text("0.0%", tag="perf_cpu_usage", color=(100, 255, 100))
    
    with dpg.group(horizontal=True):
        dpg.add_text("Memory Usage:")
        dpg.add_text("0 MB", tag="perf_memory_usage", color=(100, 255, 100))
    
    with dpg.group(horizontal=True):
        dpg.add_text("Disk Usage:")
        dpg.add_text("0 GB", tag="perf_disk_usage", color=(100, 255, 100))
    
    with dpg.group(horizontal=True):
        dpg.add_text("ESP FPS:")
        dpg.add_text("0", tag="perf_esp_fps", color=(100, 255, 100))
    
    dpg.add_spacer(height=UI_SPACING_MEDIUM)
    
    # Network Stats Section
    dpg.add_text("Network Statistics", color=(255, 255, 255))
    dpg.add_separator()
    
    with dpg.group(horizontal=True):
        dpg.add_text("Network Status:")
        dpg.add_text("Not Available", tag="perf_network_status", color=(255, 255, 100))
    
    with dpg.group(horizontal=True):
        dpg.add_text("CS2 Connection:")
        dpg.add_text("Unknown", tag="perf_cs2_connection", color=(255, 255, 100))
    
    dpg.add_spacer(height=UI_SPACING_MEDIUM)
    
    # Feature Status Section
    dpg.add_text("Feature Status", color=(255, 255, 255))
    dpg.add_separator()
    
    # ESP Status
    with dpg.group(horizontal=True):
        dpg.add_text("ESP:")
        dpg.add_text("Stopped", tag="perf_esp_status", color=(255, 100, 100))
    
    # Aimbot Status
    with dpg.group(horizontal=True):
        dpg.add_text("Aimbot:")
        dpg.add_text("Stopped", tag="perf_aimbot_status", color=(255, 100, 100))
    
    # Triggerbot Status
    with dpg.group(horizontal=True):
        dpg.add_text("Triggerbot:")
        dpg.add_text("Stopped", tag="perf_triggerbot_status", color=(255, 100, 100))
    
    # RCS Status
    with dpg.group(horizontal=True):
        dpg.add_text("RCS:")
        dpg.add_text("Stopped", tag="perf_rcs_status", color=(255, 100, 100))
    
    # ACS Status
    with dpg.group(horizontal=True):
        dpg.add_text("ACS:")
        dpg.add_text("Stopped", tag="perf_acs_status", color=(255, 100, 100))
    
    # Anti-Flash Status
    with dpg.group(horizontal=True):
        dpg.add_text("Anti-Flash:")
        dpg.add_text("Stopped", tag="perf_antiflash_status", color=(255, 100, 100))
    
    # FOV Changer Status
    with dpg.group(horizontal=True):
        dpg.add_text("FOV Changer:")
        dpg.add_text("Stopped", tag="perf_fov_status", color=(255, 100, 100))
    
    # Hitsound Status
    with dpg.group(horizontal=True):
        dpg.add_text("Hitsound:")
        dpg.add_text("Stopped", tag="perf_hitsound_status", color=(255, 100, 100))
    
    # Anti-AFK Status
    with dpg.group(horizontal=True):
        dpg.add_text("Anti-AFK:")
        dpg.add_text("Stopped", tag="perf_anti_afk_status", color=(255, 100, 100))
    
    dpg.add_spacer(height=UI_SPACING_MEDIUM)
    
    # Summary Section
    dpg.add_text("Summary", color=(255, 255, 255))
    dpg.add_separator()
    
    with dpg.group(horizontal=True):
        dpg.add_text("Active Features:")
        dpg.add_text("0", tag="perf_active_features", color=(255, 255, 255))
    
    with dpg.group(horizontal=True):
        dpg.add_text("Active Threads:")
        dpg.add_text("0", tag="perf_active_threads", color=(255, 255, 255))
    
    dpg.add_spacer(height=UI_SPACING_MEDIUM)
    
    # Controls
    with dpg.group(horizontal=True):
        dpg.add_button(label="Refresh", callback=lambda: update_performance_display())
        dpg.add_checkbox(label="Auto-refresh", default_value=True, tag="perf_auto_refresh")


def update_performance_display():
    """
    Update all performance metrics in the Performance sub-tab.
    Called periodically when auto-refresh is enabled.
    """
    try:
        # Performance Metrics
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=0)
        dpg.set_value("perf_cpu_usage", f"{cpu_percent:.1f}%")
        
        # Memory Usage
        memory = psutil.virtual_memory()
        memory_mb = memory.used / (1024 * 1024)
        dpg.set_value("perf_memory_usage", f"{memory_mb:.0f} MB")
        
        # Disk Usage
        disk = psutil.disk_usage('/')
        disk_gb = disk.used / (1024 * 1024 * 1024)
        dpg.set_value("perf_disk_usage", f"{disk_gb:.1f} GB")
        
        # ESP FPS
        esp_fps = esp_overlay.get("fps", 0)
        dpg.set_value("perf_esp_fps", str(esp_fps))
        
        # Network Stats (simplified - basic connectivity check)
        try:
            # Check if we have internet connectivity
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=0.1)
            dpg.set_value("perf_network_status", "Connected")
            dpg.configure_item("perf_network_status", color=(100, 255, 100))
        except:
            dpg.set_value("perf_network_status", "Disconnected")
            dpg.configure_item("perf_network_status", color=(255, 100, 100))
        
        # CS2 Connection Status
        cs2_running = is_cs2_running()
        cs2_status = "Connected" if cs2_running else "Disconnected"
        cs2_color = (100, 255, 100) if cs2_running else (255, 100, 100)
        dpg.set_value("perf_cs2_connection", cs2_status)
        dpg.configure_item("perf_cs2_connection", color=cs2_color)
        
        # Feature Status
        # ESP Status
        esp_running = esp_overlay.get("running", False)
        esp_status = "Running" if esp_running else "Stopped"
        esp_color = (100, 255, 100) if esp_running else (255, 100, 100)
        dpg.set_value("perf_esp_status", esp_status)
        dpg.configure_item("perf_esp_status", color=esp_color)
        
        # Aimbot Status
        aimbot_running = aimbot_state.get("running", False)
        aimbot_status = "Running" if aimbot_running else "Stopped"
        aimbot_color = (100, 255, 100) if aimbot_running else (255, 100, 100)
        dpg.set_value("perf_aimbot_status", aimbot_status)
        dpg.configure_item("perf_aimbot_status", color=aimbot_color)
        
        # Triggerbot Status
        triggerbot_running = triggerbot_state.get("running", False)
        triggerbot_status = "Running" if triggerbot_running else "Stopped"
        triggerbot_color = (100, 255, 100) if triggerbot_running else (255, 100, 100)
        dpg.set_value("perf_triggerbot_status", triggerbot_status)
        dpg.configure_item("perf_triggerbot_status", color=triggerbot_color)
        
        # RCS Status
        rcs_running = rcs_state.get("running", False)
        rcs_status = "Running" if rcs_running else "Stopped"
        rcs_color = (100, 255, 100) if rcs_running else (255, 100, 100)
        dpg.set_value("perf_rcs_status", rcs_status)
        dpg.configure_item("perf_rcs_status", color=rcs_color)
        
        # ACS Status
        acs_running = acs_state.get("running", False)
        acs_status = "Running" if acs_running else "Stopped"
        acs_color = (100, 255, 100) if acs_running else (255, 100, 100)
        dpg.set_value("perf_acs_status", acs_status)
        dpg.configure_item("perf_acs_status", color=acs_color)
        
        # Anti-Flash Status
        antiflash_running = anti_flash_state.get("running", False)
        antiflash_status = "Running" if antiflash_running else "Stopped"
        antiflash_color = (100, 255, 100) if antiflash_running else (255, 100, 100)
        dpg.set_value("perf_antiflash_status", antiflash_status)
        dpg.configure_item("perf_antiflash_status", color=antiflash_color)
        
        # FOV Changer Status
        fov_running = fov_changer_state.get("running", False)
        fov_status = "Running" if fov_running else "Stopped"
        fov_color = (100, 255, 100) if fov_running else (255, 100, 100)
        dpg.set_value("perf_fov_status", fov_status)
        dpg.configure_item("perf_fov_status", color=fov_color)
        
        # Hitsound Status
        hitsound_running = hitsound_state.get("running", False)
        hitsound_status = "Running" if hitsound_running else "Stopped"
        hitsound_color = (100, 255, 100) if hitsound_running else (255, 100, 100)
        dpg.set_value("perf_hitsound_status", hitsound_status)
        dpg.configure_item("perf_hitsound_status", color=hitsound_color)
        
        # Anti-AFK Status
        anti_afk_running = anti_afk_state.get("running", False)
        anti_afk_status = "Running" if anti_afk_running else "Stopped"
        anti_afk_color = (100, 255, 100) if anti_afk_running else (255, 100, 100)
        dpg.set_value("perf_anti_afk_status", anti_afk_status)
        dpg.configure_item("perf_anti_afk_status", color=anti_afk_color)
        
        # Summary
        active_features = sum([
            esp_running, aimbot_running, triggerbot_running, rcs_running,
            acs_running, antiflash_running, fov_running, hitsound_running,
            anti_afk_running
        ])
        dpg.set_value("perf_active_features", str(active_features))
        
        # Count active threads
        active_threads = sum([
            1 if esp_overlay.get("thread") and esp_overlay["thread"].is_alive() else 0,
            1 if aimbot_state.get("thread") and aimbot_state["thread"].is_alive() else 0,
            1 if triggerbot_state.get("thread") and triggerbot_state["thread"].is_alive() else 0,
            1 if rcs_state.get("thread") and rcs_state["thread"].is_alive() else 0,
            1 if acs_state.get("thread") and acs_state["thread"].is_alive() else 0,
            1 if anti_flash_state.get("thread") and anti_flash_state["thread"].is_alive() else 0,
            1 if fov_changer_state.get("thread") and fov_changer_state["thread"].is_alive() else 0,
            1 if hitsound_state.get("thread") and hitsound_state["thread"].is_alive() else 0,
            1 if anti_afk_state.get("thread") and anti_afk_state["thread"].is_alive() else 0,
        ])
        dpg.set_value("perf_active_threads", str(active_threads))
        
    except Exception as e:
        debug_log(f"Failed to update performance display: {str(e)}", "ERROR")


def create_offsets_tab():
    """
    Create the Offsets display tab content (legacy - kept for compatibility).
    """
    with dpg.tab(label="Offsets"):
        # Add scrollable child window for all offset values
        with dpg.child_window(border=False):
            create_offsets_content()


def create_cheat_tab():
    """
    Create the Cheat tab content (legacy - now split into ESP and Offsets tabs).
    """
    # This function is kept for backwards compatibility
    # The cheat window now uses create_esp_tab and create_offsets_tab
    create_offsets_tab()


def create_settings_tab_cheat():
    """
    Create the Miscellaneous tab content for cheat window.
    """
    with dpg.tab(label="Miscellaneous"):
        # Create sub-tabs for organization
        with dpg.tab_bar():
            # Cheat sub-tab (game-related features)
            with dpg.tab(label="Cheat"):
                # Get show_tooltips setting
                show_tips = Active_Config.get("show_tooltips", True)
                
                dpg.add_text("Cheat Features", color=(255, 255, 255))
                dpg.add_separator()
                
                # Targeting type dropdown - load from Active_Config
                targeting_value = "All Players" if Active_Config.get("targeting_type", 0) == 1 else "Enemies Only"
                dpg.add_combo(
                    items=["Enemies Only", "All Players"],
                    default_value=targeting_value,
                    label="Targeting",
                    tag="combo_targeting",
                    callback=on_targeting_type_change
                )
                with dpg.tooltip("combo_targeting", tag="tooltip_targeting", show=show_tips):
                    dpg.add_text("Target enemies only or include teammates")
                ALL_TOOLTIP_TAGS.append("tooltip_targeting")
                
                dpg.add_separator()
                
                # Anti Flash toggle
                dpg.add_checkbox(
                    label="Anti-Flash",
                    default_value=Active_Config.get("anti_flash_enabled", False),
                    tag="chk_anti_flash_enabled",
                    callback=on_anti_flash_toggle
                )
                with dpg.tooltip("chk_anti_flash_enabled", tag="tooltip_anti_flash", show=show_tips):
                    dpg.add_text("Prevents flashbang effects from blinding you")
                ALL_TOOLTIP_TAGS.append("tooltip_anti_flash")
                
                dpg.add_separator()
                
                # FOV Changer toggle
                fov_enabled = Active_Config.get("fov_changer_enabled", False)
                dpg.add_checkbox(
                    label="FOV Changer",
                    default_value=fov_enabled,
                    tag="chk_fov_changer_enabled",
                    callback=on_fov_changer_toggle
                )
                with dpg.tooltip("chk_fov_changer_enabled", tag="tooltip_fov_changer", show=show_tips):
                    dpg.add_text("Modify camera field of view")
                    dpg.add_text("Higher values give wider view")
                ALL_TOOLTIP_TAGS.append("tooltip_fov_changer")
                
                # FOV value slider (visibility controlled by toggle)
                dpg.add_slider_int(
                    label="FOV Value",
                    default_value=Active_Config.get("fov_value", 90),
                    min_value=68,
                    max_value=140,
                    tag="slider_fov_value",
                    callback=on_fov_value_change,
                    show=fov_enabled
                )
                fov_slider_show = show_tips and fov_enabled
                with dpg.tooltip("slider_fov_value", tag="tooltip_fov_value", show=fov_slider_show):
                    dpg.add_text("Camera field of view (default: 90)")
                    dpg.add_text("68 = Narrow, 140 = Very Wide")
                ALL_TOOLTIP_TAGS.append("tooltip_fov_value")
                
                dpg.add_separator()
                
                # Hitsound toggle
                hitsound_enabled = Active_Config.get("hitsound_enabled", False)
                dpg.add_checkbox(
                    label="Hitsound",
                    default_value=hitsound_enabled,
                    tag="chk_hitsound_enabled",
                    callback=on_hitsound_toggle
                )
                with dpg.tooltip("chk_hitsound_enabled", tag="tooltip_hitsound", show=show_tips):
                    dpg.add_text("Play sound when hitting enemies")
                    dpg.add_text("Select sound type from dropdown below")
                ALL_TOOLTIP_TAGS.append("tooltip_hitsound")
                
                # Hitsound selection dropdown (visibility controlled by toggle)
                dpg.add_combo(
                    items=["hitmarker", "criticalhit", "metalhit"],
                    default_value=Active_Config.get("hitsound_type", "hitmarker"),
                    label="Hitsound Type",
                    tag="combo_hitsound_type",
                    callback=on_hitsound_type_change,
                    show=hitsound_enabled
                )
                hitsound_combo_show = show_tips and hitsound_enabled
                with dpg.tooltip("combo_hitsound_type", tag="tooltip_hitsound_type", show=hitsound_combo_show):
                    dpg.add_text("Select which hitsound to play")
                    dpg.add_text("Files are downloaded automatically")
                ALL_TOOLTIP_TAGS.append("tooltip_hitsound_type")
                
                dpg.add_separator()
                
                # Anti-AFK toggle
                dpg.add_checkbox(
                    label="Anti-AFK",
                    default_value=Active_Config.get("anti_afk_enabled", False),
                    tag="chk_anti_afk_enabled",
                    callback=on_anti_afk_toggle
                )
                with dpg.tooltip("chk_anti_afk_enabled", tag="tooltip_anti_afk", show=show_tips):
                    dpg.add_text("Automatically press W,A,S,D keys to prevent AFK kick")
                ALL_TOOLTIP_TAGS.append("tooltip_anti_afk")
            
            # General settings sub-tab
            with dpg.tab(label="General"):
                # Get show_tooltips setting
                show_tips = Active_Config.get("show_tooltips", True)
                
                dpg.add_text("General Settings", color=(255, 255, 255))
                dpg.add_separator()
                
                # Rounded corners option (Windows 11 only)
                dpg.add_checkbox(label="Rounded Window Corners", tag="chk_rounded_corners_cheat", default_value=True, callback=on_rounded_corners_changed)
                with dpg.tooltip("chk_rounded_corners_cheat", tag="tooltip_rounded_corners", show=show_tips):
                    dpg.add_text("Enable rounded corners on Windows 11")
                    dpg.add_text("(Has no effect on Windows 10)")
                ALL_TOOLTIP_TAGS.append("tooltip_rounded_corners")
                
                dpg.add_separator()
                
                # FPS Cap toggle
                fps_cap_enabled = Active_Config.get("fps_cap_enabled", False)
                dpg.add_checkbox(
                    label="Cap FPS",
                    default_value=fps_cap_enabled,
                    tag="chk_fps_cap_enabled",
                    callback=on_fps_cap_toggle
                )
                with dpg.tooltip("chk_fps_cap_enabled", tag="tooltip_fps_cap_enabled", show=show_tips):
                    dpg.add_text("Limit ESP overlay framerate")
                ALL_TOOLTIP_TAGS.append("tooltip_fps_cap_enabled")
                
                # FPS Cap slider (visibility controlled by toggle)
                fps_slider_show = show_tips and fps_cap_enabled
                dpg.add_slider_int(
                    label="FPS Limit",
                    default_value=Active_Config.get("fps_cap_value", 144),
                    min_value=30,
                    max_value=500,
                    tag="slider_fps_cap",
                    callback=on_fps_cap_change,
                    show=fps_cap_enabled
                )
                with dpg.tooltip("slider_fps_cap", tag="tooltip_fps_cap_slider", show=fps_slider_show):
                    dpg.add_text("Maximum frames per second for overlay")
                ALL_TOOLTIP_TAGS.append("tooltip_fps_cap_slider")
                
                dpg.add_separator()
                
                # Hide on Tab-Out toggle
                dpg.add_checkbox(
                    label="Hide When Tabbed Out",
                    default_value=Active_Config.get("hide_on_tabout", True),
                    tag="chk_hide_on_tabout",
                    callback=on_hide_on_tabout_toggle
                )
                with dpg.tooltip("chk_hide_on_tabout", tag="tooltip_hide_on_tabout", show=show_tips):
                    dpg.add_text("Automatically hide overlay and menu when not focused on CS2")
                ALL_TOOLTIP_TAGS.append("tooltip_hide_on_tabout")
                
                dpg.add_separator()
                
                # Show status labels toggle
                dpg.add_checkbox(
                    label="Show Status Labels",
                    default_value=Active_Config.get("show_status_labels", True),
                    tag="chk_show_status_labels",
                    callback=on_show_status_labels_toggle
                )
                with dpg.tooltip("chk_show_status_labels", tag="tooltip_show_status_labels", show=show_tips):
                    dpg.add_text("Show feature status labels in the overlay")
                ALL_TOOLTIP_TAGS.append("tooltip_show_status_labels")
            
            # Keybinds sub-tab
            with dpg.tab(label="Keybinds"):
                dpg.add_text("Keybinds", color=(255, 255, 255))
                dpg.add_separator()
                dpg.add_text("Bind ESC key to remove a keybind.")
                dpg.add_separator()
                
                # Menu toggle key button
                with dpg.group(horizontal=True):
                    dpg.add_text("Menu Toggle Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('menu_toggle_key', 'f8').upper()}",
                        tag="btn_bind_menu_toggle_cheat",
                        callback=on_menu_toggle_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_menu_toggle_cheat", tag="tooltip_menu_toggle_key", show=show_tips):
                    dpg.add_text("Key or mouse button to show/hide the cheat menu")
                ALL_TOOLTIP_TAGS.append("tooltip_menu_toggle_key")
                
                dpg.add_spacer(height=2)
                
                # ESP toggle key button
                with dpg.group(horizontal=True):
                    dpg.add_text("ESP Toggle Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('esp_toggle_key', 'capslock').upper()}",
                        tag="btn_bind_esp_toggle_cheat",
                        callback=on_esp_toggle_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_esp_toggle_cheat", tag="tooltip_esp_toggle_key", show=show_tips):
                    dpg.add_text("Key or mouse button to enable/disable ESP overlay")
                ALL_TOOLTIP_TAGS.append("tooltip_esp_toggle_key")
                
                dpg.add_spacer(height=2)
                
                # Exit key button
                with dpg.group(horizontal=True):
                    dpg.add_text("Exit Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('exit_key', 'f7').upper()}",
                        tag="btn_bind_exit_cheat",
                        callback=on_exit_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_exit_cheat", tag="tooltip_exit_key", show=show_tips):
                    dpg.add_text("Key or mouse button to close the cheat")
                ALL_TOOLTIP_TAGS.append("tooltip_exit_key")
                
                dpg.add_spacer(height=2)
                
                # Aimbot key button
                with dpg.group(horizontal=True):
                    dpg.add_text("Aimbot Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('aimbot_key', 'alt').upper()}",
                        tag="btn_bind_aimbot_cheat",
                        callback=on_aimbot_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_aimbot_cheat", tag="tooltip_aimbot_key", show=show_tips):
                    dpg.add_text("Hold this key or mouse button to activate aimbot")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_key")
                
                dpg.add_spacer(height=2)
                
                # Triggerbot key button
                with dpg.group(horizontal=True):
                    dpg.add_text("Triggerbot Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('triggerbot_key', 'x').upper()}",
                        tag="btn_bind_triggerbot_cheat",
                        callback=on_triggerbot_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_triggerbot_cheat", tag="tooltip_triggerbot_key", show=show_tips):
                    dpg.add_text("Hold this key or mouse button to activate triggerbot")
                ALL_TOOLTIP_TAGS.append("tooltip_triggerbot_key")
                
                dpg.add_spacer(height=2)
                
                # ACS key button
                with dpg.group(horizontal=True):
                    dpg.add_text("ACP Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('acs_key', 'v').upper()}",
                        tag="btn_bind_acs_cheat",
                        callback=on_acs_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_acs_cheat", tag="tooltip_acs_key", show=show_tips):
                    dpg.add_text("Hold this key or mouse button to activate auto crosshair placement")
                ALL_TOOLTIP_TAGS.append("tooltip_acs_key")
                
                dpg.add_spacer(height=2)
                
                # Aimbot toggle key button
                with dpg.group(horizontal=True):
                    dpg.add_text("Aimbot Toggle Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('aimbot_toggle_key', '').upper() or 'NONE'}",
                        tag="btn_bind_aimbot_toggle_cheat",
                        callback=on_aimbot_toggle_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_aimbot_toggle_cheat", tag="tooltip_aimbot_toggle_key", show=show_tips):
                    dpg.add_text("Key or mouse button to toggle aimbot on/off")
                ALL_TOOLTIP_TAGS.append("tooltip_aimbot_toggle_key")
                
                dpg.add_spacer(height=2)
                
                # Head-only mode toggle key button
                with dpg.group(horizontal=True):
                    dpg.add_text("Head-Only Toggle Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('head_only_toggle_key', '').upper() or 'NONE'}",
                        tag="btn_bind_head_only_toggle_cheat",
                        callback=on_head_only_toggle_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_head_only_toggle_cheat", tag="tooltip_head_only_toggle_key", show=show_tips):
                    dpg.add_text("Key or mouse button to toggle head-only mode for triggerbot")
                ALL_TOOLTIP_TAGS.append("tooltip_head_only_toggle_key")
                
                dpg.add_spacer(height=2)
                
                # RCS toggle key button
                with dpg.group(horizontal=True):
                    dpg.add_text("RCS Toggle Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('rcs_toggle_key', '').upper() or 'NONE'}",
                        tag="btn_bind_rcs_toggle_cheat",
                        callback=on_rcs_toggle_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_rcs_toggle_cheat", tag="tooltip_rcs_toggle_key", show=show_tips):
                    dpg.add_text("Key or mouse button to toggle RCS on/off")
                ALL_TOOLTIP_TAGS.append("tooltip_rcs_toggle_key")
                
                dpg.add_spacer(height=2)
                
                # Anti-AFK toggle key button
                with dpg.group(horizontal=True):
                    dpg.add_text("Anti-AFK Toggle Key:")
                    dpg.add_button(
                        label=f"{Keybinds_Config.get('anti_afk_toggle_key', '').upper() or 'NONE'}",
                        tag="btn_bind_anti_afk_toggle_cheat",
                        callback=on_anti_afk_toggle_key_button,
                        width=150
                    )
                with dpg.tooltip("btn_bind_anti_afk_toggle_cheat", tag="tooltip_anti_afk_toggle_key", show=show_tips):
                    dpg.add_text("Key or mouse button to toggle anti-AFK on/off")
                ALL_TOOLTIP_TAGS.append("tooltip_anti_afk_toggle_key")


def create_main_window(title, window_type="loader"):
    """
    Create the main application window with all UI components.
    
    Structure:
    - Custom titlebar (draggable)
    - Separator line
    - Tab bar with content based on window_type
    
    Args:
        title: Application title (displayed in titlebar)
        window_type: "loader" or "cheat" - determines which tab to show
    """
    with dpg.window(label="Main Window", tag="main_window", no_title_bar=True):
        # Custom titlebar at top
        create_titlebar(title, window_type)
        
        # Visual separator between titlebar and content
        dpg.add_separator()
        
        # Main content area with tabs
        with dpg.tab_bar():
            if window_type == "loader":
                create_settings_tab()
                create_info_tab()
            else:
                # Cheat window has ESP controls, offsets display, and settings
                create_esp_tab()
                update_esp_preview()  # Initialize ESP preview
                create_aimbot_tab()
                create_settings_tab_cheat()
                create_colors_tab()
                create_config_tab()
                if loader_settings.get("ShowDebugTab", False):
                    create_debug_tab()


# =============================================================================
# APPLICATION SETUP
# =============================================================================

def setup_viewport(title, window_type="loader"):
    """
    Configure and show the DearPyGui viewport (OS window).
    
    Args:
        title: Window title (used for Win32 window lookup)
        window_type: "loader" or "cheat" - determines positioning
    """
    # Create viewport (the actual OS window)
    dpg.create_viewport(
        title=title, 
        width=Active_Config.get("window_width", WINDOW_WIDTH), 
        height=Active_Config.get("window_height", WINDOW_HEIGHT), 
        decorated=False  # No OS title bar/borders
    )
    
    # Setup DearPyGui internals
    dpg.setup_dearpygui()
    
    # Make our window fill the entire viewport
    dpg.set_primary_window("main_window", True)
    
    # Keep window above other windows
    dpg.configure_viewport(0, always_on_top=True)
    
    # Center loader window on screen, position cheat at center of CS2 window
    if window_type == "loader":
        # Center window on screen
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        # Calculate center position
        current_width = Active_Config.get("window_width", WINDOW_WIDTH)
        current_height = Active_Config.get("window_height", WINDOW_HEIGHT)
        center_x = (screen_width - current_width) // 2
        center_y = (screen_height - current_height) // 2
        
        # Set viewport position
        dpg.set_viewport_pos([center_x, center_y])
    else:
        # Position cheat window at center of CS2 window
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        cs2_x, cs2_y, cs2_width, cs2_height = get_cs2_window_rect()
        if cs2_x is not None and cs2_width is not None:
            # Calculate center of CS2 window
            current_width = Active_Config.get("window_width", WINDOW_WIDTH)
            current_height = Active_Config.get("window_height", WINDOW_HEIGHT)
            center_x = cs2_x + (cs2_width - current_width) // 2
            center_y = cs2_y + (cs2_height - current_height) // 2
            
            # Clamp to screen bounds to prevent window from going off-screen
            center_x = max(0, min(center_x, screen_width - current_width))
            center_y = max(0, min(center_y, screen_height - current_height))
            
            dpg.set_viewport_pos([center_x, center_y])
        elif app_state["last_window_pos"]:
            # Fallback to loader's saved position if CS2 rect not available
            x, y = app_state["last_window_pos"]
            dpg.set_viewport_pos([x, y])
    
    # Show the viewport
    dpg.show_viewport()


def apply_window_styles(title):
    """
    Apply Win32 window styles after viewport is visible.
    
    Must be called after show_viewport() so the window exists.
    
    Args:
        title: Window title (used to find the Win32 HWND)
    """
    # Find the Win32 window handle by title
    hwnd = win32gui.FindWindow(None, title)
    
    if hwnd:
        # Store for drag handling
        drag_state["hwnd"] = hwnd
        
        # Hide from taskbar
        hide_from_taskbar(hwnd)
        
        # Enable Windows 11 rounded corners if checkbox is enabled
        if loader_settings.get("RoundedCorners", True):
            enable_rounded_corners(hwnd)
        
        # Apply menu transparency for cheat window
        if "cheat" in title.lower():
            transparency = Active_Config.get("menu_transparency", 255)
            apply_menu_transparency(transparency)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
# Application initialization and window management.
# Coordinates loader → cheat window transition and cleanup.
# =============================================================================

def reset_drag_state():
    """Reset drag state for new window."""
    drag_state["is_dragging"] = False
    drag_state["start_mouse_x"] = 0
    drag_state["start_mouse_y"] = 0
    drag_state["start_window_x"] = 0
    drag_state["start_window_y"] = 0
    drag_state["hwnd"] = None


def run_window(window_type="loader"):
    """
    Run a DearPyGui window of the specified type.
    
    Args:
        window_type: "loader" or "cheat"
    
    Returns:
        bool: True if should switch to cheat window, False otherwise
    """
    # Reset state
    reset_drag_state()
    app_state["switch_to_cheat"] = False
    
    # Get base app title (use cached if available)
    if app_state["app_title"] is None:
        app_state["app_title"] = get_app_title()
    
    # Set titles based on window type
    # Titlebar: "App Title - Loader" or "App Title"
    # Win32 background name: "loader" or "cheat" (for FindWindow)
    if window_type == "loader":
        titlebar_title = f"{app_state['app_title']} - Loader"
        win32_title = "loader"
        app_state["current_window"] = "loader"
    else:
        titlebar_title = app_state["app_title"]
        win32_title = "cheat"
        app_state["current_window"] = "cheat"
    
    # Initialize DearPyGui context
    dpg.create_context()
    
    # Setup fonts (must be before setup_dearpygui)
    if window_type == "cheat":
        setup_fonts()
    
    # Build UI (titlebar shows user-facing title)
    create_main_window(titlebar_title, window_type)
    
    # Configure and show viewport (Win32 title used for window lookup)
    setup_viewport(win32_title, window_type)
    
    # Apply Win32 window styles (must be after viewport is shown)
    apply_window_styles(win32_title)
    
    # Save loader window position before starting cheat overlay
    if window_type == "loader" and drag_state["hwnd"]:
        try:
            rect = win32gui.GetWindowRect(drag_state["hwnd"])
            app_state["last_window_pos"] = (rect[0], rect[1])
        except Exception:
            pass
        # Apply fixed loader theme (dark gray + white)
        apply_loader_theme()
    
    # Start ESP overlay for cheat window
    if window_type == "cheat":
        start_esp_overlay()
        start_aimbot_thread()
        start_triggerbot_thread()
        start_anti_flash_thread()
        start_fov_changer_thread()
        start_rcs_thread()
        start_acs_thread()
        start_hitsound_thread()
        # Apply saved colorway theme
        colorway = Active_Config.get("menu_colorway", "Default")
        apply_colorway(colorway)
        # Apply saved font
        font = Active_Config.get("menu_font", "Default")
        apply_font(font)
    
    # FPS update counter for cheat window
    fps_update_counter = 0
    
    # Menu toggle state for cheat window visibility
    key_was_pressed = False
    window_visible = True
    
    # State trackers for other hotkeys (to prevent immediate triggering after binding)
    run_window.esp_key_was_pressed = False
    run_window.exit_key_was_pressed = False
    run_window.aimbot_toggle_key_was_pressed = False
    run_window.head_only_toggle_key_was_pressed = False
    run_window.rcs_toggle_key_was_pressed = False
    run_window.anti_afk_toggle_key_was_pressed = False
    
    # =============================================================================
    # MAIN RENDER LOOP
    # =============================================================================
    # Runs every frame (~144+ FPS) until window closes.
    # Handles: window dragging, keybind listening, menu toggle, ESP FPS updates
    # =============================================================================
    
    # Debug terminal update counter
    terminal_update_counter = 0
    
    # Performance display update counter
    perf_update_counter = 0
    
    # CS2 monitoring counter (check every ~60 frames to reduce CPU usage)
    cs2_check_counter = 0
    
    # CS2 foreground check counter and state
    foreground_check_counter = 0
    cs2_was_foreground = True
    menu_hidden_by_auto = False  # Track if menu was hidden by auto-hide (not user toggle)
    
    # Flag for one-time color picker initialization
    color_pickers_initialized = False
    frame_count = 0
    
    # Config file watcher - track current config files for auto-refresh
    config_watcher_counter = 0
    last_config_files = set(get_available_configs()) if window_type == "cheat" else set()
    
    while dpg.is_dearpygui_running():
        # Initialize color pickers after several frames (workaround for DearPyGui bug)
        # We initialize multiple times to ensure it sticks
        if window_type == "cheat" and not color_pickers_initialized:
            frame_count += 1
            if frame_count == 5:  # First attempt at frame 5
                initialize_color_pickers()
            elif frame_count == 15:  # Second attempt at frame 15
                initialize_color_pickers()
            elif frame_count == 30:  # Final attempt at frame 30
                initialize_color_pickers()
                color_pickers_initialized = True
        
        # Update debug terminal every 30 frames (reduces CPU usage)
        if window_type == "cheat":
            terminal_update_counter += 1
            if terminal_update_counter >= 30:
                update_debug_terminal()
                terminal_update_counter = 0
        
        # Update performance display every 30 frames if auto-refresh is enabled and performance tab is visible
        if window_type == "cheat":
            try:
                if dpg.does_item_exist("perf_auto_refresh") and dpg.get_value("perf_auto_refresh") and dpg.is_item_shown("tab_performance"):
                    perf_update_counter += 1
                    if perf_update_counter >= 30:
                        update_performance_display()
                        perf_update_counter = 0
            except:
                pass
        
        # Config file watcher - check for new/deleted configs every ~120 frames (~2 seconds)
        if window_type == "cheat":
            config_watcher_counter += 1
            if config_watcher_counter >= 120:
                config_watcher_counter = 0
                current_config_files = set(get_available_configs())
                if current_config_files != last_config_files:
                    last_config_files = current_config_files
                    refresh_config_list()
                    debug_log("Config folder changed - list refreshed", "INFO")
        
        # Check if CS2 is still running (only for cheat window)
        if window_type == "cheat":
            cs2_check_counter += 1
            if cs2_check_counter >= 60:  # Check every ~60 frames
                cs2_check_counter = 0
                if not is_cs2_running():
                    debug_log("CS2 closed - exiting cheat", "INFO")
                    dpg.stop_dearpygui()
        
        # Auto-hide cheat window when CS2 is not in foreground (check every 10 frames)
        if window_type == "cheat":
            foreground_check_counter += 1
            if foreground_check_counter >= 10:
                foreground_check_counter = 0
                cs2_is_foreground = is_cs2_foreground()
                
                # Check if cheat window is currently the foreground window
                try:
                    current_foreground = win32gui.GetForegroundWindow()
                    cheat_is_foreground = (current_foreground == drag_state.get("hwnd"))
                    
                    # If cheat window is in foreground, ensure it's above the overlay
                    if cheat_is_foreground and drag_state.get("hwnd"):
                        win32gui.SetWindowPos(
                            drag_state["hwnd"],
                            win32con.HWND_TOPMOST,
                            0, 0, 0, 0,
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
                        )
                except:
                    pass
                
                if cs2_is_foreground and not cs2_was_foreground:
                    # CS2 came back to foreground - show window if it was hidden by auto-hide
                    if menu_hidden_by_auto and window_visible:
                        win32gui.ShowWindow(drag_state["hwnd"], win32con.SW_SHOW)
                        menu_hidden_by_auto = False
                    cs2_was_foreground = True
                elif not cs2_is_foreground and cs2_was_foreground:
                    # CS2 lost foreground - hide window if setting enabled
                    if Active_Config.get("hide_on_tabout", True) and window_visible:
                        win32gui.ShowWindow(drag_state["hwnd"], win32con.SW_HIDE)
                        menu_hidden_by_auto = True
                    cs2_was_foreground = False
        
        # Handle window dragging (check mouse state, move window if dragging)
        update_window_drag()
        
        # Handle keybind listening for cheat window (detect key presses for binding)
        if window_type == "cheat" and keybind_listener["listening"]:
            # Check all keys in the VK_CODE_MAP for binding
            for vk_code, key_name in VK_CODE_MAP.items():
                if win32api.GetAsyncKeyState(vk_code) & 0x8000:
                    # Check if ESC key pressed - if so, set keybind to "none"
                    if key_name == "esc":
                        if keybind_listener["target"] == "menu_toggle_key":
                            Keybinds_Config["menu_toggle_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_menu_toggle_cheat", "NONE")
                            except:
                                pass
                        elif keybind_listener["target"] == "esp_toggle_key":
                            Keybinds_Config["esp_toggle_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_esp_toggle_cheat", "NONE")
                            except:
                                pass
                        elif keybind_listener["target"] == "exit_key":
                            Keybinds_Config["exit_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_exit_cheat", "NONE")
                            except:
                                pass
                        elif keybind_listener["target"] == "aimbot_key":
                            Keybinds_Config["aimbot_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_aimbot_cheat", "NONE")
                            except:
                                pass
                        elif keybind_listener["target"] == "triggerbot_key":
                            Keybinds_Config["triggerbot_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_triggerbot_cheat", "NONE")
                            except:
                                pass
                        elif keybind_listener["target"] == "acs_key":
                            Keybinds_Config["acs_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_acs_cheat", "NONE")
                            except:
                                pass
                        elif keybind_listener["target"] == "aimbot_toggle_key":
                            Keybinds_Config["aimbot_toggle_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_aimbot_toggle_cheat", "NONE")
                            except:
                                pass
                        elif keybind_listener["target"] == "head_only_toggle_key":
                            Keybinds_Config["head_only_toggle_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_head_only_toggle_cheat", "NONE")
                            except:
                                pass
                        elif keybind_listener["target"] == "rcs_toggle_key":
                            Keybinds_Config["rcs_toggle_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_rcs_toggle_cheat", "NONE")
                            except:
                                pass
                        elif keybind_listener["target"] == "anti_afk_toggle_key":
                            Keybinds_Config["anti_afk_toggle_key"] = "none"
                            try:
                                dpg.set_item_label("btn_bind_anti_afk_toggle_cheat", "NONE")
                            except:
                                pass
                    else:
                        # Normal key binding
                        if keybind_listener["target"] == "menu_toggle_key":
                            Keybinds_Config["menu_toggle_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_menu_toggle_cheat", key_name.upper())
                            except:
                                pass
                        elif keybind_listener["target"] == "esp_toggle_key":
                            Keybinds_Config["esp_toggle_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_esp_toggle_cheat", key_name.upper())
                            except:
                                pass
                        elif keybind_listener["target"] == "exit_key":
                            Keybinds_Config["exit_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_exit_cheat", key_name.upper())
                            except:
                                pass
                        elif keybind_listener["target"] == "aimbot_key":
                            Keybinds_Config["aimbot_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_aimbot_cheat", key_name.upper())
                            except:
                                pass
                        elif keybind_listener["target"] == "triggerbot_key":
                            Keybinds_Config["triggerbot_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_triggerbot_cheat", key_name.upper())
                            except:
                                pass
                        elif keybind_listener["target"] == "acs_key":
                            Keybinds_Config["acs_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_acs_cheat", key_name.upper())
                            except:
                                pass
                        elif keybind_listener["target"] == "aimbot_toggle_key":
                            Keybinds_Config["aimbot_toggle_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_aimbot_toggle_cheat", key_name.upper())
                            except:
                                pass
                        elif keybind_listener["target"] == "head_only_toggle_key":
                            Keybinds_Config["head_only_toggle_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_head_only_toggle_cheat", key_name.upper())
                            except:
                                pass
                        elif keybind_listener["target"] == "rcs_toggle_key":
                            Keybinds_Config["rcs_toggle_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_rcs_toggle_cheat", key_name.upper())
                            except:
                                pass
                        elif keybind_listener["target"] == "anti_afk_toggle_key":
                            Keybinds_Config["anti_afk_toggle_key"] = key_name
                            try:
                                dpg.set_item_label("btn_bind_anti_afk_toggle_cheat", key_name.upper())
                            except:
                                pass
                    
                    # Save keybinds after change
                    save_keybinds()
                    
                    keybind_listener["listening"] = False
                    keybind_listener["target"] = None
                    # Set all key state trackers to True to prevent immediate triggering
                    key_was_pressed = True
                    run_window.esp_key_was_pressed = True
                    run_window.exit_key_was_pressed = True
                    run_window.aimbot_toggle_key_was_pressed = True
                    run_window.head_only_toggle_key_was_pressed = True
                    run_window.rcs_toggle_key_was_pressed = True
                    run_window.anti_afk_toggle_key_was_pressed = True
                    break
        
        # Handle menu toggle key for cheat window visibility
        if window_type == "cheat" and not keybind_listener["listening"]:
            menu_key = Keybinds_Config.get("menu_toggle_key", "f8").lower()
            
            # Skip if keybind is set to "none"
            if menu_key != "none":
                vk_code = KEY_NAME_TO_VK.get(menu_key, 0x77)  # Default to F8 if key not found
                
                key_pressed = win32api.GetAsyncKeyState(vk_code) & 0x8000
                if key_pressed and not key_was_pressed:
                    # Key just pressed - toggle visibility
                    window_visible = not window_visible
                    if window_visible:
                        win32gui.ShowWindow(drag_state["hwnd"], win32con.SW_SHOW)
                    else:
                        win32gui.ShowWindow(drag_state["hwnd"], win32con.SW_HIDE)
                key_was_pressed = key_pressed
        
        # Handle ESP toggle key
        if window_type == "cheat" and not keybind_listener["listening"]:
            esp_key = Keybinds_Config.get("esp_toggle_key", "capslock").lower()
            
            # Skip if keybind is set to "none"
            if esp_key != "none":
                esp_vk_code = KEY_NAME_TO_VK.get(esp_key, 0x14)  # Default to capslock if key not found
                
                esp_key_pressed = win32api.GetAsyncKeyState(esp_vk_code) & 0x8000
                if esp_key_pressed and not run_window.esp_key_was_pressed:
                    # Key just pressed - toggle ESP
                    current_esp_state = Active_Config.get("esp_enabled", True)
                    new_esp_state = not current_esp_state
                    Active_Config["esp_enabled"] = new_esp_state
                    if esp_overlay["settings"]:
                        esp_overlay["settings"]["esp_enabled"] = new_esp_state
                    save_settings()
                    # Update checkbox in UI
                    try:
                        dpg.set_value("chk_esp_enabled", new_esp_state)
                    except:
                        pass
                    debug_log(f"ESP toggled: {'ON' if new_esp_state else 'OFF'}", "INFO")
                run_window.esp_key_was_pressed = esp_key_pressed
        
        # Handle aimbot toggle key
        if window_type == "cheat" and not keybind_listener["listening"]:
            aimbot_toggle_key = Keybinds_Config.get("aimbot_toggle_key", "").lower()
            
            # Skip if keybind is set to "none" or empty
            if aimbot_toggle_key and aimbot_toggle_key != "none":
                aimbot_toggle_vk_code = KEY_NAME_TO_VK.get(aimbot_toggle_key)
                
                if aimbot_toggle_vk_code:
                    aimbot_toggle_key_pressed = win32api.GetAsyncKeyState(aimbot_toggle_vk_code) & 0x8000
                    if aimbot_toggle_key_pressed and not run_window.aimbot_toggle_key_was_pressed:
                        # Key just pressed - toggle aimbot
                        current_aimbot_state = Active_Config.get("aimbot_enabled", False)
                        new_aimbot_state = not current_aimbot_state
                        Active_Config["aimbot_enabled"] = new_aimbot_state
                        if aimbot_state["settings"]:
                            aimbot_state["settings"]["aimbot_enabled"] = new_aimbot_state
                        if esp_overlay["settings"]:
                            esp_overlay["settings"]["aimbot_enabled"] = new_aimbot_state
                        save_settings()
                        # Update checkbox in UI
                        try:
                            dpg.set_value("chk_aimbot_enabled", new_aimbot_state)
                        except:
                            pass
                        debug_log(f"Aimbot toggled: {'ON' if new_aimbot_state else 'OFF'}", "INFO")
                    run_window.aimbot_toggle_key_was_pressed = aimbot_toggle_key_pressed
        
        # Handle head-only toggle key
        if window_type == "cheat" and not keybind_listener["listening"]:
            head_only_toggle_key = Keybinds_Config.get("head_only_toggle_key", "").lower()
            
            # Skip if keybind is set to "none" or empty
            if head_only_toggle_key and head_only_toggle_key != "none":
                head_only_toggle_vk_code = KEY_NAME_TO_VK.get(head_only_toggle_key)
                
                if head_only_toggle_vk_code:
                    head_only_toggle_key_pressed = win32api.GetAsyncKeyState(head_only_toggle_vk_code) & 0x8000
                    if head_only_toggle_key_pressed and not run_window.head_only_toggle_key_was_pressed:
                        # Key just pressed - toggle head-only mode
                        current_head_only_state = Active_Config.get("triggerbot_head_only", False)
                        new_head_only_state = not current_head_only_state
                        Active_Config["triggerbot_head_only"] = new_head_only_state
                        if triggerbot_state["settings"]:
                            triggerbot_state["settings"]["triggerbot_head_only"] = new_head_only_state
                        save_settings()
                        # Update checkbox in UI
                        try:
                            dpg.set_value("chk_triggerbot_head_only", new_head_only_state)
                        except:
                            pass
                        debug_log(f"Triggerbot head-only mode toggled: {'ON' if new_head_only_state else 'OFF'}", "INFO")
                    run_window.head_only_toggle_key_was_pressed = head_only_toggle_key_pressed
        
        # Handle RCS toggle key
        if window_type == "cheat" and not keybind_listener["listening"]:
            rcs_toggle_key = Keybinds_Config.get("rcs_toggle_key", "").lower()
            
            # Skip if keybind is set to "none" or empty
            if rcs_toggle_key and rcs_toggle_key != "none":
                rcs_toggle_vk_code = KEY_NAME_TO_VK.get(rcs_toggle_key)
                
                if rcs_toggle_vk_code:
                    rcs_toggle_key_pressed = win32api.GetAsyncKeyState(rcs_toggle_vk_code) & 0x8000
                    if rcs_toggle_key_pressed and not run_window.rcs_toggle_key_was_pressed:
                        # Key just pressed - toggle RCS
                        current_rcs_state = Active_Config.get("rcs_enabled", False)
                        new_rcs_state = not current_rcs_state
                        Active_Config["rcs_enabled"] = new_rcs_state
                        if rcs_state["settings"]:
                            rcs_state["settings"]["rcs_enabled"] = new_rcs_state
                        save_settings()
                        # Update checkbox in UI
                        try:
                            dpg.set_value("chk_rcs_enabled", new_rcs_state)
                        except:
                            pass
                        debug_log(f"RCS toggled: {'ON' if new_rcs_state else 'OFF'}", "INFO")
                    run_window.rcs_toggle_key_was_pressed = rcs_toggle_key_pressed
        
        # Handle Anti-AFK toggle key
        if window_type == "cheat" and not keybind_listener["listening"]:
            anti_afk_toggle_key = Keybinds_Config.get("anti_afk_toggle_key", "").lower()
            
            # Skip if keybind is set to "none" or empty
            if anti_afk_toggle_key and anti_afk_toggle_key != "none":
                anti_afk_toggle_vk_code = KEY_NAME_TO_VK.get(anti_afk_toggle_key)
                
                if anti_afk_toggle_vk_code:
                    anti_afk_toggle_key_pressed = win32api.GetAsyncKeyState(anti_afk_toggle_vk_code) & 0x8000
                    if anti_afk_toggle_key_pressed and not run_window.anti_afk_toggle_key_was_pressed:
                        # Key just pressed - toggle anti-AFK
                        current_anti_afk_state = Active_Config.get("anti_afk_enabled", False)
                        new_anti_afk_state = not current_anti_afk_state
                        Active_Config["anti_afk_enabled"] = new_anti_afk_state
                        save_settings()
                        # Update checkbox in UI
                        try:
                            dpg.set_value("chk_anti_afk_enabled", new_anti_afk_state)
                        except:
                            pass
                        # Start/stop the anti-AFK thread
                        if new_anti_afk_state:
                            start_anti_afk_thread()
                        else:
                            stop_anti_afk_thread()
                        debug_log(f"Anti-AFK toggled: {'ON' if new_anti_afk_state else 'OFF'}", "INFO")
                    run_window.anti_afk_toggle_key_was_pressed = anti_afk_toggle_key_pressed
        
        # Exit Key handling (works in both loader and cheat windows)
        exit_key_name = Keybinds_Config.get("exit_key", "f7")
        
        # Skip if keybind is set to "none"
        if exit_key_name != "none":
            exit_vk = KEY_NAME_TO_VK.get(exit_key_name)
            
            if exit_vk:
                exit_key_state = win32api.GetAsyncKeyState(exit_vk) & 0x8000
                
                if exit_key_state and not run_window.exit_key_was_pressed:
                    # Key just pressed - exit the application
                    run_window.exit_key_was_pressed = True
                    debug_log("Exit key pressed - closing application", "INFO")
                    dpg.stop_dearpygui()
                    
                elif not exit_key_state:
                    # Key released
                    run_window.exit_key_was_pressed = False
        
        # Update ESP FPS display in cheat window
        if window_type == "cheat":
            fps_update_counter += 1
            if fps_update_counter >= 30:  # Update every 30 frames
                fps_update_counter = 0
                try:
                    # Update FPS display
                    dpg.set_value("esp_fps_value", str(esp_overlay.get("fps", 0)))
                    
                    # Update status
                    if esp_overlay.get("running", False):
                        dpg.set_value("esp_status", "Running")
                        dpg.configure_item("esp_status", color=(0, 255, 0))
                    else:
                        dpg.set_value("esp_status", "Stopped")
                        dpg.configure_item("esp_status", color=(255, 0, 0))
                except Exception:
                    pass
        
        # Render frame
        dpg.render_dearpygui_frame()
    
    # Stop ESP overlay when window closes
    if window_type == "cheat":
        stop_esp_overlay()
        stop_aimbot_thread()
        stop_triggerbot_thread()
        stop_anti_flash_thread()
        stop_fov_changer_thread()
        stop_rcs_thread()
        stop_acs_thread()
    
    # Cleanup
    dpg.destroy_context()
    
    # Return whether we should switch to cheat window
    return app_state["switch_to_cheat"]


def initialize_config_folders():
    """
    Initialize configuration folder structure.
    Creates configs/Settings and configs/Keybinds folders if they don't exist.
    Called at application startup.
    """
    try:
        # Create main configs folder if it doesn't exist
        if not os.path.exists(CONFIGS_FOLDER):
            os.makedirs(CONFIGS_FOLDER)
            debug_log(f"Created configs folder: {CONFIGS_FOLDER}", "SUCCESS")
        
        # Create Settings subfolder
        if not os.path.exists(SETTINGS_FOLDER):
            os.makedirs(SETTINGS_FOLDER)
            debug_log(f"Created Settings folder: {SETTINGS_FOLDER}", "SUCCESS")
        
        # Create Keybinds subfolder
        if not os.path.exists(KEYBINDS_FOLDER):
            os.makedirs(KEYBINDS_FOLDER)
            debug_log(f"Created Keybinds folder: {KEYBINDS_FOLDER}", "SUCCESS")
        
        debug_log("Config folders initialized", "INFO")
    except Exception as e:
        debug_log(f"Failed to create config folders: {str(e)}", "ERROR")


def cleanup_temp_folder():
    """
    Delete the temp folder and all its contents.
    Save settings and keybinds before exit.
    Called automatically on script exit.
    """
    # Save settings and keybinds before exit
    save_settings()
    save_keybinds()
    
    # Stop ESP overlay if running
    stop_esp_overlay()
    
    # Stop aimbot thread if running
    stop_aimbot_thread()
    
    # Stop triggerbot thread if running
    stop_triggerbot_thread()
    
    # Stop anti-flash thread if running
    stop_anti_flash_thread()
    
    # Stop FOV changer thread if running
    stop_fov_changer_thread()
    
    # Stop RCS thread if running
    stop_rcs_thread()
    
    # Stop ACS thread if running
    stop_acs_thread()
    
    # Stop anti-AFK thread if running
    stop_anti_afk_thread()
    
    try:
        if os.path.exists(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)
    except Exception:
        pass  # Silently fail if cleanup fails


def main():
    """
    Main application entry point.
    
    Application flow:
    1. Create temp folder (for local offsets)
    2. Initialize config folders (Settings, Keybinds)
    3. Register cleanup function (atexit) to delete temp folder
    4. Run loader window
       - User configures settings (console, offset source)
       - User clicks Launch button
    5. If Launch clicked, run cheat window
       - ESP overlay starts automatically
       - Menu can be toggled with bound key (default F8)
       - User closes window to exit
    6. Cleanup runs automatically (delete temp, stop ESP)
    
    Window lifecycle:
    - Loader: Configure → Load offsets → Switch to cheat
    - Cheat: ESP running → Menu toggle → Close to exit
    """
    # Check if temp folder already exists (indicates another instance running)
    if os.path.exists(TEMP_FOLDER):
        # Get app title for message box
        try:
            app_title = get_app_title()
        except:
            app_title = FALLBACK_TITLE
        
        # Show topmost message box
        ctypes.windll.user32.MessageBoxW(
            0,  # No parent window
            "Error: Cheat is already running or failed to close at last exit. Either close the cheat or delete the 'temp' folder",
            f"{app_title} - Error",
            0x00001000 | 0x00000010 | 0x00040000  # MB_SYSTEMMODAL | MB_ICONERROR | MB_TOPMOST
        )
        # Exit the script
        sys.exit(1)
    
    # Create temp folder for offset downloads
    try:
        os.makedirs(TEMP_FOLDER, exist_ok=True)
    except Exception:
        pass  # Continue even if folder creation fails
    
    # Initialize config folders
    initialize_config_folders()
    
    # Check for --config argument from loader
    config_file = None
    if len(sys.argv) > 2 and sys.argv[1] == "--config":
        config_name = sys.argv[2]
        # Assume loader's directory is parent of current temp directory
        loader_dir = os.path.dirname(os.getcwd())
        config_file = os.path.join(loader_dir, 'configs', 'Settings', config_name)
        if not os.path.exists(config_file):
            # Try without Settings subfolder
            config_file = os.path.join(loader_dir, 'configs', config_name)
        if not os.path.exists(config_file):
            debug_log(f"Specified config file not found: {config_file}", "ERROR")
            config_file = None
    
    # Load settings from specified file or autosave.json or use defaults
    load_settings(config_file)
    
    # Load keybinds from autosave.json or use defaults
    load_keybinds()
    
    if SKIP_LOADER:
        # Set loader settings for cheat
        loader_settings["ShowDebugTab"] = True
        loader_settings["UseLocalOffsets"] = False
        Active_Config["show_tooltips"] = True
        
        # Download sound files to temp folder
        sound_files = [
            (HITMARKER_SOUND_URL, "hitmarker.wav"),
            (METALHIT_SOUND_URL, "metalhit.wav"),
            (CRITICALHIT_SOUND_URL, "criticalhit.wav")
        ]
        
        for url, filename in sound_files:
            try:
                filepath = os.path.join(TEMP_FOLDER, filename)
                urllib.request.urlretrieve(url, filepath)
                print(f"[SOUNDS] Downloaded {filename}")
            except Exception as e:
                print(f"[SOUNDS] Failed to download {filename}: {e}")
        
        # Wait for CS2 to be running
        print("Waiting for CS2...")
        while not is_cs2_running():
            time.sleep(0.5)
        
        print("CS2 detected. Loading offsets...")
        
        # Load offsets from GitHub
        if not load_and_initialize_offsets(use_local=False):
            print("Failed to load offsets. Exiting.")
            sys.exit(1)
        
        # Register cleanup function to run on exit
        atexit.register(cleanup_temp_folder)
        
        if RESET_GRAPHICS:
            pyautogui.hotkey('ctrl', 'shift', 'win', 'b')
            time.sleep(RESET_GRAPHICS_DELAY)
        
        # Run cheat window
        debug_log("Starting cheat window (skipping loader)...", "INFO")
        run_window("cheat")
        
    else:
        # Register cleanup function to run on exit
        atexit.register(cleanup_temp_folder)
        
        debug_log("Starting loader window...", "INFO")
        
        # Run loader window
        should_switch = run_window("loader")
        
        # If Test was clicked, run cheat window
        if should_switch:
            debug_log("Switching to cheat window...", "INFO")
            run_window("cheat")


if __name__ == "__main__":
    main()

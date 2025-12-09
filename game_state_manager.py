# ========== GAME_STATE_MANAGER.PY ==========
# File untuk mengelola game state dan event handling

import pygame
from enum import Enum

from control_settings import ControlSettings

class GameState(Enum):
    """Enum untuk game states"""
    INTRO = 0
    MENU = 1
    GAME_MODE_SELECT = 2
    PLAYING = 3
    GAME_OVER = 4
    ONLINE_MODE_SELECT = 5      # Pilih local/online
    ONLINE_HOST_JOIN = 6        # Pilih host/join
    ONLINE_HOST_WAITING = 7     # Host menunggu client
    ONLINE_JOIN_CONNECTING = 8  # Client mencoba connect

class GameStateManager:
    """Mengelola state dan event handling game"""
    
    def __init__(self):
        self.state = GameState.MENU
        self.menu_state = "main"
        self.is_multiplayer = False
        self.control_settings = ControlSettings()
    
    def set_state(self, new_state):
        """Set game state"""
        self.state = new_state
    
    def set_menu_state(self, new_menu_state):
        """Set menu state"""
        self.menu_state = new_menu_state
    
    def set_multiplayer(self, is_multiplayer):
        """Set mode: singleplayer atau multiplayer"""
        self.is_multiplayer = is_multiplayer
    
    def handle_escape_key(self, sound_manager=None, game_instance=None):
        """Handle escape key press dengan music switching - DIUBAH: tambah parameter default"""
        if self.state == GameState.GAME_OVER:
            print("⎋ ESC: Game Over → Main Menu")
            self.state = GameState.MENU
            self.menu_state = "main"
            if game_instance:
                game_instance.current_music_mode = "menu"
            # HANYA play musik jika benar-benar perlu
            if game_instance and game_instance.current_music_mode != "menu" and sound_manager:
                sound_manager.play_menu_music()
            return True
        
        if self.state == GameState.PLAYING:
            print("⎋ ESC: Playing → Pause (handled by pause manager)")
            return False
        
        elif self.state == GameState.GAME_MODE_SELECT:
            print("⎋ ESC: Mode Select → Main Menu")
            self.state = GameState.MENU
            self.menu_state = "main"
            return True
        
        elif self.state == GameState.MENU and self.menu_state != "main":
            print(f"⎋ ESC: {self.menu_state} → Main Menu")
            self.menu_state = "main"
            return True
        
        return False
    
    def should_draw_menu(self):
        """Check apakah harus draw menu"""
        return self.state in [GameState.MENU, GameState.GAME_MODE_SELECT]
    
    def should_draw_game(self):
        """Check apakah harus draw game"""
        return self.state == GameState.PLAYING
    
    def should_draw_game_over(self):
        """Check apakah harus draw game over"""
        return self.state == GameState.GAME_OVER
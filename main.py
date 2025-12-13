# ========== SPACE DEFENDER - MAIN.PY ==========
# File utama untuk menjalankan game

import sys
import pygame
import random
import json
import threading
import time

# Import dari modul-modul terpisah
from sound_manager import SoundManager
from image_manager import ImageManager
from player import Player
from bullet import Bullet
from powerup import PowerUpManager
from button import Button
from menu_pages import MenuPages
from game_over_page import GameOverPage
from game_state_manager import GameState, GameStateManager
from game_manager import GameManager
from ui_renderer import UIRenderer
from divider_manager import DividerManager
from pause_manager import PauseManager
from intro_page import IntroPage
from utils import resource_path
from network_manager import NetworkManager
from online_menu_pages import OnlineMenuPages

# ========== KONSTANTA GAME ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Space Defender"

# ========== WARNA ==========
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# ========== CLASS UTAMA GAME ==========
class Game:
    """Kelas utama untuk mengelola seluruh game"""
    def __init__(self):
        # Penting: inisialisasi pygame hanya ketika dipanggil dari entrypoint,
        # mencegah child process (multiprocessing spawn) mengeksekusi init lagi.
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            # Jika mixer gagal (headless build), lanjut tanpa crash
            pass

        # ===== SETUP WINDOW =====
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # ===== FONT UNTUK UI =====
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)
        fonts = {
            'font': self.font,
            'small_font': self.small_font,
            'tiny_font': self.tiny_font
        }
        
        # ===== MANAGER =====
        self.sound_manager = SoundManager()
        self.image_manager = ImageManager()
        self.state_manager = GameStateManager()
        self.game_manager = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui_renderer = UIRenderer(self.screen, fonts)

        # Inisialisasi pause icon melalui UI Renderer
        self.ui_renderer.init_pause_icon(self.image_manager)
        self.pause_icon_rect = self.ui_renderer.get_pause_icon_rect()
        self.pause_icon_hover = False
        
        # Set dependencies untuk game_manager
        self.game_manager.sound_manager = self.sound_manager
        self.game_manager.image_manager = self.image_manager
        
        # ===== PAGE MANAGERS =====
        self.menu_pages = MenuPages()
        self.game_over_page = GameOverPage()
        
        # ===== STATUS GAME =====
        self.running = True
        
        # ===== SPRITE GROUPS =====
        self.player1 = None
        self.player2 = None
        self.bullets_p1 = pygame.sprite.Group()
        self.bullets_p2 = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        # ===== POWERUP MANAGER =====
        self.powerup_manager_p1 = None
        self.powerup_manager_p2 = None
        
        # ===== VARIABEL GAME =====
        self.score_p1 = 0
        self.score_p2 = 0
        self.enemies_killed_p1 = 0
        self.enemies_killed_p2 = 0
        self.spawn_timer = 0
        self.spawn_rate = 120
        self.difficulty_level = 1
        self.wave_time = 0
        
        # ===== TOMBOL UI =====
        self.button_templates = {}  # Template untuk tombol berdasarkan state  <-- INI YANG BENAR
        self.current_buttons = {}   # Tombol yang aktif di state saat ini
        
        # ===== SETTINGS =====
        self.mute_sfx = False
        self.mute_music = False
        self._apply_mute_settings()

        self._init_pause_icon()

        # ===== DIVIDER MANAGER =====
        self.divider_manager = DividerManager(SCREEN_WIDTH, SCREEN_HEIGHT)

        # ===== PAUSE MANAGER =====
        self.pause_manager = PauseManager(self.sound_manager)

        # ===== GAME OVER =====
        self.game_over_sound_played = False  # Flag untuk mencegah repeat

        # ===== BACKGROUND STARS =====
        self.stars = []
        self.num_stars = 80
        for _ in range(self.num_stars):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.uniform(0.1, 0.3)
            size = random.randint(1, 2)
            brightness = random.randint(80, 200)
            self.stars.append([x, y, speed, size, brightness])

        # ===== INTRO PAGE =====
        self.intro_page = IntroPage(self.image_manager, self.sound_manager)

        # ===== ONLINE HOST STATUS TRACKING =====
        self.last_host_connection_status = False  # <-- TAMBAH INI
        self.host_info_sent = False
        
        # ===== STATE AWAL = INTRO =====
        self.state_manager.set_state(GameState.INTRO)
        self.current_music_mode = "silent"  # TAMBAH: Mode silent untuk intro

        # ===== NETWORK MANAGER =====
        self.network_manager = NetworkManager()
        self.online_menu_pages = OnlineMenuPages()

        # NEW: client/host sync flags & info
        self.client_waiting_popup = False       # client shows small popup after connect
        self.remote_host_info = None            # last host_info payload received by client
        self.client_cancel_alert_time = 0       # host shows 3s alert when client cancels

        # ===== INISIALISASI =====
        self.sound_manager.stop_pause_music()
        self._init_button_templates()  # <-- TAMBAHKAN INI DI AKHIR __init__

    def _init_pause_icon(self):
        """Initialize pause icon attributes (called from __init__)."""
        self.pause_icon = None
        self.pause_icon_rect = None
        self.pause_icon_hover = False
        # Grab icon from image manager if available
        try:
            self.pause_icon = self.image_manager.images.get('pause')
        except Exception:
            self.pause_icon = None
        # Default placement (will be adjusted each frame in draw)
        default_w, default_h = (40, 40)
        if self.pause_icon:
            default_w = self.pause_icon.get_width()
            default_h = self.pause_icon.get_height()
        # Default x (right margin 10) and default y (singleplayer)
        self.pause_icon_rect = pygame.Rect(SCREEN_WIDTH - default_w - 10, 90, default_w, default_h)
    
    def init_game(self):
        """Inisialisasi variabel game baru dengan difficulty settings - FIXED"""
        # ===== RESET GAME OVER SOUND FLAG =====
        self.game_over_sound_played = False
        
        # ===== HENTIKAN SEMUA MUSIK TERLEBIH DAHULU =====
        self.sound_manager.stop_pause_music()
        self.sound_manager.stop_music()
        
        # ===== DAPATKAN SETTINGS DIFFICULTY =====
        difficulty_settings = self.game_manager.difficulty_manager.get_settings()
        player_health = difficulty_settings["player_health"]  # AMBIL HEALTH DARI DIFFICULTY
        
        # ===== BUAT PEMAIN =====
        if self.state_manager.is_multiplayer:
            # PERBAIKAN: Tentukan apakah ini online atau local multiplayer
            is_online = hasattr(self.network_manager, 'connected') and self.network_manager.connected
            
            if is_online and self.network_manager.is_host:
                print("🖥️ HOST MODE: P1 = Host (controllable), P2 = Client (dummy)")
                
                # Player 1 - CONTROLLABLE (Host) - ambil dari control_settings
                self.player1 = Player(100, SCREEN_HEIGHT - 60, 
                                    self.image_manager.images['player'], player_id=1)
                
                # AMBIL SCHEME DARI CONTROL SETTINGS, bukan hardcode
                control_scheme_p1 = self.state_manager.control_settings.get_control_scheme_for_player(1)
                self.player1.control_scheme = control_scheme_p1
                self.player1.health = player_health
                
                # Player 2 - DUMMY REMOTE (Client) - otomatis lawan dari P1
                self.player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60,
                                    self.image_manager.images['player2'], player_id=2)
                self.player2.is_dummy = True
                self.player2.is_remote = True
                self.player2.health = player_health
                
                # Powerup managers
                self.powerup_manager_p1 = PowerUpManager(self.player1)
                self.powerup_manager_p2 = PowerUpManager(self.player2)
                
                # Kirim control scheme player 2 ke client - lawan dari P1
                try:
                    control_scheme_p2 = self.state_manager.control_settings.get_control_scheme_for_player(2)
                    self.network_manager.send_control_scheme(control_scheme_p2)
                    print(f"📤 Host sent control scheme to client: {control_scheme_p2}")
                except:
                    pass
                
            elif is_online and not self.network_manager.is_host:
                print("🔗 CLIENT MODE: P1 = Host (dummy), P2 = Client (controllable)")
                
                # Player 1 - DUMMY REMOTE (Host)
                self.player1 = Player(100, SCREEN_HEIGHT - 60, 
                                    self.image_manager.images['player'], player_id=1)
                self.player1.is_dummy = True
                self.player1.is_remote = True
                self.player1.health = player_health
                
                # Player 2 - CONTROLLABLE (Client)
                self.player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60,
                                    self.image_manager.images['player2'], player_id=2)
                
                # Terima control scheme dari host - GUNAKAN host_info yang sudah diterima
                received_scheme = None

                # PRIORITAS 1: Gunakan remote_host_info yang sudah diterima
                if self.remote_host_info:
                    controls = self.remote_host_info.get('controls', {})
                    received_scheme = controls.get('p2')  # Client adalah player 2
                    print(f"✅ Client using control scheme from host_info: {received_scheme}")

                # PRIORITAS 2: Fallback ke metode lama (receive_control_scheme)
                if not received_scheme:
                    for _ in range(5):  # Cukup 5x retry
                        try:
                            temp_scheme = self.network_manager.receive_control_scheme()
                            if temp_scheme:
                                received_scheme = temp_scheme
                                print(f"✅ Client received control scheme via old method: {received_scheme}")
                                break
                        except:
                            pass
                        pygame.time.delay(50)

                # PRIORITAS 3: Default fallback
                if not received_scheme:
                    received_scheme = "arrows"
                    print("⚠️ Client using default control scheme (arrows)")

                # TERAPKAN control scheme
                self.player2.control_scheme = received_scheme
                
                if received_scheme:
                    self.player2.control_scheme = received_scheme
                    print(f"✅ Client received control scheme from host: {received_scheme}")
                else:
                    # Fallback: jika tidak ada dari host, gunakan default
                    self.player2.control_scheme = "arrows"
                    print("⚠️ Client using default control scheme (arrows)")
                
                self.player2.health = player_health
                
                # Powerup managers - HANYA P2 punya powerup manager (P1 dummy)
                self.powerup_manager_p1 = None
                self.powerup_manager_p2 = PowerUpManager(self.player2)
            
            else:
                # ===== LOCAL MULTIPLAYER (bukan online) =====
                print("👥 Local Multiplayer: Both players controlled locally")
                self.player1 = Player(100, SCREEN_HEIGHT - 60, 
                                    self.image_manager.images['player'], player_id=1)
                self.player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60,
                                    self.image_manager.images['player2'], player_id=2)
                
                # TERAPKAN HEALTH DARI DIFFICULTY
                self.player1.health = player_health
                self.player2.health = player_health
                
                # TERAPKAN control scheme dari settings
                control_scheme_p1 = self.state_manager.control_settings.get_control_scheme_for_player(1)
                control_scheme_p2 = self.state_manager.control_settings.get_control_scheme_for_player(2)
                
                self.player1.control_scheme = control_scheme_p1
                self.player2.control_scheme = control_scheme_p2
                
                # Inisialisasi powerup manager untuk kedua player
                self.powerup_manager_p1 = PowerUpManager(self.player1)
                self.powerup_manager_p2 = PowerUpManager(self.player2)
        
        else:
            # ===== SINGLEPLAYER =====
            print("👤 Starting Singleplayer game")
            player_width = self.image_manager.images['player'].get_width()
            player_x = (SCREEN_WIDTH // 2) - (player_width // 2)
            
            self.player1 = Player(player_x, SCREEN_HEIGHT - 60, 
                                self.image_manager.images['player'], player_id=1)
            self.player2 = None
            
            self.player1.health = player_health
            
            control_scheme_p1 = self.state_manager.control_settings.get_control_scheme_for_player(1)
            self.player1.control_scheme = control_scheme_p1
            
            self.powerup_manager_p1 = PowerUpManager(self.player1)
            self.powerup_manager_p2 = None
        
        # ===== KOSONGKAN SPRITE GROUPS =====
        self.bullets_p1.empty()
        self.bullets_p2.empty()
        self.enemies.empty()
        self.powerups.empty()
        self.enemy_bullets.empty()
        
        # ===== RESET VARIABEL =====
        self.score_p1 = 0
        self.score_p2 = 0
        self.enemies_killed_p1 = 0
        self.enemies_killed_p2 = 0
        self.spawn_timer = 0
        self.spawn_rate = 120
        self.difficulty_level = 1
        self.wave_time = 0
        
        self.game_over_sound_played = False
        
        if hasattr(self.game_manager, '_enemies_passed'):
            self.game_manager._enemies_passed.clear()

        # PERBAIKAN: Reset posisi musik saat mulai game baru
        self.current_music_mode = "game"
        self.sound_manager.stop_music()
        self.sound_manager.music_position = 0
        self.sound_manager.play_game_music(0)
        print("🔄 Game initialized with game music")
        print(f"🎯 Difficulty: {self.game_manager.difficulty_manager.difficulty_mode.upper()}")
        print(f"❤️  Player Health: {player_health}")

    def _apply_mute_settings(self):
        """Terapkan setting mute ke SoundManager - VERSI DIPERBAIKI"""
        # Jangan reset volume ke default, gunakan nilai yang sudah ada
        if self.mute_sfx:
            self.sound_manager.set_sfx_volume(0.0)
        else:
            # Pertahankan nilai SFX volume yang sudah ada
            pass  # Biarkan SoundManager mengatur volumenya sendiri
            
        if self.mute_music:
            self.sound_manager.set_music_volume(0.0)
            self.sound_manager.pause_music()
        else:
            # Pertahankan nilai music volume yang sudah ada  
            self.sound_manager.unpause_music()
            # Volume musik akan diatur oleh SoundManager sendiri

    def handle_events(self):
        """Handle semua event input dari user - FIXED dengan proteksi popup"""
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        # Handle skip intro
        if self.state_manager.state == GameState.INTRO:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    self.intro_page.skip_intro()
            return
        
        # ===== PERBAIKAN: JIKA CLIENT DALAM POPUP, BLOKIR SEMUA EVENT LAIN =====
        if (self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING and 
            self.client_waiting_popup):
            print("🛡️ Popup aktif - hanya proses klik pada popup")
            # Hanya proses event yang terkait popup
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Handle click langsung ke method popup
                    self.handle_join_connecting_click(mouse_pos)
                    return
            return
        
        # ===== HANDLE SEMUA EVENT DENGAN BENAR =====
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            # ===== MOUSE CLICK =====
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # PERBAIKAN: Skip jika dalam popup waiting (sudah ditangani di atas)
                if (self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING and 
                    self.client_waiting_popup):
                    continue
                
                # Handle control selector click
                if self.state_manager.state == GameState.GAME_MODE_SELECT:
                    if self.menu_pages.handle_control_selector_click(mouse_pos, self.state_manager.control_settings):
                        continue
                
                # Handle input box untuk online join
                if self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING:
                    # PERBAIKAN: Jangan proses jika dalam popup
                    if not self.client_waiting_popup:
                        input_rect = pygame.Rect(100, 170, 400, 40)
                        if input_rect.collidepoint(mouse_pos):
                            self.online_menu_pages.input_active = True
                            print("🔤 Text input activated")
                        else:
                            self.online_menu_pages.input_active = False
                            print("🔤 Text input deactivated")
                
                # ===== Pause icon click =====
                if (self.state_manager.state == GameState.PLAYING and 
                    self.ui_renderer.get_pause_icon_rect() and 
                    self.ui_renderer.get_pause_icon_rect().collidepoint(mouse_pos)):
                    # toggle pause
                    self.pause_manager.toggle_pause()
                    if self.pause_manager.is_paused:
                        try:
                            self.sound_manager.play_pause_music()
                        except Exception:
                            pass
                        self.current_music_mode = "pause"
                    else:
                        try:
                            self.sound_manager.stop_pause_music()
                        except Exception:
                            pass
                        self.current_music_mode = "game"
                        try:
                            self.sound_manager.play_game_music()
                        except Exception:
                            pass
                    continue

                # Panggil handler click yang sesuai
                self.handle_all_clicks(mouse_pos, event)
            
            # ===== KEYBOARD =====
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.handle_escape_key()
                
                # PERBAIKAN: Handle keyboard input untuk IP address
                if (self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING and 
                    self.online_menu_pages.input_active and
                    not self.client_waiting_popup):  # PERBAIKAN: Jangan proses jika dalam popup
                    
                    if event.key == pygame.K_BACKSPACE:
                        self.online_menu_pages.input_text = self.online_menu_pages.input_text[:-1]
                        print(f"⌨️ Backspace: '{self.online_menu_pages.input_text}'")
                    
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        # Try connect ketika tekan Enter
                        if self.online_menu_pages.input_text:
                            print(f"↩️ Enter pressed, connecting to {self.online_menu_pages.input_text}")
                            threading.Thread(
                                target=self.network_manager.connect_to_host,
                                args=(self.online_menu_pages.input_text,),
                                daemon=True
                            ).start()

                            self.client_waiting_popup = True  # biar muncul popup "Connecting..."
                    
                    elif event.key == pygame.K_ESCAPE:
                        # ESC untuk keluar dari input mode
                        self.online_menu_pages.input_active = False
                        print("🔤 Text input deactivated (ESC)")
                    
                    else:
                        # Hanya allow karakter IP address
                        valid_chars = '0123456789.'
                        if event.unicode in valid_chars and len(self.online_menu_pages.input_text) < 15:
                            self.online_menu_pages.input_text += event.unicode
                            print(f"⌨️ Typed: '{self.online_menu_pages.input_text}'")
                
                elif self.state_manager.state == GameState.GAME_MODE_SELECT:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        self.state_manager.control_settings.handle_keypress(event.key)
        
        # ===== HANDLE SETTINGS EVENTS =====
        if (self.state_manager.state == GameState.MENU and 
            self.state_manager.menu_state == "settings"):
            self.menu_pages.handle_settings_events(
                events, mouse_pos, self.sound_manager, self.game_manager, self.current_buttons
            )
        
        # ===== HANDLE SCROLL UNTUK HELP MENU =====
        if (self.state_manager.state == GameState.MENU and 
            self.state_manager.menu_state == "help"):
            self.menu_pages.handle_help_scroll(events, mouse_pos)
        
        # ===== UPDATE HOVER STATUS =====
        self.update_all_buttons_hover(mouse_pos)

    def handle_all_clicks(self, mouse_pos, event):
        """Handle semua jenis click berdasarkan state - FIXED ONLINE STATES"""
        # JANGAN proses click jika sedang di settings menu dan event sudah ditangani slider
        if (self.state_manager.state == GameState.MENU and 
            self.state_manager.menu_state == "settings"):
            # Cek jika click terjadi pada area slider
            for slider_name, slider in self.menu_pages.sliders.items():
                slider_rect = pygame.Rect(
                    slider.rect.x, 
                    slider.rect.y - 30,
                    slider.rect.width + 100,
                    slider.rect.height + 60
                )
                if slider_rect.collidepoint(mouse_pos):
                    return
        
        # PERBAIKAN: Langsung panggil handler yang sesuai berdasarkan state
        if self.state_manager.state == GameState.MENU:
            self.handle_menu_click(mouse_pos)
        
        elif self.state_manager.state == GameState.GAME_MODE_SELECT:
            self.handle_mode_select_click(mouse_pos)
        
        elif self.state_manager.state == GameState.ONLINE_MODE_SELECT:
            self.handle_online_mode_click(mouse_pos)  # PERBAIKAN: Pastikan ini dipanggil
        
        elif self.state_manager.state == GameState.ONLINE_HOST_JOIN:
            self.handle_host_join_click(mouse_pos)  # PERBAIKAN: Pastikan ini dipanggil
        
        elif self.state_manager.state == GameState.ONLINE_HOST_WAITING:
            self.handle_host_waiting_click(mouse_pos)  # PERBAIKAN: Pastikan ini dipanggil
        
        elif self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING:
            self.handle_join_connecting_click(mouse_pos)  # PERBAIKAN: Pastikan ini dipanggil
        
        elif self.state_manager.state == GameState.PLAYING:
            if self.pause_manager.is_paused and not self.pause_manager.countdown_active:
                self.handle_mouse_click(mouse_pos)
        
        elif self.state_manager.state == GameState.GAME_OVER:
            self.handle_game_over_click(mouse_pos)

    def handle_keyboard_events(self, event):
        """Handle keyboard events"""
        if event.key == pygame.K_ESCAPE:
            self.handle_escape_key()
        
        elif self.state_manager.state == GameState.GAME_MODE_SELECT:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.state_manager.control_settings.handle_keypress(event.key)

    def handle_escape_key(self):
        """Handle escape key press - FIXED MUSIC"""
        if self.state_manager.state == GameState.PLAYING:
            if self.pause_manager.is_paused:
                if not self.pause_manager.countdown_active:
                    self.pause_manager.start_countdown()
                    # Hapus tombol pause karena mulai countdown
                    self.current_buttons.clear()
            else:
                # Toggle pause dan dapatkan status baru
                is_now_paused = self.pause_manager.toggle_pause()
                if is_now_paused:
                    self.load_buttons_for_state()
                    print(f"⎋ ESC: Game paused, loaded buttons")
        
        # PERBAIKAN: Tambahkan handling untuk ONLINE_HOST_WAITING
        elif self.state_manager.state == GameState.ONLINE_HOST_WAITING:
            print("⎋ ESC: Leaving host waiting screen")
            # Kirim event ke client jika masih connected
            if self.network_manager.connected:
                try:
                    self.network_manager.send_event('host_cancelled', {})
                except:
                    pass
                self.network_manager.disconnect()
                self.state_manager.set_state(GameState.ONLINE_HOST_JOIN)
                self.current_buttons.clear()
                self.client_waiting_popup = False
                self.remote_host_info = None
                # PERBAIKAN: Reset juga host_info di network_manager
                if hasattr(self.network_manager, 'host_info'):
                    self.network_manager.host_info = None
        
        else:
            if self.state_manager.handle_escape_key(self.sound_manager, self):
                self.current_buttons.clear()
                if self.state_manager.state == GameState.MENU:
                    self.pause_manager.is_paused = False
                    self.pause_manager.countdown_active = False
                    # PERBAIKAN: Pastikan musik menu diputar
                    if self.current_music_mode != "menu":
                        self.sound_manager.stop_music()
                        self.sound_manager.play_menu_music()
                        self.current_music_mode = "menu"
    
    def handle_mouse_click(self, mouse_pos):
        """Handle mouse click event - PERBAIKAN PAUSE MUSIC"""
        # ===== Pause icon click =====
        if (self.state_manager.state == GameState.PLAYING and 
            self.ui_renderer.get_pause_icon_rect() and 
            self.ui_renderer.get_pause_icon_rect().collidepoint(mouse_pos)):
            
            print("⏸️ Pause icon clicked")
            # toggle pause dan dapatkan status baru
            is_now_paused = self.pause_manager.toggle_pause()
            
            # PERBAIKAN: Load tombol pause jika game menjadi paused
            if is_now_paused:
                self.load_buttons_for_state()
                print(f"🔄 Loaded pause buttons: {list(self.current_buttons.keys())}")
            else:
                # Jika game menjadi unpaused, hapus tombol
                self.current_buttons.clear()

        # ===== HANDLE PAUSE BUTTONS =====
        if self.pause_manager.is_paused and not self.pause_manager.countdown_active:
            if 'resume' in self.current_buttons and self.current_buttons['resume'].is_clicked(mouse_pos):
                self.pause_manager.start_countdown()
                return

            if 'quit_pause' in self.current_buttons and self.current_buttons['quit_pause'].is_clicked(mouse_pos):
                print("🏠 Returning to menu from pause")
                # If host, notify client to exit too
                if self.network_manager and self.network_manager.connected and self.network_manager.is_host:
                    try:
                        self.network_manager.send_event('exit_game', {})
                    except:
                        pass

                # stop pause music and return to menu
                self.sound_manager.stop_pause_music()
                self.pause_manager.is_paused = False
                self.pause_manager.countdown_active = False
                self.state_manager.set_state(GameState.MENU)
                self.state_manager.set_menu_state("main")
                self.current_buttons.clear()
                self.sound_manager.play_menu_music()
                self.current_music_mode = "menu"
                return

        # Toggle pause via pause icon (only host can control pause)
        if (self.state_manager.state == GameState.PLAYING and 
            self.ui_renderer.get_pause_icon_rect() and 
            self.ui_renderer.get_pause_icon_rect().collidepoint(mouse_pos)):
            print("⏸️ Pause icon clicked")
            # toggle pause
            self.pause_manager.toggle_pause()
            
            # PERBAIKAN: Load tombol pause setelah toggle
            if self.pause_manager.is_paused:
                self.load_buttons_for_state()
                print(f"🔄 Loaded pause buttons: {list(self.current_buttons.keys())}")
            # only host can control pause/resume in online multiplayer
            if self.state_manager.is_multiplayer and self.network_manager.connected:
                if not self.network_manager.is_host:
                    # client cannot toggle pause
                    return
            # toggle normally
            prev = self.pause_manager.is_paused
            self.pause_manager.toggle_pause()
            # notify remote
            if self.network_manager and self.network_manager.connected and self.network_manager.is_host:
                try:
                    if self.pause_manager.is_paused:
                        self.network_manager.send_event('pause', {})
                    else:
                        self.network_manager.send_event('resume', {})
                except:
                    pass
            return
    
    def handle_menu_click(self, mouse_pos):
        """Handle click di main menu"""
        if self.state_manager.menu_state == "main":
            if 'start' in self.current_buttons and self.current_buttons['start'].is_clicked(mouse_pos):
                self.state_manager.set_state(GameState.GAME_MODE_SELECT)
                self.load_buttons_for_state()  # Load tombol baru
                return
            if 'help' in self.current_buttons and self.current_buttons['help'].is_clicked(mouse_pos):
                self.state_manager.set_menu_state("help")
                self.load_buttons_for_state()
                return
            if 'settings' in self.current_buttons and self.current_buttons['settings'].is_clicked(mouse_pos):
                self.state_manager.set_menu_state("settings")
                self.menu_pages.update_slider_values(self.sound_manager)
                self.load_buttons_for_state()
                return
            if 'quit' in self.current_buttons and self.current_buttons['quit'].is_clicked(mouse_pos):
                self.running = False
                return
        
        elif self.state_manager.menu_state == "help":
            if 'back_help' in self.current_buttons and self.current_buttons['back_help'].is_clicked(mouse_pos):
                self.state_manager.set_menu_state("main")
                self.load_buttons_for_state()
                return
        
        elif self.state_manager.menu_state == "settings":
            if 'back_settings' in self.current_buttons and self.current_buttons['back_settings'].is_clicked(mouse_pos):
                self.state_manager.set_menu_state("main")
                self.menu_pages.reset_settings_submenu()
                self.load_buttons_for_state()
                return
            
            if 'back_audio' in self.current_buttons and self.current_buttons['back_audio'].is_clicked(mouse_pos):
                self.menu_pages.settings_submenu = "main"
                self.load_buttons_for_state()
                return
            
            if 'back_difficulty' in self.current_buttons and self.current_buttons['back_difficulty'].is_clicked(mouse_pos):
                self.menu_pages.settings_submenu = "main"
                self.load_buttons_for_state()
                return
    
    def handle_mode_select_click(self, mouse_pos):
        """Handle click di game mode selection - FIXED"""
        print(f"🔍 Checking mode select buttons at {mouse_pos}")
        
        if 'back_mode' in self.current_buttons and self.current_buttons['back_mode'].is_clicked(mouse_pos):
            print("↩️ Returning to main menu from mode selection")
            self.state_manager.set_state(GameState.MENU)
            self.state_manager.set_menu_state("main")
            # JANGAN clear tombol, hanya hapus tombol mode select
            for btn in ['singleplayer', 'multiplayer', 'back_mode']:
                if btn in self.current_buttons:
                    del self.current_buttons[btn]
            return

        if 'singleplayer' in self.current_buttons and self.current_buttons['singleplayer'].is_clicked(mouse_pos):
            print("👤 Starting Singleplayer game")
            self.state_manager.set_multiplayer(False)
            self.state_manager.set_state(GameState.PLAYING)
            self.sound_manager.stop_music()
            self.init_game()
            # Hapus semua tombol karena masuk ke game
            self.current_buttons.clear()
            return

        if 'multiplayer' in self.current_buttons and self.current_buttons['multiplayer'].is_clicked(mouse_pos):
            print("👥 Entering Multiplayer selection")
            self.state_manager.set_state(GameState.ONLINE_MODE_SELECT)
            # Hapus tombol mode select saja
            for btn in ['singleplayer', 'multiplayer', 'back_mode']:
                if btn in self.current_buttons:
                    del self.current_buttons[btn]
            return
    
    def handle_game_over_click(self, mouse_pos):
        """Handle click di game over screen - FIXED BUTTON LOADING"""
        if 'restart' in self.current_buttons and self.current_buttons['restart'].is_clicked(mouse_pos):
            print("🔄 Restarting game...")
            self.state_manager.set_state(GameState.PLAYING)
            self.sound_manager.stop_music()  # Hentikan semua musik
            self.current_music_mode = "game"  # Update state musik
            self.init_game()
            self.current_buttons.clear()  # Clear tombol game over
        
        elif 'back_menu' in self.current_buttons and self.current_buttons['back_menu'].is_clicked(mouse_pos):
            print("🏠 Returning to main menu from game over")
            self.state_manager.set_state(GameState.MENU)
            self.state_manager.set_menu_state("main")
            self.current_buttons.clear()  # Clear tombol game over
            
            # PERBAIKAN: Hentikan semua musik dan mainkan menu music
            self.sound_manager.stop_music()
            self.sound_manager.play_menu_music()
            self.current_music_mode = "menu"

    def handle_online_mode_click(self, mouse_pos):
        """Handle click di online mode selection - FIXED STATE MANAGEMENT"""
        print(f"🔍 Checking online mode buttons at {mouse_pos}")
        print(f"🔍 Available buttons: {list(self.current_buttons.keys())}")
        
        if 'local_multiplayer' in self.current_buttons and self.current_buttons['local_multiplayer'].is_clicked(mouse_pos):
            print("👥 Starting Local Multiplayer game")
            self.state_manager.set_multiplayer(True)
            self.state_manager.set_state(GameState.PLAYING)
            self.sound_manager.stop_music()
            self.init_game()
            self.current_buttons.clear()  # PERBAIKAN: Clear tombol saat pindah state
            return

        if 'online_multiplayer' in self.current_buttons and self.current_buttons['online_multiplayer'].is_clicked(mouse_pos):
            print("🌐 Entering Online Multiplayer menu")
            self.state_manager.set_state(GameState.ONLINE_HOST_JOIN)
            self.current_buttons.clear()  # PERBAIKAN: Clear tombol saat pindah state
            return

        if 'back_online' in self.current_buttons and self.current_buttons['back_online'].is_clicked(mouse_pos):
            print("↩️ Returning to game mode selection")
            self.state_manager.set_state(GameState.GAME_MODE_SELECT)
            self.current_buttons.clear()  # PERBAIKAN: Clear tombol saat pindah state
            return
        
        print("❌ No button clicked in online mode selection")

    def handle_host_join_click(self, mouse_pos):
        """Handle click di host/join selection - FIXED"""
        print(f"🔍 Checking host/join buttons at {mouse_pos}")
        
        if 'host_game' in self.current_buttons and self.current_buttons['host_game'].is_clicked(mouse_pos):
            print("🖥️ Starting as Host...")
            
            # PERBAIKAN: Gunakan method dari NetworkManager
            if self.network_manager.start_host():
                # Reset UI state
                self.last_host_connection_status = False
                self.client_cancel_alert_time = 0
                
                self.state_manager.set_state(GameState.ONLINE_HOST_WAITING)
                self.current_buttons.clear()
                # PERBAIKAN: Load tombol untuk host waiting
                self.load_buttons_for_state()
                print(f"✅ Loaded buttons for host waiting: {list(self.current_buttons.keys())}")
            else:
                print(f"❌ Failed to start host: {self.network_manager.error_message}")
            return

        if 'join_game' in self.current_buttons and self.current_buttons['join_game'].is_clicked(mouse_pos):
            print("🔗 Entering Join menu...")
            self.state_manager.set_state(GameState.ONLINE_JOIN_CONNECTING)
            self.current_buttons.clear()  # Clear tombol saat pindah state
            return

        if 'back_host_join' in self.current_buttons and self.current_buttons['back_host_join'].is_clicked(mouse_pos):
            print("↩️ Returning to online mode selection")
            self.state_manager.set_state(GameState.ONLINE_MODE_SELECT)
            self.current_buttons.clear()  # Clear tombol saat kembali
            return
        
        print("❌ No button clicked in host/join selection")

    def handle_host_waiting_click(self, mouse_pos):
        """Handle click di host waiting screen - DIPERBAIKI"""
        print(f"🔍 Checking host waiting buttons at {mouse_pos}")
        print(f"📋 Available buttons: {list(self.current_buttons.keys())}")
        
        # Cek alert time (jika dalam 3 detik, ignore click di area alert)
        if self.client_cancel_alert_time > 0:
            current_time = pygame.time.get_ticks()
            if current_time - self.client_cancel_alert_time < 3000:
                # Abaikan klik di area alert
                alert_rect = pygame.Rect(50, 350, 700, 40)
                if alert_rect.collidepoint(mouse_pos):
                    return
        
        # ===== TOMBOL REFRESH IP =====
        if 'refresh_ip' in self.current_buttons and self.current_buttons['refresh_ip'].is_clicked(mouse_pos):
            print("🔄 Host: Refreshing ZeroTier IP...")
            self.network_manager.refresh_zerotier_ip()
            return
        
        # ===== TOMBOL START ONLINE GAME =====
        if 'start_online_game' in self.current_buttons and self.current_buttons['start_online_game'].is_clicked(mouse_pos):
            print("🎮 Host: START ONLINE GAME pressed")
            
            # 1. Pastikan client connected
            if not self.network_manager.connected:
                print("❌ No client connected!")
                return
            
            # 2. Kirim host_info dengan retry (sudah ada)
            for attempt in range(3):
                if self.sync_host_info_to_client():
                    print(f"✅ Host info sent (attempt {attempt+1})")
                    break
                else:
                    print(f"⚠️ Host info send failed, retrying...")
                    pygame.time.delay(100)
            
            # 3. TUNGGU 500ms untuk sinkronisasi
            pygame.time.delay(500)
            
            # 4. Kirim start_game event DUA KALI untuk memastikan sampai
            for i in range(2):
                try:
                    self.network_manager.send_event('start_game', {'timestamp': pygame.time.get_ticks()})
                    print(f"📤 Sent start_game event (attempt {i+1})")
                    pygame.time.delay(200)  # Delay antara 2 kali kirim
                except:
                    pass
            
            # 5. TUNGGU 200ms untuk memastikan client terima event
            pygame.time.delay(200)
            
            # 6. Host MASUK GAME
            print("🔄 Host: Starting game locally")
            self.state_manager.set_multiplayer(True)
            self.state_manager.set_state(GameState.PLAYING)
            self.sound_manager.stop_music()
            self.init_game()
            self.current_buttons.clear()
            return
        
        # ===== TOMBOL BACK (nama konsisten: 'back_host') =====
        if 'back_host' in self.current_buttons and self.current_buttons['back_host'].is_clicked(mouse_pos):
            print("↩️ Returning from host waiting")
            # Kirim event ke client jika masih connected
            if self.network_manager.connected:
                try:
                    self.network_manager.send_event('host_cancelled', {})
                except:
                    pass
            self.network_manager.disconnect()
            self.state_manager.set_state(GameState.ONLINE_HOST_JOIN)
            self.current_buttons.clear()
            # PERBAIKAN: Reset flag
            self.host_info_sent = False
            self.client_cancel_alert_time = 0
            return
        
        print(f"❌ No matching button clicked. Available: {list(self.current_buttons.keys())}")

    def check_stable_connection(self):
        """Cek apakah koneksi stabil dengan ping-pong sederhana"""
        if not self.network_manager.connected:
            return False
        
        try:
            # Coba kirim ping
            self.network_manager.send_event('ping', {'time': pygame.time.get_ticks()})
            return True
        except:
            return False

    def handle_join_connecting_click(self, mouse_pos):
        """Handle click di join connecting screen - DIPERBAIKI dengan blokir klik saat popup"""
        print(f"🔍 Checking join connecting buttons at {mouse_pos}")

        # ===== PERBAIKAN: KALO POPUP AKTIF, CUMA TOMBOL CANCEL YANG BISA DIPENCET =====
        if self.client_waiting_popup:
            # Cek jika ada waiting_popup_cancel_rect
            if hasattr(self, 'waiting_popup_cancel_rect') and self.waiting_popup_cancel_rect.collidepoint(mouse_pos):
                print("🚫 Client: Cancelling from waiting popup")
                # Kirim event cancel ke host
                if self.network_manager.connected:
                    try:
                        self.network_manager.send_event('client_cancelled', {})
                        print("📤 Sent client_cancelled event to host")
                    except Exception as e:
                        print(f"❌ Error sending cancel event: {e}")
                    self.network_manager.disconnect()
                self.state_manager.set_state(GameState.ONLINE_HOST_JOIN)
                self.current_buttons.clear()
                self.client_waiting_popup = False
                self.remote_host_info = None
                # PERBAIKAN: Reset error message juga
                self.online_menu_pages.error_message = ""
                if hasattr(self, 'waiting_popup_cancel_rect'):
                    delattr(self, 'waiting_popup_cancel_rect')
                return
            else:
                # Klik di luar tombol cancel popup? ABAIKAN!
                print("⚠️ Popup aktif - hanya tombol cancel yang bisa dipencet")
                return  # <-- INI YANG PENTING! JANGAN PROSES TOMBOL LAIN!
        
        # ===== HANYA JIKA TIDAK ADA POPUP, PROSES TOMBOL LAIN =====
        print("🔓 Tidak ada popup - proses tombol normal")
        
        # Tombol connect biasa (hanya jika tidak dalam popup)
        if not self.client_waiting_popup:
            if 'connect_to_host' in self.current_buttons and self.current_buttons['connect_to_host'].is_clicked(mouse_pos):
                print("✅ CONNECT TO HOST button clicked!")
                
                # PERBAIKAN: Reset error message sebelum connect baru
                self.online_menu_pages.error_message = ""
                
                if not self.online_menu_pages.input_text:
                    self.online_menu_pages.error_message = "Please enter host IP address"
                    self.online_menu_pages.error_timestamp = pygame.time.get_ticks()
                    return
                
                host_ip = self.online_menu_pages.input_text.strip()
                print(f"🔗 Attempting to connect to {host_ip}:{self.network_manager.port}")
                
                # Validasi IP
                if not self._validate_ip(host_ip):
                    self.online_menu_pages.error_message = "Invalid IP format (e.g., 192.168.1.100)"
                    self.online_menu_pages.error_timestamp = pygame.time.get_ticks()
                    return
                
                # Lakukan koneksi
                if self.network_manager.connect_to_host(host_ip):
                    # Connected sebagai client -> tampilkan popup menunggu
                    self.client_waiting_popup = True
                    self.remote_host_info = None
                    # Minta host info
                    try:
                        self.network_manager.send_event('client_connected', {'request': 'host_info'})
                        print("📤 Sent client_connected event to host")
                    except Exception as e:
                        print(f"❌ Error sending connected event: {e}")
                    # PERBAIKAN: Hapus tombol connect dari current_buttons
                    if 'connect_to_host' in self.current_buttons:
                        del self.current_buttons['connect_to_host']
                    if 'cancel_join' in self.current_buttons:
                        del self.current_buttons['cancel_join']
                    return
                else:
                    error = self.network_manager.error_message
                    self.online_menu_pages.error_message = error
                    self.online_menu_pages.error_timestamp = pygame.time.get_ticks()
                    print(f"❌ ERROR: {error}")
        
        # Tombol cancel biasa (di luar popup)
        if not self.client_waiting_popup:
            if 'cancel_join' in self.current_buttons and self.current_buttons['cancel_join'].is_clicked(mouse_pos):
                print("↩️ Cancelling join...")
                # Jika sudah connected, kirim cancel event ke host
                if self.network_manager.connected:
                    try:
                        self.network_manager.send_event('client_cancelled', {})
                    except:
                        pass
                    self.network_manager.disconnect()
                self.state_manager.set_state(GameState.ONLINE_HOST_JOIN)
                self.current_buttons.clear()
                self.client_waiting_popup = False
                self.remote_host_info = None
                # PERBAIKAN: Reset error message juga
                self.online_menu_pages.error_message = ""
                if hasattr(self, 'waiting_popup_cancel_rect'):
                    delattr(self, 'waiting_popup_cancel_rect')
                return
        
    def _validate_ip(self, ip):
        """Validate IP address format"""
        import re
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(p) <= 255 for p in parts)
        return False
    
    def update(self):
        """Game loop yang lebih robust"""
        if self.state_manager.state == GameState.INTRO:
            if self.intro_page.update():
                self.state_manager.set_state(GameState.MENU)
                self.sound_manager.play_menu_music()
                self.current_music_mode = "menu"
            return
        
        # ===== UPDATE NETWORK STATE =====
        if self.state_manager.state == GameState.ONLINE_HOST_WAITING:
            # PERBAIKAN: Update host untuk menerima koneksi
            if not self.network_manager.connected:
                self.network_manager.update_host()  # Cek koneksi baru
            
            # PERBAIKAN: Cek apakah status koneksi berubah
            current_status = self.network_manager.connected
            if current_status != self.last_host_connection_status:
                # Status berubah! Update tombol
                self.last_host_connection_status = current_status
                print(f"✅ Host connection status changed: {current_status}")
                
                # Update UI state
                self.update_host_waiting_status()
                
                # Reset host_info_sent flag
                self.host_info_sent = False
                
                # Coba kirim host_info jika baru terhubung
                if current_status:
                    print("📤 Client connected, attempting to send host info...")

            # Coba kirim host_info jika belum terkirim dan sudah connected
            if (self.network_manager.connected and not self.host_info_sent and 
                self.state_manager.state == GameState.ONLINE_HOST_WAITING):
                try:
                    payload = {
                        'difficulty': self.game_manager.difficulty_manager.difficulty_mode,
                        'controls': {
                            'p1': self.state_manager.control_settings.get_control_scheme_for_player(1),
                            'p2': self.state_manager.control_settings.get_control_scheme_for_player(2)
                        }
                    }
                    
                    # Coba kirim dengan retry
                    success = False
                    for attempt in range(3):  # Coba 3x
                        if self.network_manager.send_event('host_info', payload):
                            print(f"📤 Host sent host info to client (attempt {attempt+1}): {payload}")
                            self.host_info_sent = True
                            success = True
                            break
                        else:
                            print(f"⚠️ Failed to send host info, attempt {attempt+1}")
                            time.sleep(0.1)  # Tunggu sebentar sebelum retry
                    
                    if not success:
                        print("❌ Failed to send host info after 3 attempts")
                        
                except Exception as e:
                    print(f"❌ Error sending host info: {e}")

        # ===== NETWORK EVENT HANDLING (both sides) =====
        try:
            evt = self.network_manager.receive_event()
            if evt:
                etype = evt.get('type')
                payload = evt.get('payload', {})
                
                # CLIENT: receive host_info dan start_game
                if not self.network_manager.is_host:
                    if etype == 'host_info':
                        # PERBAIKAN: Simpan host_info ke SEMUA tempat yang diperlukan
                        self.remote_host_info = payload
                        
                        # Juga simpan ke network_manager.host_info
                        if hasattr(self.network_manager, 'host_info'):
                            self.network_manager.host_info = payload
                            print(f"📥 Client stored host_info in network_manager: {payload.get('difficulty')}")
                        
                        print(f"📥 Client received host info: Difficulty={payload.get('difficulty')}, Controls={payload.get('controls')}")
                        
                        # PERBAIKAN: Force update UI dengan menyimpan di instance game
                        self.remote_host_info = payload
                        
                        # PERBAIKAN: Kirim ACK ke host bahwa host_info diterima
                        try:
                            self.network_manager.send_event('host_info_received', {})
                        except:
                            pass
                    elif etype == 'start_game':
                        print(f"🔔 Client: Received START from host at {pygame.time.get_ticks()}")
                        
                        # CLEAR POPUP DULU sebelum apapun
                        self.client_waiting_popup = False
                        if hasattr(self, 'waiting_popup_cancel_rect'):
                            delattr(self, 'waiting_popup_cancel_rect')
                        
                        # PASTIKAN: Gunakan host_info yang sudah diterima
                        if self.remote_host_info:
                            # TERAPKAN difficulty dari host
                            if 'difficulty' in self.remote_host_info:
                                self.game_manager.difficulty_manager.set_difficulty(
                                    self.remote_host_info['difficulty']
                                )
                                print(f"🎯 Client applied host difficulty: {self.remote_host_info['difficulty']}")
                        
                        # MASUK KE GAME - TIDAK PERLU TUNGGU LAGI
                        print("🚀 Client: Entering game NOW")
                        self.state_manager.set_multiplayer(True)
                        self.state_manager.set_state(GameState.PLAYING)
                        self.sound_manager.stop_music()
                        self.init_game()  # Ini akan menggunakan remote_host_info untuk control scheme
                        self.current_buttons.clear()
                        
                        # KIRIM ACK ke host bahwa client sudah masuk game
                        try:
                            self.network_manager.send_event('client_ready', {})
                            print("📤 Client sent ready confirmation to host")
                        except:
                            pass

                    elif etype == 'host_cancelled':
                        print("⚠️ Host cancelled game")
                        # PERBAIKAN: Jangan pindah state, tetap di JOIN CONNECTING
                        self.client_waiting_popup = False
                        self.remote_host_info = None
                        # Reset juga host_info di network_manager
                        if hasattr(self.network_manager, 'host_info'):
                            self.network_manager.host_info = None
                        if hasattr(self.network_manager, 'reset_host_info'):
                            self.network_manager.reset_host_info()
                        
                        # PERBAIKAN: Set error message untuk ditampilkan selama 3 detik
                        self.online_menu_pages.error_message = "Host cancelled the game"
                        self.online_menu_pages.error_timestamp = pygame.time.get_ticks()
                        
                        # PERBAIKAN: Disconnect dari host
                        self.network_manager.disconnect()
                        
                        # PERBAIKAN: Update tombol
                        self.load_buttons_for_state()
                        
                        # PERBAIKAN: Hapus tombol popup jika ada
                        if hasattr(self, 'waiting_popup_cancel_rect'):
                            delattr(self, 'waiting_popup_cancel_rect')
                
                # HOST: receive client events
                else:
                    if etype == 'client_connected':
                        print("✅ Client connected, sending host info")
                        # PERBAIKAN: Pastikan status connected sudah benar
                        if not self.network_manager.connected:
                            self.network_manager.connected = True
                            self.last_host_connection_status = True
                        
                        # PERBAIKAN: TUNGGU SEBENTAR sebelum kirim host info
                        pygame.time.delay(100)  # Tunggu 100ms agar koneksi stabil
                        
                        # Kirim host info dengan retry
                        for attempt in range(3):
                            if self.sync_host_info_to_client():
                                break
                            else:
                                print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                                pygame.time.delay(50)
                        
                        # PERBAIKAN: Update tombol host untuk munculin START ONLINE GAME
                        self.update_host_waiting_status()
                    elif etype == 'client_cancelled':
                        print("⚠️ Client cancelled connection")
                        self.client_cancel_alert_time = pygame.time.get_ticks()
                        self.network_manager.disconnect()
                        # PERBAIKAN: Reset host_info_sent
                        self.host_info_sent = False
                        self.update_host_waiting_status()
                        self.remote_host_info = None
                        self.last_host_connection_status = False

        except Exception as e:
            print(f"⚠️ Network event error: {e}")

        # PERBAIKAN: Auto-hapus error message setelah 3 detik
        if (self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING and 
            self.online_menu_pages.error_message == "Host cancelled the game"):
            
            current_time = pygame.time.get_ticks()
            if current_time - self.online_menu_pages.error_timestamp >= 3000:
                self.online_menu_pages.error_message = ""
                print("🔄 Cleared host cancelled error message")
        
        # PERBAIKAN: Cursor blink untuk input text
        if self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING:
            # Blink cursor setiap 30 frames (0.5 detik pada 60 FPS)
            if pygame.time.get_ticks() % 1000 < 500:  # Blink setiap 500ms
                self.online_menu_pages.cursor_visible = True
            else:
                self.online_menu_pages.cursor_visible = False

        # PERBAIKAN: Cursor blink untuk input text
        if self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING:
            # Blink cursor setiap 30 frames (0.5 detik pada 60 FPS)
            if pygame.time.get_ticks() % 1000 < 500:  # Blink setiap 500ms
                self.online_menu_pages.cursor_visible = True
            else:
                self.online_menu_pages.cursor_visible = False
        
        # ===== UPDATE BACKGROUND STARS =====
        if not (self.pause_manager.is_paused or self.pause_manager.countdown_active):
            for star in self.stars:
                star[1] += star[2]
                if star[1] > SCREEN_HEIGHT:
                    star[1] = 0
                    star[0] = random.randint(0, SCREEN_WIDTH)
        
        if self.state_manager.state != GameState.PLAYING:
            # ===== PLAY GAME OVER SOUND SAAT MASUK STATE GAME_OVER =====
            if (self.state_manager.state == GameState.GAME_OVER and 
                not self.game_over_sound_played):
                if not self.mute_sfx:
                    self.sound_manager.play_sound('game_over')
                    self.game_over_sound_played = True
            return
        
        # PERBAIKAN: Backup - pastikan musik game diputar jika dalam state PLAYING
        if (self.state_manager.state == GameState.PLAYING and 
            self.current_music_mode != "game" and
            not self.pause_manager.is_paused):
            self.sound_manager.play_game_music()
            self.current_music_mode = "game"
            print("🔄 Backup: Switched to game music in update")

        
        # Handle pause
        if self.pause_manager.is_paused or self.pause_manager.countdown_active:
            if self.pause_manager.countdown_active:
                self.pause_manager.update_countdown()
            return

        # ===== UPDATE SEMUA OBJEK =====
        self.update_all_objects()
        
        # ===== HANDLE SHOOTER ATTACKS =====
        self.game_manager.handle_shooter_attacks(
            self.enemies,
            self.image_manager, 
            self.enemy_bullets
        )
        
        # ===== CHECK MUSUH KELUAR =====
        players_hit = self.game_manager.check_enemies_passed(
            self.enemies,
            [self.player1, self.player2],
            [self.powerup_manager_p1, self.powerup_manager_p2],
            self.sound_manager
        )
        
        # ===== TRIGGER GAME OVER JIKA ADA YANG MATI =====
        if players_hit:
            for player_idx in players_hit:
                player = self.player1 if player_idx == 0 else self.player2
                if player and player.health <= 0:
                    self.trigger_game_over()
                    return
        
        # ===== SPAWN & AUTO-SHOOT =====
        self.handle_spawning_and_shooting()
        
        # ===== CHECK COLLISIONS =====
        self.check_all_collisions()
        
        # ===== FINAL GAME OVER CHECK =====
        if self.player1.health <= 0 or (self.player2 and self.player2.health <= 0):
            self.trigger_game_over()

    def update_all_buttons_hover(self, mouse_pos):
        """Update hover status untuk semua tombol aktif"""
        # PERBAIKAN: Skip hover update saat popup aktif
        if (self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING and 
            self.client_waiting_popup):
            return  # <-- INI YANG PENTING: SKIP UPDATE HOVER
        
        # PERBAIKAN: Update hover untuk semua tombol
        for button in self.current_buttons.values():
            button.update_hover(mouse_pos)
        
        # PERBAIKAN: Update pause icon hover
        if self.state_manager.state == GameState.PLAYING:
            pause_rect = self.ui_renderer.get_pause_icon_rect()
            if pause_rect:
                self.pause_icon_hover = pause_rect.collidepoint(mouse_pos)

    def update_host_waiting_status(self):
        """Update status host waiting berdasarkan koneksi client"""
        if self.state_manager.state == GameState.ONLINE_HOST_WAITING:
            print(f"🔄 Updating host waiting status, connected: {self.network_manager.connected}")

            # PERBAIKAN: Jika baru terhubung, kirim host_info
            if self.network_manager.connected and not self.host_info_sent:
                print("📤 Client connected, sending host info...")
                self.sync_host_info_to_client()
                self.host_info_sent = True
            
            # PERBAIKAN: Jangan clear semua tombol, tapi load ulang template yang sesuai
            self.current_buttons.clear()  # Clear dulu
            
            # Load tombol yang sesuai
            if self.network_manager.connected:
                print("📱 Loading connected buttons (START + BACK)")
                self._load_buttons_from_template('host_waiting_connected')
            else:
                print("📡 Loading disconnected buttons (REFRESH + BACK)")
                self._load_buttons_from_template('host_waiting_disconnected')
            
            print(f"✅ Tombol setelah update: {list(self.current_buttons.keys())}")

    def trigger_game_over(self):
        """Trigger game over state dengan sound management"""
        self.state_manager.set_state(GameState.GAME_OVER)
        self.sound_manager.stop_music()
        # PERBAIKAN: Reset dan load tombol game over
        self.reset_game_over_state()
        # Sound 'game_over' akan diputar di update method

    def update_all_objects(self):
        """Update semua game objects"""
        # TAMBAH: Pengecekan null untuk menghindari error
        if self.player1:
            self.player1.update()
        if self.player2:
            self.player2.update()
        
        if self.state_manager.is_multiplayer and self.player1 and self.player2:
            self.divider_manager.update(self.player1, self.player2)
        
        # TAMBAH: Pengecekan null untuk powerup managers
        if self.powerup_manager_p1:
            self.powerup_manager_p1.update()
        if self.powerup_manager_p2:
            self.powerup_manager_p2.update()
        
        self.bullets_p1.update()
        self.bullets_p2.update()
        self.enemies.update()
        self.enemy_bullets.update()
        self.powerups.update()

    def handle_spawning_and_shooting(self):
        """Handle spawning dan shooting"""
        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_rate:
            self.spawn_enemy_wrapper()
            self.spawn_timer = 0
            if self.spawn_rate > 40:
                self.spawn_rate -= 0.5
        
        self.auto_shoot(1)
        if self.state_manager.is_multiplayer:
            self.auto_shoot(2)
    
    def spawn_enemy_wrapper(self):
        """Wrapper untuk spawn enemy"""
        x = random.randint(0, SCREEN_WIDTH - 40)
        y = -40
        
        # PERBAIKAN: Tambahkan parameter is_multiplayer
        self.game_manager.spawn_enemy(
            x, y, self.difficulty_level, self.player1,
            self.image_manager, self.enemies, self.powerup_manager_p1,
            self.state_manager.is_multiplayer  # Parameter baru
        )
    
    def auto_shoot(self, player_id):
        """Auto-shoot untuk player - DITAMBAH NULL CHECK"""
        if player_id == 1 and self.player1 and self.powerup_manager_p1:
            fire_rate = self.powerup_manager_p1.get_fire_rate()
            fire_rate = int(fire_rate * 3.5)
            self.player1.shoot_timer -= 1
            
            if self.player1.shoot_timer <= 0:
                self.shoot(1)
                self.player1.shoot_timer = fire_rate
        
        elif player_id == 2 and self.player2 and self.powerup_manager_p2:
            fire_rate = self.powerup_manager_p2.get_fire_rate()
            fire_rate = int(fire_rate * 3.5)
            self.player2.shoot_timer -= 1
            
            if self.player2.shoot_timer <= 0:
                self.shoot(2)
                self.player2.shoot_timer = fire_rate
    
    def shoot(self, player_id):
        """Shoot untuk player dengan efek visual - DITAMBAH NULL CHECK"""
        player = self.player1 if player_id == 1 else self.player2
        
        # TAMBAH: Pengecekan null
        if not player:
            return
        
        bullets_group = self.bullets_p1 if player_id == 1 else self.bullets_p2
        
        # PILIH bullet image berdasarkan player
        if player_id == 1:
            bullet_image = self.image_manager.images['bullet_p1']
        else:
            bullet_image = self.image_manager.images['bullet_p2']
        
        powerup_manager = self.powerup_manager_p1 if player_id == 1 else self.powerup_manager_p2
        
        # TAMBAH: Pengecekan null
        if not powerup_manager:
            return
        
        num_bullets = powerup_manager.get_bullet_count()
        
        # Efek muzzle flash kecil
        flash_size = 15
        flash_surface = pygame.Surface((flash_size, flash_size), pygame.SRCALPHA)
        pygame.draw.circle(flash_surface, (255, 255, 100, 150), (flash_size//2, flash_size//2), flash_size//2)
        flash_rect = flash_surface.get_rect(center=(player.rect.centerx, player.rect.top))
        self.screen.blit(flash_surface, flash_rect)
        
        if num_bullets == 1:
            bullet = Bullet(player.rect.centerx, player.rect.y, bullet_image)
            bullets_group.add(bullet)
        else:
            offsets = [-15, 0, 15]
            horizontal_speeds = [-2, 0, 2]
            for offset, speed_x in zip(offsets, horizontal_speeds):
                bullet = Bullet(player.rect.centerx + offset, player.rect.y, bullet_image, speed_x)
                bullets_group.add(bullet)
        
        if not self.mute_sfx:
            self.sound_manager.play_sound('shoot')
    
    def check_all_collisions(self):
        """Check semua collision - VERSI DIPERBAIKI"""
        # Peluru P1 vs Musuh
        score_gained_p1, killed_p1 = self.game_manager.check_bullet_enemy_collision(
            1, self.bullets_p1, self.enemies, self.sound_manager,
            self.image_manager, self.powerup_manager_p1, self.powerups
        )
        self.score_p1 += score_gained_p1
        self.enemies_killed_p1 += killed_p1
        
        # Peluru P2 vs Musuh (jika multiplayer)
        if self.state_manager.is_multiplayer:
            score_gained_p2, killed_p2 = self.game_manager.check_bullet_enemy_collision(
                2, self.bullets_p2, self.enemies, self.sound_manager,
                self.image_manager, self.powerup_manager_p2, self.powerups
            )
            self.score_p2 += score_gained_p2
            self.enemies_killed_p2 += killed_p2
        
        # Update difficulty
        max_killed = max(self.enemies_killed_p1, self.enemies_killed_p2 if self.state_manager.is_multiplayer else 0)
        self.difficulty_level = 1 + (max_killed // 5)
        
        # Powerup pickup
        self.handle_powerup_pickups()
        
        # Enemy collision dengan player - PERBAIKAN: Pindahkan ke sini
        players_dead_collision = self.game_manager.check_player_enemy_collision(
            [self.player1, self.player2], self.enemies, 
            [self.powerup_manager_p1, self.powerup_manager_p2], self.sound_manager
        )
        
        # Enemy bullets collision  
        players_dead_bullets = self.game_manager.check_enemy_bullets_collision(
            self.enemy_bullets, [self.player1, self.player2],
            [self.powerup_manager_p1, self.powerup_manager_p2], self.sound_manager
        )
        
        # Gabungkan hasil
        all_players_dead = list(set(players_dead_collision + players_dead_bullets))
        
        # Trigger game over jika ada yang mati
        for player_idx in all_players_dead:
            player = self.player1 if player_idx == 0 else self.player2
            if player and player.health <= 0:
                self.trigger_game_over()  # GUNAKAN METHOD INI, bukan set_state langsung
                return

        # Peluru P1 vs Musuh - HANYA jika powerup_manager_p1 ada
        if self.powerup_manager_p1:
            score_gained_p1, killed_p1 = self.game_manager.check_bullet_enemy_collision(
                1, self.bullets_p1, self.enemies, self.sound_manager,
                self.image_manager, self.powerup_manager_p1, self.powerups
            )
            self.score_p1 += score_gained_p1
            self.enemies_killed_p1 += killed_p1
        else:
            # Untuk client yang player1-nya dummy, tetap perlu check collision
            # tapi tanpa powerup_manager
            score_gained_p1, killed_p1 = self.game_manager.check_bullet_enemy_collision(
                1, self.bullets_p1, self.enemies, self.sound_manager,
                self.image_manager, None, self.powerups  # Gunakan None untuk powerup_manager
            )
            self.score_p1 += score_gained_p1
            self.enemies_killed_p1 += killed_p1

    def handle_powerup_pickups(self):
        """Handle powerup pickups - METHOD BARU - DITAMBAH NULL CHECK"""
        if self.player1 and self.powerup_manager_p1:
            hit_powerups_p1 = pygame.sprite.spritecollide(self.player1, self.powerups, True)
            for powerup in hit_powerups_p1:
                self.powerup_manager_p1.activate_powerup(powerup.powerup_type)
                self.sound_manager.play_sound('powerup')
                # SYNC: notify remote about powerup used (host authoritative preferred)
                try:
                    if self.network_manager and self.network_manager.connected:
                        # send which player and type
                        self.network_manager.send_event('powerup_used', {'player_id': 1, 'powerup_type': powerup.powerup_type})
                except:
                    pass

        if self.player2 and self.powerup_manager_p2:
            hit_powerups_p2 = pygame.sprite.spritecollide(self.player2, self.powerups, True)
            for powerup in hit_powerups_p2:
                self.powerup_manager_p2.activate_powerup(powerup.powerup_type)
                if not self.mute_sfx:
                    self.sound_manager.play_sound('powerup')
                try:
                    if self.network_manager and self.network_manager.connected:
                        self.network_manager.send_event('powerup_used', {'player_id': 2, 'powerup_type': powerup.powerup_type})
                except:
                    pass
    
    def draw(self):
        """Menggambar semua elemen game - DIPERBARUI dengan state online"""
        # ===== BACKGROUND DENGAN BINTANG =====
        self.screen.fill(BLACK)

        # Handle intro drawing
        if self.state_manager.state == GameState.INTRO:
            self.intro_page.draw(self.screen)
            pygame.display.flip()
            return
        
        for x, y, speed, size, brightness in self.stars:
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), size)
        
        # ===== DRAW BERDASARKAN STATE =====
        if self.state_manager.state == GameState.PLAYING:
            self._draw_game_playing()
        
        elif self.state_manager.state == GameState.GAME_MODE_SELECT:
            self.menu_pages.draw_game_mode_selection(self.screen, self.current_buttons, self.state_manager.control_settings)
        
        elif self.state_manager.state == GameState.ONLINE_MODE_SELECT:
            self.online_menu_pages.draw_online_mode_selection(self.screen, self.current_buttons)
        
        elif self.state_manager.state == GameState.ONLINE_HOST_JOIN:
            self.online_menu_pages.draw_host_join_selection(self.screen, self.current_buttons)
        
        elif self.state_manager.state == GameState.ONLINE_HOST_WAITING:
            self.online_menu_pages.draw_host_waiting(
                self.screen, 
                self.network_manager, 
                self.current_buttons,
                self.game_manager.difficulty_manager.difficulty_mode,
                self.state_manager.control_settings,
                self.client_cancel_alert_time  # Parameter baru
            )
        
        elif self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING:
                self.online_menu_pages.draw_join_connecting(
                    self.screen, 
                    self.network_manager, 
                    self.current_buttons,
                    self  # <-- TAMBAHKAN INI
                )

        # Gambar popup waiting jika diperlukan
        if self.client_waiting_popup and self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING:
            cancel_rect = self.online_menu_pages.draw_waiting_for_host_popup(self.screen)
            # Simpan rect untuk klik detection
            self.waiting_popup_cancel_rect = cancel_rect
        
        elif self.state_manager.state == GameState.MENU:
            self._draw_menu()
        
        elif self.state_manager.state == GameState.GAME_OVER:
            self._draw_game_over()
        
        pygame.display.flip()

    def _draw_game_playing(self):
        """Draw saat game sedang berjalan"""
        # 1. Gambar SEMUA game objects dulu
        self._draw_all_game_objects()
        
        # 2. Gambar UI SETELAH game objects
        if self.state_manager.is_multiplayer:
            self._draw_multiplayer_ui()
        else:
            self._draw_singleplayer_ui()
        
        # 3. Draw pause icon via UI Renderer
        mouse_pos = pygame.mouse.get_pos()
        self.pause_icon_hover = self.ui_renderer.draw_pause_icon(
            self.screen, 
            mouse_pos,
            self.state_manager.is_multiplayer
        )
        self.pause_icon_rect = self.ui_renderer.get_pause_icon_rect()

        # 4. Jika sedang pause atau countdown
        if self.pause_manager.countdown_active:
            self.pause_manager.draw_countdown(self.screen)
            return

        # PERBAIKAN: Update hover dan gambar tombol pause
        if self.pause_manager.is_paused:
            # Update hover untuk tombol pause
            self.update_all_buttons_hover(mouse_pos)
            
            # Gambar overlay pause
            self.pause_manager.draw_pause_screen(self.screen, is_multiplayer=self.state_manager.is_multiplayer)
            
            # Gambar tombol pause
            self.draw_pause_buttons()
            return

    def _draw_all_game_objects(self):
        """Gambar SEMUA game objects (tanpa UI)"""
        # Gambar powerups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Gambar enemy bullets
        for enemy_bullet in self.enemy_bullets:
            enemy_bullet.draw(self.screen)
        
        # Gambar bullets player
        for bullet in self.bullets_p1:
            bullet.draw(self.screen)
        for bullet in self.bullets_p2:
            bullet.draw(self.screen)
        
        # Gambar enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Gambar players (di atas musuh) - health bar sudah include di dalam draw()
        self.player1.draw(self.screen)
        if self.player2:
            self.player2.draw(self.screen)
        
        # Gambar divider untuk multiplayer
        if self.state_manager.is_multiplayer:
            self.divider_manager.draw_divider(self.screen)

    def _draw_singleplayer_ui(self):
        """Gambar UI untuk singleplayer (DI ATAS semua game objects)"""
        self.ui_renderer.draw_playing_singleplayer(
            self.player1, 
            self.score_p1, 
            self.enemies_killed_p1,
            self.difficulty_level, 
            self.powerup_manager_p1
        )

    def _draw_multiplayer_ui(self):
        """Gambar UI untuk multiplayer (DI ATAS semua game objects)"""
        self.ui_renderer.draw_playing_multiplayer(
            self.player1, 
            self.player2,
            self.score_p1, 
            self.score_p2, 
            self.enemies_killed_p1, 
            self.enemies_killed_p2,
            self.difficulty_level, 
            self.powerup_manager_p1, 
            self.powerup_manager_p2
        )

    def draw_pause_buttons(self):
        """Menggambar tombol-tombol di layar pause"""
        if self.pause_manager.countdown_active:
            return
        
        # Load tombol jika belum ada
        if not self.current_buttons:
            self.load_buttons_for_state()
        
        # Gambar tombol
        if 'resume' in self.current_buttons:
            self.current_buttons['resume'].draw(self.screen)
        if 'quit_pause' in self.current_buttons:
            self.current_buttons['quit_pause'].draw(self.screen)

    
    def _draw_menu(self):
        """Draw menu"""
        if self.state_manager.menu_state == "main":
            self.menu_pages.draw_main_menu(self.screen, self.current_buttons)
        elif self.state_manager.menu_state == "help":
            self.menu_pages.draw_help_menu(self.screen, self.current_buttons)
        elif self.state_manager.menu_state == "settings":
            self.menu_pages.draw_settings_menu(
                self.screen, self.current_buttons, 
                self.sound_manager, self.game_manager
            )

    def _draw_game_over(self):
        """Draw game over screen - FIXED BUTTON LOADING"""
        # PERBAIKAN: Selalu load tombol saat draw pertama kali
        if not self.current_buttons:
            self.reset_game_over_state()
        
        if self.state_manager.is_multiplayer:
            self.draw_multiplayer_game_over()
        else:
            self.game_over_page.draw_game_over(
                self.screen, self.current_buttons, self.score_p1,
                self.enemies_killed_p1, self.difficulty_level,
                self.game_manager.difficulty_manager.difficulty_mode
            )
        
        # Gambar tombol (setelah background)
        if 'restart' in self.current_buttons:
            self.current_buttons['restart'].draw(self.screen)
        if 'back_menu' in self.current_buttons:
            self.current_buttons['back_menu'].draw(self.screen)
        
        # Debug: Tampilkan jumlah tombol yang aktif
        # print(f"🎮 Game Over: {len(self.current_buttons)} buttons loaded")
    
    def draw_multiplayer_game_over(self):
        """Draw multiplayer game over dengan layout yang lebih baik"""
        # Background
        for i in range(SCREEN_HEIGHT):
            color_intensity = int(30 + (i / SCREEN_HEIGHT) * 50)
            pygame.draw.line(self.screen, (color_intensity, 0, 0), (0, i), (SCREEN_WIDTH, i))
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        game_over_text = self.large_font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 50)))
        
        # ===== GARIS PEMBUNGKUS ATAS =====
        pygame.draw.line(self.screen, RED, (80, 100), (SCREEN_WIDTH - 80, 100), 3)
        
        # P1 Stats
        p1_title = self.font.render("PLAYER 1", True, CYAN)
        self.screen.blit(p1_title, (80, 120))
        
        p1_score = self.font.render(f"Score: {self.score_p1}", True, YELLOW)
        self.screen.blit(p1_score, (80, 160))
        
        p1_killed = self.font.render(f"Killed: {self.enemies_killed_p1}", True, GREEN)
        self.screen.blit(p1_killed, (80, 200))
        
        # P2 Stats
        p2_title = self.font.render("PLAYER 2", True, CYAN)
        self.screen.blit(p2_title, p2_title.get_rect(topright=(SCREEN_WIDTH - 80, 120)))
        
        p2_score = self.font.render(f"Score: {self.score_p2}", True, YELLOW)
        self.screen.blit(p2_score, p2_score.get_rect(topright=(SCREEN_WIDTH - 80, 160)))
        
        p2_killed = self.font.render(f"Killed: {self.enemies_killed_p2}", True, GREEN)
        self.screen.blit(p2_killed, p2_killed.get_rect(topright=(SCREEN_WIDTH - 80, 200)))
        
        # ===== Difficulty =====
        difficulty_text = self.font.render(
            f"Difficulty: {self.game_manager.difficulty_manager.difficulty_mode.upper()}", 
            True, YELLOW
        )
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(difficulty_text, difficulty_rect)
        
        # ===== VS SPRITE DI TENGAH YANG LEBIH TEPAT =====
        vs_center_x = SCREEN_WIDTH // 2
        vs_center_y = 180
        
        # Background circle untuk VS - DIKECILKAN DAN DIPUSATKAN
        pygame.draw.circle(self.screen, (50, 50, 50), (vs_center_x, vs_center_y), 30)  # Radius 30
        pygame.draw.circle(self.screen, ORANGE, (vs_center_x, vs_center_y), 30, 3)
        
        # Gambar VS dengan font yang lebih sesuai
        vs_text = self.font.render("VS", True, ORANGE)  # Gunakan font biasa, bukan large_font
        vs_rect = vs_text.get_rect(center=(vs_center_x, vs_center_y))
        self.screen.blit(vs_text, vs_rect)
        
        # ===== GARIS PEMBUNGKUS TENGAH =====
        pygame.draw.line(self.screen, RED, (80, 250), (SCREEN_WIDTH - 80, 250), 2)
        
        # Winner - TANPA SPRITE/EFFECT
        total_p1 = self.score_p1 + self.enemies_killed_p1
        total_p2 = self.score_p2 + self.enemies_killed_p2
        
        if total_p1 > total_p2:
            winner_text = self.large_font.render("PLAYER 1 WINS!", True, GREEN)
        elif total_p2 > total_p1:
            winner_text = self.large_font.render("PLAYER 2 WINS!", True, GREEN)
        else:
            winner_text = self.large_font.render("TIE GAME!", True, YELLOW)
        
        # Winner text di bawah garis tengah
        self.screen.blit(winner_text, winner_text.get_rect(center=(SCREEN_WIDTH // 2, 335)))
        
        # ===== GARIS PEMBUNGKUS BAWAH =====
        pygame.draw.line(self.screen, RED, (80, 380), (SCREEN_WIDTH - 80, 380), 3)
        
        # ===== TAMBAH KETERANGAN ESC =====
        footer = self.tiny_font.render("Press ESC to go to Main Menu", True, YELLOW)
        footer_rect = footer.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(footer, footer_rect)

        if not self.current_buttons:
            self.load_buttons_for_state()

    def _init_button_templates(self):
        """Inisialisasi template tombol untuk semua state"""
        # Main Menu
        self.button_templates['main_menu'] = {
            'start': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': 230, 'width': 200, 'height': 50,
                'text': "START GAME", 'color': GREEN, 'text_color': BLACK,
                'hover_color': (0, 255, 100)
            },
            'help': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': 300, 'width': 200, 'height': 50,
                'text': "HOW TO PLAY", 'color': BLUE, 'text_color': WHITE,
                'hover_color': (100, 200, 255)
            },
            'settings': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': 370, 'width': 200, 'height': 50,
                'text': "SETTINGS", 'color': PURPLE, 'text_color': WHITE,
                'hover_color': (200, 100, 255)
            },
            'quit': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': 440, 'width': 200, 'height': 50,
                'text': "QUIT GAME", 'color': RED, 'text_color': WHITE,
                'hover_color': (255, 100, 100)
            }
        }
        
        # Game Mode Selection
        self.button_templates['game_mode'] = {
            'singleplayer': {
                'x': SCREEN_WIDTH // 2 - 230, 'y': 160, 'width': 200, 'height': 80,
                'text': "SINGLEPLAYER\n1 Player", 'color': GREEN, 'text_color': BLACK,
                'hover_color': (0, 255, 100)
            },
            'multiplayer': {
                'x': SCREEN_WIDTH // 2 + 30, 'y': 160, 'width': 200, 'height': 80,
                'text': "MULTIPLAYER\n2 Players", 'color': ORANGE, 'text_color': BLACK,
                'hover_color': (255, 200, 0)
            },
            'back_mode': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': SCREEN_HEIGHT - 100,
                'width': 200, 'height': 50, 'text': "BACK",
                'color': (0, 100, 200), 'text_color': WHITE,
                'hover_color': (100, 200, 255)
            }
        }
        
        # Online Mode Selection - UBAH 'local_multiplayer' dan 'online_multiplayer'
        self.button_templates['online_mode'] = {
            'local_multiplayer': {
                'x': SCREEN_WIDTH // 2 - 175, 'y': 180, 'width': 350, 'height': 80,
                'text': "LOCAL MULTIPLAYER", 'color': (0, 200, 0), 'text_color': BLACK,  # DIUBAH DARI WHITE KE BLACK
                'hover_color': (0, 255, 100)
            },
            'online_multiplayer': {
                'x': SCREEN_WIDTH // 2 - 175, 'y': 280, 'width': 350, 'height': 80,
                'text': "ONLINE MULTIPLAYER", 'color': (0, 100, 200), 'text_color': WHITE,  # BIRU, BIARKAN PUTIH
                'hover_color': (100, 200, 255)
            },
            'back_online': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': 500, 'width': 200, 'height': 50,
                'text': "BACK", 'color': (0, 100, 200), 'text_color': WHITE,  # BIRU, BIARKAN PUTIH
                'hover_color': (100, 200, 255)
            }
        }
        
        # Host/Join Selection - UBAH 'host_game'
        self.button_templates['host_join'] = {
            'host_game': {
                'x': SCREEN_WIDTH // 2 - 150, 'y': 180, 'width': 300, 'height': 70,
                'text': "HOST GAME", 'color': (0, 200, 0), 'text_color': BLACK,  # DIUBAH DARI WHITE KE BLACK
                'hover_color': (0, 255, 100)
            },
            'join_game': {
                'x': SCREEN_WIDTH // 2 - 150, 'y': 270, 'width': 300, 'height': 70,
                'text': "JOIN GAME", 'color': (0, 100, 200), 'text_color': WHITE,  # BIRU, BIARKAN PUTIH
                'hover_color': (100, 200, 255)
            },
            'back_host_join': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': 500, 'width': 200, 'height': 50,
                'text': "BACK", 'color': (0, 100, 200), 'text_color': WHITE,  # BIRU, BIARKAN PUTIH
                'hover_color': (100, 200, 255)
            }
        }
        
        # Join Connecting - update posisi tombol sesuai yang kamu atur
        self.button_templates['join_connecting'] = {
            'connect_to_host': {
                'x': 520, 'y': 440, 'width': 200, 'height': 50,  # POSISI BARU
                'text': "CONNECT TO HOST", 'color': (0, 180, 0), 'text_color': (0, 0, 0),  # teks hitam
                'hover_color': (0, 255, 100), 'font_size': 22
            },
            'cancel_join': {
                'x': 520, 'y': 500, 'width': 200, 'height': 50,  # POSISI BARU
                'text': "BACK", 'color': (200, 50, 50), 'text_color': (255, 255, 255),  # teks putih
                'hover_color': (255, 100, 100), 'font_size': 22
            }
        }

        # Host Waiting (ketika client connected) - POSISI DISAMAKAN DENGAN CLIENT
        self.button_templates['host_waiting_connected'] = {
            'start_online_game': {
                'x': 50, 'y': 230, 'width': 240, 'height': 50,  # SAMA DENGAN CONNECT TO HOST
                'text': "START ONLINE GAME", 'color': (0, 200, 0), 'text_color': WHITE,
                'hover_color': (0, 255, 100), 'font_size': 22
            },
            'back_host': {  # SAMA DENGAN BACK CLIENT
                'x': 550, 'y': 230, 'width': 200, 'height': 50,  # SAMA DENGAN BACK CLIENT
                'text': "BACK", 'color': (200, 0, 0), 'text_color': WHITE,
                'hover_color': (255, 100, 100), 'font_size': 22
            }
        }

        # Host Waiting (ketika tidak ada client) - POSISI DISAMAKAN DENGAN CLIENT
        self.button_templates['host_waiting_disconnected'] = {
            'refresh_ip': {
                'x': 50, 'y': 230, 'width': 200, 'height': 50,  # SAMA DENGAN CONNECT TO HOST
                'text': "REFRESH IP", 'color': (0, 100, 200), 'text_color': WHITE,
                'hover_color': (100, 200, 255), 'font_size': 22
            },
            'back_host': {  # SAMA DENGAN BACK CLIENT
                'x': 550, 'y': 230, 'width': 200, 'height': 50,  # SAMA DENGAN BACK CLIENT
                'text': "BACK", 'color': (200, 0, 0), 'text_color': WHITE,
                'hover_color': (255, 100, 100), 'font_size': 22
            }
        }

        
        # Pause Menu
        self.button_templates['pause_menu'] = {
            'resume': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': 350, 'width': 200, 'height': 50,
                'text': "RESUME GAME", 'color': GREEN, 'text_color': BLACK,
                'hover_color': (0, 255, 100)
            },
            'quit_pause': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': 420, 'width': 200, 'height': 50,
                'text': "QUIT TO MENU", 'color': RED, 'text_color': WHITE,
                'hover_color': (255, 100, 100)
            }
        }
        
        # Game Over
        self.button_templates['game_over'] = {
            'restart': {
                'x': SCREEN_WIDTH // 2 - 200, 'y': SCREEN_HEIGHT - 100,
                'width': 180, 'height': 50, 'text': "PLAY AGAIN",
                'color': GREEN, 'text_color': BLACK,
                'hover_color': (0, 255, 100)
            },
            'back_menu': {
                'x': SCREEN_WIDTH // 2 + 20, 'y': SCREEN_HEIGHT - 100,
                'width': 180, 'height': 50, 'text': "MAIN MENU",
                'color': BLUE, 'text_color': WHITE,
                'hover_color': (100, 200, 255)
            }
        }
        
        # Help Menu
        self.button_templates['help_menu'] = {
            'back_help': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': SCREEN_HEIGHT - 80,
                'width': 200, 'height': 50, 'text': "BACK",
                'color': BLUE, 'text_color': WHITE,
                'hover_color': (100, 200, 255)
            }
        }
        
        # Settings Submenus
        self.button_templates['settings_main'] = {
            'audio_settings': {
                'x': SCREEN_WIDTH // 2 - 150, 'y': 180, 'width': 300, 'height': 60,
                'text': "AUDIO SETTINGS", 'color': BLUE, 'text_color': WHITE,
                'hover_color': (100, 200, 255)
            },
            'difficulty_settings': {
                'x': SCREEN_WIDTH // 2 - 150, 'y': 260, 'width': 300, 'height': 60,
                'text': "DIFFICULTY SETTINGS", 'color': PURPLE, 'text_color': WHITE,
                'hover_color': (200, 100, 255)
            },
            'back_settings': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': SCREEN_HEIGHT - 80,
                'width': 200, 'height': 50, 'text': "BACK",
                'color': BLUE, 'text_color': WHITE,
                'hover_color': (100, 200, 255)
            }
        }
        
        self.button_templates['settings_audio'] = {
            'back_audio': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': SCREEN_HEIGHT - 80,
                'width': 200, 'height': 50, 'text': "BACK",
                'color': BLUE, 'text_color': WHITE,
                'hover_color': (100, 200, 255)
            }
        }
        
        self.button_templates['settings_difficulty'] = {
            'back_difficulty': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': SCREEN_HEIGHT - 80,
                'width': 200, 'height': 50, 'text': "BACK",
                'color': BLUE, 'text_color': WHITE,
                'hover_color': (100, 200, 255)
            }
        }

    def load_buttons_for_state(self):
        """Load tombol berdasarkan state saat ini"""
        self.current_buttons.clear()
        
        if self.state_manager.state == GameState.MENU:
            if self.state_manager.menu_state == "main":
                self._load_buttons_from_template('main_menu')
            elif self.state_manager.menu_state == "help":
                self._load_buttons_from_template('help_menu')
            elif self.state_manager.menu_state == "settings":
                if self.menu_pages.settings_submenu == "main":
                    self._load_buttons_from_template('settings_main')
                elif self.menu_pages.settings_submenu == "audio":
                    self._load_buttons_from_template('settings_audio')
               
                elif self.menu_pages.settings_submenu == "difficulty":
                    self._load_buttons_from_template('settings_difficulty')
        
        elif self.state_manager.state == GameState.GAME_MODE_SELECT:
            self._load_buttons_from_template('game_mode')
        
        elif self.state_manager.state == GameState.ONLINE_MODE_SELECT:
            self._load_buttons_from_template('online_mode')
        
        elif self.state_manager.state == GameState.ONLINE_HOST_JOIN:
            self._load_buttons_from_template('host_join')
        
        elif self.state_manager.state == GameState.ONLINE_HOST_WAITING:
            if self.network_manager.connected:
                self._load_buttons_from_template('host_waiting_connected')
            else:
                self._load_buttons_from_template('host_waiting_disconnected')
        
        elif self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING:
            self._load_buttons_from_template('join_connecting')
        
        elif self.state_manager.state == GameState.PLAYING and self.pause_manager.is_paused:
            self._load_buttons_from_template('pause_menu')
        
        elif self.state_manager.state == GameState.GAME_OVER:
            self._load_buttons_from_template('game_over')

    def _load_buttons_from_template(self, template_name):
        """Load tombol dari template"""
        if template_name not in self.button_templates:
            return
        
        template = self.button_templates[template_name]
        
        for btn_name, btn_config in template.items():
            font_size = btn_config.get('font_size', 24)
            
            # PERBAIKAN: Teruskan hover_color ke constructor Button
            hover_color = btn_config.get('hover_color')
            
            self.current_buttons[btn_name] = Button(
                btn_config['x'], btn_config['y'],
                btn_config['width'], btn_config['height'],
                btn_config['text'], btn_config['color'],
                btn_config['text_color'], font_size,
                hover_color=hover_color  # TAMBAHKAN INI!
            )

    def toggle_pause_from_button(self):
        """Toggle pause dari tombol (bukan dari icon atau ESC)"""
        # Toggle pause dan dapatkan status baru
        is_now_paused = self.pause_manager.toggle_pause()
        if is_now_paused:
            self.load_buttons_for_state()
        else:
            self.current_buttons.clear()
        return is_now_paused

    def reset_game_over_state(self):
        """Reset state game over dan load tombol dengan benar"""
        self.current_buttons.clear()  # Pastikan kosong dulu
        self.load_buttons_for_state()  # Load tombol game over
        # If multiplayer client, hide host-only buttons
        if self.state_manager.is_multiplayer and self.network_manager and not self.network_manager.is_host:
            # remove restart/back buttons so client won't see them
            for key in ['restart', 'back_menu']:
                if key in self.current_buttons:
                    del self.current_buttons[key]
        print("🔄 Game over buttons loaded")

    def sync_host_info_to_client(self):
        """Kirim info host ke client (difficulty & controls) - VERSI DIPERBAIKI"""
        if self.network_manager.is_host and self.network_manager.connected:
            try:
                # PERBAIKAN: Gunakan payload yang SAMA dengan yang diterima client
                payload = {
                    'difficulty': self.game_manager.difficulty_manager.difficulty_mode,
                    'controls': {
                        'p1': self.state_manager.control_settings.get_control_scheme_for_player(1),
                        'p2': self.state_manager.control_settings.get_control_scheme_for_player(2)
                    },
                    'timestamp': pygame.time.get_ticks()
                }
                
                # Encode JSON dengan ensure_ascii=False untuk karakter unicode
                import json
                success = self.network_manager.send_event('host_info', payload)
                
                if success:
                    print(f"📤 Host sent host info: {json.dumps(payload, ensure_ascii=False)}")
                    # Simpan juga di network_manager host_info untuk konsistensi
                    self.network_manager.host_info = payload
                else:
                    print("❌ Failed to send host info")
                
                return success
                    
            except Exception as e:
                print(f"❌ Error sending host info: {e}")
                import traceback
                traceback.print_exc()
                return False
        return False
    
    def run(self):
        """Main game loop"""
        print("🚀 Game started")
        
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        finally:
            # Pastikan koneksi ditutup dengan benar
            self.network_manager.disconnect()
        
        print("👋 Game closed")
        pygame.quit()
        sys.exit()

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    game = Game()
    game.run()
# ========== SPACE DEFENDER - MAIN.PY ==========
# File utama untuk menjalankan game

import sys
import pygame
import random

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

# ========== INISIALISASI PYGAME ==========
pygame.init()
pygame.mixer.init()

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
        
        # ===== STATE AWAL = INTRO =====
        self.state_manager.set_state(GameState.INTRO)
        self.current_music_mode = "silent"  # TAMBAH: Mode silent untuk intro

        # ===== NETWORK MANAGER =====
        self.network_manager = NetworkManager()
        self.online_menu_pages = OnlineMenuPages()
        
        # ===== NETWORK AUTO-CHECK =====
        self._check_network_status()

        # ===== INISIALISASI =====
        self.sound_manager.stop_pause_music()
        self._init_for_intro()
        self._init_button_templates()  # <-- TAMBAHKAN INI DI AKHIR __init__

    def _init_for_intro(self):
        """Inisialisasi minimal untuk intro tanpa memutar musik"""
        # Reset flags
        self.game_over_sound_played = False
        
        # Pastikan musik benar-benar stop
        self.sound_manager.stop_music()
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    
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
                # HOST: Player 1 dengan kontrol default, Player 2 menerima kontrol dari setting
                self.player1 = Player(100, SCREEN_HEIGHT - 60, 
                                    self.image_manager.images['player'], player_id=1)
                self.player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60,
                                    self.image_manager.images['player2'], player_id=2)
                
                # TERAPKAN HEALTH DARI DIFFICULTY  <-- PERBAIKAN DI SINI
                self.player1.health = player_health
                self.player2.health = player_health
                
                # TERAPKAN control scheme SESUAI SETTING AWAL
                control_scheme_p1 = self.state_manager.control_settings.get_control_scheme_for_player(1)
                control_scheme_p2 = self.state_manager.control_settings.get_control_scheme_for_player(2)
                
                self.player1.control_scheme = control_scheme_p1
                self.player2.control_scheme = control_scheme_p2
                
                # ===== PERBAIKAN: Inisialisasi powerup manager dengan player object =====
                self.powerup_manager_p1 = PowerUpManager(self.player1)
                self.powerup_manager_p2 = PowerUpManager(self.player2)
                
                # PERBAIKAN: KIRIM control scheme Player 2 ke Client (jika online)
                try:
                    self.network_manager.send_control_scheme(control_scheme_p2)
                except:
                    print("⚠️ Could not send control scheme (not implemented)")
                
            elif is_online and not self.network_manager.is_host:
                # CLIENT: Menerima control scheme dari Host
                print("🔄 Client: Waiting for control scheme from host...")
                
                # PERBAIKAN: Tunggu sebentar untuk menerima skema kontrol
                received_scheme = None
                for _ in range(10):  # Coba 10 kali
                    try:
                        received_scheme = self.network_manager.receive_control_scheme()
                        if received_scheme:
                            break
                    except:
                        pass
                    pygame.time.delay(50)  # Tunggu 50ms
                
                if received_scheme:
                    control_scheme_p2 = received_scheme
                    print(f"✅ Client received control scheme: {control_scheme_p2}")
                else:
                    # Fallback ke kontrol default (Arrow Keys)
                    control_scheme_p2 = "arrows"
                    print("⚠️ Client using default control scheme (arrows)")
                
                # Client adalah Player 2 di sisi kanan
                self.player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60,
                                    self.image_manager.images['player2'], player_id=2)
                self.player2.control_scheme = control_scheme_p2
                
                # TERAPKAN HEALTH DARI DIFFICULTY  <-- PERBAIKAN DI SINI
                self.player2.health = player_health
                
                # ===== PERBAIKAN: Inisialisasi powerup manager untuk player2 =====
                self.powerup_manager_p2 = PowerUpManager(self.player2)
                
                # Player 1 adalah dummy (hanya untuk render) - POSISI DARI HOST
                self.player1 = Player(100, SCREEN_HEIGHT - 60, 
                                    self.image_manager.images['player'], player_id=1)
                self.player1.is_dummy = True  # Tidak bisa dikontrol
                self.player1.is_remote = True  # Posisi akan diupdate dari host
                
                # TERAPKAN HEALTH DARI DIFFICULTY UNTUK DUMMY JUGA  <-- PERBAIKAN
                self.player1.health = player_health
                
                # ===== PERBAIKAN: Dummy player tidak perlu powerup manager =====
                self.powerup_manager_p1 = None
                
            else:
                # LOCAL MULTIPLAYER (bukan online)
                print("👥 Local Multiplayer: Both players controlled locally")
                self.player1 = Player(100, SCREEN_HEIGHT - 60, 
                                    self.image_manager.images['player'], player_id=1)
                self.player2 = Player(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60,
                                    self.image_manager.images['player2'], player_id=2)
                
                # TERAPKAN HEALTH DARI DIFFICULTY  <-- PERBAIKAN DI SINI
                self.player1.health = player_health
                self.player2.health = player_health
                
                # TERAPKAN control scheme dari settings
                control_scheme_p1 = self.state_manager.control_settings.get_control_scheme_for_player(1)
                control_scheme_p2 = self.state_manager.control_settings.get_control_scheme_for_player(2)
                
                self.player1.control_scheme = control_scheme_p1
                self.player2.control_scheme = control_scheme_p2
                
                # ===== PERBAIKAN: Inisialisasi powerup manager untuk kedua player =====
                self.powerup_manager_p1 = PowerUpManager(self.player1)
                self.powerup_manager_p2 = PowerUpManager(self.player2)
        else:
            # ===== SINGLEPLAYER =====
            print("👤 Starting Singleplayer game")
            # Hitung posisi x di tengah layar
            player_width = self.image_manager.images['player'].get_width()
            player_x = (SCREEN_WIDTH // 2) - (player_width // 2)
            
            self.player1 = Player(player_x, SCREEN_HEIGHT - 60, 
                                self.image_manager.images['player'], player_id=1)
            self.player2 = None  # Tidak ada player2 di singleplayer
            
            # TERAPKAN HEALTH DARI DIFFICULTY  <-- PERBAIKAN DI SINI
            self.player1.health = player_health
            
            # TERAPKAN control scheme dari settings
            control_scheme_p1 = self.state_manager.control_settings.get_control_scheme_for_player(1)
            self.player1.control_scheme = control_scheme_p1
            
            # ===== PERBAIKAN: Inisialisasi powerup manager dengan player object, bukan integer =====
            self.powerup_manager_p1 = PowerUpManager(self.player1)  # Player 1 powerup manager
            self.powerup_manager_p2 = None  # Player 2 tidak ada
        
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
        
        # Reset game over flag
        self.game_over_sound_played = False
        
        # Clear enemies passed tracker
        if hasattr(self.game_manager, '_enemies_passed'):
            self.game_manager._enemies_passed.clear()

        # PERBAIKAN: Reset posisi musik saat mulai game baru
        self.current_music_mode = "game"
        self.sound_manager.stop_music()  # Hentikan semua musik
        self.sound_manager.music_position = 0  # Reset posisi
        self.sound_manager.play_game_music(0)  # Mulai dari awal
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
        """Handle semua event input dari user - FIXED TEXT INPUT"""
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
        
        # ===== HANDLE SEMUA EVENT DENGAN BENAR =====
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            # ===== MOUSE CLICK =====
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Handle control selector click
                if self.state_manager.state == GameState.GAME_MODE_SELECT:
                    if self.menu_pages.handle_control_selector_click(mouse_pos, self.state_manager.control_settings):
                        continue
                
                # Handle input box untuk online join
                if self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING:
                    input_rect = pygame.Rect(100, 170, 400, 40)  # PERBAIKAN: Koordinat yang benar
                    if input_rect.collidepoint(mouse_pos):
                        self.online_menu_pages.input_active = True
                        print("🔤 Text input activated")
                    else:
                        self.online_menu_pages.input_active = False
                        print("🔤 Text input deactivated")
                
                # Panggil handler click yang sesuai
                self.handle_all_clicks(mouse_pos, event)
            
            # ===== KEYBOARD =====
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.handle_escape_key()
                
                # PERBAIKAN: Handle keyboard input untuk IP address - lebih robust
                if (self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING and 
                    self.online_menu_pages.input_active):
                    
                    if event.key == pygame.K_BACKSPACE:
                        self.online_menu_pages.input_text = self.online_menu_pages.input_text[:-1]
                        print(f"⌨️ Backspace: '{self.online_menu_pages.input_text}'")
                    
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        # Try connect ketika tekan Enter
                        if self.online_menu_pages.input_text:
                            print(f"↩️ Enter pressed, connecting to {self.online_menu_pages.input_text}")
                            self.network_manager.connect_to_host(self.online_menu_pages.input_text)
                    
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
            else:
                self.pause_manager.toggle_pause()
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
        
        # ===== HANDLE PAUSE BUTTONS =====
        if self.pause_manager.is_paused and not self.pause_manager.countdown_active:
            if 'resume' in self.current_buttons and self.current_buttons['resume'].is_clicked(mouse_pos):
                self.pause_manager.start_countdown()
                return
            
            if 'quit_pause' in self.current_buttons and self.current_buttons['quit_pause'].is_clicked(mouse_pos):
                print("🏠 Returning to menu from pause")
                
                # PERBAIKAN: Hentikan pause music sebelum kembali ke menu
                self.sound_manager.stop_pause_music()
                self.pause_manager.is_paused = False
                self.pause_manager.countdown_active = False
                
                self.state_manager.set_state(GameState.MENU)
                self.state_manager.set_menu_state("main")
                self.current_buttons.clear()
                
                # PERBAIKAN: Mainkan menu music dengan benar
                self.current_music_mode = "menu"
                self.sound_manager.stop_music()  # Hentikan game music
                self.sound_manager.play_menu_music()
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
        """Handle click di game over screen - FIXED MUSIC"""
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
            if self.network_manager.start_host():
                self.state_manager.set_state(GameState.ONLINE_HOST_WAITING)
                self.current_buttons.clear()  # Clear tombol saat pindah state
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
        """Handle click di host waiting screen"""
        print(f"🔍 Checking host waiting buttons at {mouse_pos}")
        
        # Check expand/collapse instructions area
        # Area header instructions: Rect(20, instruct_y, SCREEN_WIDTH - 40, 40)
        instruct_y = 90 + 70  # ip_y + 70 = 160
        instruct_header = pygame.Rect(20, instruct_y, SCREEN_WIDTH - 40, 40)
        
        if instruct_header.collidepoint(mouse_pos):
            print("📖 Toggling instructions")
            self.online_menu_pages.instructions_expanded = not getattr(self.online_menu_pages, 'instructions_expanded', False)
            return
        
        # Check refresh IP button
        if 'refresh_ip' in self.current_buttons and self.current_buttons['refresh_ip'].is_clicked(mouse_pos):
            print("🔄 Refreshing ZeroTier IP...")
            self.network_manager.refresh_zerotier_ip()
            return
        
        # Check other buttons
        if self.network_manager.connected:
            if 'start_online_game' in self.current_buttons and self.current_buttons['start_online_game'].is_clicked(mouse_pos):
                print("🎮 Starting Online Multiplayer Game as Host")
                self.state_manager.set_multiplayer(True)
                self.state_manager.set_state(GameState.PLAYING)
                self.sound_manager.stop_music()
                self.init_game()
                self.current_buttons.clear()
                return

        if 'cancel_host' in self.current_buttons and self.current_buttons['cancel_host'].is_clicked(mouse_pos):
            print("❌ Cancelling host...")
            self.network_manager.disconnect()
            self.state_manager.set_state(GameState.ONLINE_HOST_JOIN)
            self.current_buttons.clear()
            return
        
        print("❌ No button clicked in host waiting screen")

    def handle_join_connecting_click(self, mouse_pos):
        """Handle click di join connecting screen - DIPERBAIKI"""
        print(f"🔍 Checking join connecting buttons at {mouse_pos}")
        
        if 'connect_to_host' in self.current_buttons and self.current_buttons['connect_to_host'].is_clicked(mouse_pos):
            print("✅ CONNECT TO HOST button clicked!")
            
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
            
            # Coba koneksi dengan timeout feedback
            self.online_menu_pages.error_message = ""
            
            # Tampilkan status connecting
            print(f"🔄 Connecting to {host_ip}...")
            
            # Lakukan koneksi
            if self.network_manager.connect_to_host(host_ip):
                print("✅ Connected successfully!")
                self.state_manager.set_multiplayer(True)
                self.state_manager.set_state(GameState.PLAYING)
                self.sound_manager.stop_music()
                self.init_game()
                self.current_buttons.clear()
            else:
                error = self.network_manager.error_message
                print(f"❌ ERROR: {error}")
                print(f"Check: IP valid? Port open? Host running?")

        if 'cancel_join' in self.current_buttons and self.current_buttons['cancel_join'].is_clicked(mouse_pos):
            print("↩️ Cancelling join...")
            self.network_manager.disconnect()
            self.state_manager.set_state(GameState.ONLINE_HOST_JOIN)
            self.current_buttons.clear()
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
            # Update host untuk menerima koneksi
            if self.network_manager.update_host():
                print("✅ Player connected to host")

        # ===== NETWORK SYNC UNTUK ONLINE MULTIPLAYER =====
        if (self.state_manager.state == GameState.PLAYING and 
            self.state_manager.is_multiplayer and 
            hasattr(self, 'network_manager') and 
            self.network_manager.connected):
            
            if self.network_manager.is_host:
                # HOST: Kirim posisi Player 1 (normal) ke Client
                if self.player1 and not self.player1.is_dummy:
                    self.network_manager.send_player_position(
                        1, 
                        self.player1.rect.x,
                        self.player1.rect.y
                    )
                
                # HOST: Terima posisi Player 2 (dummy remote) dari Client
                pos_data = self.network_manager.receive_player_position()
                if pos_data and len(pos_data) == 3:
                    player_id, x, y = pos_data
                    if player_id == 2 and self.player2 and self.player2.is_dummy:
                        # Update posisi dummy Player 2 dari input client
                        self.player2.update_remote_position(x, y)
            
            else:  # CLIENT
                # CLIENT: Kirim posisi Player 2 (normal) ke Host
                if self.player2 and not self.player2.is_dummy:
                    self.network_manager.send_player_position(
                        2,
                        self.player2.rect.x,
                        self.player2.rect.y
                    )
                
                # CLIENT: Terima posisi Player 1 (dummy remote) dari Host
                pos_data = self.network_manager.receive_player_position()
                if pos_data and len(pos_data) == 3:
                    player_id, x, y = pos_data
                    if player_id == 1 and self.player1 and self.player1.is_dummy:
                        # Update posisi dummy Player 1 dari input host
                        self.player1.update_remote_position(x, y)

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
        for button in self.current_buttons.values():
            button.update_hover(mouse_pos)

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

    def handle_powerup_pickups(self):
        """Handle powerup pickups - METHOD BARU - DITAMBAH NULL CHECK"""
        if self.player1 and self.powerup_manager_p1:
            hit_powerups_p1 = pygame.sprite.spritecollide(self.player1, self.powerups, True)
            for powerup in hit_powerups_p1:
                self.powerup_manager_p1.activate_powerup(powerup.powerup_type)
                self.sound_manager.play_sound('powerup')
        
        if self.player2 and self.powerup_manager_p2:
            hit_powerups_p2 = pygame.sprite.spritecollide(self.player2, self.powerups, True)
            for powerup in hit_powerups_p2:
                self.powerup_manager_p2.activate_powerup(powerup.powerup_type)
                if not self.mute_sfx:
                    self.sound_manager.play_sound('powerup')
    
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
            self.game_manager.difficulty_manager.difficulty_mode,  # difficulty parameter
            self.state_manager.control_settings  # control settings parameter
        )
        
        elif self.state_manager.state == GameState.ONLINE_JOIN_CONNECTING:
            self.online_menu_pages.draw_join_connecting(self.screen, self.network_manager, self.current_buttons)
        
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
        
        # 3. Gambar pause overlay jika sedang pause
        if self.pause_manager.is_paused:
            if self.pause_manager.countdown_active:
                self.pause_manager.draw_countdown(self.screen)
            else:
                self.pause_manager.draw_pause_screen(self.screen)
                self.draw_pause_buttons()

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
        
        # Host Waiting - UBAH 'start_online_game'
        self.button_templates['host_waiting'] = {
            'start_online_game': {
                'x': SCREEN_WIDTH // 2 - 120, 'y': 450, 'width': 240, 'height': 60,
                'text': "START ONLINE GAME", 'color': (0, 200, 0), 'text_color': BLACK,  # DIUBAH DARI WHITE KE BLACK
                'hover_color': (0, 255, 100)
            },
            'cancel_host': {
                'x': SCREEN_WIDTH // 2 - 100, 'y': 530, 'width': 200, 'height': 50,
                'text': "CANCEL HOST", 'color': (200, 0, 0), 'text_color': WHITE,  # MERAH, BIARKAN PUTIH
                'hover_color': (255, 100, 100)
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
            self._load_buttons_from_template('host_waiting')
        
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

    def reset_game_over_state(self):
        """Reset state game over dan load tombol dengan benar"""
        self.current_buttons.clear()  # Pastikan kosong dulu
        self.load_buttons_for_state()  # Load tombol game over
        print("🔄 Game over buttons loaded")

    def _check_network_status(self):
        """Check network status and suggest fixes"""
        import platform
        import os
        
        if platform.system() == "Windows":
            print("\n🔍 Checking network setup...")
            
            # Check if fix script exists
            batch_path = os.path.join(os.path.dirname(__file__), "fix_network.bat")
            if not os.path.exists(batch_path):
                print("⚠️  Network fix script not found!")
                print("👉 Download fix_network.bat from game folder")
                self._create_fix_network_batch()
            else:
                print("✅ Network fix script available")
                print("👉 Run 'fix_network.bat' as Admin if connection issues")
            
            # Check port 5555 status
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                result = sock.connect_ex(("127.0.0.1", 5555))
                if result == 0:
                    print("⚠️  Port 5555 is in use (maybe by another game)")
            except:
                pass

    def _create_fix_network_batch(self):
        """Create the fix_network.bat file if missing"""
        import os
        
        batch_path = os.path.join(os.path.dirname(__file__), "fix_network.bat")
        
        # Create minimal batch file that downloads the full one
        mini_batch = '''@echo off
    echo Space Defender Network Fixer missing!
    echo.
    echo Please download the full fix_network.bat from:
    echo https://github.com/your-repo/SpaceDefender/files/
    echo.
    echo Or contact the game distributor.
    pause
    '''
        
        try:
            with open(batch_path, 'w') as f:
                f.write(mini_batch)
            print(f"✅ Created placeholder fix_network.bat")
        except Exception as e:
            print(f"❌ Could not create batch file: {e}")
    
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
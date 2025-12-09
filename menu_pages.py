# ========== MENU_PAGES.PY ==========
# File lengkap dengan semua method termasuk handle_help_scroll

import math
import pygame
from button import Button
from slider import Slider
from radio_button import RadioButton

# ========== CONSTANTS ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

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
DARK_BLUE = (10, 10, 40)
GRAY = (100, 100, 100)
MAGENTA = (255, 0, 255)

class MenuPages:
    """Mengelola semua halaman menu"""
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)
        self.control_selector_hovered = False
        
        # Variabel untuk scroll help menu
        self.help_scroll_y = 0
        self.help_content_height = 0
        self.is_dragging = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0
        
        # Sliders untuk settings
        self.sliders = {}
        self.preview_sound_active = False
        self.preview_sound_timer = 0

        # Tambahkan untuk difficulty scroll:
        self.difficulty_scroll_y = 0
        self.difficulty_content_height = 0
        self.difficulty_boxes = {}
        self.difficulty_dragging = False
        self.difficulty_drag_start_y = 0
        self.difficulty_drag_start_scroll = 0
        
        # State untuk settings submenu
        self.settings_submenu = "main"  # "main", "audio", "difficulty"
    
    # ===== MAIN MENU =====
    def draw_main_menu(self, screen, buttons):
        """Menggambar main menu dengan 4 tombol - FIXED: Hover bekerja"""
        # ===== BACKGROUND GRADIENT EFFECT =====
        for i in range(SCREEN_HEIGHT):
            color_intensity = int(20 + (i / SCREEN_HEIGHT) * 40)
            pygame.draw.line(screen, (color_intensity, 0, color_intensity * 2), (0, i), (SCREEN_WIDTH, i))
        
        # ===== TITLE =====
        title = self.large_font.render("SPACE DEFENDER", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 70))
        screen.blit(title, title_rect)
        
        # ===== SUBTITLE =====
        subtitle = self.font.render("Defend the Galaxy", True, CYAN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        screen.blit(subtitle, subtitle_rect)
        
        # ===== SEPARATOR LINE =====
        pygame.draw.line(screen, YELLOW, (100, 180), (SCREEN_WIDTH - 100, 180), 2)
        
        # ===== CREATE BUTTONS JIKA BELUM ADA =====
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = 230
        button_spacing = 70
        
        if 'start' not in buttons:
            buttons['start'] = Button(
                button_x,
                button_y,
                button_width,
                button_height,
                "START GAME",
                GREEN,
                BLACK
            )
        if 'help' not in buttons:
            buttons['help'] = Button(
                button_x,
                button_y + button_spacing,
                button_width,
                button_height,
                "HOW TO PLAY",
                BLUE,
                WHITE
            )
        if 'settings' not in buttons:
            buttons['settings'] = Button(
                button_x,
                button_y + (button_spacing * 2),
                button_width,
                button_height,
                "SETTINGS",
                PURPLE,
                WHITE
            )
        if 'quit' not in buttons:
            buttons['quit'] = Button(
                button_x,
                button_y + (button_spacing * 3),
                button_width,
                button_height,
                "QUIT GAME",
                RED,
                WHITE
            )
        
        # ===== DRAW BUTTONS =====
        buttons['start'].draw(screen)
        buttons['help'].draw(screen)
        buttons['settings'].draw(screen)
        buttons['quit'].draw(screen)
        
        # ===== TAMBAHKAN ORNAMENT/SPRITE HIASAN =====
        self._draw_menu_ornaments(screen)
        
        # ===== FOOTER INFO =====
        footer = self.tiny_font.render("Made with Python & Pygame", True, CYAN)
        footer_rect = footer.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        screen.blit(footer, footer_rect)

        # ===== UPDATE HOVER SETELAH MENGGAMBAR =====
        mouse_pos = pygame.mouse.get_pos()
        for btn in ['start', 'help', 'settings', 'quit']:
            if btn in buttons:
                buttons[btn].update_hover(mouse_pos)

    def _draw_menu_ornaments(self, screen):
        """Gambar ornamen hiasan di main menu"""
        # Ornamen kiri atas - pesawat kecil
        pygame.draw.polygon(screen, GREEN, [(50, 50), (30, 70), (70, 70)])
        pygame.draw.circle(screen, CYAN, (50, 60), 3)
        
        # Ornamen kanan atas - bintang
        star_points = []
        for i in range(5):
            angle = math.pi/2 + i * 2*math.pi/5
            outer_x = SCREEN_WIDTH - 50 + 15 * math.cos(angle)
            outer_y = 50 + 15 * math.sin(angle)
            inner_x = SCREEN_WIDTH - 50 + 7 * math.cos(angle + math.pi/5)
            inner_y = 50 + 7 * math.sin(angle + math.pi/5)
            star_points.extend([(outer_x, outer_y), (inner_x, inner_y)])
        pygame.draw.polygon(screen, YELLOW, star_points)
        
        # Ornamen kiri bawah - planet kecil
        pygame.draw.circle(screen, ORANGE, (60, SCREEN_HEIGHT - 60), 20)
        pygame.draw.circle(screen, (200, 100, 0), (45, SCREEN_HEIGHT - 70), 5)
        
        # Ornamen kanan bawah - asteroid
        pygame.draw.circle(screen, GRAY, (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60), 15)
        pygame.draw.circle(screen, (80, 80, 80), (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 65), 5)
        pygame.draw.circle(screen, (80, 80, 80), (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 55), 4)

    # ===== GAME MODE SELECTION =====
    def draw_game_mode_selection(self, screen, buttons, control_settings):
        """Menggambar layar pilih game mode - FIXED HOVER"""
        # ===== BACKGROUND GRADIENT =====
        for i in range(SCREEN_HEIGHT):
            color_intensity = int(20 + (i / SCREEN_HEIGHT) * 40)
            pygame.draw.line(screen, (0, color_intensity, color_intensity * 2), (0, i), (SCREEN_WIDTH, i))
        
        # ===== TITLE =====
        title = self.large_font.render("SELECT GAME MODE", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        # ===== SEPARATOR =====
        pygame.draw.line(screen, CYAN, (80, 100), (SCREEN_WIDTH - 80, 100), 2)
        
        # ===== BUTTON POSITIONS =====
        button_width = 200
        button_height = 80
        button_x_left = SCREEN_WIDTH // 2 - button_width - 30
        button_x_right = SCREEN_WIDTH // 2 + 30
        button_y = 160
        
        # PERBAIKAN: HANYA BUAT TOMBOL JIKA BELUM ADA - JANGAN CLEAR
        if 'singleplayer' not in buttons:
            buttons['singleplayer'] = Button(
                button_x_left,
                button_y,
                button_width,
                button_height,
                "SINGLEPLAYER\n1 Player",
                GREEN,
                BLACK
            )
        
        if 'multiplayer' not in buttons:
            buttons['multiplayer'] = Button(
                button_x_right,
                button_y,
                button_width,
                button_height,
                "MULTIPLAYER\n2 Players", 
                ORANGE,
                BLACK
            )
        
        if 'back_mode' not in buttons:
            buttons['back_mode'] = Button(
                SCREEN_WIDTH // 2 - 100,
                SCREEN_HEIGHT - 100,
                200,
                50,
                "BACK",
                (0, 100, 200),
                WHITE
            )
        
        # ===== DRAW BUTTONS =====
        buttons['singleplayer'].draw(screen)
        buttons['multiplayer'].draw(screen)
        buttons['back_mode'].draw(screen)
        
        # ===== DESCRIPTION TEXT =====
        desc1_text = self.tiny_font.render("Play alone", True, YELLOW)
        desc1_rect = desc1_text.get_rect(center=(button_x_left + button_width // 2, button_y + 105))
        screen.blit(desc1_text, desc1_rect)
        
        desc2_text = self.tiny_font.render("Challenge friend", True, YELLOW)
        desc2_rect = desc2_text.get_rect(center=(button_x_right + button_width // 2, button_y + 105))
        screen.blit(desc2_text, desc2_rect)
        
        # ===== CONTROL SELECTOR =====
        control_x = SCREEN_WIDTH // 2 - 150
        control_y = 300
        control_width = 300
        control_height = 120
        
        # Check hover
        mouse_pos = pygame.mouse.get_pos()
        control_rect = pygame.Rect(control_x, control_y, control_width, control_height)
        self.control_selector_rect = control_rect
        self.control_selector_hovered = control_rect.collidepoint(mouse_pos)
        
        if self.control_selector_hovered:
            glow_surface = pygame.Surface((control_width + 10, control_height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 255, 0, 50), (0, 0, control_width + 10, control_height + 10), border_radius=15)
            screen.blit(glow_surface, (control_x - 5, control_y - 5))
        
        control_settings.draw_control_selector(
            screen, control_x, control_y, control_width, control_height,
            self.control_selector_hovered
        )

        # ===== UPDATE HOVER =====
        mouse_pos = pygame.mouse.get_pos()
        for btn in ['singleplayer', 'multiplayer', 'back_mode']:
            if btn in buttons:
                buttons[btn].update_hover(mouse_pos)

    # ===== HELP MENU DENGAN SCROLL =====
    def draw_help_menu(self, screen, buttons):
        """Menggambar help menu dengan sistem scroll"""
        # ===== BACKGROUND =====
        screen.fill(DARK_BLUE)
        for i in range(SCREEN_HEIGHT):
            color_intensity = int(30 + (i / SCREEN_HEIGHT) * 60)
            pygame.draw.line(screen, (color_intensity//2, color_intensity//3, color_intensity), 
                           (0, i), (SCREEN_WIDTH, i))
        
        # ===== TITLE =====
        title_bg = pygame.Rect(SCREEN_WIDTH//2 - 220, 15, 440, 60)
        pygame.draw.rect(screen, (0, 0, 0, 180), title_bg, border_radius=15)
        pygame.draw.rect(screen, YELLOW, title_bg, 3, border_radius=15)
        
        title = self.large_font.render("HOW TO PLAY", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 45))
        screen.blit(title, title_rect)
        
        # ===== SCROLLABLE CONTENT AREA =====
        content_rect = pygame.Rect(40, 90, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 180)
        
        # Background content area
        content_bg = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        content_bg.fill((0, 0, 0, 180))
        pygame.draw.rect(content_bg, YELLOW, (0, 0, content_rect.width, content_rect.height), 2, border_radius=10)
        screen.blit(content_bg, content_rect)
        
        # Buat surface untuk konten
        content_surface = pygame.Surface((content_rect.width - 25, 1400))
        content_surface.fill((0, 0, 0, 0))
        
        current_y = 15
        
        # ===== GAME OBJECTIVE =====
        objective_title = self.font.render("GAME OBJECTIVE", True, CYAN)
        content_surface.blit(objective_title, (15, current_y))
        current_y += 35

        objectives = [
            "- Defend your ship from waves of alien invaders",
            "- Prevent enemies from reaching the bottom of screen", 
            "- Shoot enemies to earn points and collect power-ups",
            "- Survive as long as possible and achieve high score",
            "- In multiplayer: Cooperate with your partner"
        ]

        for obj in objectives:
            text = self.small_font.render(obj, True, WHITE)
            content_surface.blit(text, (25, current_y))
            current_y += 22
        
        current_y += 15

        # ===== CONTROLS SECTION =====
        controls_title = self.font.render("CONTROLS", True, CYAN)
        content_surface.blit(controls_title, (15, current_y))
        current_y += 35

        controls = [
            "SINGLEPLAYER MODE:",
            "  Movement: W-A-S-D keys",
            "  Shooting: Automatic (no input needed)",
            "  Pause/Resume: ESC key",
            "",
            "MULTIPLAYER MODE:",
            "  Player 1 (Left): W-A-S-D keys",
            "  Player 2 (Right): Arrow keys (Up, Down, Left, Right)",
            "  Alternative: I-J-K-L keys (if configured)",
            "",
            "GENERAL CONTROLS:",
            "  ESC: Pause game / Return to menu",
            "  Mouse: Click buttons in menus",
            "  Scroll: Mouse wheel in help/settings"
        ]

        for control in controls:
            if control == "SINGLEPLAYER MODE:" or control == "MULTIPLAYER MODE:" or control == "GENERAL CONTROLS:":
                text = self.small_font.render(control, True, GREEN if "SINGLE" in control else ORANGE)
            elif control == "":
                current_y += 8
                continue
            else:
                text = self.small_font.render(control, True, WHITE)
            
            content_surface.blit(text, (25, current_y))
            current_y += 20
        current_y += 12

        # ===== POWER-UPS SECTION =====
        powerup_title = self.font.render("POWER-UPS", True, CYAN)
        content_surface.blit(powerup_title, (15, current_y))
        current_y += 35

        powerups = [
            ("Rapid Fire", "Doubles your firing speed", YELLOW),
            ("Slow Enemies", "Slows all enemies by 50%", CYAN),
            ("Multiple Bullets", "Fire 3 bullets at once", ORANGE),
            ("Health Regeneration", "Restores 1 health point", (255, 100, 100)),
            ("Speed Boost", "Doubles movement speed", PURPLE), 
            ("Invincibility", "Temporary damage immunity", GREEN),
            ("Double Score", "Earn 2x points from kills", (255, 255, 100))
        ]

        # Power-up dalam 2 kolom
        col_width = (content_surface.get_width() - 40) // 2
        col1_x = 20
        col2_x = col1_x + col_width + 5

        rows_needed = (len(powerups) + 1) // 2

        for i, (name, desc, color) in enumerate(powerups):
            if i < 4:
                x_pos = col1_x
                y_pos = current_y + (i * 32)
            else:
                x_pos = col2_x
                y_pos = current_y + ((i - 4) * 32)
            
            name_text = self.small_font.render(name, True, color)
            desc_text = self.tiny_font.render(desc, True, (200, 200, 200))
            
            content_surface.blit(name_text, (x_pos, y_pos))
            content_surface.blit(desc_text, (x_pos, y_pos + 18))

        current_y += (rows_needed * 32) + 15

        # ===== ENEMIES SECTION =====
        enemy_title = self.font.render("ENEMY TYPES", True, CYAN)
        content_surface.blit(enemy_title, (15, current_y))
        current_y += 35

        # Klasifikasi musuh berdasarkan kesulitan
        basic_enemies = [
            ("Normal", "Standard alien, moves straight down", "5"),
            ("Fast", "Moves quickly, hard to hit", "20"),
            ("Bouncer", "Bounces side to side while descending", "12"),
            ("Shooter", "Fires bullets at your ship", "15"),
            ("Kamikaze", "Chases your ship when close", "20"),
            ("Follower", "Tracks your horizontal movement", "18")
        ]

        advanced_enemies = [
            ("Tank", "High health, moves slowly", "50"),
            ("Strong", "3 health points, tougher to kill", "30"),
            ("Splitter", "Splits into 2 smaller enemies when hit", "25"),
            ("Spiral", "Moves in spiral/zigzag pattern", "15"),
            ("Armored", "Requires 2 hits to destroy", "20"),
            ("Regenerator", "Slowly regenerates health over time", "35")
        ]

        # Basic Enemies
        basic_text = self.small_font.render("BASIC ENEMIES (Early Game):", True, GREEN)
        content_surface.blit(basic_text, (20, current_y))
        current_y += 25

        for i, (name, desc, score) in enumerate(basic_enemies):
            x_pos = 25 if i % 2 == 0 else col2_x
            y_pos = current_y + (i // 2) * 30
            
            enemy_text = self.small_font.render(f"{name} - {score} pts", True, WHITE)
            desc_text = self.tiny_font.render(desc, True, (200, 200, 200))
            
            content_surface.blit(enemy_text, (x_pos, y_pos))
            content_surface.blit(desc_text, (x_pos, y_pos + 18))

        current_y += ((len(basic_enemies) + 1) // 2) * 30

        # Advanced Enemies
        current_y += 10
        spec_text = self.small_font.render("ADVANCED ENEMIES (Later Game):", True, ORANGE)
        content_surface.blit(spec_text, (20, current_y))
        current_y += 25

        for i, (name, desc, score) in enumerate(advanced_enemies):
            x_pos = 25 if i % 2 == 0 else col2_x
            y_pos = current_y + (i // 2) * 30
            
            max_x = content_surface.get_width() - 100
            if x_pos > max_x:
                x_pos = max_x
            
            enemy_text = self.small_font.render(f"{name} - {score} pts", True, WHITE)
            desc_text = self.tiny_font.render(desc, True, (200, 200, 200))
            
            content_surface.blit(enemy_text, (x_pos, y_pos))
            content_surface.blit(desc_text, (x_pos, y_pos + 18))

        current_y += ((len(advanced_enemies) + 1) // 2) * 30
        current_y += 15

        # ===== STRATEGY SECTION =====
        strategy_title = self.font.render("GAME STRATEGY", True, CYAN)
        content_surface.blit(strategy_title, (15, current_y))
        current_y += 35

        strategies = [
            "- Score points by shooting enemies (5-50 points per enemy)",
            "- Difficulty increases every 5 enemies defeated",
            "- Power-ups drop randomly from destroyed enemies",
            "- Collect power-ups to gain temporary advantages",
            "- Health power-ups instantly restore 1 health point",
            "- Use invincibility power-up during difficult waves",
            "- In multiplayer: Cover both sides of the screen",
            "- Watch for enemy patterns: some move predictably",
            "- Destroy shooter enemies quickly to avoid their bullets"
        ]

        for strategy in strategies:  # BUKAN: for strategy in enumerate(strategies):
            text = self.small_font.render(strategy, True, WHITE)
            content_surface.blit(text, (25, current_y))
            current_y += 22

        # ===== DIFFICULTY INFO =====
        current_y += 10
        diff_title = self.small_font.render("DIFFICULTY LEVELS:", True, YELLOW)
        content_surface.blit(diff_title, (15, current_y))
        current_y += 25

        difficulties = [
            ("EASY", "Beginner friendly, more health, slower enemies", GREEN),
            ("NORMAL", "Balanced challenge for most players", BLUE),
            ("HARD", "Tougher enemies, faster spawn rate", ORANGE),
            ("EXTREME", "Maximum challenge for expert players", RED)
        ]

        for name, desc, color in difficulties:
            diff_name = self.small_font.render(name, True, color)
            diff_desc = self.tiny_font.render(desc, True, (200, 200, 200))
            
            content_surface.blit(diff_name, (25, current_y))
            content_surface.blit(diff_desc, (25, current_y + 18))
            current_y += 35

        current_y += 10
        
        # Simpan tinggi total konten
        self.help_content_height = current_y + 50
        
        # ===== APPLY SCROLL =====
        max_scroll = max(0, self.help_content_height - content_rect.height)
        self.help_scroll_y = max(0, min(self.help_scroll_y, max_scroll))
        
        # Gambar konten yang terlihat saja
        visible_rect = pygame.Rect(0, self.help_scroll_y, content_rect.width - 25, content_rect.height)
        screen.blit(content_surface, (content_rect.x + 10, content_rect.y), visible_rect)
        
        # ===== SCROLL BAR =====
        if self.help_content_height > content_rect.height:
            scroll_ratio = content_rect.height / self.help_content_height
            scrollbar_height = max(30, content_rect.height * scroll_ratio)
            scrollbar_y = content_rect.y + (self.help_scroll_y / self.help_content_height) * content_rect.height
            
            scrollbar_bg = pygame.Rect(content_rect.right - 12, content_rect.y, 6, content_rect.height)
            pygame.draw.rect(screen, (50, 50, 80), scrollbar_bg, border_radius=3)
            
            scrollbar_rect = pygame.Rect(
                content_rect.right - 12,
                scrollbar_y,
                6,
                scrollbar_height
            )
            scrollbar_color = YELLOW if self.is_dragging else CYAN
            pygame.draw.rect(screen, scrollbar_color, scrollbar_rect, border_radius=3)
        
        # ===== SCROLL INSTRUCTIONS - DI KIRI BAWAH =====
        instructions = [
            "Mouse Wheel or Click & Drag to Scroll",
            "BACK to return to Main Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.tiny_font.render(instruction, True, YELLOW)
            text_rect = text.get_rect(topleft=(20, SCREEN_HEIGHT - 50 + i * 15))
            screen.blit(text, text_rect)
        
        # ===== BACK BUTTON =====
        if 'back_help' not in buttons:
            buttons['back_help'] = Button(
                SCREEN_WIDTH // 2 - 100,
                SCREEN_HEIGHT - 80,
                200,
                50,
                "BACK",
                BLUE,
                WHITE
            )

        # ===== UPDATE HOVER =====
        mouse_pos = pygame.mouse.get_pos()
        if 'back_help' in buttons:
            buttons['back_help'].update_hover(mouse_pos)
        
        buttons['back_help'].draw(screen)

    def handle_control_selector_click(self, mouse_pos, control_settings):
        """Handle click pada control selector"""
        if hasattr(self, 'control_selector_rect') and self.control_selector_rect:
            return control_settings.handle_click(mouse_pos, self.control_selector_rect)
        return False
    
    def handle_help_scroll(self, events, mouse_pos):
        """Handle scroll events untuk help menu dengan drag support"""
        content_rect = pygame.Rect(40, 90, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 180)
        scrollbar_rect = pygame.Rect(content_rect.right - 12, content_rect.y, 6, content_rect.height)
        
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.help_scroll_y -= event.y * 20
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if scrollbar_rect.collidepoint(mouse_pos) or content_rect.collidepoint(mouse_pos):
                        self.is_dragging = True
                        self.drag_start_y = mouse_pos[1]
                        self.drag_start_scroll = self.help_scroll_y
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    delta_y = mouse_pos[1] - self.drag_start_y
                    max_scroll = max(0, self.help_content_height - content_rect.height)
                    scroll_ratio = self.help_content_height / content_rect.height
                    
                    new_scroll = self.drag_start_scroll + (delta_y * scroll_ratio)
                    self.help_scroll_y = max(0, min(new_scroll, max_scroll))

    # ===== SETTINGS MENU =====
    def draw_settings_menu(self, screen, buttons, sound_manager, game_manager=None):
        """Menggambar settings menu dengan struktur submenu baru"""
        # ===== BACKGROUND (HANYA UNTUK MAIN DAN AUDIO) =====
        if self.settings_submenu != "difficulty":  # TAMBAHKAN KONDISI INI
            for i in range(SCREEN_HEIGHT):
                color_intensity = int(20 + (i / SCREEN_HEIGHT) * 40)
                pygame.draw.line(screen, (color_intensity, 0, color_intensity * 2), (0, i), (SCREEN_WIDTH, i))
        
        # ===== TITLE (HANYA UNTUK MAIN DAN AUDIO) =====
        if self.settings_submenu != "difficulty":  # TAMBAHKAN KONDISI INI
            title_text = "SETTINGS"
            if self.settings_submenu == "audio":
                title_text = "AUDIO SETTINGS"
            elif self.settings_submenu == "difficulty":
                title_text = "DIFFICULTY SETTINGS"
                
            title = self.large_font.render(title_text, True, YELLOW)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
            screen.blit(title, title_rect)
            
            # ===== SEPARATOR (HANYA UNTUK MAIN DAN AUDIO) =====
            if self.settings_submenu != "difficulty":  # TAMBAHKAN KONDISI INI
                pygame.draw.line(screen, YELLOW, (100, 120), (SCREEN_WIDTH - 100, 120), 2)
        
        # ===== BERDASARKAN SUBMENU =====
        if self.settings_submenu == "main":
            self._draw_settings_main(screen, buttons)
        elif self.settings_submenu == "audio":
            self._draw_settings_audio(screen, buttons, sound_manager)
        elif self.settings_submenu == "difficulty":
            self._draw_settings_difficulty(screen, buttons, game_manager)

        # ===== UPDATE HOVER =====
        mouse_pos = pygame.mouse.get_pos()
        
        if self.settings_submenu == "main":
            for btn in ['audio_settings', 'difficulty_settings', 'back_settings']:
                if btn in buttons:
                    buttons[btn].update_hover(mouse_pos)
        elif self.settings_submenu == "audio":
            if 'back_audio' in buttons:
                buttons['back_audio'].update_hover(mouse_pos)
        elif self.settings_submenu == "difficulty":
            if 'back_difficulty' in buttons:
                buttons['back_difficulty'].update_hover(mouse_pos)
    
    def _draw_settings_main(self, screen, buttons):
        """Menggambar main settings menu dengan pilihan submenu - FIXED: Hover bekerja"""
        # ===== AUDIO SETTINGS BUTTON =====
        audio_button_y = 180
        if 'audio_settings' not in buttons:
            buttons['audio_settings'] = Button(
                SCREEN_WIDTH // 2 - 150,
                audio_button_y,
                300,
                60,
                "AUDIO SETTINGS",
                BLUE,
                WHITE
            )
        
        buttons['audio_settings'].draw(screen)
        
        # ===== DIFFICULTY SETTINGS BUTTON =====
        difficulty_button_y = audio_button_y + 80
        if 'difficulty_settings' not in buttons:
            buttons['difficulty_settings'] = Button(
                SCREEN_WIDTH // 2 - 150,
                difficulty_button_y,
                300,
                60,
                "DIFFICULTY SETTINGS",
                PURPLE,
                WHITE
            )
        
        buttons['difficulty_settings'].draw(screen)
        
        # ===== BACK BUTTON =====
        if 'back_settings' not in buttons:
            buttons['back_settings'] = Button(
                SCREEN_WIDTH // 2 - 100,
                SCREEN_HEIGHT - 80,
                200,
                50,
                "BACK",
                BLUE,
                WHITE
            )
        
        buttons['back_settings'].draw(screen)
    
    def _draw_settings_audio(self, screen, buttons, sound_manager):
        """Menggambar audio settings submenu - REVISED: Music di atas, SFX di bawah"""
        # ===== GET CURRENT VOLUMES =====
        volumes = sound_manager.get_volumes()
        
        # ===== SLIDER VOLUME - REVISED: Music di atas, SFX di bawah =====
        slider_y = 180
        
        # Music Volume Slider (SEKARANG DI ATAS)
        if 'music' not in self.sliders:
            self.sliders['music'] = Slider(
                100, slider_y, 500, 10,
                initial_val=volumes['music'],
                track_color=(120, 80, 80),
                handle_color=(255, 100, 100)
            )
        else:
            if not self.sliders['music'].dragging and abs(self.sliders['music'].value - volumes['music']) > 1:
                self.sliders['music'].value = volumes['music']
                self.sliders['music'].handle_x = self.sliders['music'].value_to_pixel()
        
        self.sliders['music'].draw(screen, self.font, "MUSIC VOLUME")
        
        # SFX Volume Slider (SEKARANG DI BAWAH)
        slider_y += 70
        if 'sfx' not in self.sliders:
            self.sliders['sfx'] = Slider(
                100, slider_y, 500, 10,
                initial_val=volumes['sfx'],
                track_color=(80, 120, 80),
                handle_color=(0, 255, 100)
            )
        else:
            if not self.sliders['sfx'].dragging and abs(self.sliders['sfx'].value - volumes['sfx']) > 1:
                self.sliders['sfx'].value = volumes['sfx']
                self.sliders['sfx'].handle_x = self.sliders['sfx'].value_to_pixel()
        
        self.sliders['sfx'].draw(screen, self.font, "SOUND EFFECTS VOLUME")
        
        # ===== BACK BUTTON =====
        if 'back_audio' not in buttons:
            buttons['back_audio'] = Button(
                SCREEN_WIDTH // 2 - 100,
                SCREEN_HEIGHT - 80,
                200,
                50,
                "BACK",
                BLUE,
                WHITE
            )
        
        buttons['back_audio'].draw(screen)
    
    def _draw_settings_difficulty(self, screen, buttons, game_manager):
        """Menggambar difficulty settings submenu dengan header mirip how to play"""
        # ===== BACKGROUND =====
        screen.fill(DARK_BLUE)
        for i in range(SCREEN_HEIGHT):
            color_intensity = int(30 + (i / SCREEN_HEIGHT) * 60)
            pygame.draw.line(screen, (color_intensity//2, color_intensity//3, color_intensity), 
                        (0, i), (SCREEN_WIDTH, i))
        
        # ===== HEADER/TITLE MIRIP HOW TO PLAY =====
        title_bg = pygame.Rect(SCREEN_WIDTH//2 - 320, 15, 640, 60)
        pygame.draw.rect(screen, (0, 0, 0, 180), title_bg, border_radius=15)
        pygame.draw.rect(screen, YELLOW, title_bg, 3, border_radius=15)
        
        title = self.large_font.render("DIFFICULTY SETTINGS", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 45))
        screen.blit(title, title_rect)
        
        # ===== SCROLLABLE CONTENT AREA =====
        content_rect = pygame.Rect(40, 90, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 180)
        
        # Background content area
        content_bg = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        content_bg.fill((0, 0, 0, 180))
        pygame.draw.rect(content_bg, YELLOW, (0, 0, content_rect.width, content_rect.height), 2, border_radius=10)
        screen.blit(content_bg, content_rect)
        
        # Buat surface untuk konten
        content_surface = pygame.Surface((content_rect.width - 25, 800))  # Tinggi konten
        content_surface.fill((0, 0, 0, 0))
        
        current_y = 15
        
        # ===== SELECT DIFFICULTY TITLE =====
        select_title = self.font.render("SELECT DIFFICULTY LEVEL", True, CYAN)
        content_surface.blit(select_title, (15, current_y))
        current_y += 40
        
        # ===== DIFFICULTY OPTIONS =====
        difficulties = [
            ("easy", "EASY", "Beginner-friendly mode", GREEN),
            ("normal", "NORMAL", "Standard challenge for most players", BLUE),
            ("hard", "HARD", "Tough challenge for experienced players", ORANGE),
            ("extreme", "EXTREME", "Brutal challenge for experts only", RED)
        ]
        
        # Dapatkan current difficulty
        current_difficulty = "normal"
        if game_manager and hasattr(game_manager, 'difficulty_manager'):
            current_difficulty = game_manager.difficulty_manager.difficulty_mode
        
        # Buat difficulty cards
        card_height = 70
        card_spacing = 15
        self.difficulty_boxes = {}
        
        for difficulty_key, difficulty_name, description, color in difficulties:
            card_rect = pygame.Rect(20, current_y, content_surface.get_width() - 40, card_height)
            self.difficulty_boxes[difficulty_key] = card_rect
            
            # Background card
            card_bg_color = (30, 30, 40, 180)
            if difficulty_key == current_difficulty:
                card_bg_color = (40, 40, 60, 220)
                # Glow effect untuk yang aktif
                glow = pygame.Surface((card_rect.width + 6, card_rect.height + 6), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*color, 60), (0, 0, glow.get_width(), glow.get_height()), 
                            border_radius=8)
                content_surface.blit(glow, (card_rect.x - 3, card_rect.y - 3))
            
            pygame.draw.rect(content_surface, card_bg_color, card_rect, border_radius=8)
            
            # Border
            border_width = 3 if difficulty_key == current_difficulty else 2
            pygame.draw.rect(content_surface, color, card_rect, border_width, border_radius=8)
            
            # Radio button indicator
            radio_radius = 8
            radio_center = (card_rect.x + 30, card_rect.centery)
            pygame.draw.circle(content_surface, color, radio_center, radio_radius)
            
            if difficulty_key == current_difficulty:
                # Inner dot untuk yang terpilih
                pygame.draw.circle(content_surface, WHITE, radio_center, radio_radius - 3)
            
            # Difficulty name
            name_color = WHITE if difficulty_key == current_difficulty else color
            name_text = self.font.render(difficulty_name, True, name_color)
            content_surface.blit(name_text, (card_rect.x + 60, card_rect.y + 10))
            
            # Description
            desc_text = self.tiny_font.render(description, True, (200, 200, 200))
            content_surface.blit(desc_text, (card_rect.x + 60, card_rect.y + 35))
            
            current_y += card_height + card_spacing
        
        # Separator
        current_y += 10
        pygame.draw.line(content_surface, YELLOW, (20, current_y), (content_surface.get_width() - 20, current_y), 2)
        current_y += 20
        
        # ===== CURRENT SETTINGS DETAILS =====
        if game_manager and hasattr(game_manager, 'difficulty_manager'):
            settings = game_manager.difficulty_manager.get_settings()
            
            # Title
            details_title = self.font.render("CURRENT SETTINGS", True, CYAN)
            content_surface.blit(details_title, (15, current_y))
            current_y += 35
            
            # Detail dalam 2 kolom
            col1_x = 30
            col2_x = content_surface.get_width() // 2 + 10
            
            # Kolom 1
            details_left = [
                ("Player Health", f"{settings['player_health']} HP", YELLOW),
                ("Enemy Speed", f"{int(settings['enemy_speed_multiplier'] * 100)}%", GREEN),
                ("Enemy Health", f"{int(settings['enemy_health_multiplier'] * 100)}%", RED),
                ("Enemy Damage", f"{int(settings['enemy_damage_multiplier'] * 100)}%", ORANGE),
                ("Fire Rate", f"{int(settings['fire_rate_multiplier'] * 100)}%", MAGENTA)
            ]
            
            for label, value, color in details_left:
                label_text = self.small_font.render(label, True, (200, 200, 200))
                value_text = self.small_font.render(value, True, color)
                
                content_surface.blit(label_text, (col1_x, current_y))
                content_surface.blit(value_text, (col1_x + 200, current_y))
                current_y += 25
            
            # Kolom 2 (mulai dari posisi yang sama dengan kolom 1)
            current_y = current_y - (len(details_left) * 25)  # Kembali ke posisi awal
            
            details_right = [
                ("Spawn Rate", f"{int(settings['spawn_rate_multiplier'] * 100)}%", CYAN),
                ("Powerup Chance", f"{int(settings['powerup_drop_chance'] * 100)}%", BLUE),
                ("Powerup Duration", f"{int(settings['powerup_duration_multiplier'] * 100)}%", PURPLE),
            ]
            
            for label, value, color in details_right:
                label_text = self.small_font.render(label, True, (200, 200, 200))
                value_text = self.small_font.render(value, True, color)
                
                content_surface.blit(label_text, (col2_x, current_y))
                content_surface.blit(value_text, (col2_x + 200, current_y))
                current_y += 25
            
            # Pindah ke posisi setelah kedua kolom
            current_y += 60
            
            # ===== ALLOWED ENEMIES =====
            enemies_title = self.font.render("ALLOWED ENEMIES", True, CYAN)
            content_surface.blit(enemies_title, (15, current_y))
            current_y += 40
            
            # Tampilkan enemies yang diizinkan
            allowed_enemies = settings.get("allowed_enemies", [])
            
            # Format enemy names agar lebih readable
            enemy_display_names = {
                "normal": "Normal",
                "fast": "Fast",
                "bouncer": "Bouncer",
                "red_shooter": "Red Shooter",
                "kamikaze": "Kamikaze",
                "follower": "Follower",
                "strong": "Strong",
                "tank": "Tank",
                "splitter": "Splitter",
                "spiral": "Spiral",
                "armored": "Armored",
                "bee": "Bee Swarm",
                "regenerator": "Regenerator"
            }
            
            # Tampilkan dalam grid 3 kolom
            col_width = (content_surface.get_width() - 60) // 3
            
            for i, enemy_key in enumerate(allowed_enemies):
                if enemy_key in enemy_display_names:
                    enemy_name = enemy_display_names[enemy_key]
                    col = i % 3
                    row = i // 3
                    
                    enemy_text = self.tiny_font.render(f"• {enemy_name}", True, GREEN)
                    content_surface.blit(enemy_text, 
                                    (30 + col * col_width, 
                                        current_y + row * 18))
            
            rows_needed = (len(allowed_enemies) + 2) // 3  # Pembulatan ke atas
            current_y += rows_needed * 18 + 20
            
            # ===== DIFFICULTY DESCRIPTION =====
            desc_title = self.font.render("DESCRIPTION", True, CYAN)
            content_surface.blit(desc_title, (15, current_y))
            current_y += 35
            
            difficulty_descriptions = {
                "easy": "Perfect for beginners. Enemies are slower and weaker, powerups drop more often.",
                "normal": "Balanced experience. Standard challenge for most players.",
                "hard": "For experienced players. Enemies are tougher and faster, fewer powerups.",
                "extreme": "Only for the bravest. Maximum challenge with minimal health and tough enemies."
            }
            
            current_desc = difficulty_descriptions.get(current_difficulty, "")
            # Word wrap untuk description
            words = current_desc.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                if self.tiny_font.size(test_line)[0] < content_surface.get_width() - 40:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            
            if current_line:
                lines.append(current_line)
            
            for line in lines:
                desc_text = self.tiny_font.render(line, True, (200, 200, 200))
                content_surface.blit(desc_text, (20, current_y))
                current_y += 18
            
            current_y += 10
        
        # Simpan tinggi total konten
        self.difficulty_content_height = current_y + 15
        
        # ===== APPLY SCROLL =====
        max_scroll = max(0, self.difficulty_content_height - content_rect.height)
        self.difficulty_scroll_y = max(0, min(self.difficulty_scroll_y, max_scroll))
        
        # Gambar konten yang terlihat saja
        visible_rect = pygame.Rect(0, self.difficulty_scroll_y, content_rect.width - 25, content_rect.height)
        screen.blit(content_surface, (content_rect.x + 10, content_rect.y), visible_rect)
        
        # ===== SCROLL BAR =====
        if self.difficulty_content_height > content_rect.height:
            scroll_ratio = content_rect.height / self.difficulty_content_height
            scrollbar_height = max(30, content_rect.height * scroll_ratio)
            scrollbar_y = content_rect.y + (self.difficulty_scroll_y / self.difficulty_content_height) * content_rect.height
            
            scrollbar_bg = pygame.Rect(content_rect.right - 12, content_rect.y, 6, content_rect.height)
            pygame.draw.rect(screen, (50, 50, 80), scrollbar_bg, border_radius=3)
            
            scrollbar_rect = pygame.Rect(
                content_rect.right - 12,
                scrollbar_y,
                6,
                scrollbar_height
            )
            scrollbar_color = YELLOW if self.difficulty_dragging else CYAN
            pygame.draw.rect(screen, scrollbar_color, scrollbar_rect, border_radius=3)
        
        # ===== INSTRUCTIONS =====
        # instructions = [
        #     "Click on difficulty card to select",
        #     "Mouse Wheel or Drag to Scroll",
        #     "BACK to return to Settings Menu"
        # ]
        
        # for i, instruction in enumerate(instructions):
        #     text = self.tiny_font.render(instruction, True, YELLOW)
        #     text_rect = text.get_rect(topleft=(20, SCREEN_HEIGHT - 50 + i * 15))
        #     screen.blit(text, text_rect)
        
        # ===== BACK BUTTON =====
        if 'back_difficulty' not in buttons:
            buttons['back_difficulty'] = Button(
                SCREEN_WIDTH // 2 - 100,
                SCREEN_HEIGHT - 80,
                200,
                50,
                "BACK",
                BLUE,
                WHITE
            )
        
        buttons['back_difficulty'].draw(screen)

    def handle_settings_events(self, events, mouse_pos, sound_manager, game_manager=None, buttons=None):
        """Handle events untuk settings menu dengan struktur submenu - FIXED: Lengkap"""
        volume_changed = False
        difficulty_changed = False
        current_time = pygame.time.get_ticks()
        
        # PERBAIKAN: Pastikan buttons tidak None
        if buttons is None:
            buttons = {}
        
        # Handle preview sound timing
        if self.preview_sound_active:
            if current_time - self.preview_sound_timer > 300:
                sound_manager.play_preview_sound()
                self.preview_sound_timer = current_time
        
        for event in events:
            # ===== MOUSE CLICK NAVIGATION =====
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Handle navigation berdasarkan submenu
                if self.settings_submenu == "main":
                    if 'audio_settings' in buttons and buttons['audio_settings'].is_clicked(mouse_pos):
                        self.settings_submenu = "audio"
                        return True
                    elif 'difficulty_settings' in buttons and buttons['difficulty_settings'].is_clicked(mouse_pos):
                        self.settings_submenu = "difficulty"
                        return True
                    elif 'back_settings' in buttons and buttons['back_settings'].is_clicked(mouse_pos):
                        self.settings_submenu = "main"
                        return True
                
                elif self.settings_submenu == "audio":
                    if 'back_audio' in buttons and buttons['back_audio'].is_clicked(mouse_pos):
                        self.settings_submenu = "main"
                        return True
                
                elif self.settings_submenu == "difficulty":
                    if 'back_difficulty' in buttons and buttons['back_difficulty'].is_clicked(mouse_pos):
                        self.settings_submenu = "main"
                        return True
            
            # ===== HANDLE SLIDER EVENTS (audio submenu) =====
            if self.settings_submenu == "audio":
                for slider_name, slider in self.sliders.items():
                    slider_changed = slider.handle_event(event, mouse_pos)
                    
                    if slider_changed:
                        volume_changed = True
                        
                        # Update sound manager berdasarkan slider yang diubah
                        new_value = slider.get_value()
                        new_volume = new_value / 100.0
                        
                        if slider_name == 'sfx':
                            sound_manager.set_sfx_volume(new_volume)
                            
                            # Aktifkan preview sound
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                self.preview_sound_active = True
                                self.preview_sound_timer = current_time
                                sound_manager.play_preview_sound()
                            elif event.type == pygame.MOUSEMOTION and slider.dragging:
                                self.preview_sound_active = True
                                if current_time - self.preview_sound_timer > 150:
                                    sound_manager.play_preview_sound()
                                    self.preview_sound_timer = current_time
                        
                        elif slider_name == 'music':
                            sound_manager.set_music_volume(new_volume)
            
            # ===== HANDLE DIFFICULTY CARD CLICKS (difficulty submenu) =====
            if self.settings_submenu == "difficulty" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for difficulty_key, card_rect in self.difficulty_boxes.items():
                    if card_rect.collidepoint(mouse_pos):
                        difficulty_changed = True
                        
                        # Update difficulty di game_manager
                        if game_manager and hasattr(game_manager, 'difficulty_manager'):
                            game_manager.difficulty_manager.set_difficulty(difficulty_key)
                        
                        # Play sound feedback
                        if sound_manager:
                            sound_manager.play_sound('button_click')

            # ===== HANDLE DIFFICULTY SCROLL EVENTS =====
            if self.settings_submenu == "difficulty":
                content_rect = pygame.Rect(50, 100, 700, 430)
                scrollbar_rect = pygame.Rect(content_rect.right - 12, content_rect.y, 6, content_rect.height)
                
                for event in events:
                    if event.type == pygame.MOUSEWHEEL:
                        self.difficulty_scroll_y -= event.y * 20
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Handle click pada difficulty cards
                        for difficulty_key, card_rect in self.difficulty_boxes.items():
                            # Sesuaikan koordinat card dengan scroll
                            adjusted_rect = pygame.Rect(
                                card_rect.x + content_rect.x + 10,
                                card_rect.y + content_rect.y - self.difficulty_scroll_y,
                                card_rect.width,
                                card_rect.height
                            )
                            
                            if adjusted_rect.collidepoint(mouse_pos):
                                difficulty_changed = True
                                
                                # Update difficulty di game_manager
                                if game_manager and hasattr(game_manager, 'difficulty_manager'):
                                    game_manager.difficulty_manager.set_difficulty(difficulty_key)
                                
                                # Play sound feedback
                                sound_manager.play_sound('button_click')
                        
                        # Handle scroll bar drag
                        if scrollbar_rect.collidepoint(mouse_pos) or content_rect.collidepoint(mouse_pos):
                            self.difficulty_dragging = True
                            self.difficulty_drag_start_y = mouse_pos[1]
                            self.difficulty_drag_start_scroll = self.difficulty_scroll_y
                    
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.difficulty_dragging = False
                    
                    elif event.type == pygame.MOUSEMOTION:
                        if self.difficulty_dragging:
                            delta_y = mouse_pos[1] - self.difficulty_drag_start_y
                            max_scroll = max(0, self.difficulty_content_height - content_rect.height)
                            scroll_ratio = self.difficulty_content_height / content_rect.height
                            
                            new_scroll = self.difficulty_drag_start_scroll + (delta_y * scroll_ratio)
                            self.difficulty_scroll_y = max(0, min(new_scroll, max_scroll))
            
            # ===== HANDLE MOUSE BUTTON UP =====
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.preview_sound_active = False
        
        # Nonaktifkan preview sound jika mouse tidak ditekan
        mouse_buttons = pygame.mouse.get_pressed()
        if not mouse_buttons[0]:
            self.preview_sound_active = False
        
        return volume_changed or difficulty_changed
    
    def _handle_audio_sliders(self, events, mouse_pos, sound_manager):
        """Handle audio slider events - SIMPLIFIED"""
        volume_changed = False
        for slider_name, slider in self.sliders.items():
            if slider.handle_event(events, mouse_pos):
                new_volume = slider.get_value() / 100.0
                if slider_name == 'sfx':
                    sound_manager.set_sfx_volume(new_volume)
                elif slider_name == 'music':
                    sound_manager.set_music_volume(new_volume)
                volume_changed = True
        return volume_changed

    def update_slider_values(self, sound_manager):
        """Update nilai slider berdasarkan sound manager"""
        volumes = sound_manager.get_volumes()
        
        for slider_name, slider in self.sliders.items():
            if slider_name in volumes and not slider.dragging:
                if abs(slider.value - volumes[slider_name]) > 1:
                    slider.value = volumes[slider_name]
                    slider.handle_x = slider.value_to_pixel()

    # PERBAIKAN: Tambahkan method reset_settings_submenu yang hilang
    def reset_settings_submenu(self):
        """Reset settings submenu ke main saat keluar dari settings"""
        self.settings_submenu = "main"
        # Reset scroll position
        self.difficulty_scroll_y = 0
        self.difficulty_dragging = False
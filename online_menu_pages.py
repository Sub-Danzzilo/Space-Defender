import pygame
import random
from button import Button

# ========== KONSTANTA ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class OnlineMenuPages:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)
        self.input_text = ""
        self.input_active = False
        self.cursor_visible = True  # PERBAIKAN: Untuk cursor blink
        self.error_message = ""
        self.error_timestamp = 0

        # TAMBAHKAN KONSTANTA WARNA DI SINI
        self.DIFFICULTY_COLORS = {
            "easy": (0, 255, 0),      # HIJAU
            "normal": (0, 150, 255),  # BIRU
            "hard": (255, 150, 0),    # ORANGE
            "extreme": (255, 0, 0)    # MERAH
        }
        self.COLOR_P1 = (0, 255, 0)   # HIJAU untuk P1
        self.COLOR_P2 = (0, 255, 255) # CYAN untuk P2
    
    def draw_online_mode_selection(self, screen, buttons):
        """Pilih antara local dan online multiplayer - FIXED HOVER"""
        # Background dengan gradient
        for i in range(600):
            color_intensity = int(20 + (i / 600) * 40)
            pygame.draw.line(screen, (color_intensity, 0, color_intensity * 2), (0, i), (800, i))
        
        # Title dengan underline
        title = pygame.font.Font(None, 72).render("SELECT MULTIPLAYER MODE", True, (0, 255, 255))
        title_rect = title.get_rect(center=(400, 60))
        screen.blit(title, title_rect)
        
        # Underline
        pygame.draw.line(screen, (0, 255, 255), (100, 120), (700, 120), 2)
        
        # PERBAIKAN: JANGAN CLEAR TOMBOL - hanya buat jika belum ada
        button_width, button_height = 350, 80
        button_x = 400 - button_width//2
        
        if 'local_multiplayer' not in buttons:
            buttons['local_multiplayer'] = Button(
                button_x, 180, button_width, button_height,
                "LOCAL MULTIPLAYER", (0, 200, 0), (0, 0, 0),
                font_size=24,
                hover_color=(0, 255, 100)  # TAMBAHKAN INI
            )
        
        if 'online_multiplayer' not in buttons:
            buttons['online_multiplayer'] = Button(
                button_x, 280, button_width, button_height, 
                "ONLINE MULTIPLAYER", (0, 100, 200), (255, 255, 255)
            )
        
        if 'back_online' not in buttons:
            buttons['back_online'] = Button(
                400 - 100, 500, 200, 50, "BACK", (0, 100, 200), (255, 255, 255)
            )
        
        # ===== DRAW BUTTONS =====
        for button in buttons.values():
            button.draw(screen)

        # ===== INSTRUCTIONS =====
        instructions = [
            "Local: Play with a friend on the same computer",
            "Online: Play with a friend over the internet (requires ZeroTier)"
        ]

        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, (200, 200, 100))
            screen.blit(text, (400 - text.get_width()//2, 390 + i * 25))

        # ===== UPDATE HOVER =====
        mouse_pos = pygame.mouse.get_pos()
        for btn in ['local_multiplayer', 'online_multiplayer', 'back_online']:
            if btn in buttons:
                buttons[btn].update_hover(mouse_pos)

    
    def draw_host_join_selection(self, screen, buttons):
        """Pilih antara host atau join game - FIXED HOVER"""
        # Background dengan gradient
        for i in range(600):
            color_intensity = int(20 + (i / 600) * 40)
            pygame.draw.line(screen, (0, color_intensity, color_intensity * 2), (0, i), (800, i))
        
        # Title dengan underline
        title = pygame.font.Font(None, 72).render("ONLINE MULTIPLAYER", True, (0, 255, 255))
        title_rect = title.get_rect(center=(400, 60))
        screen.blit(title, title_rect)
        
        # Underline
        pygame.draw.line(screen, (0, 255, 255), (100, 120), (700, 120), 2)
        
        # PERBAIKAN: HANYA BUAT TOMBOL JIKA BELUM ADA - JANGAN CLEAR
        button_width, button_height = 350, 80
        button_x = 400 - button_width//2

        if 'host_game' not in buttons:
            buttons['host_game'] = Button(
                button_x, 180, button_width, button_height,
                "HOST GAME", (0, 200, 0), (0, 0, 0),
                font_size=24,
                hover_color=(0, 255, 100)
            )

        if 'join_game' not in buttons:
            buttons['join_game'] = Button(
                button_x, 280, button_width, button_height,
                "JOIN GAME", (0, 100, 200), (255, 255, 255)
            )

        if 'back_host_join' not in buttons:
            buttons['back_host_join'] = Button(
                400 - 100, 500, 200, 50, "BACK", (0, 100, 200), (255, 255, 255)
            )
        
        # Draw buttons
        for button in buttons.values():
            button.draw(screen)
            
        # Instructions
        instructions = [
            "Host: Create a game and wait for players to join",
            "Join: Connect to an existing game using host's IP"
        ]
        
        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, (200, 200, 100))
            screen.blit(text, (400 - text.get_width()//2, 390 + i * 25))  # Dari 370 ke 380

        # ===== UPDATE HOVER =====
        mouse_pos = pygame.mouse.get_pos()
        for btn in ['host_game', 'join_game', 'back_host_join']:
            if btn in buttons:
                buttons[btn].update_hover(mouse_pos)
    
    def draw_host_waiting(self, screen, network_manager, buttons, difficulty_mode=None, control_settings=None):
        """Screen host waiting for client - WITH PROPER STAR BACKGROUND"""
        
        # ===== TITLE SECTION =====
        title_bg = pygame.Rect(SCREEN_WIDTH//2 - 250, 20, 500, 80)
        pygame.draw.rect(screen, (0, 0, 0, 180), title_bg, border_radius=15)
        pygame.draw.rect(screen, (0, 200, 200), title_bg, 3, border_radius=15)
        
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("HOST GAME", True, (0, 200, 255))
        
        if network_manager.connected:
            subtitle = self.small_font.render("Player Connected!", True, (0, 255, 0))
        else:
            dot_count = (pygame.time.get_ticks() // 500) % 4
            dots = "." * dot_count
            subtitle = self.small_font.render(f"Waiting for player{dots}", True, (200, 200, 255))
        
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 35))
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 75))
        
        # ===== IP DISPLAY SECTION =====
        ip_section_y = 120
        
        # Label
        ip_label = self.font.render("YOUR ZEROTIER IP:", True, (200, 240, 255))
        screen.blit(ip_label, (SCREEN_WIDTH//2 - ip_label.get_width()//2, ip_section_y))
        
        # Display box
        display_width = 500
        display_rect = pygame.Rect(
            SCREEN_WIDTH//2 - display_width//2, 
            ip_section_y + 40, 
            display_width, 
            50
        )
        
        # Warna box
        box_color = (60, 100, 180)
        border_color = (100, 255, 255)
        
        pygame.draw.rect(screen, box_color, display_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, display_rect, 3, border_radius=8)
        
        # IP text
        if hasattr(network_manager, 'zerotier_ip'):
            zt_ip = network_manager.zerotier_ip
            
            if zt_ip == "MANUAL_REQUIRED" or zt_ip == "ERROR" or not zt_ip:
                display_text = "IP not detected - Click Refresh"
                text_color = (255, 200, 100)
            else:
                display_text = zt_ip
                text_color = (255, 255, 255)
        else:
            display_text = "IP not detected - Click Refresh"
            text_color = (255, 200, 100)
        
        # Potong teks jika terlalu panjang
        text_surface = self.small_font.render(display_text, True, text_color)
        max_width = display_rect.width - 40
        
        if text_surface.get_width() > max_width:
            while text_surface.get_width() > max_width and len(display_text) > 10:
                display_text = "..." + display_text[4:]
                text_surface = self.small_font.render(display_text, True, text_color)
        
        screen.blit(text_surface, (display_rect.x + 20, display_rect.y + 12))
        
        # ===== BUTTONS SECTION =====
        buttons_y = ip_section_y + 110
        
        # Tombol Refresh IP (KIRI)
        refresh_width = 240
        refresh_x = 50
        
        if 'refresh_ip' not in buttons:
            buttons['refresh_ip'] = Button(
                refresh_x, buttons_y, refresh_width, 50,
                "REFRESH IP", 
                (0, 100, 200), (255, 255, 255),
                font_size=24,
                hover_color=(100, 200, 255)
            )
        buttons['refresh_ip'].draw(screen)
        
        # Tombol Back (KANAN)
        cancel_width = 200
        cancel_x = SCREEN_WIDTH - 50 - cancel_width
        
        if 'cancel_host' not in buttons:
            buttons['cancel_host'] = Button(
                cancel_x, buttons_y, cancel_width, 50,
                "BACK",
                (180, 0, 0), (255, 255, 255),
                font_size=22,
                hover_color=(255, 100, 100)
            )
        buttons['cancel_host'].draw(screen)
        
        # ===== STATUS SECTION =====
        status_y = buttons_y + 80
        
        status_rect = pygame.Rect(50, status_y, SCREEN_WIDTH - 100, 80)
        pygame.draw.rect(screen, (0, 0, 0, 180), status_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 120, 180), status_rect, 2, border_radius=10)
        
        # Status text
        if network_manager.connected:
            status_color = (0, 255, 0)
            status_text = "PLAYER CONNECTED!"
            detail_text = "Click 'START GAME' to begin"
        else:
            status_color = (255, 255, 0)
            dot_count = (pygame.time.get_ticks() // 500) % 4
            dots = "." * dot_count
            status_text = f"WAITING FOR PLAYER{dots}"
            detail_text = "Share IP above with player"
        
        status_label = self.font.render(status_text, True, status_color)
        screen.blit(status_label, (SCREEN_WIDTH//2 - status_label.get_width()//2, status_y + 15))
        
        detail = self.small_font.render(detail_text, True, (200, 200, 200))
        screen.blit(detail, (SCREEN_WIDTH//2 - detail.get_width()//2, status_y + 50))
        
        # ===== DETAILED CONTROLS SECTION =====
        controls_y = status_y + 100
        
        # Box untuk controls yang lebih besar
        controls_rect = pygame.Rect(50, controls_y, SCREEN_WIDTH - 100, 150)  # Ditinggikan
        pygame.draw.rect(screen, (20, 20, 40, 180), controls_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 0, 150), controls_rect, 2, border_radius=10)
        
        # Title untuk controls
        controls_title = self.font.render("GAME SETTINGS", True, (255, 100, 255))
        screen.blit(controls_title, (SCREEN_WIDTH//2 - controls_title.get_width()//2, controls_y + 10))
        
        # Difficulty dengan warna
        if difficulty_mode:
            diff_colors = {
                "easy": (0, 255, 0),      # Hijau
                "normal": (0, 150, 255),  # Biru
                "hard": (255, 150, 0),    # Orange
                "extreme": (255, 0, 0)    # Merah
            }
            diff_color = diff_colors.get(difficulty_mode, (255, 255, 255))
            diff_display = difficulty_mode.upper()
            
            diff_surface = self.small_font.render(f"Difficulty: {diff_display}", True, diff_color)
            screen.blit(diff_surface, (controls_rect.x + 30, controls_y + 45))
        
        # Controls detail
        if control_settings:
            p1_controls = control_settings.get_player_controls(1)
            p2_controls = control_settings.get_player_controls(2)
            
            # Player 1 Controls detail
            p1_y = controls_y + 45
            p1_label = self.small_font.render("Player 1 Controls:", True, (200, 200, 200))
            p1_scheme = self.small_font.render(p1_controls['name'], True, (0, 255, 0))
            screen.blit(p1_label, (controls_rect.x + 250, p1_y))
            screen.blit(p1_scheme, (controls_rect.x + 400, p1_y))
            
            # Player 2 Controls detail
            p2_y = p1_y + 25
            p2_label = self.small_font.render("Player 2 Controls:", True, (200, 200, 200))
            p2_scheme = self.small_font.render(p2_controls['name'], True, (0, 200, 255))
            screen.blit(p2_label, (controls_rect.x + 250, p2_y))
            screen.blit(p2_scheme, (controls_rect.x + 400, p2_y))
        
        # Port info
        port_y = controls_y + 85
        port_text = self.small_font.render(f"Port: {network_manager.port}", True, (200, 200, 200))
        screen.blit(port_text, (controls_rect.x + 30, port_y))
        
        # Connection info
        conn_y = port_y + 25
        conn_text = self.small_font.render("Both players must be in same ZeroTier network", True, (255, 255, 100))
        screen.blit(conn_text, (SCREEN_WIDTH//2 - conn_text.get_width()//2, conn_y))
        
        # ===== START GAME BUTTON SECTION =====
        if network_manager.connected:
            start_y = controls_y + 160  # Disesuaikan dengan box controls yang lebih tinggi
            
            if 'start_online_game' not in buttons:
                buttons['start_online_game'] = Button(
                    SCREEN_WIDTH//2 - 150, start_y, 300, 60,
                    "START ONLINE GAME",
                    (0, 180, 0), (255, 255, 255),
                    font_size=26,
                    hover_color=(0, 255, 0)
                )
            buttons['start_online_game'].draw(screen)
            
            # Status final
            final_y = start_y + 70
            final_text = self.small_font.render("Ready! Game will start for both players.", True, (0, 255, 0))
            screen.blit(final_text, (SCREEN_WIDTH//2 - final_text.get_width()//2, final_y))
        
        # ===== UPDATE HOVER =====
        mouse_pos = pygame.mouse.get_pos()
        for btn in ['refresh_ip', 'cancel_host', 'start_online_game']:
            if btn in buttons:
                buttons[btn].update_hover(mouse_pos)

    def draw_join_connecting(self, screen, network_manager, buttons):
        """Screen client mencoba connect - COMPACT VERSION"""
        
        # ===== TITLE =====
        title_bg = pygame.Rect(SCREEN_WIDTH//2 - 250, 20, 500, 80)
        pygame.draw.rect(screen, (0, 0, 0, 180), title_bg, border_radius=15)
        pygame.draw.rect(screen, (0, 150, 200), title_bg, 3, border_radius=15)
        
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("JOIN ONLINE GAME", True, (0, 200, 255))
        subtitle = self.small_font.render("Connect to Host", True, (150, 220, 255))
        
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 35))
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 75))
        
        # ===== IP INPUT =====
        ip_section_y = 120
        
        # Label
        ip_label = self.font.render("ENTER HOST IP:", True, (200, 240, 255))
        screen.blit(ip_label, (SCREEN_WIDTH//2 - ip_label.get_width()//2, ip_section_y))
        
        # Input box
        input_width = 500
        input_rect = pygame.Rect(
            SCREEN_WIDTH//2 - input_width//2, 
            ip_section_y + 40, 
            input_width, 
            50
        )
        
        if self.input_active:
            box_color = (60, 100, 180)
            border_color = (100, 255, 255)
        else:
            box_color = (30, 50, 100)
            border_color = (80, 160, 220)
        
        pygame.draw.rect(screen, box_color, input_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, input_rect, 3, border_radius=8)
        
        # Text input
        display_text = self.input_text
        if not display_text and not self.input_active:
            display_text = "e.g., 192.168.1.100"
            text_color = (150, 150, 180)
        else:
            text_color = (255, 255, 255)
        
        text_surface = self.small_font.render(display_text, True, text_color)
        
        # Clip text
        max_width = input_rect.width - 40
        if text_surface.get_width() > max_width:
            while text_surface.get_width() > max_width and len(display_text) > 3:
                display_text = "..." + display_text[4:]
                text_surface = self.small_font.render(display_text, True, text_color)
        
        screen.blit(text_surface, (input_rect.x + 20, input_rect.y + 12))
        
        # Cursor
        if self.input_active and self.cursor_visible:
            cursor_x = input_rect.x + 20 + text_surface.get_width()
            cursor_rect = pygame.Rect(cursor_x, input_rect.y + 10, 2, 30)
            pygame.draw.rect(screen, (255, 255, 255), cursor_rect)
        
        # ===== BUTTONS (SEJAJAR - KEBALIKAN) =====
        buttons_y = ip_section_y + 110

        # Connect to Host button (KIRI)
        connect_width = 240
        connect_x = 50  # 50px dari kiri

        if 'connect_to_host' not in buttons:
            buttons['connect_to_host'] = Button(
                connect_x, buttons_y, connect_width, 50,
                "CONNECT TO HOST", 
                (0, 180, 0), (255, 255, 255),
                font_size=24,
                hover_color=(0, 255, 0)
            )
        buttons['connect_to_host'].draw(screen)

        # Back button (KANAN)
        back_width = 200
        back_x = SCREEN_WIDTH - 50 - back_width  # 50px dari kanan

        if 'cancel_join' not in buttons:
            buttons['cancel_join'] = Button(
                back_x, buttons_y, back_width, 50,
                "BACK", 
                (180, 0, 0), (255, 255, 255),
                font_size=22,
                hover_color=(255, 100, 100)
            )
        buttons['cancel_join'].draw(screen)
        
        # ===== STATUS =====
        status_y = buttons_y + 80
        
        # PERBAIKAN: Ambil error dari network_manager jika ada
        if not self.error_message and hasattr(network_manager, 'error_message') and network_manager.error_message:
            self.error_message = network_manager.error_message
            self.error_timestamp = pygame.time.get_ticks()
        
        # PERBAIKAN: Tampilkan error lebih lama (10 detik)
        current_time = pygame.time.get_ticks()
        show_error = (self.error_message and 
                    current_time - getattr(self, 'error_timestamp', 0) < 10000)  # 10 detik
        
        status_rect = pygame.Rect(50, status_y, SCREEN_WIDTH - 100, 80)
        pygame.draw.rect(screen, (0, 0, 0, 180), status_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 120, 180), status_rect, 2, border_radius=10)
        
        # Status text berdasarkan kondisi
        if network_manager.connected:
            status_color = (0, 255, 0)
            status_text = "CONNECTED"
            detail_text = "Waiting for host to start game..."
        elif show_error:
            status_color = (255, 50, 50)  # Merah untuk error
            status_text = "CONNECTION FAILED!"
            detail_text = f"{self.error_message}"
        else:
            status_color = (255, 255, 0)
            dot_count = (pygame.time.get_ticks() // 500) % 4
            dots = "." * dot_count
            status_text = f"READY TO CONNECT{dots}"
            detail_text = "Enter host IP and click CONNECT"
        
        status_label = self.font.render(status_text, True, status_color)
        screen.blit(status_label, (SCREEN_WIDTH//2 - status_label.get_width()//2, status_y + 15))
        
        detail = self.small_font.render(detail_text, True, (200, 200, 200))
        screen.blit(detail, (SCREEN_WIDTH//2 - detail.get_width()//2, status_y + 50))
        
        # ===== SHORT INSTRUCTIONS =====
        if not network_manager.connected:  # Hanya tampilkan jika belum connect
            instruct_y = status_y + 100
            
            # TINGGIKAN KOTAK: dari 100 menjadi 140 (atau 160 untuk lebih lega)
            box_height = 140  # Ganti dari 100 ke 140 atau sesuaikan kebutuhan
            instruct_rect = pygame.Rect(50, instruct_y, SCREEN_WIDTH - 100, box_height)
            pygame.draw.rect(screen, (20, 20, 40, 180), instruct_rect, border_radius=10)
            pygame.draw.rect(screen, (150, 0, 150), instruct_rect, 2, border_radius=10)
            
            instruct_title = self.small_font.render("QUICK GUIDE:", True, (255, 100, 255))
            screen.blit(instruct_title, (SCREEN_WIDTH//2 - instruct_title.get_width()//2, instruct_y + 15))
            
            instructions = [
                "• Ask host for ZeroTier IP",
                "• Enter IP above and click CONNECT",
                "• Both must be on same ZeroTier"
            ]
            
            # SESUAIKAN POSISI TEKS DENGAN KOTAK YANG LEBIH TINGGI
            # Hitung total tinggi konten teks: 3 baris × 25 spacing = 75
            # Beri margin atas lebih besar (30) dan margin bawah otomatis
            start_y = instruct_y + 45  # Dari 35 menjadi 45 untuk memberikan ruang lebih
            
            for i, line in enumerate(instructions):
                text = self.small_font.render(line, True, (220, 200, 255))
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, start_y + i * 30))  # Spacing dari 25 ke 30
        
        # # ===== FOOTER KEYS =====
        # footer_y = SCREEN_HEIGHT - 40
        # shortcuts = [
        #     "Press ENTER to connect • Press ESC to go back",
        #     "Click IP field to type • Tab to switch fields"
        # ]
        
        # for i, text in enumerate(shortcuts):
        #     shortcut = self.tiny_font.render(text, True, (150, 200, 255))
        #     screen.blit(shortcut, (SCREEN_WIDTH//2 - shortcut.get_width()//2, footer_y + i * 15))
        
        # ===== UPDATE HOVER & CURSOR =====
        mouse_pos = pygame.mouse.get_pos()
        if 'connect_to_host' in buttons:
            buttons['connect_to_host'].update_hover(mouse_pos)
        if 'cancel_join' in buttons:
            buttons['cancel_join'].update_hover(mouse_pos)
        
        # Cursor blink
        if self.input_active:
            if pygame.time.get_ticks() % 1000 < 500:
                self.cursor_visible = True
            else:
                self.cursor_visible = False
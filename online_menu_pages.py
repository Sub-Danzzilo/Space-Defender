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
    
    def draw_host_waiting(self, screen, network_manager, buttons, difficulty_mode=None, control_settings=None, client_cancel_alert_time=0):
        """Screen host waiting for client - WITH PROPER STAR BACKGROUND"""
        
        # ===== TITLE SECTION =====
        title_bg = pygame.Rect(SCREEN_WIDTH//2 - 250, 20, 500, 80)
        pygame.draw.rect(screen, (0, 0, 0, 180), title_bg, border_radius=15)
        pygame.draw.rect(screen, (0, 200, 200), title_bg, 3, border_radius=15)

        title_font = pygame.font.Font(None, 48)
        title = title_font.render("HOST GAME", True, (0, 200, 255))

        # PERBAIKAN: Subtitle tetap, tidak ada animasi dots
        if network_manager.connected:
            subtitle = self.small_font.render("Player Connected - Ready to Start", True, (0, 255, 0))
        else:
            subtitle = self.small_font.render("Waiting for player to connect", True, (200, 200, 255))

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
        
        # ===== TIDAK ADA KODE PEMBUATAN TOMBOL DI SINI =====
        # Tombol sudah dibuat oleh Game.load_buttons_for_state() berdasarkan template
        # Jangan hapus atau buat tombol di sini
        
        # ===== CLIENT CANCELLED ALERT =====
        if client_cancel_alert_time > 0:
            current_time = pygame.time.get_ticks()
            if current_time - client_cancel_alert_time < 3000:  # 3 detik
                alert_y = 350
                alert_rect = pygame.Rect(50, alert_y, SCREEN_WIDTH - 100, 40)
                pygame.draw.rect(screen, (100, 20, 20, 200), alert_rect, border_radius=8)
                pygame.draw.rect(screen, (255, 100, 100), alert_rect, 2, border_radius=8)
                
                alert_text = self.small_font.render("Client cancelled connection", True, (255, 200, 200))
                screen.blit(alert_text, (SCREEN_WIDTH//2 - alert_text.get_width()//2, alert_y + 10))
        
        # ===== STATUS SECTION =====
        # PERBAIKAN: Gunakan network_manager.connected untuk status
        status_y = 310
        
        status_rect = pygame.Rect(50, status_y, SCREEN_WIDTH - 100, 80)
        pygame.draw.rect(screen, (0, 0, 0, 180), status_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 120, 180), status_rect, 2, border_radius=10)
        
        # Status text - PERBAIKAN: Gunakan network_manager.connected
        if network_manager.connected:
            status_color = (0, 255, 0)
            status_text = "PLAYER CONNECTED!"
            detail_text = "Click 'START GAME' to begin"
            # PERBAIKAN: Tampilkan informasi tambahan
            if hasattr(network_manager, 'client_socket'):
                try:
                    client_ip = network_manager.client_socket.getpeername()[0]
                    detail_text = f"Player connected from {client_ip}"
                except:
                    pass
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
        controls_y = 410
        
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
            p1_label = self.small_font.render("Player 1 Controls (YOU):", True, (200, 200, 200))
            p1_scheme = self.small_font.render(p1_controls['name'], True, (0, 255, 0))
            screen.blit(p1_label, (controls_rect.x + 250, p1_y))
            screen.blit(p1_scheme, (controls_rect.x + 475, p1_y))
            
            # Player 2 Controls detail
            p2_y = p1_y + 25
            p2_label = self.small_font.render("Player 2 Controls (CLIENT):", True, (200, 200, 200))
            p2_scheme = self.small_font.render(p2_controls['name'], True, (0, 200, 255))
            screen.blit(p2_label, (controls_rect.x + 250, p2_y))
            screen.blit(p2_scheme, (controls_rect.x + 475, p2_y))
        
        # Port info
        port_y = controls_y + 70
        port_text = self.small_font.render(f"Port: {network_manager.port}", True, (200, 200, 200))
        screen.blit(port_text, (controls_rect.x + 30, port_y))
        
        # Connection info
        conn_y = port_y + 45
        conn_text = self.small_font.render("Both players must be in same ZeroTier network", True, (255, 255, 100))
        screen.blit(conn_text, (SCREEN_WIDTH//2 - conn_text.get_width()//2, conn_y))
        
        # ===== UPDATE HOVER SEBELUM MENGGAMBAR =====
        # Harus update hover dulu agar draw() memakai state is_hovered yang up-to-date
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons.values():
            btn.update_hover(mouse_pos)
        
        # ===== GAMBAR TOMBOL =====
        # PERBAIKAN: Hanya gambar tombol yang ada di buttons
        for button in buttons.values():
            button.draw(screen)

    def draw_waiting_for_host_popup(self, screen):
        """Popup kecil untuk client yang menunggu host - FIXED OVERFLOW"""
        # Overlay semi-transparent (seperti pause)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # Sedikit lebih gelap dari pause
        screen.blit(overlay, (0, 0))
        
        # Kotak popup - LEBIH BESAR dikit
        popup_width, popup_height = 500, 200
        popup_x = (SCREEN_WIDTH - popup_width) // 2
        popup_y = (SCREEN_HEIGHT - popup_height) // 2
        
        # Background popup
        pygame.draw.rect(screen, (30, 40, 60), (popup_x, popup_y, popup_width, popup_height), border_radius=15)
        pygame.draw.rect(screen, (0, 150, 200), (popup_x, popup_y, popup_width, popup_height), 3, border_radius=15)
        
        # Judul - SINGKAT AJA
        title_font = pygame.font.Font(None, 32)
        title = title_font.render("WAITING FOR HOST", True, (0, 200, 255))
        screen.blit(title, (popup_x + (popup_width - title.get_width()) // 2, popup_y + 20))
        
        # Pesan - DIPENDEKIN DAN DIPECAH
        message_lines = [
            "Connected to host!",
            "Waiting for host to start game..."
        ]
        
        for i, line in enumerate(message_lines):
            line_surface = self.small_font.render(line, True, (200, 200, 200))
            # CENTER TEXT, JANGAN MANUAL POSITIONING
            screen.blit(line_surface, (popup_x + (popup_width - line_surface.get_width()) // 2, popup_y + 60 + i * 25))
        
        # Tombol Cancel dengan hover effect
        cancel_width, cancel_height = 180, 40
        cancel_x = popup_x + (popup_width - cancel_width) // 2
        cancel_y = popup_y + popup_height - cancel_height - 20
        
        # Cek hover
        mouse_pos = pygame.mouse.get_pos()
        cancel_rect = pygame.Rect(cancel_x, cancel_y, cancel_width, cancel_height)
        is_hover = cancel_rect.collidepoint(mouse_pos)
        
        # Warna tombol berdasarkan hover
        if is_hover:
            btn_color = (220, 60, 60)  # Merah terang saat hover
            border_color = (255, 120, 120)
        else:
            btn_color = (180, 40, 40)  # Merah gelap saat normal
            border_color = (255, 100, 100)
        
        # Gambar tombol cancel
        pygame.draw.rect(screen, btn_color, cancel_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, cancel_rect, 2, border_radius=8)
        
        cancel_text = self.small_font.render("CANCEL CONNECT", True, (255, 255, 255))
        screen.blit(cancel_text, (cancel_x + (cancel_width - cancel_text.get_width()) // 2, cancel_y + 12))
        
        return cancel_rect  # Kembalikan rect untuk klik detection

    def draw_join_connecting(self, screen, network_manager, buttons, game_instance=None):
        """
        Screen client mencoba connect - COMPACT VERSION
        - Shows Host Info area: Difficulty & Controls (N/A until host info arrives)
        - Shows a small centered popup when client is connected and waiting for host to START
        """
        
        # ===== TITLE =====
        title_bg = pygame.Rect(SCREEN_WIDTH//2 - 250, 20, 500, 80)
        pygame.draw.rect(screen, (0, 0, 0, 180), title_bg, border_radius=15)
        pygame.draw.rect(screen, (0, 150, 200), title_bg, 3, border_radius=15)

        title_font = pygame.font.Font(None, 48)
        title = title_font.render("JOIN ONLINE GAME", True, (0, 200, 255))
        # PERBAIKAN: Subtitle statis untuk client
        subtitle = self.small_font.render("Enter host IP address to connect", True, (150, 220, 255))

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
        
        # ===== BUTTONS (SEJAJAR) =====
        buttons_y = ip_section_y + 110

        # Selalu gunakan CONNECT TO HOST (jangan ubah jadi START ONLINE GAME)
        connect_width = 240
        connect_x = 50
        if 'connect_to_host' not in buttons:
            buttons['connect_to_host'] = Button(
                connect_x, buttons_y, connect_width, 50,
                "CONNECT TO HOST",
                (0, 100, 200), (255, 255, 255),
                font_size=22,
                hover_color=(100, 200, 255)
            )
        buttons['connect_to_host'].draw(screen)

        # Back button (KANAN) - selalu ada
        back_width = 200
        back_x = SCREEN_WIDTH - 50 - back_width

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
        
        # PERBAIKAN: Ambil error dari game_instance juga
        if not self.error_message and game_instance and hasattr(game_instance, 'online_menu_pages'):
            if game_instance.online_menu_pages.error_message:
                self.error_message = game_instance.online_menu_pages.error_message
                self.error_timestamp = game_instance.online_menu_pages.error_timestamp
        
        # PERBAIKAN: Logic yang benar untuk show_error
        current_time = pygame.time.get_ticks()
        show_error = False
        error_duration = 10000  # Default 10 detik untuk semua error
        
        # Tentukan apakah harus show error
        if self.error_message:
            # PERBAIKAN: Bedakan durasi berdasarkan jenis error
            if "Host cancelled the game" in self.error_message:
                error_duration = 3000  # 3 detik khusus untuk host cancelled
                show_error = (current_time - self.error_timestamp < error_duration)
            else:
                # Untuk error lainnya (connection, invalid IP, dll)
                show_error = (current_time - self.error_timestamp < error_duration)
        
        status_rect = pygame.Rect(50, status_y, SCREEN_WIDTH - 100, 80)
        pygame.draw.rect(screen, (0, 0, 0, 180), status_rect, border_radius=10)
        
        # PERBAIKAN: Tentukan status_text berdasarkan jenis error
        if network_manager.connected:
            status_color = (0, 200, 0)  # Hijau jika connected
            status_text = "CONNECTED"
            detail_text = "Connected to host"
            border_color = (0, 200, 0)
        
        elif show_error and self.error_message:
            status_color = (255, 50, 50)  # Merah untuk error
            
            # PERBAIKAN: Tentukan status_text berdasarkan jenis error
            if "Host cancelled the game" in self.error_message:
                status_text = "HOST CANCELLED"
                detail_text = "Host cancelled the connection"
            elif "Please enter host IP address" in self.error_message:
                status_text = "IP REQUIRED"
                detail_text = "Please enter host IP address"
            elif "Invalid IP format" in self.error_message:
                status_text = "INVALID IP FORMAT"
                detail_text = "Enter a valid IP (e.g., 192.168.1.100)"
            elif "Host not responding" in self.error_message:
                status_text = "NO RESPONSE"
                detail_text = "Host is not responding"
            elif "Connection refused" in self.error_message:
                status_text = "CONNECTION REFUSED"
                detail_text = "Host refused connection (check IP/port)"
            elif "Connection failed" in self.error_message or "timed out" in self.error_message.lower():
                status_text = "CONNECTION FAILED"
                detail_text = "Failed to connect to host"
            else:
                # Fallback untuk error lainnya
                status_text = "CONNECTION ERROR"
                detail_text = self.error_message[:40] + "..." if len(self.error_message) > 40 else self.error_message
            
            border_color = (255, 50, 50)
        
        else:
            status_color = (255, 255, 0)  # Kuning untuk ready
            dot_count = (pygame.time.get_ticks() // 500) % 4
            dots = "." * dot_count
            status_text = f"READY TO CONNECT{dots}"
            detail_text = "Enter host IP and click CONNECT"
            border_color = (0, 120, 180)
        
        pygame.draw.rect(screen, border_color, status_rect, 2, border_radius=10)
        
        status_label = self.font.render(status_text, True, status_color)
        screen.blit(status_label, (SCREEN_WIDTH//2 - status_label.get_width()//2, status_y + 15))
        
        detail = self.small_font.render(detail_text, True, (200, 200, 200))
        screen.blit(detail, (SCREEN_WIDTH//2 - detail.get_width()//2, status_y + 50))
        
        # ===== HOST INFO PANEL =====
        host_info_y = status_y + 100
        host_info_rect = pygame.Rect(50, host_info_y, SCREEN_WIDTH - 100, 150)
        pygame.draw.rect(screen, (20, 20, 40, 180), host_info_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 0, 150), host_info_rect, 2, border_radius=10)

        # Title untuk host info
        host_info_title = self.font.render("HOST INFO", True, (255, 100, 255))
        screen.blit(host_info_title, (SCREEN_WIDTH//2 - host_info_title.get_width()//2, host_info_y + 10))
        
        # PERBAIKAN: Reset host_info jika host cancelled
        if show_error and self.error_message == "Host cancelled the game":
            # Force reset host info
            if game_instance:
                game_instance.remote_host_info = None
            
            # PERBAIKAN: Juga reset network_manager.host_info
            if hasattr(network_manager, 'reset_host_info'):
                network_manager.reset_host_info()
            
            # Gambar teks N/A
            diff_surface = self.small_font.render("Difficulty: N/A", True, (200, 200, 200))
            screen.blit(diff_surface, (host_info_rect.x + 30, host_info_y + 45))
            
            p1_label = self.small_font.render("Player 1 Controls (HOST):", True, (200, 200, 200))
            p1_scheme = self.small_font.render("N/A", True, self.COLOR_P1)
            screen.blit(p1_label, (host_info_rect.x + 250, host_info_y + 45))
            screen.blit(p1_scheme, (host_info_rect.x + 460, host_info_y + 45))
            
            p2_label = self.small_font.render("Player 2 Controls (YOU):", True, (200, 200, 200))
            p2_scheme = self.small_font.render("N/A", True, self.COLOR_P2)
            screen.blit(p2_label, (host_info_rect.x + 250, host_info_y + 70))
            screen.blit(p2_scheme, (host_info_rect.x + 460, host_info_y + 70))
        
        else:
            # Kode normal untuk menampilkan host info
            # PERBAIKAN: Prioritas pengambilan host_info untuk client
            host_info = None
            # PRIORITAS 1: Gunakan network_manager.host_info
            if hasattr(network_manager, 'host_info') and network_manager.host_info:
                host_info = network_manager.host_info
                print(f"📊 Using host_info from network_manager: {host_info.get('difficulty', 'N/A')}")
            # PRIORITAS 2: Gunakan game_instance.remote_host_info
            elif game_instance and hasattr(game_instance, 'remote_host_info') and game_instance.remote_host_info:
                host_info = game_instance.remote_host_info
                # Simpan juga ke network_manager untuk konsistensi
                if hasattr(network_manager, 'host_info'):
                    network_manager.host_info = host_info
                print(f"📊 Using host_info from game_instance: {host_info.get('difficulty', 'N/A')}")
            # PRIORITAS 3: Gunakan last_event
            elif hasattr(network_manager, 'last_event') and isinstance(network_manager.last_event, dict):
                if network_manager.last_event.get('type') == 'host_info':
                    host_info = network_manager.last_event.get('payload', {})
                    print(f"📊 Using host_info from last_event: {host_info.get('difficulty', 'N/A')}")
            
            # PERBAIKAN: Jika connected tapi host_info masih None, coba request
            if network_manager.connected and not host_info and game_instance:
                print("⚠️ Connected but no host_info, requesting...")
                try:
                    network_manager.send_event('client_connected', {'request': 'host_info'})
                except:
                    pass
            
            # Difficulty
            if host_info:
                diff_text = host_info.get('difficulty', 'N/A')
                diff_color = self.DIFFICULTY_COLORS.get(diff_text, (255, 255, 255))
                diff_display = diff_text.upper()
            else:
                diff_text = "N/A"
                diff_color = (200, 200, 200)
                diff_display = "N/A"
            
            diff_surface = self.small_font.render(f"Difficulty: {diff_display}", True, diff_color)
            screen.blit(diff_surface, (host_info_rect.x + 30, host_info_y + 45))
            
            # Controls detail
            if host_info:
                ctrls = host_info.get('controls', {})
                p1_ctrl = ctrls.get('p1', 'N/A')
                p2_ctrl = ctrls.get('p2', 'N/A')
            else:
                p1_ctrl = "N/A"
                p2_ctrl = "N/A"
            
            # Player 1 Controls
            p1_y = host_info_y + 45
            p1_label = self.small_font.render("Player 1 Controls (HOST):", True, (200, 200, 200))
            p1_scheme = self.small_font.render(p1_ctrl, True, self.COLOR_P1)
            screen.blit(p1_label, (host_info_rect.x + 250, p1_y))
            screen.blit(p1_scheme, (host_info_rect.x + 460, p1_y))
            
            # Player 2 Controls
            p2_y = p1_y + 25
            p2_label = self.small_font.render("Player 2 Controls (YOU):", True, (200, 200, 200))
            p2_scheme = self.small_font.render(p2_ctrl, True, self.COLOR_P2)
            screen.blit(p2_label, (host_info_rect.x + 250, p2_y))
            screen.blit(p2_scheme, (host_info_rect.x + 460, p2_y))
        
        # Connection info
        conn_y = host_info_y + 115
        conn_text = self.small_font.render("Both players must be in same ZeroTier network", True, (255, 255, 100))
        screen.blit(conn_text, (SCREEN_WIDTH//2 - conn_text.get_width()//2, conn_y))
        
        # --- Client waiting popup (small) ---
        if game_instance and getattr(game_instance, 'client_waiting_popup', False):
            # PERBAIKAN: Hanya tampilkan popup jika tidak ada error
            if not show_error:
                # dim background (like pause)
                overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                screen.blit(overlay, (0, 0))

                popup_w, popup_h = 420, 120
                popup_x = (800 - popup_w) // 2
                popup_y = (600 - popup_h) // 2
                pygame.draw.rect(screen, (20, 20, 30), (popup_x, popup_y, popup_w, popup_h), border_radius=8)
                pygame.draw.rect(screen, (120, 180, 220), (popup_x, popup_y, popup_w, popup_h), 2, border_radius=8)

                title = pygame.font.Font(None, 28).render("Connected - Waiting for Host", True, (255, 255, 255))
                screen.blit(title, (popup_x + 20, popup_y + 12))
                msg = pygame.font.Font(None, 20).render("Please wait until the host presses START. Do not exit.", True, (200, 200, 200))
                screen.blit(msg, (popup_x + 20, popup_y + 50))

                # Cancel button inside popup (draw but actual cancel handled by main)
                cancel_rect = pygame.Rect(popup_x + popup_w - 110, popup_y + popup_h - 38, 90, 28)
                pygame.draw.rect(screen, (160, 40, 40), cancel_rect, border_radius=6)
                cancel_text = pygame.font.Font(None, 20).render("CANCEL", True, (255, 255, 255))
                screen.blit(cancel_text, (cancel_rect.x + 14, cancel_rect.y + 4))
        
        # ===== UPDATE HOVER & CURSOR =====
        mouse_pos = pygame.mouse.get_pos()
        
        # PERBAIKAN: Jangan update hover jika popup aktif
        popup_active = False
        if game_instance and hasattr(game_instance, 'client_waiting_popup'):
            popup_active = game_instance.client_waiting_popup
        
        if not popup_active:
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
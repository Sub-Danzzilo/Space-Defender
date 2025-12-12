# ========== UI_RENDERER.PY ==========
# File untuk mengelola semua UI rendering (draw game screen)

import pygame

# ========== KONSTANTA ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# ========== WARNA ==========
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_CYAN = (200, 255, 255)
CYAN = (0, 255, 255)
DARK_CYAN = (0, 200, 200)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

class UIRenderer:
    """Mengelola rendering UI game"""
    
    def __init__(self, screen, fonts):
        self.screen = screen
        self.font = fonts['font']
        self.small_font = fonts['small_font']
        self.tiny_font = fonts['tiny_font']
    
    def draw_playing_singleplayer(self, player1, score_p1, enemies_killed_p1, 
                                difficulty_level, powerup_manager_p1):
        """Draw UI untuk singleplayer - HANYA UI, TANPA GAME OBJECTS"""
        # ===== SCORE =====
        score_text = self.font.render(f"Score: {score_p1}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # ===== HP =====
        health_color = self._get_health_color(player1)
        health_text = self.font.render(f"HP: {player1.health}", True, health_color)
        self.screen.blit(health_text, (10, 50))
        
        # ===== LEVEL =====
        level_text = self.font.render(f"Lv: {difficulty_level}", True, YELLOW)
        level_rect = level_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        self.screen.blit(level_text, level_rect)
        
        # ===== KILLED =====
        killed_text = self.small_font.render(f"Killed: {enemies_killed_p1}", True, CYAN)
        killed_rect = killed_text.get_rect(topright=(SCREEN_WIDTH - 10, 50))
        self.screen.blit(killed_text, killed_rect)
        
        # ===== POWERUP STATUS =====
        self._draw_powerup_status_singleplayer(powerup_manager_p1, SCREEN_WIDTH - 200, 80)
    
    def draw_playing_multiplayer(self, player1, player2, score_p1, score_p2, 
                                enemies_killed_p1, enemies_killed_p2, 
                                difficulty_level, powerup_manager_p1, powerup_manager_p2):
        """Draw UI untuk multiplayer - HANYA UI, TANPA GAME OBJECTS"""
        # ===== PLAYER 1 INFO (LEFT SIDE) =====
        score_text_p1 = self.font.render(f"P1: {score_p1}", True, WHITE)
        self.screen.blit(score_text_p1, (10, 10))
        
        health_color_p1 = self._get_health_color(player1)
        health_text_p1 = self.font.render(f"HP: {player1.health}", True, health_color_p1)
        self.screen.blit(health_text_p1, (10, 40))
        
        killed_text_p1 = self.small_font.render(f"K: {enemies_killed_p1}", True, CYAN)
        self.screen.blit(killed_text_p1, (10, 70))
        
        # ===== PLAYER 2 INFO (RIGHT SIDE) =====
        score_text_p2 = self.font.render(f"P2: {score_p2}", True, WHITE)
        score_rect_p2 = score_text_p2.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        self.screen.blit(score_text_p2, score_rect_p2)
        
        health_color_p2 = self._get_health_color(player2)
        health_text_p2 = self.font.render(f"HP: {player2.health}", True, health_color_p2)
        health_rect_p2 = health_text_p2.get_rect(topright=(SCREEN_WIDTH - 10, 40))
        self.screen.blit(health_text_p2, health_rect_p2)
        
        killed_text_p2 = self.small_font.render(f"K: {enemies_killed_p2}", True, CYAN)
        killed_rect_p2 = killed_text_p2.get_rect(topright=(SCREEN_WIDTH - 10, 70))
        self.screen.blit(killed_text_p2, killed_rect_p2)
        
        # ===== CENTER: LEVEL =====
        level_text = self.font.render(f"Lv {difficulty_level}", True, YELLOW)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        self.screen.blit(level_text, level_rect)
        
        # ===== POWERUP STATUS MULTIPLAYER =====
        self._draw_powerup_status_multiplayer(powerup_manager_p1, powerup_manager_p2)
    
    def _get_health_color(self, player):
        """Mendapatkan warna health berdasarkan status damage dan health"""
        # PERBAIKAN: Cek apakah atribut ada
        if hasattr(player, 'recently_damaged') and player.recently_damaged:
            # Berkedip antara merah dan putih setiap 5 frame
            if hasattr(player, 'damage_timer') and (player.damage_timer % 10) < 5:
                return RED
            else:
                return WHITE
        else:
            # Warna berdasarkan jumlah health
            if player.health <= 1:
                return RED  # Merah untuk health rendah
            elif player.health == 2:
                return YELLOW  # Kuning untuk health sedang
            else:
                return GREEN  # Hijau untuk health penuh
    
    def _draw_powerup_status_multiplayer(self, powerup_manager_p1, powerup_manager_p2):
        """Draw status powerup untuk multiplayer dengan helper method"""
        # Player 1 Powerups (kiri)
        self._draw_player_powerups(powerup_manager_p1, 10, 100, "P1 Powerups:", False)
        
        # Player 2 Powerups (kanan)
        self._draw_player_powerups(powerup_manager_p2, SCREEN_WIDTH - 200, 100, "P2 Powerups:", True)

    def _draw_player_powerups(self, powerup_manager, x, y, header, right_aligned=False):
        """Helper method untuk menggambar powerups seorang player"""
        if powerup_manager is None:
            return  # Jangan gambar apa-apa jika tidak ada powerup manager

        # Draw header
        header_text = self.tiny_font.render(header, True, MAGENTA)
        if right_aligned:
            header_rect = header_text.get_rect(topright=(SCREEN_WIDTH - 10, y))
            self.screen.blit(header_text, header_rect)
        else:
            self.screen.blit(header_text, (x, y))
        
        y += 15
        
        # Draw powerups menggunakan list untuk menghindari if berulang
        powerup_list = [
            ('rapid_fire', "Rapid", YELLOW),
            ('slow_enemies', "Slow", CYAN),
            ('multiple_bullets', "Multi", ORANGE),
            ('speed_boost', "Speed", PURPLE),
            ('invincibility', "Shield", GREEN),
            ('double_score', "2xScore", YELLOW)
        ]
        
        for i, (key, name, color) in enumerate(powerup_list):
            if powerup_manager.active_powerups[key]:
                remaining_time = powerup_manager.powerup_timers[key] // 60
                text = self.tiny_font.render(f"{name}: {remaining_time}s", True, color)
                
                if right_aligned:
                    text_rect = text.get_rect(topright=(SCREEN_WIDTH - 15, y + i * 15))
                    self.screen.blit(text, text_rect)
                else:
                    self.screen.blit(text, (x + 5, y + i * 15))

    def _draw_powerup_status_singleplayer(self, powerup_manager, x_pos, y_offset):
        """Draw status powerup untuk singleplayer (text only)"""
        active_count = 0
        
        if powerup_manager.active_powerups['rapid_fire']:
            remaining_time = powerup_manager.powerup_timers['rapid_fire'] // 60
            text = self.tiny_font.render(f"Rapid: {remaining_time}s", True, YELLOW)
            self.screen.blit(text, (x_pos, y_offset + (active_count * 15)))
            active_count += 1
        
        if powerup_manager.active_powerups['slow_enemies']:
            remaining_time = powerup_manager.powerup_timers['slow_enemies'] // 60
            text = self.tiny_font.render(f"Slow: {remaining_time}s", True, CYAN)
            self.screen.blit(text, (x_pos, y_offset + (active_count * 15)))
            active_count += 1
        
        if powerup_manager.active_powerups['multiple_bullets']:
            remaining_time = powerup_manager.powerup_timers['multiple_bullets'] // 60
            text = self.tiny_font.render(f"Multi: {remaining_time}s", True, ORANGE)
            self.screen.blit(text, (x_pos, y_offset + (active_count * 15)))
            active_count += 1
        
        if powerup_manager.active_powerups['speed_boost']:
            remaining_time = powerup_manager.powerup_timers['speed_boost'] // 60
            text = self.tiny_font.render(f"Speed: {remaining_time}s", True, PURPLE)
            self.screen.blit(text, (x_pos, y_offset + (active_count * 15)))
            active_count += 1
        
        if powerup_manager.active_powerups['invincibility']:
            remaining_time = powerup_manager.powerup_timers['invincibility'] // 60
            # Warna berubah jadi merah saat hampir habis
            color = RED if remaining_time <= 3 else GREEN
            text = self.tiny_font.render(f"Shield: {remaining_time}s", True, color)
            self.screen.blit(text, (x_pos, y_offset + (active_count * 15)))
            active_count += 1
        
        if powerup_manager.active_powerups['double_score']:
            remaining_time = powerup_manager.powerup_timers['double_score'] // 60
            text = self.tiny_font.render(f"2xScore: {remaining_time}s", True, YELLOW)
            self.screen.blit(text, (x_pos, y_offset + (active_count * 15)))

    def init_pause_icon(self, image_manager=None):
        """Initialize pause icon attributes"""
        self.pause_icon = None
        self.pause_icon_rect = None
        self.pause_icon_hover = False
        
        # Grab icon from image manager if available
        if image_manager:
            try:
                self.pause_icon = image_manager.images.get('pause')
            except Exception:
                self.pause_icon = None
        
        # Default placement
        default_w, default_h = (40, 40)
        if self.pause_icon:
            default_w = self.pause_icon.get_width()
            default_h = self.pause_icon.get_height()
        
        # Default position (akan diadjust di draw_pause_icon)
        self.pause_icon_rect = pygame.Rect(
            SCREEN_WIDTH - default_w - 10, 90, default_w, default_h
        )
        return self.pause_icon_rect

    def draw_pause_icon(self, screen, mouse_pos, is_multiplayer=False):
        """Draw pause icon with hover effect"""
        if not self.pause_icon_rect:
            return False
        
        # Adjust position based on game mode
        if self.pause_icon:
            w = self.pause_icon.get_width()
            h = self.pause_icon.get_height()
        else:
            w, h = (40, 40)
        
        x = SCREEN_WIDTH - w - 10
        y = 140 if is_multiplayer else 90

        if is_multiplayer:
            # Untuk multiplayer: TENGAH BAWAH - di bawah level (tengah horizontal)
            x = (SCREEN_WIDTH - w) // 2
            y = SCREEN_HEIGHT - 550
        
        # Update rect
        self.pause_icon_rect.x = x
        self.pause_icon_rect.y = y
        self.pause_icon_rect.w = w
        self.pause_icon_rect.h = h
        
        # Check hover
        self.pause_icon_hover = self.pause_icon_rect.collidepoint(mouse_pos)
        
        # Draw icon with hover effect
        if self.pause_icon:
            if self.pause_icon_hover:
                # Draw glow effect
                glow = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow, (255, 255, 255, 20), 
                    (glow.get_width()//2, glow.get_height()//2),
                    max(glow.get_width(), glow.get_height())//2
                )
                screen.blit(glow, (x - 4, y - 4))
            
            # Draw actual icon
            screen.blit(self.pause_icon, (x, y))
        else:
            # Fallback: draw simple pause symbol
            color = (200, 200, 200) if self.pause_icon_hover else (150, 150, 150)
            pygame.draw.rect(screen, (30, 30, 30), self.pause_icon_rect, border_radius=8)
            pygame.draw.rect(
                screen, color, 
                (x + 8, y + 8, 6, h - 16), 
                border_radius=2
            )
            pygame.draw.rect(
                screen, color, 
                (x + 16 + 6, y + 8, 6, h - 16), 
                border_radius=2
            )
        
        return self.pause_icon_hover

    def get_pause_icon_rect(self):
        """Get current pause icon rectangle for click detection"""
        return self.pause_icon_rect
# ========== GAME_OVER_PAGE.PY ==========
# File khusus untuk halaman game over
# REVISED: Untuk singleplayer saja (multiplayer punya custom game over di main.py)

import pygame
from button import Button

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
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)

# ========== CLASS GAME OVER PAGE ==========
class GameOverPage:
    """Mengelola halaman game over"""
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)
    
    def draw_game_over(self, screen, buttons, score, enemies_killed, difficulty_level, difficulty_mode):
        """Menggambar layar game over dengan layout yang bagus (SINGLEPLAYER ONLY)"""
        # ===== BACKGROUND DENGAN GRADIENT MERAH =====
        for i in range(SCREEN_HEIGHT):
            color_intensity = int(30 + (i / SCREEN_HEIGHT) * 50)
            pygame.draw.line(screen, (color_intensity, 0, 0), (0, i), (SCREEN_WIDTH, i))
        
        # ===== OVERLAY SEMI-TRANSPARENT =====
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # ===== GAME OVER TEXT (BESAR) =====
        game_over_text = self.large_font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(game_over_text, game_over_rect)
        
        # ===== SEPARATOR =====
        pygame.draw.line(screen, RED, (100, 140), (SCREEN_WIDTH - 100, 140), 3)
        
        # ===== STATS SECTION DENGAN WARNA BERBEDA =====
        stats_y = 120
        
        # Score
        stats_y += 40
        score_label = self.font.render("Final Score", True, YELLOW)
        score_label_rect = score_label.get_rect(topleft=(80, stats_y))
        screen.blit(score_label, score_label_rect)
        
        score_value = self.font.render(str(score), True, YELLOW)  # KUNING
        score_value_rect = score_value.get_rect(topright=(SCREEN_WIDTH - 80, stats_y))
        screen.blit(score_value, score_value_rect)
        
        # Enemies Killed
        stats_y += 40
        killed_label = self.font.render("Enemies Killed", True, GREEN)
        killed_label_rect = killed_label.get_rect(topleft=(80, stats_y))
        screen.blit(killed_label, killed_label_rect)
        
        killed_value = self.font.render(str(enemies_killed), True, GREEN)  # HIJAU
        killed_value_rect = killed_value.get_rect(topright=(SCREEN_WIDTH - 80, stats_y))
        screen.blit(killed_value, killed_value_rect)
        
        # Max Level
        stats_y += 40
        level_label = self.font.render("Max Level Reached", True, ORANGE)
        level_label_rect = level_label.get_rect(topleft=(80, stats_y))
        screen.blit(level_label, level_label_rect)
        
        level_value = self.font.render(str(difficulty_level), True, ORANGE)  # ORANGE
        level_value_rect = level_value.get_rect(topright=(SCREEN_WIDTH - 80, stats_y))
        screen.blit(level_value, level_value_rect)

        # difficulty mode
        stats_y += 40
        difficulty_label = self.font.render("Difficulty Mode", True, PURPLE)
        difficulty_label_rect = difficulty_label.get_rect(topleft=(80, stats_y))
        screen.blit(difficulty_label, difficulty_label_rect)
        
        # Dapatkan difficulty mode dari game_manager (asumsi sudah ada akses)
        difficulty_mode = "Normal"  # Default, nanti akan diganti dengan nilai sebenarnya
        difficulty_value = self.font.render(f"{difficulty_mode}", True, PURPLE)  # UNGU
        difficulty_value_rect = difficulty_value.get_rect(topright=(SCREEN_WIDTH - 80, stats_y))
        screen.blit(difficulty_value, difficulty_value_rect)
        
        # ===== PERFORMANCE RATING BERDASARKAN SCORE =====
        stats_y += 40
        if score >= 1000:
            rating = "LEGENDARY!"
            rating_color = GOLD
        elif score >= 500:
            rating = "EXCELLENT!"
            rating_color = PURPLE
        elif score >= 200:
            rating = "GOOD JOB!"
            rating_color = BLUE
        elif score >= 100:
            rating = "NOT BAD!"
            rating_color = GREEN
        else:
            rating = "KEEP TRYING!"
            rating_color = YELLOW
        
        rating_label = self.font.render("Performance", True, CYAN)
        rating_label_rect = rating_label.get_rect(topleft=(80, stats_y))
        screen.blit(rating_label, rating_label_rect)
        
        rating_value = self.font.render(rating, True, rating_color)  # WARNA BERDASARKAN PERFORMANCE
        rating_value_rect = rating_value.get_rect(topright=(SCREEN_WIDTH - 80, stats_y))
        screen.blit(rating_value, rating_value_rect)
        
        # ===== SEPARATOR =====
        pygame.draw.line(screen, RED, (100, stats_y + 45), (SCREEN_WIDTH - 100, stats_y + 45), 3)
        
        # ===== FOOTER =====
        footer = self.tiny_font.render("Press ESC to go to Main Menu", True, YELLOW)
        footer_rect = footer.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        screen.blit(footer, footer_rect)
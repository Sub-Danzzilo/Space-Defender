# ========== DIVIDER_MANAGER.PY ==========
# File untuk mengelola batas tengah (divider) antara kedua player

import pygame

class DividerManager:
    """Mengelola batas tengah antara kedua player"""
    
    def __init__(self, screen_width=800, screen_height=600):
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.divider_x = screen_width // 2
        self.divider_width = 4
        self.divider_color = (128, 128, 128)   # Abu-abu
        self.margin = 10  # Margin dari divider
    
    def check_player_bounds(self, player1, player2):
        """Memastikan player tidak melewati batas tengah"""
        # Batas untuk Player 1 (kiri)
        if player1.rect.right > self.divider_x - self.margin:
            player1.rect.right = self.divider_x - self.margin
        
        # Batas untuk Player 2 (kanan)  
        if player2.rect.left < self.divider_x + self.margin:
            player2.rect.left = self.divider_x + self.margin
    
    def draw_divider(self, surface):
        """Menggambar garis divider di tengah layar"""
        # Garis solid di tengah
        pygame.draw.line(
            surface, 
            self.divider_color,
            (self.divider_x, 0),
            (self.divider_x, self.SCREEN_HEIGHT),
            self.divider_width
        )
    
    def update(self, player1, player2):
        """Update batas player setiap frame"""
        self.check_player_bounds(player1, player2)
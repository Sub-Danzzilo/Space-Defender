# ========== BUTTON.PY ==========
# File untuk class Button

import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, font_size=24, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        
        # JIKA hover_color diberikan, PAKAI itu. Jika tidak, hitung otomatis
        if hover_color is not None:
            self.hover_color = hover_color
        else:
            # Hitung warna hover yang lebih terang
            self.hover_color = tuple(min(255, c + 50) for c in color)
    
    def draw(self, screen):
        # Pilih warna berdasarkan hover
        current_color = self.hover_color if self.is_hovered else self.color
        border_color = (255, 255, 200) if self.is_hovered else (255, 255, 255)
        border_width = 3 if self.is_hovered else 2
        
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=10)
        
        # Gambar teks
        lines = self.text.split('\n')
        total_height = 0
        text_surfaces = []
        
        for line in lines:
            text_surface = self.font.render(line, True, self.text_color)
            text_surfaces.append(text_surface)
            total_height += text_surface.get_height()
        
        spacing = 5 if len(lines) > 1 else 0
        total_height += spacing * (len(lines) - 1)
        
        start_y = self.rect.centery - (total_height // 2)
        current_y = start_y
        
        for text_surface in text_surfaces:
            text_rect = text_surface.get_rect(center=(self.rect.centerx, current_y + text_surface.get_height() // 2))
            screen.blit(text_surface, text_rect)
            current_y += text_surface.get_height() + spacing
    
    def update_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
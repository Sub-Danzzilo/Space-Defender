# ========== RADIO_BUTTON.PY ==========
# File untuk komponen radio button UI

import pygame

class RadioButton:
    """Kelas untuk radio button UI"""
    
    def __init__(self, x, y, size, text, font, group_name, is_selected=False, 
                 color=(200, 200, 200), selected_color=(0, 200, 255), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, size, size)
        self.text = text
        self.font = font
        self.group_name = group_name
        self.is_selected = is_selected
        self.color = color
        self.selected_color = selected_color
        self.text_color = text_color
        self.hover = False
        
    def draw(self, surface):
        """Menggambar radio button"""
        # Warna berdasarkan state
        current_color = self.selected_color if self.is_selected else self.color
        if self.hover and not self.is_selected:
            current_color = tuple(min(c + 30, 255) for c in self.color)
        
        # Gambar lingkaran luar
        pygame.draw.circle(surface, current_color, self.rect.center, self.rect.width // 2)
        pygame.draw.circle(surface, (255, 255, 255), self.rect.center, self.rect.width // 2, 2)
        
        # Gambar titik di tengah jika selected
        if self.is_selected:
            pygame.draw.circle(surface, (255, 255, 255), self.rect.center, self.rect.width // 4)
        
        # Gambar text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)
        
        return text_rect.right  # Return right position untuk alignment
    
    def is_clicked(self, mouse_pos):
        """Cek apakah radio button diklik"""
        return self.rect.collidepoint(mouse_pos)
    
    def update_hover(self, mouse_pos):
        """Update status hover"""
        self.hover = self.rect.collidepoint(mouse_pos)
# ========== SLIDER.PY ==========
# File untuk komponen slider UI

import pygame

class Slider:
    """Kelas untuk slider volume dengan bulatan handle"""
    
    def __init__(self, x, y, width, height, min_val=0, max_val=100, initial_val=50, 
                 track_color=(100, 100, 100), handle_color=(0, 200, 255),
                 text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.track_color = track_color
        self.handle_color = handle_color
        self.text_color = text_color
        # PERBAIKAN: Perkecil handle_radius dari height * 1.5 menjadi height * 1.0
        self.handle_radius = height * 1.0
        self.dragging = False
        
        # Hitung posisi handle berdasarkan value
        self.handle_x = self.value_to_pixel()
    
    def value_to_pixel(self):
        """Konversi value ke posisi pixel pada slider"""
        value_range = self.max_val - self.min_val
        pixel_range = self.rect.width - (2 * self.handle_radius)
        return self.rect.x + self.handle_radius + ((self.value - self.min_val) / value_range) * pixel_range
    
    def pixel_to_value(self, x):
        """Konversi posisi pixel ke value"""
        value_range = self.max_val - self.min_val
        pixel_range = self.rect.width - (2 * self.handle_radius)
        
        # Clamp x dalam bounds slider
        min_x = self.rect.x + self.handle_radius
        max_x = self.rect.x + self.rect.width - self.handle_radius
        clamped_x = max(min_x, min(x, max_x))
        
        return self.min_val + ((clamped_x - min_x) / pixel_range) * value_range
    
    def handle_event(self, event, mouse_pos):
        """Handle events untuk slider - VERSI DIPERBAIKI"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Cek jika klik di handle
            handle_rect = pygame.Rect(
                self.handle_x - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
            
            # Cek jika klik di track area
            track_rect = pygame.Rect(
                self.rect.x - 10,
                self.rect.y - 15,
                self.rect.width + 20,
                self.rect.height + 30
            )
            
            if handle_rect.collidepoint(mouse_pos):
                # Klik di handle - hanya aktifkan drag, jangan ubah nilai
                self.dragging = True
                return True
            elif track_rect.collidepoint(mouse_pos):
                # Klik di track - pindahkan handle ke posisi klik DAN ubah nilai
                self.dragging = True
                new_value = self.pixel_to_value(mouse_pos[0])
                
                # PERBAIKAN: Hanya ubah nilai jika benar-benar berbeda
                if new_value != self.value:
                    self.value = new_value
                    self.handle_x = self.value_to_pixel()
                    return True
                else:
                    # Jika nilai sama, tetap return True untuk menandai drag aktif
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_dragging = self.dragging
            self.dragging = False
            return was_dragging
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_value = self.pixel_to_value(mouse_pos[0])
            # Update value selama drag
            if new_value != self.value:
                self.value = new_value
                self.handle_x = self.value_to_pixel()
                return True
                
        return False
    
    def draw(self, surface, font, label):
        """Gambar slider dengan label dan value"""
        # Gambar label
        label_text = font.render(label, True, self.text_color)
        surface.blit(label_text, (self.rect.x, self.rect.y - 30))
        
        # Gambar track
        pygame.draw.rect(surface, self.track_color, self.rect, border_radius=3)  # PERBAIKAN: border_radius lebih kecil
        
        # Gambar fill (progress)
        fill_width = (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        fill_color = tuple(min(c + 50, 255) for c in self.track_color)  # Warna lebih terang
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=3)  # PERBAIKAN: border_radius lebih kecil
        
        # Gambar handle (bulatan) - PERBAIKAN: Handle lebih kecil
        pygame.draw.circle(surface, self.handle_color, (int(self.handle_x), self.rect.centery), self.handle_radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.handle_x), self.rect.centery), self.handle_radius, 1)  # PERBAIKAN: Border lebih tipis
        
        # Gambar value text
        value_text = font.render(f"{int(self.value)}%", True, self.text_color)
        value_rect = value_text.get_rect(midleft=(self.rect.right + 20, self.rect.centery))
        surface.blit(value_text, value_rect)
    
    def get_value(self):
        """Dapatkan nilai slider"""
        return int(self.value)
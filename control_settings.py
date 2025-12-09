# ========== CONTROL_SETTINGS.PY ==========
# File untuk mengelola pengaturan kontrol pemain

import pygame

# ========== CONSTANTS ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# ========== WARNA ==========
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_BLUE = (10, 10, 40)

class ControlSettings:
    """Mengelola pengaturan kontrol pemain"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Default control scheme
        self.control_scheme = "default"  # "default" atau "swapped"
        
        # Control mappings
        self.control_mappings = {
            "default": {
                "p1": {"name": "WASD", "keys": ["W", "A", "S", "D"], "color": GREEN},
                "p2": {"name": "Arrow Keys", "keys": ["↑", "↓", "←", "→"], "color": CYAN}
            },
            "swapped": {
                "p1": {"name": "Arrow Keys", "keys": ["↑", "↓", "←", "→"], "color": CYAN},
                "p2": {"name": "WASD", "keys": ["W", "A", "S", "D"], "color": GREEN}
            }
        }
    
    def toggle_controls(self):
        """Toggle antara default dan swapped controls"""
        self.control_scheme = "swapped" if self.control_scheme == "default" else "default"
    
    def get_player_controls(self, player_id):
        """Dapatkan kontrol untuk player tertentu"""
        if player_id == 1:
            return self.control_mappings[self.control_scheme]["p1"]
        else:
            return self.control_mappings[self.control_scheme]["p2"]
    
    def draw_control_selector(self, screen, x, y, width, height, is_hovered=False):
        """Menggambar selector kontrol yang interaktif - FIXED: Better visual feedback"""
        # Background kotak dengan efek hover
        bg_color = (40, 40, 80) if not is_hovered else (60, 60, 100)
        border_color = CYAN if not is_hovered else YELLOW
        border_width = 3 if not is_hovered else 4
        
        # Draw background
        pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=10)
        pygame.draw.rect(screen, border_color, (x, y, width, height), border_width, border_radius=10)
        
        # Title
        title = self.font.render("CONTROLS", True, YELLOW)
        screen.blit(title, (x + width//2 - title.get_width()//2, y + 10))
        
        # Player 1 Controls
        p1_controls = self.get_player_controls(1)
        p1_text = self.small_font.render(f"P1: {p1_controls['name']}", True, p1_controls['color'])
        screen.blit(p1_text, (x + 20, y + 40))
        
        # Player 2 Controls (hanya untuk multiplayer)
        p2_controls = self.get_player_controls(2)
        p2_text = self.small_font.render(f"P2: {p2_controls['name']}", True, p2_controls['color'])
        screen.blit(p2_text, (x + 20, y + 70))
        
        # Switch Arrow dengan efek hover
        arrow_x = x + width - 40
        arrow_y = y + height//2 - 15
        
        # PERBAIKAN: Buat area arrow lebih jelas
        arrow_color = YELLOW if is_hovered else WHITE
        
        # Draw up arrow
        pygame.draw.polygon(screen, arrow_color, [
            (arrow_x, arrow_y),
            (arrow_x - 12, arrow_y + 12),
            (arrow_x + 12, arrow_y + 12)
        ])
        
        # Draw down arrow
        pygame.draw.polygon(screen, arrow_color, [
            (arrow_x, arrow_y + 30),
            (arrow_x - 12, arrow_y + 18),
            (arrow_x + 12, arrow_y + 18)
        ])
        
        # Instructions - PERBAIKAN: Tambahkan instruksi klik
        if is_hovered:
            instruct_text = self.small_font.render("Click anywhere to switch controls", True, YELLOW)
        else:
            instruct_text = self.small_font.render("Press UP/DOWN or click to switch", True, CYAN)
        screen.blit(instruct_text, (x + width//2 - instruct_text.get_width()//2, y + height - 25))
    
    def handle_keypress(self, key):
        """Handle keypress untuk toggle controls"""
        if key == pygame.K_UP or key == pygame.K_DOWN:
            self.toggle_controls()
            return True
        return False
    
    def handle_click(self, mouse_pos, rect):
        """Handle mouse click pada control selector"""
        # Area panah (kanan control selector)
        arrow_area = pygame.Rect(
            rect.right - 50,  # 50 pixel dari kanan
            rect.top,
            50,
            rect.height
        )
        
        if arrow_area.collidepoint(mouse_pos):
            self.toggle_controls()
            return True
        return False

    def get_control_scheme_for_player(self, player_id):
        """Dapatkan skema kontrol untuk player tertentu"""
        if self.control_scheme == "default":
            return "wasd" if player_id == 1 else "arrows"
        else:  # swapped
            return "arrows" if player_id == 1 else "wasd"

import pygame
import math
import os
from utils import resource_path

# ========== CONSTANTS ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class IntroPage:
    """Mengelola halaman intro dengan efek fade in/out dan grow"""
    
    def __init__(self, image_manager, sound_manager):
        self.image_manager = image_manager
        self.sound_manager = sound_manager
        
        # ===== PASTIKAN MUSIK DIMATIKAN SAAT INTRO =====
        self.sound_manager.stop_music()
        pygame.mixer.music.stop()  # Force stop pygame music
        pygame.mixer.music.unload()  # Unload dari memory
        
        # PERBAIKAN TAMBAHAN: Pastikan tidak ada musik yang tersisa
        pygame.mixer.music.set_volume(0.0)  # Set volume ke 0 sementara
        
        # State intro
        self.current_logo = 0  # 0: Space Defender, 1: Python
        self.phase = "fade_in"  # fade_in, display, fade_out
        self.alpha = 0
        self.scale = 0.8  # ⭐ UKURAN AWAL LOGO - ubah nilai ini untuk mengubah ukuran minimum
        self.timer = 0
        self.duration = 180  # 3 detik per logo (60 FPS)
        
        # Load atau buat logo
        self.load_logos()
        
        # Flag untuk menandakan intro selesai
        self.finished = False
    
    def load_logos(self):
        """Load atau buat logo untuk intro"""
        # Logo Space Defender
        if not self._load_logo('logo', 'assets/images/logo.png'):
            self.image_manager.images['logo'] = self.create_space_defender_logo()
        
        # Logo Python
        if not self._load_logo('logo_python', 'assets/images/logo_python.png'):
            self.image_manager.images['logo_python'] = self.create_python_logo()
    
    def _load_logo(self, logo_name, file_path):
        """Helper untuk load logo - FIXED untuk .exe"""
        try:
            abs_path = resource_path(file_path)
            
            # Debug info
            print(f"🖼️ Trying to load logo: {file_path}")
            print(f"📁 Absolute path: {abs_path}")
            print(f"📁 File exists: {os.path.exists(abs_path)}")
            
            if os.path.exists(abs_path):
                loaded_image = pygame.image.load(abs_path).convert_alpha()
                self.image_manager.images[logo_name] = loaded_image
                print(f"✅ Loaded logo: {file_path}")
                return True
            else:
                print(f"❌ Logo file missing: {file_path}")
                return False
        except Exception as e:
            print(f"❌ Error loading logo {file_path}: {e}")
            return False
    
    def create_space_defender_logo(self):
        """Buat logo Space Defender secara procedural"""
        surface = pygame.Surface((300, 300), pygame.SRCALPHA)
        
        # Background gradient
        for i in range(200):
            alpha = int(100 + (i / 200) * 100)
            color = (0, 50, 100, alpha)
            pygame.draw.line(surface, color, (0, i), (400, i))
        
        # Text "SPACE DEFENDER"
        title_font = pygame.font.Font(None, 80)
        title = title_font.render("SPACE DEFENDER", True, (0, 255, 255))
        title_rect = title.get_rect(center=(200, 80))
        
        # Efek outline untuk text
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    outline = title_font.render("SPACE DEFENDER", True, (0, 100, 200))
                    surface.blit(outline, (title_rect.x + dx, title_rect.y + dy))
        
        surface.blit(title, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 36)
        subtitle = subtitle_font.render("Galactic Arcade Shooter", True, (255, 255, 0))
        subtitle_rect = subtitle.get_rect(center=(200, 140))
        surface.blit(subtitle, subtitle_rect)
        
        # Efek bintang di background logo
        for _ in range(20):
            x = pygame.time.get_ticks() % 400
            y = pygame.time.get_ticks() % 200
            size = 2
            brightness = 200
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), size)
        
        return surface
    
    def create_python_logo(self):
        """Buat logo Python secara procedural"""
        surface = pygame.Surface((300, 300), pygame.SRCALPHA)
        
        # Background circle (biru python)
        pygame.draw.circle(surface, (50, 100, 200, 200), (150, 150), 120)
        pygame.draw.circle(surface, (30, 70, 180, 240), (150, 150), 120, 8)
        
        # Text "PYTHON"
        python_font = pygame.font.Font(None, 70)
        python_text = python_font.render("PYTHON", True, (255, 200, 0))
        python_rect = python_text.get_rect(center=(150, 150))
        
        # Efek snake/python (simplified)
        pygame.draw.ellipse(surface, (0, 200, 100), (130, 80, 40, 60))
        pygame.draw.ellipse(surface, (0, 200, 100), (90, 120, 60, 40))
        pygame.draw.ellipse(surface, (0, 200, 100), (170, 160, 40, 60))
        
        surface.blit(python_text, python_rect)
        
        return surface
    
    def update(self):
        """Update state intro"""
        if self.finished:
            return True
        
        self.timer += 1
        progress = self.timer / self.duration
        
        if self.phase == "fade_in":
            self.alpha = min(255, int(progress * 255 * 3))  # 1/3 durasi untuk fade in
            self.scale = 0.8 + (progress * 0.4)  # ⭐ GROW EFFECT - ubah 0.8 (min) dan 0.4 (range) untuk mengubah animasi zoom in
            
            if progress >= 0.33:
                self.phase = "display"
                self.timer = int(self.duration * 0.33)
        
        elif self.phase == "display":
            # Tetap di alpha 255 dan scale maksimal
            self.alpha = 255
            self.scale = 1.2  # ⭐ UKURAN MAKSIMAL LOGO - ubah nilai ini untuk mengubah ukuran maksimum
            
            if progress >= 0.66:
                self.phase = "fade_out"
                self.timer = int(self.duration * 0.66)
        
        elif self.phase == "fade_out":
            self.alpha = max(0, int((1 - (progress - 0.66) * 3) * 255))  # 1/3 durasi untuk fade out
            self.scale = 1.2 - ((progress - 0.66) * 0.4)  # ⭐ SHRINK EFFECT - ubah 1.2 (max) dan 0.4 (range) untuk mengubah animasi zoom out
            
            if progress >= 1.0:
                # Pindah ke logo berikutnya atau selesai
                self.current_logo += 1
                if self.current_logo >= 2:
                    self.finished = True
                    return True
                else:
                    # Reset untuk logo berikutnya
                    self.phase = "fade_in"
                    self.alpha = 0
                    self.scale = 0.8  # ⭐ RESET KE UKURAN AWAL - ubah nilai ini
                    self.timer = 0
        
        return False
    
    def draw(self, screen):
        """Gambar intro page"""
        screen.fill(BLACK)
        
        if self.current_logo == 0:
            logo = self.image_manager.images['logo']
        else:
            logo = self.image_manager.images['logo_python']
        
        # Apply alpha dan scale
        scaled_logo = pygame.transform.scale(
            logo, 
            (int(logo.get_width() * self.scale), int(logo.get_height() * self.scale))
        )
        
        # Apply alpha
        if self.alpha < 255:
            alpha_surface = pygame.Surface(scaled_logo.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, self.alpha))
            scaled_logo.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Center logo
        logo_rect = scaled_logo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(scaled_logo, logo_rect)
        
        # Progress indicator (opsional)
        progress_bar_width = 400
        progress_bar_height = 4
        progress_bar_x = (SCREEN_WIDTH - progress_bar_width) // 2
        progress_bar_y = SCREEN_HEIGHT - 50
        
        # Background progress bar
        pygame.draw.rect(screen, (50, 50, 50), 
                        (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
        
        # Current progress
        current_progress = (self.current_logo + (self.timer / self.duration)) / 2
        progress_width = int(progress_bar_width * current_progress)
        pygame.draw.rect(screen, (0, 200, 255), 
                        (progress_bar_x, progress_bar_y, progress_width, progress_bar_height))
    
    def skip_intro(self):
        """Skip intro dan langsung ke main menu"""
        # PERBAIKAN: Restore volume music sebelum keluar
        pygame.mixer.music.set_volume(self.sound_manager.music_volume)
        self.finished = True
        return True
    
    def is_finished(self):
        """Cek apakah intro sudah selesai"""
        return self.finished
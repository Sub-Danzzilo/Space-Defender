import pygame
# HAPUS: from button import Button (tidak digunakan)

# ========== CONSTANTS ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# ========== WARNA ==========
BLACK = (0, 0, 0, 180)  # Semi-transparent
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class PauseManager:
    """Mengelola sistem pause game dengan countdown resume"""
    
    def __init__(self, sound_manager=None):
        self.font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 36)
        self.countdown_font = pygame.font.Font(None, 120)
        self.is_paused = False
        self.countdown_active = False
        self.countdown_number = 3
        self.countdown_timer = 0
        self.countdown_duration = 60  # 60 frames = 1 detik (asumsi 60 FPS)
        self.sound_manager = sound_manager
    
    def draw_pause_screen(self, screen, is_multiplayer=False):  # Biarkan 2 parameter
        """Menggambar layar pause dengan opsi resume dan quit"""
        # Buat overlay semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Judul PAUSE
        title = self.font.render("GAME PAUSED", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Mode info
        mode_text = self.small_font.render(
            f"Mode: {'Multiplayer' if is_multiplayer else 'Singleplayer'}", 
            True, CYAN
        )
        mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(mode_text, mode_rect)
        
        # Instructions
        instructions = [
            "Press ESC to resume with countdown",
            "Use buttons below for other options"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 270 + i * 30))
            screen.blit(text, text_rect)
    
    def draw_countdown(self, screen):
        """Menggambar countdown di tengah layar"""
        # Buat overlay semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Text "RESUMING IN"
        resuming_text = self.small_font.render("RESUMING IN", True, CYAN)
        resuming_rect = resuming_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(resuming_text, resuming_rect)
        
        # Gambar angka countdown
        count_text = self.countdown_font.render(str(self.countdown_number), True, YELLOW)
        count_rect = count_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(count_text, count_rect)
    
    def update_countdown(self):
        """Update countdown dan return True jika countdown selesai"""
        self.countdown_timer += 1
        if self.countdown_timer >= self.countdown_duration:
            self.countdown_timer = 0
            self.countdown_number -= 1
            
            # PERBAIKAN: Mainkan sound countdown untuk angka 3, 2, dan 1
            if self.sound_manager:
                # Mainkan sound saat countdown_number = 3, 2, 1
                if self.countdown_number >= 1:  # 3, 2, 1, 0 (0 tidak berbunyi)
                    self.sound_manager.play_sound('shoot', cooldown=0)
            
            if self.countdown_number <= 0:
                # Countdown selesai, RESUME GAME
                self.countdown_active = False
                self.countdown_number = 3
                self.is_paused = False
                
                # PERBAIKAN: Lanjutkan musik game dari posisi terakhir
                if self.sound_manager:
                    self.sound_manager.unpause_music()  # GANTI: play_game_music() -> unpause_music()
                return True
        return False
    
    def toggle_pause(self):
        """Toggle status pause - SIMPAN POSISI MUSIK"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            print("⏸️ Game paused...")
            self.countdown_active = False
            self.countdown_number = 3
            self.countdown_timer = 0
            
            # PAUSE musik game dan simpan posisi
            if self.sound_manager:
                self.sound_manager.pause_music()
                self.sound_manager.play_pause_music()
        else:
            print("▶️ Game unpaused...")
            # Hentikan pause music dan resume game music
            if self.sound_manager:
                self.sound_manager.stop_pause_music()
                self.sound_manager.unpause_music()  # Ini akan melanjutkan dari posisi terakhir
        return self.is_paused

    def start_countdown(self):
        """Memulai countdown resume - PASTIKAN PAUSE MUSIC BERHENTI"""
        print("▶️ Starting countdown, stopping pause music...")
        
        # HENTIKAN pause music SEBELUM countdown
        if self.sound_manager:
            self.sound_manager.stop_pause_music()
        
        # Baru mulai countdown
        self.countdown_active = True
        self.countdown_number = 3
        self.countdown_timer = 0

        # TAMBAH: Mainkan sound untuk angka 3 saat countdown dimulai
        if self.sound_manager:
            self.sound_manager.play_sound('shoot', cooldown=0)
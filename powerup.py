# ========== POWERUP.PY ==========
# File untuk class PowerUp dengan berbagai tipe powerup
# Beginner Friendly: Health Regen, Speed Boost, Invincibility, Double Score

import pygame

class PowerUp(pygame.sprite.Sprite):
    """Kelas utama untuk powerup"""
    def __init__(self, x, y, powerup_type, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.powerup_type = powerup_type  # Tipe powerup
        self.speed = 1  # Kecepatan jatuh powerup
    
    def update(self):
        """Update posisi powerup (jatuh ke bawah)"""
        self.rect.y += self.speed
        # Hapus powerup jika sudah keluar layar
        if self.rect.y > 600:
            self.kill()
    
    def draw(self, surface):
        """Menggambar powerup dengan efek visual"""
        surface.blit(self.image, self.rect)
        # Gambar lingkaran cahaya di sekitar powerup
        pygame.draw.circle(surface, (255, 255, 0), self.rect.center, 20, 2)


# ========== POWERUP MANAGER ==========
# Modul untuk mengelola semua efek powerup

class PowerUpManager:
    """Mengelola semua powerup yang aktif dan durasi mereka"""
    def __init__(self, player):
        self.player = player
        
        # ===== DAFTAR POWERUP AKTIF =====
        # Format: { 'nama_powerup': True/False }
        self.active_powerups = {
            'rapid_fire': False,          # Tembak 2x lebih cepat
            'slow_enemies': False,        # Musuh 50% lebih lambat
            'multiple_bullets': False,    # 3 peluru sekaligus
            'health_regen': False,        # Nyawa +1
            'speed_boost': False,         # Bergerak 2x lebih cepat
            'invincibility': False,       # Kebal musuh
            'double_score': False         # Score 2x lipat
        }
        
        # ===== TIMER UNTUK SETIAP POWERUP =====
        # Format: { 'nama_powerup': durasi_sisa_frame }
        self.powerup_timers = {
            'rapid_fire': 0,
            'slow_enemies': 0,
            'multiple_bullets': 0,
            'health_regen': 0,
            'speed_boost': 0,
            'invincibility': 0,
            'double_score': 0
        }
        
        # ===== DURASI POWERUP (dalam frame) =====
        self.powerup_duration = 300  # 5 detik (60 FPS)
    
    def update(self):
        """Update timer semua powerup - FIXED invincibility"""
        for powerup_name in self.powerup_timers:
            # Kurangi timer
            if self.powerup_timers[powerup_name] > 0:
                self.powerup_timers[powerup_name] -= 1
            else:
                # Powerup selesai, nonaktifkan
                if self.active_powerups[powerup_name]:
                    self.active_powerups[powerup_name] = False
                    # PERBAIKAN KRITIS: Pastikan invincibility dimatikan
                    if powerup_name == 'invincibility':
                        self.player.is_invincible = False
                        # MATIKAN SHIELD VISUAL
                        self.player.deactivate_shield()
        
        # Apply speed boost effect
        if self.active_powerups['speed_boost']:
            self.player.speed = 8
        else:
            self.player.speed = 4
    
    def activate_powerup(self, powerup_type):
        """Aktivasi powerup - FIXED invincibility"""
        self.active_powerups[powerup_type] = True
        self.powerup_timers[powerup_type] = self.powerup_duration
        
        # Powerup instan (langsung efek)
        if powerup_type == 'health_regen':
            if self.player.health < 3:
                self.player.health += 1
            self.active_powerups['health_regen'] = False
        
        # PERBAIKAN: Invincibility - pastikan diaktifkan dengan benar
        elif powerup_type == 'invincibility':
            self.player.is_invincible = True
            self.player.activate_shield(self.powerup_duration)  # AKTIFKAN SHIELD VISUAL
    
    def deactivate_powerup(self, powerup_type):
        """Nonaktifkan powerup tertentu"""
        self.active_powerups[powerup_type] = False
        
        # ===== CLEANUP EFFECT =====
        if powerup_type == 'invincibility':
            self.player.is_invincible = False
    
    def get_fire_rate(self):
        """Dapatkan fire rate berdasarkan powerup aktif"""
        # ===== NORMAL FIRE RATE =====
        fire_rate = 5  # Tembak setiap 5 frame
        
        # ===== RAPID FIRE: 2x lebih cepat =====
        if self.active_powerups['rapid_fire']:
            fire_rate = 2  # Tembak setiap 2 frame (2.5x lebih cepat)
        
        return fire_rate
    
    def get_bullet_count(self):
        """Dapatkan jumlah peluru berdasarkan powerup aktif"""
        # ===== DEFAULT: 1 PELURU =====
        num_bullets = 1
        
        # ===== MULTIPLE BULLETS: 3 PELURU =====
        if self.active_powerups['multiple_bullets']:
            num_bullets = 3
        
        return num_bullets
    
    def get_score_multiplier(self):
        """Dapatkan multiplier score berdasarkan powerup aktif"""
        # ===== DEFAULT: 1x =====
        multiplier = 1
        
        # ===== DOUBLE SCORE: 2x =====
        if self.active_powerups['double_score']:
            multiplier = 2
        
        return multiplier
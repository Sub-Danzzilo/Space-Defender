# ========== ENEMY.PY ==========
# File untuk class Enemy dengan berbagai variasi
# Must Have + Nice to Have enemies dengan visual unik

import pygame
import math

# ========== HELPER FUNCTION: HITUNG JARAK ==========
def distance(pos1, pos2):
    """Hitung jarak antara 2 posisi"""
    return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])

# ========== CLASS DASAR ENEMY ==========
class Enemy(pygame.sprite.Sprite):
    """Kelas dasar untuk semua musuh"""
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # PERBAIKAN: Tambah mask untuk collision yang akurat
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 2
        self.health = 1
        self.max_health = 1  # PERBAIKAN: Tambah max_health
        self.score_value = 10
        self.enemy_type = "normal"
    
    def update(self):
        """Update dengan forced movement"""
        self.rect.y += self.speed
        
        # FORCE MOVEMENT: Jika stuck di atas, turun paksa
        if self.rect.y < -50:
            self.rect.y += 5
    
    def take_damage(self, damage):
        """Musuh terkena damage"""
        self.health -= damage
    
    def draw(self, surface):
        """Menggambar musuh dengan health bar jika health > 1"""
        surface.blit(self.image, self.rect)
        
        # PERBAIKAN: Gambar health bar jika health lebih dari 1
        if self.max_health > 1:
            self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        """Gambar health bar di atas musuh"""
        bar_width = self.rect.width
        bar_height = 4
        bar_x = self.rect.x
        bar_y = self.rect.y - 8
        
        # Background bar (merah)
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar (hijau) berdasarkan persentase health
        health_width = int((self.health / self.max_health) * bar_width)
        if health_width > 0:
            pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
        
        # Border bar
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

# ========== MUST HAVE: RED SHOOTER ==========
class RedShooter(Enemy):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 1.5  # Lebih lambat agar punya waktu menembak
        self.health = 1
        self.score_value = 15
        self.enemy_type = "red_shooter"
        self.shoot_timer = 0
        self.shoot_interval = 80  # Tembak setiap 1 detik (60 frames)
        self.bullets = []
    
    def should_shoot(self):
        """Cek apakah musuh harus menembak - FIXED"""
        # Hanya tembak jika sudah cukup turun (di layar) dan timer cukup
        if self.rect.y > 50 and self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0  # Reset timer
            return True
        return False

    def update(self):
        """Update posisi dan tembak - FIXED"""
        self.rect.y += self.speed
        self.shoot_timer += 1  # Timer selalu bertambah
    
    def draw(self, surface):
        """Gambar dengan indikator tembak"""
        surface.blit(self.image, self.rect)
        
        # Indikator sedang menembak (lingkaran merah)
        if self.shoot_timer > self.shoot_interval - 20:  # 20 frame sebelum tembak
            pygame.draw.circle(surface, (255, 0, 0), 
                             (self.rect.centerx, self.rect.bottom + 10), 5, 2)

# ========== MUST HAVE: BOUNCER ==========
class Bouncer(Enemy):
    """Musuh yang memantul ke kiri-kanan saat jatuh"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 1.5
        self.health = 1
        self.score_value = 12
        self.enemy_type = "bouncer"
        self.bounce_speed = 3
        self.bounce_direction = 1
        self.bounce_time = 0
    
    def update(self):
        """Update dengan boundary protection"""
        self.rect.y += self.speed
        self.rect.x += self.bounce_speed * self.bounce_direction
        self.bounce_time += 1
        
        if self.bounce_time > 30:
            self.bounce_direction *= -1
            self.bounce_time = 0
        
        # PERBAIKAN: Boundary check yang lebih ketat
        if self.rect.left < 0:
            self.rect.left = 0
            self.bounce_direction = 1
        elif self.rect.right > 800:
            self.rect.right = 800  
            self.bounce_direction = -1

# ========== MUST HAVE: KAMIKAZE ==========
class Kamikaze(Enemy):
    """Musuh yang lari cepat menuju pemain saat deket"""
    def __init__(self, x, y, image, player=None):
        super().__init__(x, y, image)
        self.speed = 1.5
        self.health = 1
        self.score_value = 20
        self.enemy_type = "kamikaze"
        self.player = player
        self.normal_speed = 1.5
        self.chase_speed = 5
        self.chase_distance = 150
    
    def update(self):
        """Update dengan logika chase - PERBAIKAN: Hapus kondisi kill"""
        if self.player and distance(self.rect.center, self.player.rect.center) < self.chase_distance:
            self.speed = self.chase_speed
            if self.player.rect.x < self.rect.x:
                self.rect.x -= self.chase_speed
            elif self.player.rect.x > self.rect.x:
                self.rect.x += self.chase_speed
        else:
            self.speed = self.normal_speed
        
        self.rect.y += self.speed
        
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > 800 - self.rect.width:
            self.rect.x = 800 - self.rect.width

# ========== MUST HAVE: TANK ==========
class Tank(Enemy):
    """Musuh besar bergerak lambat, HP banyak (5 HP)"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 1.0
        self.health = 5
        self.max_health = 5  # PERBAIKAN: Set max_health
        self.score_value = 50
        self.enemy_type = "tank"
        self.min_speed = 0.5
    
    def update(self):
        """Update dengan anti-stuck protection"""
        current_speed = max(self.speed, self.min_speed)
        self.rect.y += current_speed
        
        # PERBAIKAN EXTRA: Jika stuck, force movement
        if self.rect.y < -50:  # Jika terlalu tinggi
            self.rect.y += 10
        elif self.rect.y < 0 and current_speed < 0.5:  # Jika hampir stuck
            self.rect.y += 2

# ========== MUST HAVE: SPLITTER ==========
class Splitter(Enemy):
    """Musuh saat mati jadi 2 musuh lebih kecil"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 1.5
        self.health = 1
        self.score_value = 25
        self.enemy_type = "splitter"
    
    def update(self):
        """Update posisi - PERBAIKAN: Hapus kondisi kill"""
        self.rect.y += self.speed

class SplitterChild(Enemy):
    """Musuh kecil hasil split dari Splitter"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 2.5
        self.health = 1
        self.score_value = 10
        self.enemy_type = "splitter_child"
    
    def update(self):
        """Update posisi - PERBAIKAN: Hapus kondisi kill"""
        self.rect.y += self.speed

# ========== NICE TO HAVE: SPIRAL ENEMY ==========
class SpiralEnemy(Enemy):
    """Musuh bergerak spiral/zigzag saat turun"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 1.5
        self.health = 1
        self.score_value = 15
        self.enemy_type = "spiral"
        self.time = 0
        self.spiral_amplitude = 30
    
    def update(self):
        """Update dengan pattern spiral - PERBAIKAN: Hapus kondisi kill"""
        self.rect.y += self.speed
        self.rect.x += math.sin(self.time * 0.15) * 2
        self.time += 1
        
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > 800 - self.rect.width:
            self.rect.x = 800 - self.rect.width

# ========== NICE TO HAVE: ARMORED ==========
class Armored(Enemy):
    """Musuh berlapis armor (butuh 2x tembak untuk 1 HP damage)"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 1.2
        self.health = 2
        self.max_health = 2  # PERBAIKAN: Set max_health
        self.score_value = 20
        self.enemy_type = "armored"
        self.armor = 1
    
    def take_damage(self, damage):
        """Armor reduce damage"""
        if self.armor > 0:
            self.armor -= damage
        else:
            self.health -= damage
    
    def update(self):
        """Update posisi - PERBAIKAN: Hapus kondisi kill"""
        self.rect.y += self.speed
    
    def draw(self, surface):
        """Gambar dengan armor indicator dan health bar"""
        surface.blit(self.image, self.rect)
        
        # Gambar health bar
        if self.max_health > 1:
            self.draw_health_bar(surface)
        
        # Gambar armor indicator
        if self.armor > 0:
            pygame.draw.circle(surface, (255, 255, 0), self.rect.center, 35, 3)

# ========== NICE TO HAVE: BEE SWARM ==========
class BeeSwarm(Enemy):
    """Banyak musuh kecil yang terbang bersamaan (score kecil tapi banyak)"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 2
        self.health = 1
        self.score_value = 5
        self.enemy_type = "bee"
        self.time = 0
        self.hover_height = y
    
    def update(self):
        """Update dengan flutter effect - PERBAIKAN: Hapus kondisi kill"""
        self.rect.y += self.speed
        self.rect.x += math.cos(self.time * 0.2) * 1.5
        self.time += 1

# ========== NICE TO HAVE: REGENERATOR ==========
class Regenerator(Enemy):
    """Musuh yang recover 1 HP per 3 detik"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 1.8
        self.health = 3
        self.max_health = 3  # PERBAIKAN: Set max_health
        self.score_value = 35
        self.enemy_type = "regenerator"
        self.regen_timer = 0
        self.regen_interval = 180
    
    def update(self):
        """Update dengan regeneration"""
        self.rect.y += self.speed
        
        self.regen_timer += 1
        if self.regen_timer >= self.regen_interval:
            if self.health < self.max_health:
                self.health += 1
            self.regen_timer = 0
    
    def draw(self, surface):
        """Gambar dengan regen indicator dan health bar"""
        surface.blit(self.image, self.rect)
        
        # Gambar health bar
        if self.max_health > 1:
            self.draw_health_bar(surface)
        
        # Gambar regen indicator
        regen_progress = self.regen_timer / self.regen_interval
        pygame.draw.circle(surface, (255, 100, 255), self.rect.center, int(30 * regen_progress), 2)

# ========== NICE TO HAVE: FOLLOWER ==========
class Follower(Enemy):
    """Musuh mengikuti/chase pemain horizontal"""
    def __init__(self, x, y, image, player=None):
        super().__init__(x, y, image)
        self.speed = 1
        self.health = 1
        self.score_value = 18
        self.enemy_type = "follower"
        self.player = player
        self.follow_speed = 2.5
    
    def update(self):
        """Update dengan follow logic - PERBAIKAN: Hapus kondisi kill"""
        self.rect.y += self.speed
        
        if self.player:
            if self.player.rect.centerx < self.rect.centerx:
                self.rect.x -= self.follow_speed
            elif self.player.rect.centerx > self.rect.centerx:
                self.rect.x += self.follow_speed
        
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > 800 - self.rect.width:
            self.rect.x = 800 - self.rect.width

# ========== STRONG ENEMY ==========
class StrongEnemy(Enemy):
    """Kelas untuk musuh kuat (HP lebih banyak, gerak lebih lambat)"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 1.2
        self.health = 3
        self.max_health = 3  # PERBAIKAN: Set max_health
        self.score_value = 30
        self.enemy_type = "strong"
    
    def draw(self, surface):
        """Gambar health bar di atas musuh"""
        surface.blit(self.image, self.rect)
        
        bar_width = 50
        bar_height = 5
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.y - 15
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        health_width = (self.health / self.max_health) * bar_width
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))

# ========== FAST ENEMY ==========
class FastEnemy(Enemy):
    """Kelas untuk musuh cepat (HP sedikit, gerak cepat)"""
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 4
        self.health = 1
        self.score_value = 20
        self.enemy_type = "fast"
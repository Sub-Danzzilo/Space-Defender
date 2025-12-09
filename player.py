# ========== PLAYER.PY ==========
# File untuk class Player
# REVISED: Support 2 player dengan control berbeda + damage indicator

import pygame
import math
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image, player_id=1):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.health = 3
        self.max_health = 3
        self.player_id = player_id
        
        # Sistem kontrol
        self.control_scheme = None  # Akan diatur nanti
        self.shoot_timer = 0
        
        # Flags untuk network play
        self.is_dummy = False        # True = tidak bisa dikontrol (hanya tampil)
        self.is_remote = False       # True = posisi dikontrol via network
        self.remote_x = x            # Posisi target dari network
        self.remote_y = y
        
        # Interpolation untuk smooth movement
        self.interpolation_speed = 0.2
        self.show_shield = False
        self.shield_timer = 0

        # ===== TAMBAH: Atribut untuk efek damage =====
        self.recently_damaged = False
        self.damage_timer = 0
        self.is_invincible = False  # Untuk powerup invincibility
        
    def update(self):
        """Update player position dengan 3 mode: normal, dummy, remote"""
        
        # ===== MODE 1: DUMMY REMOTE (posisi dari network) =====
        if self.is_dummy and self.is_remote:
            # Interpolasi smooth ke posisi remote
            dx = self.remote_x - self.rect.x
            dy = self.remote_y - self.rect.y
            
            # Gunakan interpolation untuk pergerakan smooth
            self.rect.x += dx * self.interpolation_speed
            self.rect.y += dy * self.interpolation_speed
            
            # Batasi pergerakan maksimal
            max_move = 10  # Pixel per frame
            if abs(dx) < 1 and abs(dy) < 1:
                self.rect.x = self.remote_x
                self.rect.y = self.remote_y
            else:
                # Clamp movement untuk mencegah overshoot
                if abs(dx) > max_move:
                    self.rect.x += max_move if dx > 0 else -max_move
                if abs(dy) > max_move:
                    self.rect.y += max_move if dy > 0 else -max_move
            return
            
        # ===== MODE 2: DUMMY STATIC (tidak bergerak) =====
        elif self.is_dummy:
            # Tidak melakukan apa-apa, tetap di posisi awal
            return
            
        # ===== MODE 3: PLAYER NORMAL (dikontrol lokal) =====
        else:
            # Tangani input keyboard berdasarkan control_scheme
            keys = pygame.key.get_pressed()
            
            # Debug: Tampilkan control_scheme jika belum diatur
            if self.control_scheme is None:
                self.control_scheme = "wasd" if self.player_id == 1 else "arrows"
                print(f"⚠️ Player {self.player_id}: control_scheme was None, default to {self.control_scheme}")
            
            # Kontrol berdasarkan scheme
            if self.control_scheme == "wasd":
                if keys[pygame.K_w]:  # Up
                    self.rect.y -= self.speed
                if keys[pygame.K_s]:  # Down
                    self.rect.y += self.speed
                if keys[pygame.K_a]:  # Left
                    self.rect.x -= self.speed
                if keys[pygame.K_d]:  # Right
                    self.rect.x += self.speed
                    
            elif self.control_scheme == "arrows":
                if keys[pygame.K_UP]:
                    self.rect.y -= self.speed
                if keys[pygame.K_DOWN]:
                    self.rect.y += self.speed
                if keys[pygame.K_LEFT]:
                    self.rect.x -= self.speed
                if keys[pygame.K_RIGHT]:
                    self.rect.x += self.speed
                    
            elif self.control_scheme == "ijkl":
                if keys[pygame.K_i]:  # I = Up
                    self.rect.y -= self.speed
                if keys[pygame.K_k]:  # K = Down
                    self.rect.y += self.speed
                if keys[pygame.K_j]:  # J = Left
                    self.rect.x -= self.speed
                if keys[pygame.K_l]:  # L = Right
                    self.rect.x += self.speed
            
            # Boundary checking
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > 800:  # SCREEN_WIDTH
                self.rect.right = 800
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > 600:  # SCREEN_HEIGHT
                self.rect.bottom = 600
                
            # Update shield effect
            if self.show_shield:
                self.shield_timer -= 1
                if self.shield_timer <= 0:
                    self.show_shield = False

            # ===== UPDATE DAMAGE TIMER =====
            if self.recently_damaged:
                self.damage_timer -= 1
                if self.damage_timer <= 0:
                    self.recently_damaged = False
    
    def update_remote_position(self, x, y):
        """Update posisi dari network (untuk dummy player)"""
        self.remote_x = x
        self.remote_y = y
    
    def take_damage(self, damage):
        """Player menerima damage"""
        # PERBAIKAN: Tambahkan pengecekan invincibility
        if self.show_shield or self.is_invincible:  # Immune jika shield atau invincibility aktif
            return False
            
        self.health -= damage
        if self.health < 0:
            self.health = 0
        
        # ===== TAMBAH: Set damage effect =====
        self.recently_damaged = True
        self.damage_timer = 30  # 0.5 detik @60fps
        
        # Flash effect (bisa ditambahkan visual)
        return True
    
    def activate_shield(self, duration=180):  # 3 detik @60fps
        """Aktifkan shield sementara"""
        self.show_shield = True
        self.shield_timer = duration

    def deactivate_shield(self):
        """Nonaktifkan shield visual"""
        self.show_shield = False
        self.shield_timer = 0
    
    def draw(self, screen):
        """Gambar player dan shield jika aktif"""
        # Gambar player utama
        screen.blit(self.image, self.rect)
        
        # Gambar health bar di atas player (hanya jika health ≤ 6)
        if self.health > 0 and self.health <= 6:
            self._draw_health_bar(screen)
        
        # Gambar efek invincibility (jika ada)
        if self.recently_damaged:
            # Efek flash merah yang berkedip
            # Berkedip setiap 6 frame (3 frame nyala, 3 frame mati)
            if self.damage_timer % 6 < 3:
                flash_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                flash_surface.fill((255, 0, 0, 180))  # Merah dengan opacity 180
                screen.blit(flash_surface, self.rect)
        
        # Gambar shield effect jika aktif - BUBBLE ENERGY SHIELD
        if self.show_shield and self.shield_timer > 0:
            center_x = self.rect.centerx
            center_y = self.rect.centery
            shield_radius = max(self.rect.width, self.rect.height) // 2 + 15
            
            # ===== BUBBLE ENERGY SHIELD EFFECT =====
            
            # 1. Pulsating outer bubble (efek denyut)
            pulse_time = pygame.time.get_ticks() * 0.002  # Untuk animasi halus
            pulse_factor = (math.sin(pulse_time) + 1) * 0.5  # 0 to 1
            
            # Radius berdenyut
            current_radius = shield_radius + 5 + int(8 * pulse_factor)
            
            # 2. Buat surface untuk bubble shield
            bubble_size = current_radius * 2 + 20
            bubble_surf = pygame.Surface((bubble_size, bubble_size), pygame.SRCALPHA)
            
            # 3. Gambar bubble shield (gradien transparan)
            for radius_offset in range(0, 15, 3):
                alpha = 40 - radius_offset * 2
                color = (100, 200, 255, alpha)
                
                # Outer glow
                pygame.draw.circle(bubble_surf, color, 
                                 (bubble_size//2, bubble_size//2), 
                                 current_radius - radius_offset)
            
            # 4. Main bubble (energi padat tapi transparan)
            # Gradient dari dalam ke luar
            for i in range(5):
                radius = current_radius - i * 3
                if radius > 0:
                    # Warna semakin terang ke tengah
                    intensity = 150 + i * 20
                    alpha = 80 - i * 15
                    color = (0, intensity, 255, alpha)
                    pygame.draw.circle(bubble_surf, color,
                                     (bubble_size//2, bubble_size//2), 
                                     radius)
            
            # 5. Efek ripple/bercahaya di permukaan
            ripple_count = 8
            for i in range(ripple_count):
                angle = pulse_time * 2 + (i * math.pi * 2 / ripple_count)
                ripple_x = bubble_size//2 + int(current_radius * 0.8 * math.cos(angle))
                ripple_y = bubble_size//2 + int(current_radius * 0.8 * math.sin(angle))
                
                # Ripple kecil bercahaya
                ripple_alpha = int(150 * (0.5 + 0.5 * math.sin(pulse_time * 3 + i)))
                pygame.draw.circle(bubble_surf, (255, 255, 255, ripple_alpha),
                                 (ripple_x, ripple_y), 3)
            
            # 6. Efek energi berputar (partikel kecil)
            particle_count = 12
            for i in range(particle_count):
                particle_angle = pulse_time * 3 + (i * math.pi * 2 / particle_count)
                particle_radius = current_radius + 3
                particle_x = bubble_size//2 + int(particle_radius * math.cos(particle_angle))
                particle_y = bubble_size//2 + int(particle_radius * math.sin(particle_angle))
                
                # Warna partikel berubah-ubah
                hue = int((pulse_time * 50 + i * 30) % 255)
                particle_color = pygame.Color(0, 0, 0, 0)
                particle_color.hsva = (hue, 80, 100, 80)
                
                pygame.draw.circle(bubble_surf, particle_color,
                                 (particle_x, particle_y), 2)
            
            # 7. Outline bubble (cahaya tepi)
            pygame.draw.circle(bubble_surf, (200, 230, 255, 120),
                             (bubble_size//2, bubble_size//2), 
                             current_radius, 2)
            
            # 8. Blit bubble ke screen
            screen.blit(bubble_surf, (center_x - bubble_size//2, center_y - bubble_size//2))
            
            # 9. Efek kilatan acak (sparkles)
            if random.random() < 0.3:  # 30% chance per frame
                sparkle_angle = random.random() * math.pi * 2
                sparkle_radius = current_radius - 5
                sparkle_x = center_x + int(sparkle_radius * math.cos(sparkle_angle))
                sparkle_y = center_y + int(sparkle_radius * math.sin(sparkle_angle))
                
                # Kilatan kecil
                sparkle_size = random.randint(2, 4)
                pygame.draw.circle(screen, (255, 255, 255, 200),
                                 (sparkle_x, sparkle_y), sparkle_size)
        
    def _draw_health_bar(self, screen):
        """Menggambar health bar di atas player - VERSI SEDERHANA"""
        # Health bar hanya ditampilkan jika health ≤ 6
        if self.health > 6:
            return  # Auto hide jika health > 6
        
        # Posisi dan ukuran
        bar_width = 40
        bar_height = 5
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 8
        
        # Background
        pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Tentukan warna
        if self.health <= 1:
            color = (255, 0, 0)  # Merah
        elif self.health == 2:
            color = (255, 200, 0)  # Kuning
        elif self.health == 3:
            color = (0, 255, 0)  # Hijau
        else:  # 4, 5, 6
            color = (0, 255, 255)  # Cyan (semua cyan untuk 4-6)
        
        # Hitung fill
        max_display = 6  # Maksimal 6 untuk display
        fill_percent = min(self.health, max_display) / max_display
        fill_width = fill_percent * bar_width
        
        # Gambar fill
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
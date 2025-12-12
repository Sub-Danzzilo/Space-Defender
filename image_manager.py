# ========== IMAGE_MANAGER.PY (UPDATED) ==========
# File untuk mengelola semua gambar/sprite
# Mendukung 10 variasi musuh baru + custom asset loading

import pygame
import math
import os
from utils import resource_path

class ImageManager:
    """Mengelola semua gambar dan sprite"""
    def __init__(self):
        self.images = {}
        self.assets_loaded = 0
        self.assets_created = 0
        self.load_or_create_images()
    
    def load_or_create_images(self):
        """Load gambar dari folder atau buat jika tidak ada"""
        print("=== LOADING GAME ASSETS ===")

            # ===== LOGO UNTUK INTRO =====
        # Your logo
        if self.load_image('logo', 'assets/images/logo.png'):
            pass
        else:
            print("Creating space defender logo...")
            # Akan dibuat di intro_page.py
        
        # Logo Python  
        if self.load_image('logo_python', 'assets/images/logo_python.png'):
            pass
        else:
            print("Creating python logo...")
            # Akan dibuat di intro_page.py
        
        # ===== PLAYER =====
        if self.load_image('player', 'assets/images/player.png'):
            pass
        else:
            print("Creating player sprite...")
            self.images['player'] = self.create_player_image()
            self.assets_created += 1

        # ===== PLAYER 2 =====
        if self.load_image('player2', 'assets/images/player2.png'):
            pass
        else:
            print("Creating player2 sprite...")
            self.images['player2'] = self.create_player2_image()
            self.assets_created += 1
        
        # ===== BULLET PLAYER 1 =====
        if self.load_image('bullet_p1', 'assets/images/bullet_p1.png'):
            pass
        else:
            print("Creating bullet_p1 sprite...")
            self.images['bullet_p1'] = self.create_bullet_p1_image()
            self.assets_created += 1

        # ===== BULLET PLAYER 2 =====
        if self.load_image('bullet_p2', 'assets/images/bullet_p2.png'):
            pass
        else:
            print("Creating bullet_p2 sprite...")
            self.images['bullet_p2'] = self.create_bullet_p2_image()
            self.assets_created += 1

        # ===== BULLET MULTIPLE =====
        if self.load_image('bullet_multiple', 'assets/images/bullet_multiple.png'):
            pass
        else:
            print("Creating bullet_multiple sprite...")
            self.images['bullet_multiple'] = self.create_bullet_multiple_image()
            self.assets_created += 1

        # ===== ENEMY BULLET =====
        if self.load_image('enemy_bullet', 'assets/images/enemy_bullet.png'):
            pass
        else:
            print("Creating enemy bullet sprite...")
            self.images['enemy_bullet'] = self.create_enemy_bullet_image()
            self.assets_created += 1

        # ===== SHIELD EFFECT =====
        if self.load_image('shield', 'assets/images/shield.png'):
            pass
        else:
            print("Creating shield sprite...")
            self.images['shield'] = self.create_shield_image()
            self.assets_created += 1

        # ===== PAUSE ICON =====
        if self.load_image('pause', 'assets/images/pause.png'):
            pass
        else:
            print("Creating pause icon sprite...")
            self.images['pause'] = self.create_pause_image()
            self.assets_created += 1

        # ===== ENEMIES =====
        enemy_images = [
            ('enemy', 'assets/images/enemy.png'),
            ('red_shooter', 'assets/images/red_shooter.png'),
            ('bouncer', 'assets/images/bouncer.png'),
            ('kamikaze', 'assets/images/kamikaze.png'),
            ('tank', 'assets/images/tank.png'),
            ('splitter', 'assets/images/splitter.png'),
            ('splitter_child', 'assets/images/splitter_child.png'),
            ('spiral', 'assets/images/spiral.png'),
            ('armored', 'assets/images/armored.png'),
            ('bee', 'assets/images/bee.png'),
            ('regenerator', 'assets/images/regenerator.png'),
            ('follower', 'assets/images/follower.png'),
            ('strong_enemy', 'assets/images/strong_enemy.png'),
            ('fast_enemy', 'assets/images/fast_enemy.png')
        ]
        
        for image_name, file_path in enemy_images:
            if self.load_image(image_name, file_path):
                pass
            else:
                print(f"Creating {image_name} sprite...")
                creation_method = getattr(self, f'create_{image_name}_image', None)
                if creation_method:
                    self.images[image_name] = creation_method()
                    self.assets_created += 1
                else:
                    # Fallback ke enemy biasa
                    self.images[image_name] = self.create_enemy_image()
                    self.assets_created += 1

        # ===== BACKGROUND STARS =====
        if self.load_image('star', 'assets/images/star.png'):
            pass
        else:
            print("Creating star sprite...")
            self.images['star'] = self.create_star_image()
            self.assets_created += 1
        
        # ===== POWERUP =====
        if self.load_image('powerup', 'assets/images/powerup.png'):
            pass
        else:
            print("Creating powerup sprite...")
            self.images['powerup'] = self.create_powerup_image()
            self.assets_created += 1
        
        # ===== SUMMARY =====
        print(f"=== ASSETS SUMMARY ===")
        print(f"Loaded from files: {self.assets_loaded}")
        print(f"Created procedurally: {self.assets_created}")
        print(f"Total assets: {len(self.images)}")
        print("======================")
    
    def load_image(self, name, path, alpha=True):
        """Load image dengan alpha channel - FIXED untuk .exe"""
        try:
            abs_path = resource_path(path)
            
            # Debug: print path untuk troubleshooting
            print(f"🖼️ Trying to load: {path}")
            print(f"📁 Absolute path: {abs_path}")
            print(f"📁 File exists: {os.path.exists(abs_path)}")
            
            if os.path.exists(abs_path):
                if alpha:
                    image = pygame.image.load(abs_path).convert_alpha()
                else:
                    image = pygame.image.load(abs_path).convert()
                self.images[name] = image
                self.assets_loaded += 1
                print(f"✅ Successfully loaded: {path}")
                return True
            else:
                print(f"❌ Missing image: {path}")
                return False
        except Exception as e:
            print(f"❌ Error loading image {path}: {e}")
            return False
    
    def save_procedural_assets(self):
        """Simpan aset procedural ke folder images (untuk development)"""
        if not os.path.exists('images'):
            os.makedirs('images')
        
        saved_count = 0
        for name, surface in self.images.items():
            # Hanya simpan yang dibuat procedural (belum ada file)
            file_path = f'assets/images/{name}.png'
            if not os.path.exists(file_path):
                try:
                    pygame.image.save(surface, file_path)
                    print(f"💾 Saved procedural asset: {file_path}")
                    saved_count += 1
                except Exception as e:
                    print(f"Error saving {file_path}: {e}")
        
        if saved_count > 0:
            print(f"Saved {saved_count} procedural assets to 'images' folder")
    
    # ========== BASIC SPRITES ==========
    def create_player_image(self):
        """Generate gambar pesawat player (segitiga hijau)"""
        surface = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(surface, (0, 255, 0), [(25, 0), (0, 40), (50, 40)])
        pygame.draw.circle(surface, (0, 255, 255), (25, 15), 4)
        return surface
    
    def create_player2_image(self):
        """Generate gambar pesawat player 2 (segitiga cyan)"""
        surface = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(surface, (0, 255, 255), [(25, 0), (0, 40), (50, 40)])  # CYAN
        pygame.draw.circle(surface, (255, 255, 255), (25, 15), 4)  # Lampu putih
        return surface
    
    def create_bullet_p1_image(self):
        """Generate gambar peluru player 1 (laser hijau dengan efek)"""
        surface = pygame.Surface((8, 20), pygame.SRCALPHA)
        
        # Body peluru (hijau gradient)
        for i in range(8):
            alpha = 200 - i * 15
            color = (0, 255, 0, alpha)
            pygame.draw.rect(surface, color, (i, 5, 1, 10))
        
        # Head peluru (putih terang)
        pygame.draw.rect(surface, (200, 255, 200), (2, 0, 4, 8))
        pygame.draw.rect(surface, (255, 255, 255), (3, 2, 2, 4))
        
        # Trail effect (hijau transparan)
        for i in range(3):
            trail_height = 4 - i
            trail_alpha = 100 - i * 30
            trail_color = (0, 255, 0, trail_alpha)
            pygame.draw.rect(surface, trail_color, (1, 15 + i * 2, 6, trail_height))
        
        # Outline
        pygame.draw.rect(surface, (100, 255, 100), (0, 4, 8, 12), 1)
        
        return surface

    def create_bullet_p2_image(self):
        """Generate gambar peluru player 2 (laser cyan dengan efek)"""
        surface = pygame.Surface((8, 20), pygame.SRCALPHA)
        
        # Body peluru (cyan gradient)
        for i in range(8):
            alpha = 200 - i * 15
            color = (0, 255, 255, alpha)
            pygame.draw.rect(surface, color, (i, 5, 1, 10))
        
        # Head peluru (putih terang)
        pygame.draw.rect(surface, (200, 255, 255), (2, 0, 4, 8))
        pygame.draw.rect(surface, (255, 255, 255), (3, 2, 2, 4))
        
        # Trail effect (cyan transparan)
        for i in range(3):
            trail_height = 4 - i
            trail_alpha = 100 - i * 30
            trail_color = (0, 255, 255, trail_alpha)
            pygame.draw.rect(surface, trail_color, (1, 15 + i * 2, 6, trail_height))
        
        # Outline
        pygame.draw.rect(surface, (100, 255, 255), (0, 4, 8, 12), 1)
        
        return surface

    # OPTIONAL: Buat juga peluru untuk powerup multiple bullets yang lebih kecil
    def create_bullet_multiple_image(self):
        """Generate gambar peluru untuk multiple bullets (lebih kecil)"""
        surface = pygame.Surface((6, 15), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 255, 0), (1, 0, 4, 10))
        pygame.draw.rect(surface, (255, 200, 0), (2, 2, 2, 6))
        return surface
    
    def create_enemy_bullet_image(self):
        """Buat gambar bullet musuh yang sangat jelas (merah besar)"""
        surface = pygame.Surface((8, 16), pygame.SRCALPHA)
        
        # Bullet merah besar untuk musuh
        pygame.draw.rect(surface, (255, 0, 0), (1, 0, 6, 12))
        
        # Efek api/ledakan di ujung
        points = [
            (4, 16),  # Bawah tengah
            (0, 12),  # Bawah kiri  
            (8, 12),  # Bawah kanan
            (4, 16)   # Kembali ke tengah
        ]
        pygame.draw.polygon(surface, (255, 150, 0), points)
        
        # Highlight
        pygame.draw.line(surface, (255, 200, 200), (4, 2), (4, 8), 2)
        
        return surface
    
    def create_powerup_image(self):
        """Generate gambar powerup (bintang kuning)"""
        surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        points = []
        for i in range(10):
            angle = math.pi / 2 + (i * math.pi / 5)
            radius = 15 if i % 2 == 0 else 7
            x = 15 + radius * math.cos(angle)
            y = 15 - radius * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(surface, (255, 255, 0), points)
        pygame.draw.polygon(surface, (255, 200, 0), points, 2)
        return surface
    
    def create_shield_image(self):
        """Buat gambar shield (lingkaran biru transparan)"""
        surface = pygame.Surface((80, 80), pygame.SRCALPHA)
        
        # Lingkaran biru transparan
        pygame.draw.circle(surface, (0, 100, 255, 150), (40, 40), 35)
        
        # Outline biru terang
        pygame.draw.circle(surface, (0, 200, 255, 200), (40, 40), 35, 4)
        
        # Efek kilau
        pygame.draw.circle(surface, (200, 230, 255, 180), (25, 25), 8)
        
        return surface

    def create_pause_image(self):
        """Generate simple pause icon (circle + dua batang)"""
        size = 40
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        # Circular background
        pygame.draw.circle(surface, (30, 30, 30, 220), (size//2, size//2), size//2)
        pygame.draw.circle(surface, (255, 255, 255, 30), (size//2, size//2), size//2, 2)
        # Two pause bars
        bar_w = 6
        bar_h = 20
        gap = 6
        left_x = (size//2) - gap - bar_w
        right_x = (size//2) + gap
        top_y = (size//2) - (bar_h//2)
        pygame.draw.rect(surface, (220, 220, 220), (left_x, top_y, bar_w, bar_h), border_radius=2)
        pygame.draw.rect(surface, (220, 220, 220), (right_x, top_y, bar_w, bar_h), border_radius=2)
        return surface
    
    def create_star_image(self):
        """Generate gambar bintang untuk background"""
        surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 255, 255), (2, 2), 2)
        return surface
    
    # ========== MUST HAVE ENEMIES ==========
    def create_red_shooter_image(self):
        """Red Shooter - Kotak merah dengan nozzle"""
        surface = pygame.Surface((40, 45), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 0), (0, 0, 40, 35))
        pygame.draw.rect(surface, (100, 100, 100), (15, 32, 10, 15))
        pygame.draw.circle(surface, (200, 200, 200), (20, 47), 4)
        pygame.draw.circle(surface, (255, 255, 0), (12, 10), 3)
        pygame.draw.circle(surface, (255, 255, 0), (28, 10), 3)
        return surface
    
    def create_bouncer_image(self):
        """Bouncer - Lingkaran biru dengan spring"""
        surface = pygame.Surface((40, 45), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 150, 255), (20, 20), 18)
        pygame.draw.line(surface, (200, 200, 0), (20, 2), (15, 8), 3)
        pygame.draw.line(surface, (200, 200, 0), (15, 8), (25, 14), 3)
        pygame.draw.line(surface, (200, 200, 0), (25, 14), (20, 2), 3)
        pygame.draw.circle(surface, (255, 255, 0), (12, 15), 3)
        pygame.draw.circle(surface, (255, 255, 0), (28, 15), 3)
        return surface
    
    def create_kamikaze_image(self):
        """Kamikaze - Oranye dengan pedang"""
        surface = pygame.Surface((40, 45), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 100, 0), (5, 8, 30, 30))
        pygame.draw.line(surface, (200, 200, 200), (35, 5), (20, 35), 4)
        pygame.draw.circle(surface, (255, 255, 0), (38, 8), 2)
        pygame.draw.circle(surface, (255, 255, 0), (25, 32), 2)
        return surface
    
    def create_tank_image(self):
        """Tank - Persegi panjang hitam besar dengan turret"""
        surface = pygame.Surface((50, 55), pygame.SRCALPHA)
        pygame.draw.rect(surface, (50, 50, 50), (0, 15, 50, 40))
        pygame.draw.rect(surface, (100, 100, 100), (0, 15, 50, 40), 3)
        pygame.draw.circle(surface, (80, 80, 80), (25, 15), 12)
        pygame.draw.circle(surface, (120, 120, 120), (25, 15), 12, 2)
        pygame.draw.line(surface, (100, 100, 100), (25, 5), (25, 20), 4)
        pygame.draw.rect(surface, (100, 100, 200), (10, 25, 8, 8))
        pygame.draw.rect(surface, (100, 100, 200), (32, 25, 8, 8))
        return surface
    
    def create_splitter_image(self):
        """Splitter - Ungu muda yang bisa split"""
        surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(surface, (200, 100, 255), (0, 0, 40, 40))
        pygame.draw.line(surface, (255, 255, 0), (5, 20), (35, 20), 2)
        pygame.draw.circle(surface, (255, 255, 0), (12, 12), 3)
        pygame.draw.circle(surface, (255, 255, 0), (28, 12), 3)
        pygame.draw.circle(surface, (200, 100, 255), (20, 20), 22, 2)
        return surface
    
    # ========== NICE TO HAVE ENEMIES ==========
    def create_splitter_child_image(self):
        """Splitter Child - Ungu muda lebih kecil"""
        surface = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.rect(surface, (180, 120, 255), (0, 0, 25, 25))
        pygame.draw.circle(surface, (255, 255, 0), (8, 8), 2)
        pygame.draw.circle(surface, (255, 255, 0), (17, 8), 2)
        pygame.draw.circle(surface, (200, 100, 255), (12, 12), 14, 1)
        return surface
    
    def create_spiral_image(self):
        """Spiral Enemy - Hijau terang dengan spiral pattern"""
        surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(surface, (100, 255, 100), (0, 0, 40, 40))
        for i in range(0, 40, 10):
            pygame.draw.line(surface, (255, 255, 100), (i, 0), (i+5, 40), 1)
        pygame.draw.circle(surface, (255, 255, 0), (10, 10), 3)
        pygame.draw.circle(surface, (255, 255, 0), (30, 10), 3)
        return surface
    
    def create_armored_image(self):
        """Armored - Coklat dengan armor layers"""
        surface = pygame.Surface((45, 40), pygame.SRCALPHA)
        pygame.draw.rect(surface, (139, 69, 19), (5, 5, 35, 30))
        pygame.draw.rect(surface, (200, 200, 200), (0, 8, 8, 12))
        pygame.draw.rect(surface, (200, 200, 200), (37, 8, 8, 12))
        pygame.draw.circle(surface, (255, 200, 0), (15, 15), 3)
        pygame.draw.circle(surface, (255, 200, 0), (30, 15), 3)
        return surface
    
    def create_bee_image(self):
        """Bee Swarm - Kuning kecil dengan sayap"""
        surface = pygame.Surface((20, 25), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, (255, 200, 0), (5, 10, 10, 12))
        pygame.draw.circle(surface, (255, 150, 0), (10, 8), 4)
        pygame.draw.line(surface, (200, 220, 255), (3, 15), (3, 22), 1)
        pygame.draw.line(surface, (200, 220, 255), (17, 15), (17, 22), 1)
        pygame.draw.line(surface, (100, 100, 0), (10, 13), (10, 20), 1)
        return surface
    
    def create_regenerator_image(self):
        """Regenerator - Pink bersinar"""
        surface = pygame.Surface((45, 45), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 100, 200), (22, 22), 18)
        pygame.draw.circle(surface, (255, 150, 220), (22, 22), 20, 2)
        pygame.draw.circle(surface, (255, 200, 150), (15, 15), 4)
        pygame.draw.circle(surface, (255, 200, 150), (29, 15), 4)
        pygame.draw.line(surface, (255, 255, 100), (22, 12), (22, 32), 2)
        pygame.draw.line(surface, (255, 255, 100), (12, 22), (32, 22), 2)
        return surface
    
    def create_follower_image(self):
        """Follower - Biru tua dengan mata mengikuti"""
        surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 100, 200), (0, 0, 40, 40))
        pygame.draw.circle(surface, (255, 255, 255), (12, 15), 6)
        pygame.draw.circle(surface, (255, 255, 255), (28, 15), 6)
        pygame.draw.circle(surface, (0, 0, 0), (12, 15), 3)
        pygame.draw.circle(surface, (0, 0, 0), (28, 15), 3)
        pygame.draw.arc(surface, (255, 100, 0), (10, 20, 20, 15), 0, 3.14, 2)
        return surface
    
    # ========== OLD ENEMIES (from previous version) ==========
    def create_enemy_image(self):
        """Generate gambar musuh normal (kotak merah)"""
        surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 0), (0, 0, 40, 40))
        pygame.draw.circle(surface, (255, 255, 0), (12, 12), 4)
        pygame.draw.circle(surface, (255, 255, 0), (28, 12), 4)
        pygame.draw.line(surface, (255, 255, 0), (10, 25), (30, 25), 2)
        return surface
    
    def create_strong_enemy_image(self):
        """Generate gambar musuh kuat (kotak besar ungu dengan border)"""
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(surface, (128, 0, 128), (0, 0, 50, 50))
        pygame.draw.rect(surface, (255, 255, 0), (0, 0, 50, 50), 3)
        pygame.draw.circle(surface, (255, 255, 0), (15, 15), 5)
        pygame.draw.circle(surface, (255, 255, 0), (35, 15), 5)
        pygame.draw.circle(surface, (255, 255, 0), (25, 35), 5)
        return surface
    
    def create_fast_enemy_image(self):
        """Generate gambar musuh cepat (segitiga orange)"""
        surface = pygame.Surface((35, 40), pygame.SRCALPHA)
        pygame.draw.polygon(surface, (255, 165, 0), [(17, 40), (0, 0), (35, 0)])
        pygame.draw.circle(surface, (255, 255, 0), (17, 15), 3)
        return surface
# ========== GAME_MANAGER.PY ==========

import pygame
import random
from enemy import (Enemy, StrongEnemy, FastEnemy, RedShooter, Bouncer, Kamikaze, 
                   Tank, Splitter, SplitterChild, SpiralEnemy, Armored, BeeSwarm, 
                   Regenerator, Follower)
from bullet import EnemyBullet
from powerup import PowerUp

class GameManager:
    """Mengelola semua logika game"""
    
    def __init__(self, screen_width=800, screen_height=600):
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.sound_manager = None
        self.image_manager = None
        self.difficulty_manager = DifficultyManager()
    
    def spawn_enemy(self, x, y, difficulty_level, player1, image_manager, enemies_group, powerup_manager, is_multiplayer=False):
        """Buat musuh baru dengan variasi tipe berdasarkan level dan difficulty"""
        enemy_type = random.random()
        
        # PERBAIKAN: Untuk multiplayer, atur ulang posisi x agar tidak di area tengah
        if is_multiplayer:
            safe_margin = 50
            center_x = self.SCREEN_WIDTH // 2
            side = random.randint(0, 1)
            if side == 0:
                x = random.randint(0, center_x - safe_margin - 40)
            else:
                x = random.randint(center_x + safe_margin, self.SCREEN_WIDTH - 40)
        
        # Dapatkan allowed enemies berdasarkan difficulty
        allowed_enemies = self.difficulty_manager.get_settings()["allowed_enemies"]
        
        # Filter enemy types berdasarkan difficulty
        enemy_pool = []
        
        if difficulty_level <= 2:
            if "normal" in allowed_enemies and enemy_type < 0.5:
                enemy = Enemy(x, y, image_manager.images['enemy'])
            elif "red_shooter" in allowed_enemies and enemy_type < 0.6:
                enemy = RedShooter(x, y, image_manager.images['red_shooter'])
            elif "fast" in allowed_enemies:
                enemy = FastEnemy(x, y, image_manager.images['fast_enemy'])
            else:
                enemy = Enemy(x, y, image_manager.images['enemy'])
        
        elif difficulty_level <= 4:
            if "normal" in allowed_enemies and enemy_type < 0.25:
                enemy = Enemy(x, y, image_manager.images['enemy'])
            elif "red_shooter" in allowed_enemies and enemy_type < 0.35:
                enemy = RedShooter(x, y, image_manager.images['red_shooter'])
            elif "bouncer" in allowed_enemies and enemy_type < 0.45:
                enemy = Bouncer(x, y, image_manager.images['bouncer'])
            elif "kamikaze" in allowed_enemies and enemy_type < 0.55:
                enemy = Kamikaze(x, y, image_manager.images['kamikaze'], player1)
            elif "follower" in allowed_enemies and enemy_type < 0.65:
                enemy = Follower(x, y, image_manager.images['follower'], player1)
            elif "strong" in allowed_enemies and enemy_type < 0.8:
                enemy = StrongEnemy(x, y, image_manager.images['strong_enemy'])
            elif "tank" in allowed_enemies:
                enemy = Tank(x, y, image_manager.images['tank'])
            else:
                enemy = Enemy(x, y, image_manager.images['enemy'])
        
        elif difficulty_level <= 6:
            if "normal" in allowed_enemies and enemy_type < 0.15:
                enemy = Enemy(x, y, image_manager.images['enemy'])
            elif "red_shooter" in allowed_enemies and enemy_type < 0.22:
                enemy = RedShooter(x, y, image_manager.images['red_shooter'])
            elif "bouncer" in allowed_enemies and enemy_type < 0.28:
                enemy = Bouncer(x, y, image_manager.images['bouncer'])
            elif "splitter" in allowed_enemies and enemy_type < 0.34:
                enemy = Splitter(x, y, image_manager.images['splitter'])
            elif "spiral" in allowed_enemies and enemy_type < 0.4:
                enemy = SpiralEnemy(x, y, image_manager.images['spiral'])
            elif "armored" in allowed_enemies and enemy_type < 0.46:
                enemy = Armored(x, y, image_manager.images['armored'])
            elif "kamikaze" in allowed_enemies and enemy_type < 0.56:
                enemy = Kamikaze(x, y, image_manager.images['kamikaze'], player1)
            elif "strong" in allowed_enemies and enemy_type < 0.66:
                enemy = StrongEnemy(x, y, image_manager.images['strong_enemy'])
            elif "tank" in allowed_enemies and enemy_type < 0.76:
                enemy = Tank(x, y, image_manager.images['tank'])
            elif "fast" in allowed_enemies:
                enemy = FastEnemy(x, y, image_manager.images['fast_enemy'])
            else:
                enemy = Enemy(x, y, image_manager.images['enemy'])
        
        else:
            if "bee" in allowed_enemies and enemy_type < 0.1:
                enemy = BeeSwarm(x, y, image_manager.images['bee'])
            elif "regenerator" in allowed_enemies and enemy_type < 0.18:
                enemy = Regenerator(x, y, image_manager.images['regenerator'])
            elif "splitter" in allowed_enemies and enemy_type < 0.26:
                enemy = Splitter(x, y, image_manager.images['splitter'])
            elif "tank" in allowed_enemies and enemy_type < 0.34:
                enemy = Tank(x, y, image_manager.images['tank'])
            elif "strong" in allowed_enemies and enemy_type < 0.42:
                enemy = StrongEnemy(x, y, image_manager.images['strong_enemy'])
            elif "armored" in allowed_enemies and enemy_type < 0.5:
                enemy = Armored(x, y, image_manager.images['armored'])
            else:
                # Pilih dari allowed enemies yang tersisa
                available_enemies = []
                if "bouncer" in allowed_enemies:
                    available_enemies.append(Bouncer(x, y, image_manager.images['bouncer']))
                if "kamikaze" in allowed_enemies:
                    available_enemies.append(Kamikaze(x, y, image_manager.images['kamikaze'], player1))
                if "spiral" in allowed_enemies:
                    available_enemies.append(SpiralEnemy(x, y, image_manager.images['spiral']))
                if "follower" in allowed_enemies:
                    available_enemies.append(Follower(x, y, image_manager.images['follower'], player1))
                if "fast" in allowed_enemies:
                    available_enemies.append(FastEnemy(x, y, image_manager.images['fast_enemy']))
                
                if available_enemies:
                    enemy = random.choice(available_enemies)
                else:
                    enemy = Enemy(x, y, image_manager.images['enemy'])
        
        # Terapkan difficulty settings ke enemy
        self.difficulty_manager.apply_to_enemy(enemy)
        
        # Set max_health untuk semua enemy yang membutuhkan
        if hasattr(enemy, 'health') and not hasattr(enemy, 'max_health'):
            enemy.max_health = enemy.health
        
        if powerup_manager and powerup_manager.active_powerups.get('slow_enemies', False):
            enemy.speed *= 0.5
        
        enemies_group.add(enemy)
    
    def check_enemies_passed(self, enemies, player_list, powerup_managers, sound_manager):
        """Versi SIMPLE: Musuh lewat = damage ke player di sisi yang sama"""
        players_hit = []
        
        # Hitung player yang aktif (tidak None)
        active_players = [i for i, p in enumerate(player_list) if p is not None]
        
        for enemy in list(enemies):
            # PERBAIKAN: Gunakan kondisi yang lebih longgar
            if enemy.rect.top > self.SCREEN_HEIGHT - 20:  # 20 pixel sebelum benar-benar keluar
                # Tentukan player berdasarkan posisi x musuh
                if len(active_players) == 1:
                    # Single player: semua musuh ke player 1
                    player_idx = 0
                else:
                    # Multiplayer: kiri = P1, kanan = P2
                    if enemy.rect.centerx < self.SCREEN_WIDTH // 2:
                        player_idx = 0  # Kiri = P1
                    else:
                        player_idx = 1  # Kanan = P2
                
                # Beri damage jika player ada
                if player_idx < len(player_list) and player_list[player_idx]:
                    if player_list[player_idx].take_damage(1):
                        sound_manager.play_sound('player_hit')
                        players_hit.append(player_idx)
                
                enemy.kill()
        
        return players_hit
    
    def check_player_enemy_collision(self, player_list, enemies, powerup_managers, sound_manager):
        """FIXED: Player vs Enemy collision - HANYA di sini shield berlaku"""
        players_dead = []
        
        for player_idx, player in enumerate(player_list):
            if player and player.health > 0:
                # PERBAIKAN: Gunakan collide_mask untuk hitbox yang lebih akurat
                hit_enemies = pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_mask)
                if hit_enemies:
                    is_invincible = (powerup_managers[player_idx] and 
                                powerup_managers[player_idx].active_powerups.get('invincibility', False))
                    
                    # PERBAIKAN: Shield hanya berlaku di sini (tabrakan langsung)
                    if not is_invincible:
                        total_damage = 0
                        for enemy in hit_enemies:
                            if hasattr(enemy, 'collision_damage'):
                                total_damage += enemy.collision_damage
                            else:
                                total_damage += 1
                            enemy.kill()  # Hapus musuh setelah kena
                        
                        if player.take_damage(total_damage):
                            sound_manager.play_sound('player_hit')
                            if player.health <= 0:
                                players_dead.append(player_idx)
        
        return players_dead

    def check_enemy_bullets_collision(self, enemy_bullets, player_list, powerup_managers, sound_manager):
        """FIXED: Enemy bullets collision - HANYA di sini shield berlaku"""
        players_dead = []
        
        for player_idx, player in enumerate(player_list):
            if player and player.health > 0:
                # PERBAIKAN: Gunakan collide_rect untuk hitbox sederhana tapi akurat
                hit_bullets = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_rect)
                if hit_bullets:
                    is_invincible = (player_idx < len(powerup_managers) and 
                                powerup_managers[player_idx] and 
                                powerup_managers[player_idx].active_powerups.get('invincibility', False))
                    
                    # PERBAIKAN: Shield hanya berlaku di sini (peluru musuh)
                    if not is_invincible:
                        if player.take_damage(len(hit_bullets)):
                            sound_manager.play_sound('player_hit')
                            if player.health <= 0:
                                players_dead.append(player_idx)
        
        return players_dead
    
    def check_bullet_enemy_collision(self, player_id, bullets, enemies, sound_manager, 
                                    image_manager, powerup_manager, powerups_group):
        """Check collision antara bullet player dan enemies - METHOD BARU"""
        score_gained = 0
        enemies_killed = 0
        
        # PERBAIKAN: Handle jika powerup_manager adalah None
        if powerup_manager is None:
            score_multiplier = 1.0
        else:
            score_multiplier = powerup_manager.get_score_multiplier()
        
        # Check collisions
        hit_dict = pygame.sprite.groupcollide(bullets, enemies, True, False)
        
        for bullet, hit_enemies in hit_dict.items():
            for enemy in hit_enemies:
                enemy.take_damage(1)
                
                if enemy.health <= 0:
                    # Add score dengan multiplier
                    score_gained += enemy.score_value * score_multiplier
                    enemies_killed += 1
                    
                    # Handle splitter enemy
                    if enemy.enemy_type == "splitter":
                        self.spawn_splitter_children(
                            enemy.rect.centerx, enemy.rect.centery, 
                            enemies, image_manager
                        )

                    # Chance untuk spawn powerup berdasarkan difficulty settings
                    powerup_chance = self.difficulty_manager.get_settings()["powerup_drop_chance"]
                    if random.random() < powerup_chance:
                        self.spawn_powerup(
                            enemy.rect.centerx, enemy.rect.centery,
                            image_manager, powerups_group
                        )
                    
                    enemy.kill()
                
                # Play sound
                sound_manager.play_sound('explosion')
        
        return score_gained, enemies_killed
    
    def spawn_splitter_children(self, x, y, enemies_group, image_manager):
        """Spawn 2 anak Splitter saat parent mati"""
        for offset in [-20, 20]:
            child = SplitterChild(x + offset, y, image_manager.images['splitter_child'])
            enemies_group.add(child)
    
    def spawn_powerup(self, x, y, image_manager, powerups_group):
        """Spawn powerup di posisi musuh yang mati dengan chance berdasarkan difficulty"""
        
        powerup_types = [
            'rapid_fire',
            'slow_enemies', 
            'multiple_bullets',
            'health_regen',
            'speed_boost',
            'invincibility',
            'double_score'
        ]
        powerup_type = random.choice(powerup_types)
        powerup = PowerUp(x, y, powerup_type, image_manager.images['powerup'])
        powerups_group.add(powerup)
    
    def handle_shooter_attacks(self, enemies, image_manager, enemy_bullets_group):
        """Handle semua enemy yang bisa menembak - FIXED dengan fallback yang aman"""
        for enemy in enemies:
            if hasattr(enemy, 'should_shoot') and enemy.should_shoot():
                # Gunakan enemy_bullet image jika ada, jika tidak buat fallback
                bullet_image = image_manager.images.get('enemy_bullet')
                if bullet_image is None:
                    # Fallback: buat enemy bullet secara manual
                    bullet_image = self.create_fallback_enemy_bullet()
                    # Simpan ke image_manager untuk penggunaan berikutnya
                    image_manager.images['enemy_bullet'] = bullet_image
                
                # Buat peluru musuh
                enemy_bullet = EnemyBullet(
                    enemy.rect.centerx,
                    enemy.rect.bottom,
                    bullet_image
                )
                enemy_bullets_group.add(enemy_bullet)
                
                # PERBAIKAN: Gunakan sound khusus enemy_shoot dengan cooldown
                if self.sound_manager and not self.sound_manager.is_sfx_muted():
                    self.sound_manager.play_sound('enemy_shoot', cooldown=100)
    def create_fallback_enemy_bullet(self):
        """Buat fallback enemy bullet jika image tidak tersedia"""
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

class DifficultyManager:
    """Mengelola pengaturan difficulty game"""
    
    def __init__(self):
        self.difficulty_mode = "normal"  # easy, normal, hard, extreme
        self.difficulty_settings = {
            "easy": {
                "enemy_speed_multiplier": 0.5,
                "enemy_health_multiplier": 0.7,
                "enemy_damage_multiplier": 0.5,
                "spawn_rate_multiplier": 0.6,
                "player_health": 5,
                "fire_rate_multiplier": 1.2,
                "powerup_drop_chance": 0.4,
                "powerup_duration_multiplier": 1.25,
                "allowed_enemies": ["normal", "fast", "bouncer"],
                "color": (0, 255, 0)  # Hijau
            },
            "normal": {
                "enemy_speed_multiplier": 1.0,
                "enemy_health_multiplier": 1.0,
                "enemy_damage_multiplier": 1.0,
                "spawn_rate_multiplier": 1.0,
                "player_health": 3,
                "fire_rate_multiplier": 1.0,
                "powerup_drop_chance": 0.25,
                "powerup_duration_multiplier": 1.0,
                "allowed_enemies": ["normal", "fast", "bouncer", "red_shooter", "kamikaze", "follower", "strong", "tank"],
                "color": (0, 150, 255)  # Biru
            },
            "hard": {
                "enemy_speed_multiplier": 1.25,
                "enemy_health_multiplier": 1.5,
                "enemy_damage_multiplier": 1.5,
                "spawn_rate_multiplier": 1.4,
                "player_health": 2,
                "fire_rate_multiplier": 0.85,
                "powerup_drop_chance": 0.15,
                "powerup_duration_multiplier": 0.75,
                "allowed_enemies": ["normal", "fast", "bouncer", "red_shooter", "kamikaze", "follower", "strong", "tank", "splitter", "spiral", "armored"],
                "color": (255, 150, 0)  # Orange
            },
            "extreme": {
                "enemy_speed_multiplier": 1.5,
                "enemy_health_multiplier": 2.0,
                "enemy_damage_multiplier": 2.0,
                "spawn_rate_multiplier": 2.0,
                "player_health": 1,
                "fire_rate_multiplier": 0.7,
                "powerup_drop_chance": 0.05,
                "powerup_duration_multiplier": 0.5,
                "allowed_enemies": ["red_shooter", "kamikaze", "tank", "splitter", "armored", "regenerator"],
                "color": (255, 0, 0)  # Merah
            }
        }
    
    def set_difficulty(self, mode):
        """Set difficulty mode"""
        if mode in self.difficulty_settings:
            self.difficulty_mode = mode
    
    def get_settings(self):
        """Dapatkan pengaturan difficulty saat ini"""
        return self.difficulty_settings[self.difficulty_mode]
    
    def get_color(self):
        """Dapatkan warna difficulty saat ini"""
        return self.difficulty_settings[self.difficulty_mode]["color"]
    
    def apply_to_enemy(self, enemy):
        """Terapkan difficulty settings ke enemy"""
        settings = self.get_settings()
        
        # Apply multipliers
        enemy.speed *= settings["enemy_speed_multiplier"]
        if hasattr(enemy, 'health'):
            enemy.health = int(enemy.health * settings["enemy_health_multiplier"])
            enemy.max_health = enemy.health
        if hasattr(enemy, 'collision_damage'):
            enemy.collision_damage *= settings["enemy_damage_multiplier"]
        
        # Apply to enemy bullets speed
        if hasattr(enemy, 'bullets'):
            for bullet in enemy.bullets:
                bullet.speed *= settings["enemy_speed_multiplier"]
    
    def get_spawn_rate(self, base_spawn_rate):
        """Dapatkan spawn rate berdasarkan difficulty"""
        return base_spawn_rate * self.get_settings()["spawn_rate_multiplier"]
    
    def can_spawn_enemy(self, enemy_type):
        """Cek apakah enemy type boleh di-spawn di difficulty ini"""
        return enemy_type in self.get_settings()["allowed_enemies"]
    
    def should_drop_powerup(self):
        """Cek apakah harus drop powerup berdasarkan chance"""
        return random.random() < self.get_settings()["powerup_drop_chance"]
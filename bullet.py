# ========== BULLET.PY ==========

import pygame

class Bullet(pygame.sprite.Sprite):
    """Peluru player (naik)"""
    def __init__(self, x, y, image, speed_x=0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y
        self.speed_y = -8
        self.speed_x = speed_x
    
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x  # TAMBAH: pergerakan horizontal
        if self.rect.y < 0 or self.rect.x < 0 or self.rect.x > 800:  # Hapus jika keluar layar
            self.kill()
    
    def draw(self, surface):  # TAMBAHKAN METHOD DRAW
        surface.blit(self.image, self.rect)

class EnemyBullet(pygame.sprite.Sprite):
    """Peluru musuh (turun)"""
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y
        self.speed = 6
        # PERBAIKAN: Buat rect yang lebih kecil untuk hitbox yang lebih akurat
        self.hitbox = pygame.Rect(x-2, y, 4, 12)
    
    def update(self):
        self.rect.y += self.speed
        # PERBAIKAN: Update hitbox bersama rect
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery
        if self.rect.y > 600:
            self.kill()
    
    def draw(self, surface):  # TAMBAHKAN METHOD DRAW
        surface.blit(self.image, self.rect)
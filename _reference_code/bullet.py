import pygame as pg  
import math
from settings import *
pg.init()

# Класс Пули
class Bullet:
    def __init__(self, x, y, damage, weapon_type, angle):
        self.x = x
        self.y = y
        self.damage = damage
        self.weapon_type = weapon_type
        self.angle = angle
        self.speed = 15  # Увеличил скорость для лучшей визуализации
        self.width = 8
        self.height = 3
        
        # Создаем спрайт пули
        self.sprite = pg.Surface((self.width, self.height), pg.SRCALPHA)
        if weapon_type == "pistol":
            pg.draw.rect(self.sprite, (255, 255, 0), (0, 0, self.width, self.height))
        elif weapon_type == "rifle":
            pg.draw.rect(self.sprite, (0, 255, 255), (0, 0, self.width, self.height))
        elif weapon_type == "shotgun":
            pg.draw.rect(self.sprite, (255, 165, 0), (0, 0, self.width, self.height))
        
        self.rect = pg.Rect(x, y, self.width, self.height)

    def move(self):
        """Обновление позиции пули"""
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.rect.center = (self.x, self.y)

    def draw(self, camera_x, camera_y):
        """Отрисовка пули с учетом камеры"""
        rotated_sprite = pg.transform.rotate(self.sprite, -math.degrees(self.angle))
        rect = rotated_sprite.get_rect(center=(self.x - camera_x, self.y - camera_y))
        screen.blit(rotated_sprite, rect.topleft)
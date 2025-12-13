import pygame as pg
import math
from settings import *

# Инициализация Pygame
pg.init()

class Laser:
    """Класс лазерного снаряда"""
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.sprite = pg.transform.scale(bullet_sprite, (15, 15))
        self.rect = pg.Rect(int(self.x), int(self.y), 15, 15)

    def move(self):
        """Перемещение снаряда"""
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, camera_x, camera_y):
        """Отрисовка снаряда"""
        screen.blit(self.sprite, (self.x - camera_x, self.y - camera_y))

    def check_collision(self, target):
        """Проверка столкновения"""
        return self.rect.colliderect(target.rect)



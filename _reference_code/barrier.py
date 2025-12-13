import pygame as pg  
from settings import *
pg.init()
# Класс преграды
class Barrier:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 60
        self.max_health = 8
        self.health = self.max_health
        self.sprite = pg.transform.scale(sprite, (self.width, self.height))
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.alive = True

    def check_bullet_collision(self, bullet):
        """Проверяет столкновение с пулей и наносит урон"""
        if self.alive and self.rect.colliderect(bullet.rect):
            self.take_damage(1)
            return True
        return False

    def take_damage(self, damage=1):
        """Принимает урон от роботов и пуль"""
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            # Удаляем коллайдер после уничтожения
            self.rect = pg.Rect(0, 0, 0, 0)

    def draw(self, camera_x, camera_y):
        """Отрисовка барьера с индикатором здоровья"""
        if not self.alive:
            return
            
        # Основной спрайт
        screen.blit(self.sprite, (self.x - camera_x, self.y - camera_y))
        
        # Индикатор здоровья сверху
        health_width = 30
        health_height = 5
        health_x = self.x - camera_x + (self.width - health_width) // 2
        health_y = self.y - camera_y - 10
        
        # Фон индикатора (серый)
        pg.draw.rect(screen, (50, 50, 50), 
                     (health_x, health_y, health_width, health_height))
        
        # Здоровье (цвет от зеленого к красному)
        health_ratio = self.health / self.max_health
        health_color = (
            int(255 * (1 - health_ratio)),
            int(255 * health_ratio),
            0
        )
        current_width = int(health_width * health_ratio)
        pg.draw.rect(screen, health_color, 
                     (health_x, health_y, current_width, health_height))
import pygame as pg
import math
from settings import *
from laser import Laser
# Инициализация Pygame
pg.init()

# Глобальные настройки
map_width = 1000
map_height = 1000
wave_text_timer = 0

class BossMissile:
    def __init__(self, x, y, target, sprite):
        self.x = x
        self.y = y
        self.target = target  # Теперь храним ссылку на игрока
        self.speed = 3
        self.damage = 30
        self.original_sprite = pg.transform.scale(sprite, (30, 30))
        self.sprite = self.original_sprite  # Будем поворачивать копию
        self.rect = pg.Rect(x, y, 30, 30)
        self.lifetime = 300  # 5 секунды при 60 FPS
        self.exploded = False
        self.homing_duration = 300 # 5 секунды преследования
        self.current_homing_time = 0
        
        # Начальное направление к цели
        angle = math.atan2(self.target.y - y, self.target.x - x)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.rotate_sprite(angle)  # Первоначальный поворот

    def rotate_sprite(self, angle):
        """Поворачивает спрайт в направлении движения"""
        # Конвертируем радианы в градусы (pygame использует градусы)
        degrees = math.degrees(angle)
        # Поворачиваем спрайт, сохраняя центр
        self.sprite = pg.transform.rotate(self.original_sprite, -degrees)
        # Обновляем rect для корректного отображения
        self.rect = self.sprite.get_rect(center=(self.x, self.y))

    def update(self):
        """Обновление позиции ракеты с преследованием"""
        if self.exploded:
            return False
            
        # Преследование цели только в течение homing_duration
        if self.current_homing_time < self.homing_duration:
            # Пересчитываем направление к цели
            angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            self.dx = math.cos(angle) * self.speed
            self.dy = math.sin(angle) * self.speed
            self.rotate_sprite(angle)  # Обновляем поворот спрайта
            self.current_homing_time += 1
        
        # Движение
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (int(self.x), int(self.y))
        self.lifetime -= 1
        
        return self.lifetime > 0

    def draw(self, camera_x, camera_y):
        """Отрисовка ракеты с учетом поворота"""
        if not self.exploded:
            # Рисуем спрайт с учетом его центра
            sprite_rect = self.sprite.get_rect(center=(self.x - camera_x, self.y - camera_y))
            screen.blit(self.sprite, sprite_rect)

    def explode(self):
        """Обработка взрыва ракеты"""
        self.exploded = True
        return self.damage

    def check_collision(self, target):
        """Проверка столкновения"""
        return not self.exploded and self.rect.colliderect(target.rect)


class Boss:
    """Класс босса с анимациями для всех направлений"""
    def __init__(self, x, y, sprites):
        # Позиция и размеры
        self.x = x
        self.y = y
        self.width = 150
        self.height = 150
        
        # Характеристики
        self.speed = 1.5
        self.health = 2000
        self.detection_range = 500
        self.attack_cooldown = 0
        self.last_missile_time = 0
        self.alive = True
        
        # Анимации для разных направлений
        self.sprites = {
            "up": [pg.transform.scale(sprite, (self.width, self.height)) for sprite in sprites["up"]],
            "down": [pg.transform.scale(sprite, (self.width, self.height)) for sprite in sprites["down"]],
            "left": [pg.transform.scale(sprite, (self.width, self.height)) for sprite in sprites["left"]],
            "right": [pg.transform.scale(sprite, (self.width, self.height)) for sprite in sprites["right"]]
        }
        
        # Текущее направление и кадр анимации
        self.direction = "down"
        self.animation_frame = 0
        self.animation_speed = 0.3  # Скорость анимации
        
        # Графика
        self.current_sprite = self.sprites[self.direction][self.animation_frame]
        self.lasers = []
        self.rect = pg.Rect(int(self.x), int(self.y), self.width, self.height)
        self.alive = True
        
        # Сообщения
        self.death_text = None
        self.death_text_timer = 0
        
        self.missiles = []
        self.missile_cooldown = 0

    def update(self, player, walls, robots, boss):
        """Логика поведения босса"""
        if not self.alive or self.health <= 0:
            self.alive = False
            return

        # Движение к игроку
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Определение направления движения
        if abs(dx) > abs(dy):
            self.direction = "left" if dx < 0 else "right"
        else:
            self.direction = "up" if dy < 0 else "down"
        
        # Обновление анимации
        self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.sprites[self.direction])
        self.current_sprite = self.sprites[self.direction][int(self.animation_frame)]
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            self.rect.topleft = (int(self.x), int(self.y))

        # Логика стрельбы лазерами
        if self.attack_cooldown == 0 and distance <= self.detection_range:
            angle = math.atan2(player.y - self.y, player.x - self.x)
            self.lasers.append(Laser(
                self.x + self.width//2,
                self.y + self.height//2,
                angle
            ))
            self.attack_cooldown = 20
        else:
            self.attack_cooldown = max(0, self.attack_cooldown - 1)

        # Логика стрельбы ракетами
        if self.missile_cooldown == 0 and distance <= self.detection_range:
            self.missiles.append(BossMissile(
                self.x + self.width//2,
                self.y + self.height//2,
                player,  # Передаем игрока как цель
                boss_missile_sprite
            ))
            self.missile_cooldown = 120
            missile_sound.play()
        else:
            self.missile_cooldown = max(0, self.missile_cooldown - 1)

        # Обновление лазеров
        for laser in self.lasers[:]:
            laser.move()
            laser.rect.x = int(laser.x)
            laser.rect.y = int(laser.y)
            
            if laser.check_collision(player):
                player.take_damage(10)
                self.lasers.remove(laser)

        # Обновление ракет
        for missile in self.missiles[:]:
            if not missile.update():  # Если время жизни истекло
                self.missiles.remove(missile)
                explosion_sound.play()
                continue
                      
            if missile.check_collision(player):
                damage = missile.explode()
                player.take_damage(damage)
                explosion_sound.play()
                self.missiles.remove(missile)

    def draw(self, camera_x, camera_y):
        """Отрисовка босса, его лазеров и ракет"""
        if not self.alive:
            return
            
        screen.blit(self.current_sprite, (self.x - camera_x, self.y - camera_y))
        
        # Отрисовка лазеров
        for laser in self.lasers:
            laser.draw(camera_x, camera_y)
            
        # Отрисовка ракет
        for missile in self.missiles:
            missile.draw(camera_x, camera_y)
            
        if self.death_text_timer > 0:
            text_rect = self.death_text.get_rect(
                center=(self.x - camera_x + self.width//2,
                       self.y - camera_y - 20)
            )
            screen.blit(self.death_text, text_rect)
            self.death_text_timer -= 1
    def take_damage(self, damage):
        """Обработка получения урона"""
        if not self.alive:
            return
            
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            self.death_text = font.render("БОСС ПОБЕЖДЕН!", True, (0, 255, 0))
            self.death_text_timer = 120
            explosion_sound.play()        
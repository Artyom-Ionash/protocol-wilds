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

class Robot:
    def __init__(self, x, y, sprites):
        """Класс робота-противника"""
        # Позиция и размеры
        self.x = x
        self.y = y
        self.initial_x = x
        self.initial_y = y
        self.width = 40
        self.height = 40
        
        # Характеристики
        self.speed = 1
        self.health = 50
        self.detection_range = 400
        self.attack_cooldown = 0
        self.hit_count = 0
        self.collision_radius = 25  # Радиус для столкновений
        self.push_force = 0.5  # Сила отталкивания
        # Графика и анимация
        self.sprites = sprites
        self.robot_sprites = self.sprites["down"][0] if "down" in self.sprites else None
        self.animation_index = 0
        self.animation_speed = 0.2
        self.direction = "down"
        
        # Боевые системы
        self.lasers = []
        self.rect = pg.Rect(int(self.x), int(self.y), self.width, self.height)
        self.alive = True
        
        # Сообщения
        self.death_text = None
        self.death_text_timer = 0

    def draw(self, camera_x, camera_y):
        """Отрисовка робота и его лазеров"""
        if not self.alive:
            return
        
        # Рассчитываем экранные координаты
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Проверка видимости (с небольшим запасом)
        if not (-100 <= screen_x <= SCREEN_WIDTH + 100 and 
                -100 <= screen_y <= SCREEN_HEIGHT + 100):
            return
        
        # Отрисовка спрайта робота
        if self.direction in self.sprites and len(self.sprites[self.direction]) > 0:
            frame = int(self.animation_index) % len(self.sprites[self.direction])
            sprite = self.sprites[self.direction][frame]
            screen.blit(sprite, (screen_x, screen_y))
        
        # Отрисовка лазеров
        for laser in self.lasers:
            laser.draw(camera_x, camera_y)

    def update_animation(self):
        """Обновление анимации робота"""
        if self.direction in self.sprites:
            sprite_list = self.sprites[self.direction]
            self.animation_index += self.animation_speed
            if self.animation_index >= len(sprite_list):
                self.animation_index = 0
            self.robot_sprites = sprite_list[int(self.animation_index)]

    def update(self, player, walls, barriers, robots, boss):
        """Логика поведения робота"""
        if not self.alive or self.health <= 0 or not player.alive:
            self.alive = False
            return

        # Движение к игроку
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Определение направления
        if abs(dx) > abs(dy):
            self.direction = "left" if dx < 0 else "right"
        else:
            self.direction = "up" if dy < 0 else "down"

        if distance > 0:
            # Расчет новой позиции
            direction_x = dx / distance
            direction_y = dy / distance
            new_x = self.x + direction_x * self.speed
            new_y = self.y + direction_y * self.speed

            # Проверка столкновений с активными барьерами
            temp_rect = pg.Rect(new_x, new_y, self.width, self.height)
            can_move = True
            
            for barrier in barriers:
                if barrier.alive and temp_rect.colliderect(barrier.rect):
                    barrier.take_damage(1)
                    can_move = False
                    self.speed = 0  # Остановка на короткое время
                    break

            if can_move:
                self._handle_robot_collisions(robots, new_x, new_y)
                self.x = new_x
                self.y = new_y
                self.rect.topleft = (int(self.x), int(self.y))
                self.speed = 1  # Восстанавливаем скорость

        # Обновление анимации
        self.update_animation()

        # Логика стрельбы
        if self.attack_cooldown == 0 and distance <= self.detection_range:
            angle = math.atan2(player.y - self.y, player.x - self.x)
            self.lasers.append(Laser(
                self.x + self.width//2, 
                self.y + self.height//2, 
                angle
            ))
            self.attack_cooldown = 60
            shoot_enemy_sound.play()
        else:
            self.attack_cooldown = max(0, self.attack_cooldown - 1)

        for laser in self.lasers[:]:  # Используем копию списка для безопасного удаления
            laser.move()
            
            # Проверка столкновения с игроком
            if laser.check_collision(player):
                player.take_damage(5)
                self.lasers.remove(laser)
                continue
                
            # Проверка столкновения с барьерами
            for barrier in barriers:
                if barrier.alive and laser.rect.colliderect(barrier.rect):
                    barrier.take_damage(1)
                    if laser in self.lasers:
                        self.lasers.remove(laser)
                    break
    def _handle_robot_collisions(self, robots, new_x, new_y):
        """Обрабатывает столкновения между роботами"""
        for other_robot in robots:
            if other_robot is self or not other_robot.alive:
                continue
                
            # Проверяем расстояние между центрами
            dx = (new_x + self.width//2) - (other_robot.x + other_robot.width//2)
            dy = (new_y + self.height//2) - (other_robot.y + other_robot.height//2)
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Если роботы слишком близко - отталкиваем
            min_distance = self.collision_radius + other_robot.collision_radius
            if distance < min_distance and distance > 0:
                # Нормализуем вектор
                dx /= distance
                dy /= distance
                
                # Применяем силу отталкивания
                push_strength = self.push_force * (min_distance - distance) / min_distance
                self.x += dx * push_strength
                self.y += dy * push_strength
                
    def get_center(self):
        """Возвращает центр робота"""
        return (self.x + self.width//2, self.y + self.height//2)            

    def take_damage(self, damage, robots, boss):
        """Обработка получения урона"""
        if self.health > 0:
            self.health -= damage
            if self.health <= 0:
                self.die()

    def die(self):
        """Обработка смерти робота"""
        self.alive = False
        self.death_text = font.render("Робот уничтожен!", True, (255, 0, 0))
        self.death_text_timer = 120

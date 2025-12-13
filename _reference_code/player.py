import pygame as pg
import math
from settings import *
from bullet import Bullet
import random
from barrier import Barrier
from grenade import Grenade
# Инициализация Pygame
pg.init()

# Размеры игровой карты
map_width = 1000
map_height = 1000


class Player:
    def __init__(self, x, y, health, speed, damage, equipment):
        self.grenades = player_stats["grenades"]
        self.has_pistol = player_stats["has_pistol"]
        self.has_rifle = player_stats["has_rifle"]
        self.has_shotgun = player_stats["has_shotgun"]
        self.has_assault = player_stats.get("has_assault", False) 
        self.melee_range = 50
        self.melee_damage = 20
        self.melee_cooldown = 0
        self.melee_attack = False
        self.melee_animation_timer = 0
         
        self.x = x
        self.y = y
        self.health = health
        self.speed = speed
        self.damage = damage
        self.equipment = equipment
        
        # Атрибуты для барьеров
        self.barrier_cost = 1  # Стоимость создания барьера
        self.barrier_cooldown = 0  # Таймер перезарядки
        
        self.grenades = 0
        self.active_grenades = [] # Список активных гранат
        self.grenade_cooldown = 0 
        
        self.width = 60
        self.height = 45
        self.sprite = pg.transform.scale(player_sprites[equipment], (self.width, self.height))
        self.angle = 0
        self.bullets = []
        self.fire_cooldown = 0
        self.rect = pg.Rect(x + 10, y + 10, 40, 30)
        self.alive = True
        self.shooting = False
        self.last_shot_time = 0


    def update(self, keys, walls, robots, boss, camera_x, camera_y):
        """Обновление состояния игрока"""
        if not self.alive:
            return
            
        # Обновление перезарядки рукопашной атаки
        if self.melee_cooldown > 0:
            self.melee_cooldown -= 1
            
        # Обработка рукопашной атаки
        if self.melee_attack:
            self.melee_animation_timer -= 1
            if self.melee_animation_timer <= 0:
                self.melee_attack = False
            else:
                self._perform_melee_attack(robots, boss)
        # Обновление перезарядки барьеров
        if self.barrier_cooldown > 0:
            self.barrier_cooldown -= 1
            
        # Движение игрока
        self.move(keys, walls)
        
        # Обновление направления взгляда
        self.update_rotation(camera_x, camera_y)        
           
    def start_melee_attack(self):
        """Начало рукопашной атаки"""
        if self.melee_cooldown <= 0 and self.alive:
            self.melee_attack = True
            self.melee_animation_timer = 15  # Длительность анимации
            self.melee_cooldown = 30  # Перезарядка атаки
            return True
        return False
        
    def _perform_melee_attack(self, robots, boss):
        """Выполнение рукопашной атаки"""
        # Создаем область атаки перед игроком
        attack_angle = self.angle
        attack_range = self.melee_range
        attack_width = 30  # Ширина области атаки
        
        # Проверяем попадание по роботам
        for robot in robots:
            if robot.alive and self._check_melee_hit(robot, attack_angle, attack_range, attack_width):
                robot.take_damage(self.melee_damage, robots, boss)
                
        # Проверяем попадание по боссу
        if boss and boss.alive and self._check_melee_hit(boss, attack_angle, attack_range, attack_width):
            boss.take_damage(self.melee_damage)
            
    def _check_melee_hit(self, target, angle, range, width):
        """Проверяет попадание рукопашной атаки по цели"""
        # Вектор от игрока к цели
        dx = target.x + target.width//2 - (self.x + self.width//2)
        dy = target.y + target.height//2 - (self.y + self.height//2)
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > range + max(target.width, target.height)//2:
            return False
            
        # Угол между направлением атаки и направлением к цели
        target_angle = math.atan2(dy, dx)
        angle_diff = abs(target_angle - angle)
        
        # Нормализуем разницу углов
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        angle_diff = abs(angle_diff)
        
        # Проверяем, находится ли цель в секторе атаки
        return angle_diff <= math.radians(width)
        
    def throw_grenade(self, target_x, target_y):
        """Бросает гранату в указанную точку"""
        if self.grenades > 0 and self.grenade_cooldown <= 0:
            self.grenades -= 1
            self.active_grenades.append(Grenade(
                self.x + self.width//2,
                self.y + self.height//2,
                target_x,
                target_y
            ))
            self.grenade_cooldown = 30  # Задержка между бросками
            return True
        return False
        
    def update_grenades(self, enemies, boss, barriers):
        """Обновляет состояние всех гранат и проверяет попадания"""
        for grenade in self.active_grenades[:]:
            if grenade.update():  # Если граната еще летит
                continue
                
            # Граната взорвалась
            explosion_damage = grenade.damage
            explosion_radius = grenade.radius
            
            # Проверяем попадание по врагам
            for enemy in enemies[:]:
                dist = math.sqrt((enemy.x - grenade.x)**2 + (enemy.y - grenade.y)**2)
                if dist <= explosion_radius + enemy.width//2:
                    enemy.take_damage(explosion_damage, enemies, boss)
                    
            # Проверяем попадание по боссу
            if boss and boss.alive:
                dist = math.sqrt((boss.x - grenade.x)**2 + (boss.y - grenade.y)**2)
                if dist <= explosion_radius + boss.width//2:
                    boss.take_damage(explosion_damage)
                    
            # Проверяем попадание по барьерам
            for barrier in barriers[:]:
                dist = math.sqrt((barrier.x - grenade.x)**2 + (barrier.y - grenade.y)**2)
                if dist <= explosion_radius + barrier.width//2:
                    barrier.take_damage(3)
                    
            self.active_grenades.remove(grenade)
            
        if self.grenade_cooldown > 0:
            self.grenade_cooldown -= 1
                
    def draw_grenades(self, camera_x, camera_y):
        """Отрисовывает все активные гранаты и их взрывы"""
        for grenade in self.active_grenades:
            if grenade.exploded:
                if not grenade.draw_explosion(camera_x, camera_y):
                    self.active_grenades.remove(grenade)
            else:
                grenade.draw(camera_x, camera_y)

    def start_shooting(self):
        self.shooting = True

    def stop_shooting(self):
        self.shooting = False

    def update_shooting(self, target_x, target_y):
        if not self.shooting or not self.alive:
            return
            
        current_time = pg.time.get_ticks()
        if self.equipment == "pistol" and current_time - self.last_shot_time < 500:
            return
        elif self.equipment == "rifle" and current_time - self.last_shot_time < 100:
            return
        elif self.equipment == "shotgun" and current_time - self.last_shot_time < 800:
            return
        elif self.equipment == "assault" and current_time - self.last_shot_time < 80:  # Очень высокая скорострельность
            return
            
        self.shoot(target_x, target_y)
        self.last_shot_time = current_time

    def shoot(self, target_x, target_y):
        if not self.alive or self.fire_cooldown > 0:
            return
            
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.angle = angle
        
        if self.equipment == "basic":
            return
        elif self.equipment == "pistol":
            self._shoot_pistol(angle)
        elif self.equipment == "rifle":
            self._shoot_rifle(angle)
        elif self.equipment == "shotgun":
            self._shoot_shotgun(angle)
        elif self.equipment == "assault":
            self._shoot_assault(angle)  # Новый метод стрельбы
            
        shoot_player_sound.play()
    def _shoot_assault(self, angle):
        """Стрельба из автомата (быстрая с небольшим разбросом)"""
        # Небольшой случайный разброс
        angle_offset = random.uniform(-0.2, 0.2)  # +/- ~10 градусов
        self.bullets.append(Bullet(
            self.x + self.width//2,
            self.y + self.height//2,
            self.damage,
            "assault",
            angle + angle_offset
        ))
        self.fire_cooldown = 5  # Очень короткая перезарядка    

    def update_rotation(self, camera_x, camera_y):
        mouse_x, mouse_y = pg.mouse.get_pos()
        target_x = mouse_x + camera_x
        target_y = mouse_y + camera_y
        self.angle = math.atan2(target_y - self.y, target_x - self.x)
    
    def equip(self, equipment):
        self.equipment = equipment
        self.sprite = pg.transform.scale(player_sprites[equipment], (self.width, self.height))
        
        if equipment == "pistol":
            self.damage = 15
            self.has_pistol = True
        elif equipment == "rifle":
            self.damage = 10
            self.fire_cooldown = 10
            self.has_rifle = True
        elif equipment == "shotgun":
            self.damage = 25
            self.has_shotgun = True
        elif equipment == "assault":
            self.damage = 8
            self.fire_cooldown = 8
            self.has_assault = True
        
        player_stats["equipment"] = equipment
        player_stats["has_pistol"] = self.has_pistol
        player_stats["has_rifle"] = self.has_rifle
        player_stats["has_shotgun"] = self.has_shotgun
        player_stats["has_assault"] = self.has_assault 
        save_player_stats()
    
    def take_damage(self, damage):
        if not self.alive:
            return
            
        self.health -= damage
        if self.health <= 0:
            self.die()

    def move(self, keys, walls):
        if not self.alive:
            return
            
        dx, dy = 0, 0
        if keys[pg.K_a]:
            dx = -self.speed
        if keys[pg.K_d]:
            dx = self.speed
        if keys[pg.K_w]:
            dy = -self.speed
        if keys[pg.K_s]:
            dy = self.speed
        
        new_x = max(0, min(self.x + dx, map_width - self.width))
        new_y = max(0, min(self.y + dy, map_height - self.height))

        if not self._check_wall_collision(new_x, self.y, walls):
            self.x = new_x
        if not self._check_wall_collision(self.x, new_y, walls):
            self.y = new_y

        self.rect.topleft = (self.x, self.y)

    def draw(self, camera_x, camera_y):
        if not self.alive:
            return
        # Анимация рукопашной атаки
        if self.melee_attack:
            self._draw_melee_attack(camera_x, camera_y)
                
        rotated_sprite = pg.transform.rotate(self.sprite, -math.degrees(self.angle))
        rect = rotated_sprite.get_rect(
            center=(self.x + self.width//2 - camera_x, 
                   self.y + self.height//2 - camera_y)
        )
        screen.blit(rotated_sprite, rect.topleft)
        self.rect.topleft = (self.x, self.y)
        self._draw_health(camera_x, camera_y)
    
    def _draw_melee_attack(self, camera_x, camera_y):
        """Отрисовка визуального эффекта рукопашной атаки"""
        progress = self.melee_animation_timer / 15.0
        alpha = int(255 * progress)
        length = int(self.melee_range * (1 - progress))
        
        # Создаем поверхность для эффекта атаки
        attack_surface = pg.Surface((length, 20), pg.SRCALPHA)
        color = (255, 255, 0, alpha)  # Желтый цвет с прозрачностью
        
        # Рисуем треугольник атаки
        points = [
            (0, 10),
            (length, 0),
            (length, 20)
        ]
        pg.draw.polygon(attack_surface, color, points)
        
        # Поворачиваем и рисуем
        rotated_attack = pg.transform.rotate(attack_surface, -math.degrees(self.angle))
        attack_rect = rotated_attack.get_rect(
            center=(self.x + self.width//2 - camera_x, 
                   self.y + self.height//2 - camera_y)
        )
        screen.blit(rotated_attack, attack_rect.topleft)    

    def _check_bullet_collisions(self, robots, boss=None):
        for bullet in self.bullets[:]:
            for robot in robots:
                if bullet.rect.colliderect(robot.rect) and robot.alive:
                    robot.take_damage(bullet.damage, robots, boss)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
            
            if boss is not None and boss.alive and bullet.rect.colliderect(boss.rect):
                boss.take_damage(bullet.damage)
                if bullet in self.bullets:
                    self.bullets.remove(bullet)

    def die(self):
        self.alive = False  

    def reset(self):
        self.alive = True
        self.health = 100
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.bullets = []
        self.fire_cooldown = 0
        self.rect.topleft = (self.x, self.y)

    def _check_wall_collision(self, x, y, walls):
        temp_rect = pg.Rect(x, y, self.width, self.height)
        return any(temp_rect.colliderect(wall.rect) for wall in walls)

    def _shoot_pistol(self, angle):
        self.bullets.append(Bullet(
            self.x + self.width//2,
            self.y + self.height//2,
            self.damage,
            "pistol",
            angle
        ))
        self.fire_cooldown = 20

    def _shoot_rifle(self, angle):
        self.bullets.append(Bullet(
            self.x + self.width//2,
            self.y + self.height//2,
            self.damage,
            "rifle",
            angle
        ))
        self.fire_cooldown = 10

    def _shoot_shotgun(self, angle):
        for angle_offset in range(-15, 16, 5):
            self.bullets.append(Bullet(
                self.x + self.width//2,
                self.y + self.height//2,
                self.damage,
                "shotgun",
                angle + math.radians(angle_offset)
            ))
        self.fire_cooldown = 40

    def _draw_health(self, camera_x, camera_y):
        health_text = font.render(f"HP: {self.health}", True, (255, 0, 0))
        screen.blit(health_text, (self.x - camera_x, self.y - camera_y - 20))
    
    def draw_bullets(self, camera_x, camera_y):
        for bullet in self.bullets:
            bullet.draw(camera_x, camera_y)
    
    def create_barrier(self, x, y, barriers, coins, walls):
        """Создает барьер, если есть деньги и нет перезарядки"""
        if (self.barrier_cooldown <= 0 and 
            coins >= self.barrier_cost):
            
            # Проверяем, нет ли стен или других барьеров на этом месте
            barrier_rect = pg.Rect(x - 20, y - 20, 40, 40)
            valid_position = True
            
            for wall in walls:
                if barrier_rect.colliderect(wall.rect):
                    valid_position = False
                    break
                    
            for existing_barrier in barriers:
                if barrier_rect.colliderect(existing_barrier.rect):
                    valid_position = False
                    break
                    
            if valid_position:
                barriers.append(Barrier(x, y, barrier_sprite))
                self.barrier_cooldown = 30  # Задержка 0.5 секунды при 60 FPS
                return coins - self.barrier_cost  # Возвращаем новое количество монет
        
        return coins
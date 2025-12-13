from settings import *
import math
class Grenade:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 5
        self.max_distance = 150
        self.radius = 100
        self.damage = 100
        self.exploded = False
        self.landed = False
        self.fuse_timer = 120  # 2 секунды до взрыва
        self.explosion_timer = 30  # 0.5 секунды анимации взрыва
        self.sprite = pg.transform.scale(grenade_sprite, (30, 30))
        self.rect = pg.Rect(x-15, y-15, 30, 30)
        
        angle = math.atan2(target_y - y, target_x - x)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.distance_traveled = 0

    def update(self):
        if self.exploded:
            # Обратный отсчет анимации взрыва
            self.explosion_timer -= 1
            return self.explosion_timer > 0  # True пока идет анимация
            
        if not self.landed:
            self.x += self.dx
            self.y += self.dy
            self.distance_traveled += self.speed
            self.rect.center = (int(self.x), int(self.y))
            
            if self.distance_traveled >= self.max_distance:
                self.landed = True
        else:
            self.fuse_timer -= 1
            if self.fuse_timer <= 0:
                self.exploded = True
                return True
            
        return True

    def draw(self, camera_x, camera_y):
        if self.exploded:
            # Рисуем взрыв
            self.draw_explosion(camera_x, camera_y)
        elif not self.landed:
            rotated_sprite = pg.transform.rotate(self.sprite, self.distance_traveled * 2)
            screen.blit(rotated_sprite, (self.x - camera_x - 15, self.y - camera_y - 15))
        else:
            screen.blit(self.sprite, (self.x - camera_x - 15, self.y - camera_y - 15))
            if self.fuse_timer % 20 < 10:
                pg.draw.circle(screen, (255, 100, 0), (int(self.x - camera_x), int(self.y - camera_y)), 5)
            
    def draw_explosion(self, camera_x, camera_y):
        if self.exploded and self.explosion_timer > 0:
            explosion_sound.play() # Звук взрыва
            # Плавное увеличение и затухание взрыва
            progress = 1 - (self.explosion_timer / 30)  # от 0 до 1
            current_radius = int(self.radius * progress)
            alpha = int(255 * (1 - progress))
            
            # Создаем поверхность для взрыва с альфа-каналом
            explosion_surf = pg.Surface((current_radius*2, current_radius*2), pg.SRCALPHA)
            
            # Рисуем взрыв с градиентом
            pg.draw.circle(explosion_surf, (255, 100, 0, alpha), 
                          (current_radius, current_radius), current_radius)
            pg.draw.circle(explosion_surf, (255, 200, 0, alpha), 
                          (current_radius, current_radius), current_radius//2)
            
            # Рисуем поверхность на экране
            screen.blit(explosion_surf, 
                       (self.x - camera_x - current_radius, 
                        self.y - camera_y - current_radius))
            return True
        return False
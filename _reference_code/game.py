import pygame as pg
import random
from settings import *
from walls import generate_walls
from player import *
from boss import Boss
from die_menu import _show_game_over_screen
from shop import draw_shop
from robot import Robot
import math

# Импортируем настройки экрана
from window_settings import SCREEN_WIDTH, SCREEN_HEIGHT


def game_loop():
    """Основной игровой цикл"""
    from window_settings import SCREEN_WIDTH, SCREEN_HEIGHT
    # ===== ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ =====
    global map_width, map_height
    map_width = 1000  # Ширина игровой карты
    map_height = 1000  # Высота игровой карты

    # Создаем масштабированный фон для текущего размера экрана
    background_sprite_scaled = pg.transform.scale(background_sprite, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Игровые параметры
    spawn_timer = 0  # Таймер спавна врагов
    robots_killed = 0  # Счетчик убитых роботов
    wave = 1  # Текущая волна
    wave_enemies = 2  # Количество врагов в волне
    coins = 25  # Количество монет
    enemies_spawned = 0  # Сколько врагов уже заспавнено
    
    # Флаг паузы
    paused = False

    # Создание игровых объектов
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 100, 5, 10, "basic")
    player.grenades = 0  # Начальное количество гранат
    walls = generate_walls()  # Генерация стен
    robots = []  # Список роботов
    boss = None  # Босс (появляется позже)
    barriers = []  # Барьеры, создаваемые игроком
    
    # Параметры камеры
    camera_x, camera_y = 0, 0
    
    # Игровые состояния
    running = True  # Главный цикл игры
    game_over = False  # Конец игры
    in_shop = False  # Открыт ли магазин
    scroll_offset = 0  # Смещение для магазина

    # Текстовые уведомления
    wave_text = None  # Текст волны
    wave_text_timer = 0  # Таймер отображения текста волны
    boss_text = None  # Текст появления босса
    boss_text_timer = 0  # Таймер текста босса
    heal_text = None  # Текст восстановления здоровья
    heal_text_timer = 0  # Таймер текста здоровья
    heal_text_pos = (0, 0)  # Позиция текста здоровья
    
    # Загрузка сохранений
    global player_stats
    player_stats = load_player_stats()
    
    # Создание игрока с сохранёнными параметрами
    player = Player(
        SCREEN_WIDTH // 2,  # x
        SCREEN_HEIGHT // 2, # y
        100,                # health
        5,                  # speed
        10 if player_stats["equipment"] == "basic" else
        15 if player_stats["equipment"] == "pistol" else
        10 if player_stats["equipment"] == "rifle" else
        8  if player_stats["equipment"] == "assault" else
        25,                 # damage (для shotgun)
        player_stats["equipment"]  # equipment
    )
    
    # Загружаем все параметры из сохранения
    player.grenades = player_stats["grenades"]
    player.equipment = player_stats["equipment"]
    player.has_pistol = player_stats.get("has_pistol", False)
    player.has_rifle = player_stats.get("has_rifle", False)
    player.has_shotgun = player_stats.get("has_shotgun", False)
    player.has_assault = player_stats.get("has_assault", False)
    # Инициализация монет
    coins = player_stats["coins"]
    
    # ===== ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ =====
    try:
        while running:
            # Получаем состояние мыши
            mouse_buttons = pg.mouse.get_pressed()
            
            # Обработка событий
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                
                    if in_shop:
                        from settings import update_scaled_backgrounds
                        update_scaled_backgrounds()
                
                # Обработка паузы
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    paused = not paused  # Переключаем состояние паузы
                
                # Создание барьера по нажатию X
                if event.type == pg.KEYDOWN and event.key == pg.K_x and not in_shop and not paused:
                    # Создаем барьер перед игроком (с небольшим смещением)
                    barrier_x = player.x + math.cos(math.radians(player.angle)) * 50
                    barrier_y = player.y + math.sin(math.radians(player.angle)) * 50
                    
                    # Проверяем, нет ли стен или других барьеров на этом месте
                    barrier_rect = pg.Rect(barrier_x - 20, barrier_y - 20, 40, 40)
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
                        coins = player.create_barrier(barrier_x, barrier_y, barriers, coins, walls)
                
                # Рукопашная атака по нажатию E
                if event.type == pg.KEYDOWN and event.key == pg.K_e and not in_shop and not paused:
                    player.start_melee_attack()
                
                # Обновление перезарядки барьеров
                if player.barrier_cooldown > 0:
                    player.barrier_cooldown -= 1
                    
                # Выход в меню по TAB
                if event.type == pg.KEYDOWN and event.key == pg.K_TAB and running == True:
                    # Сохраняем все параметры игрока
                    player_stats.update({
                        "coins": coins,
                        "grenades": player.grenades,
                        "equipment": player.equipment,
                        "has_pistol": player.has_pistol,
                        "has_rifle": player.has_rifle,
                        "has_shotgun": player.has_shotgun,
                        "has_assault": player.has_assault
                    })
                    save_player_stats()
                    return 
                
                # Обработка нажатия кнопки мыши (только если не в паузе)
                if event.type == pg.MOUSEBUTTONDOWN and not in_shop and not paused:
                    if event.button == 1:
                        player.start_shooting()
                    if event.button == 3:  # Правая кнопка мыши
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        
                        # Передаем координаты с учетом камеры
                        target_x = mouse_x + camera_x
                        target_y = mouse_y + camera_y
                        
                        # Попробуем создать гранату
                        if player.grenades > 0:
                            grenade = Grenade(player.x, player.y, target_x, target_y)
                            player.active_grenades.append(grenade)  # Добавляем гранату в список
                            player.grenades -= 1                  
                # Обработка отпускания кнопки мыши
                if event.type == pg.MOUSEBUTTONUP and not in_shop:
                    if event.button == 1:
                        player.stop_shooting()
            
            # Если игра на паузе - отображаем экран паузы
            if paused:
                # Создаем полупрозрачное затемнение
                pause_overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                pause_overlay.fill((0, 0, 0))
                pause_overlay.set_alpha(150)
                screen.blit(pause_overlay, (0, 0))
                
                # Текст паузы
                pause_text = font.render("ПАУЗА", True, (255, 255, 255))
                screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, 
                                    SCREEN_HEIGHT//2 - pause_text.get_height()//2))
                
                # Подсказка для продолжения
                hint_text = small_font.render("Нажмите ESCAPE чтобы продолжить", True, (200, 200, 200))
                screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, 
                                    SCREEN_HEIGHT//2 + 50))
                
                pg.display.flip()
                clock.tick(FPS)
                continue  # Пропускаем остальную часть цикла
            
            # Обновление стрельбы при зажатой кнопке (если не в паузе)
            if not in_shop and mouse_buttons[0]:
                mouse_x, mouse_y = pg.mouse.get_pos()
                player.update_shooting(mouse_x + camera_x, mouse_y + camera_y)

            # ===== ОБНОВЛЕНИЕ СОСТОЯНИЯ ИГРЫ =====
            if not game_over and not paused:
                # Обновляем направление взгляда игрока
                player.update_rotation(camera_x, camera_y)
                # Обновление гранат
                player.update_grenades(robots, boss, barriers)
                # Движение игрока
                keys = pg.key.get_pressed()
                player.move(keys, walls)
                
                # Обновление камеры (слежение за игроком)
                camera_x = max(0, min(player.x - SCREEN_WIDTH // 2, map_width - SCREEN_WIDTH))
                camera_y = max(0, min(player.y - SCREEN_HEIGHT // 2, map_height - SCREEN_HEIGHT))

                # Спавн новых роботов
                if enemies_spawned < wave_enemies:
                    spawn_timer += 1
                    if spawn_timer >= 60:  # Спавн каждую секунду
                        # Генерация позиции сверху экрана
                        spawn_x = random.randint(50, map_width - 50)
                        spawn_y = random.randint(-200, -50)
                        
                        # Проверка, чтобы робот не появился на стене
                        spawn_rect = pg.Rect(spawn_x, spawn_y, 40, 40)
                        valid_spawn = True
                        for wall in walls:
                            if spawn_rect.colliderect(wall.rect):
                                valid_spawn = False
                                break
                                
                        if valid_spawn:
                            new_robot = Robot(spawn_x, spawn_y, robot_sprites)
                            new_robot.direction = "down"  # Начальное направление
                            new_robot.speed = 1.5  # Скорость движения
                            robots.append(new_robot)
                            enemies_spawned += 1
                            spawn_timer = 0
                
                # Обновление состояния роботов
                for robot in robots[:]:
                    if robot.alive:
                        robot.update(player, walls, barriers, robots, boss)
                        robot.draw(camera_x, camera_y)
                    else:
                        robots.remove(robot)
                        robots_killed += 1
                        coins += 1  # Награда за убийство
                        player.health = min(100, player.health + 5)  # Восстановление здоровья
                        
                        # Текст восстановления здоровья
                        heal_text = font.render("+5 HP", True, (0, 255, 0))
                        heal_text_timer = 30
                        heal_text_pos = (robot.x - camera_x, robot.y - camera_y)
                for robot in robots:
                    for bullet in robot.lasers[:]:  # Используем копию списка для безопасного удаления
                        for barrier in barriers:
                            if barrier.check_bullet_collision(bullet):
                                if bullet in robot.lasers:
                                    robot.lasers.remove(bullet)
                                break  # Пуля может столкнуться только с одним барьером
                
                # Обновляем гранаты игрока
                for grenade in player.active_grenades[:]:
                    if grenade.update():  # Если граната еще активна (летит или взрывается)
                        grenade.draw(camera_x, camera_y)  # Рисуем гранату/взрыв
                        
                        # Если граната только что взорвалась
                        if grenade.exploded and grenade.explosion_timer == 30:
                            for robot in robots[:]:
                                if math.sqrt((grenade.x - robot.x)**2 + (grenade.y - robot.y)**2) <= grenade.radius:
                                    robot.take_damage(grenade.damage, robots, boss)
                            # Проверка на попадание по боссу
                            if boss and math.sqrt((grenade.x - boss.x)**2 + (grenade.y - boss.y)**2) <= grenade.radius:
                                boss.take_damage(grenade.damage)
                    else:
                        # Удаляем гранату, если анимация завершена
                        player.active_grenades.remove(grenade)      
                # Обновление пуль
                for bullet in player.bullets[:]:
                    bullet.move()
                    # Удаление пуль за границами карты
                    if (bullet.x < 0 or bullet.x > map_width or 
                        bullet.y < 0 or bullet.y > map_height):
                        player.bullets.remove(bullet)

                # Переход на следующую волну
                if robots_killed >= wave_enemies and len(robots) == 0:
                    wave += 1
                    wave_enemies += 4  # Увеличиваем сложность
                    robots_killed = 0
                    enemies_spawned = 0
                    
                    # Текст новой волны
                    wave_text = font.render(f"Волна {wave} началась!", True, (255, 255, 255))
                    wave_text_timer = 120
                    
                    # Спавн босса каждые 5 волн
                    if wave % 5 == 0:
                        boss = Boss(SCREEN_WIDTH // 2, -100, boss_sprites)
                        boss_text = font.render("ПОЯВЛЕНИЕ БОССА!", True, (255, 0, 0))
                        boss_text_timer = 120
                        siren_sound.play()

                # Обновление босса
                if boss and boss.alive:
                    boss.update(player, walls, robots, boss)
                    boss.draw(camera_x, camera_y)

                # Обновление перезарядки оружия
                if player.fire_cooldown > 0:
                    player.fire_cooldown -= 1
                player.update(keys, walls, robots, boss, camera_x, camera_y)
            # ===== ОТРИСОВКА ИГРЫ =====
            # 1. Фон
            screen.blit(background_sprite_scaled, (-camera_x, -camera_y))
            
            # Если открыт магазин
            if in_shop:
                coins, scroll_offset = draw_shop(screen, coins, player, scroll_offset)
                screen.blit(shop_background_scaled, (0, 0))
            else:    
                # 2. Стены
                for wall in walls:
                    wall.draw(camera_x, camera_y)

                # 3. Барьеры
                for barrier in barriers:
                    barrier.draw(camera_x, camera_y)

                # 4. Роботы
                for robot in robots:
                    if robot.alive:
                        robot.draw(camera_x, camera_y)

                # 5. Игрок и пули
                if not in_shop:
                    player.draw(camera_x, camera_y)
                    player.draw_bullets(camera_x, camera_y) 
                    player._check_bullet_collisions(robots, boss)
                # 6. Босс
                if boss and boss.alive:
                    boss.draw(camera_x, camera_y)

                # 7. Текстовые уведомления
                if heal_text and heal_text_timer > 0:
                    screen.blit(heal_text, heal_text_pos)
                    heal_text_timer -= 1

                if wave_text and wave_text_timer > 0:
                    text_rect = wave_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
                    screen.blit(wave_text, text_rect)
                    wave_text_timer -= 1
                    
                if boss_text and boss_text_timer > 0:
                    text_rect = boss_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
                    screen.blit(boss_text, text_rect)
                    boss_text_timer -= 1

                # 8. Интерфейс
                coins_text = font.render(f"{coins}", True, (255, 255, 255))
                screen.blit(coins_text, (55, 20))
                screen.blit(coin_sprite, (10, 10))
                
                # Отображение гранат (в правом верхнем углу)
                screen.blit(grenade_sprite, (SCREEN_WIDTH - 80, 10))
                grenades_count = small_font.render(f"x{player.grenades}", True, WHITE)
                screen.blit(grenades_count, (SCREEN_WIDTH - 40, 15))
                
                exit_text = small_font.render("Нажмите TAB чтобы выйти в меню", True, (255, 255, 255))
                screen.blit(exit_text, (SCREEN_WIDTH//2 - exit_text.get_width()//2, SCREEN_HEIGHT - 70))
                
                # Отрисовка гранат и их взрывов
                player.draw_grenades(camera_x, camera_y)
                # Отображение информации о барьерах
                barrier_text = small_font.render(f"Барьер (X): {player.barrier_cost} монет", True, WHITE)
                screen.blit(barrier_text, (20, SCREEN_HEIGHT - 40))
                if player.barrier_cooldown > 0:
                    cooldown_text = small_font.render(f"Перезарядка: {player.barrier_cooldown//10}", True, RED)
                    screen.blit(cooldown_text, (20, SCREEN_HEIGHT - 70))

            # ===== ПРОВЕРКА СОСТОЯНИЯ ИГРОКА =====
            if not player.alive and not game_over:
                game_over = True
                # Остановка всех врагов
                for robot in robots:
                    robot.speed = 0
                if boss:
                    boss.speed = 0
                
                # Показ экрана окончания игры
                result = _show_game_over_screen(player, coins)
                if result == "restart":
                    return game_loop()  # Перезапуск игры
                elif result == "menu":
                    return  # Возврат в меню
                elif result == "quit_game":
                    running = False  # Полный выход из игры
                else:
                    running = False  # Выход из игры
            
            # Обновление экрана
            pg.display.flip()
            clock.tick(FPS)
            
    finally:
        # Гарантированное сохранение при выходе
        player_stats.update({
            "coins": coins,
            "grenades": player.grenades,
            "equipment": player.equipment,
            "has_pistol": player.has_pistol,
            "has_rifle": player.has_rifle,
            "has_shotgun": player.has_shotgun,
            "has_assault": player.has_assault
        })
        save_player_stats()
        
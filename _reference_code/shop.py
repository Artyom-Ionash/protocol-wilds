import pygame as pg
from settings import *

def draw_shop(screen, player, coins, player_stats):
    """Отрисовка магазина с функциональными предметами"""
    # Импортируем текущие размеры экрана и обновленный фон
    from window_settings import SCREEN_WIDTH, SCREEN_HEIGHT
    from settings import shop_background_scaled
    
    # Фон - используем масштабированный фон
    screen.blit(shop_background_scaled, (0, 0))
    
    # Обновляем количество гранат из player_stats перед отображением
    player.grenades = player_stats.get("grenades", 0)
    
    # Заголовок и информация о валюте
    title = font.render("МАГАЗИН", True, (255, 255, 0))
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
    
    coins_text = font.render(f"{coins}", True, (255, 255, 0))
    grenades_text = font.render(f"Гранаты: {player.grenades}", True, (255, 255, 0))
    
    screen.blit(coin_sprite, (SCREEN_WIDTH//2 - 100, 55))
    screen.blit(coins_text, (SCREEN_WIDTH//2 - coins_text.get_width()//2, 60))
    screen.blit(grenades_text, (SCREEN_WIDTH//2 - grenades_text.get_width()//2, 90))
    
    
    
    # Список предметов
    shop_items = [
        {"id": "pistol", "name": "Пистолет", "price": 25, 
         "desc": "Урон: 15", "available": not player.has_pistol},
        {"id": "rifle", "name": "Пулемёт", "price": 35, 
         "desc": "Урон: 10, скорострельность", "available": not player.has_rifle},
        {"id": "shotgun", "name": "Дробовик", "price": 45, 
         "desc": "Урон: 25, медленная стрельба", "available": not player.has_shotgun},
        {"id": "assault", "name": "Автомат", "price": 40,
         "desc": "Урон: 8, небольшой разброс", "available": not player.has_assault},
        {"id": "grenade", "name": "Граната", "price": 5, 
         "desc": "Взрывной урон 100", "available": True},
    ]
    
    # Параметры отображения
    item_height = 90
    start_y = 130
    mouse_pos = pg.mouse.get_pos()
    mouse_clicked = False
    
    # Обработка событий
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_clicked = True
    
    # Отрисовка всех предметов
    for i, item in enumerate(shop_items):
        y_pos = start_y + i * item_height
        
        # Фон предмета
        item_bg = pg.Surface((450, 80), pg.SRCALPHA)
        item_bg.fill((100, 100, 100, 150) if not item["available"] and item["id"] != "grenade" else (50, 50, 50, 150))
        screen.blit(item_bg, (SCREEN_WIDTH//2 - 225, y_pos))
        
        # Иконка
        item_img = pg.transform.scale(player_sprites[item["id"]], (60, 60))
        screen.blit(item_img, (SCREEN_WIDTH//2 - 200, y_pos + 10))
        
        # Текст
        name_text = small_font.render(item["name"], True, (255, 255, 255))
        price_text = small_font.render(f"Цена: {item['price']}", True, (255, 255, 0))
        desc_text = tiny_font.render(item["desc"], True, (200, 200, 200))
        
        screen.blit(name_text, (SCREEN_WIDTH//2 - 120, y_pos + 10))
        screen.blit(price_text, (SCREEN_WIDTH//2 - 120, y_pos + 30))
        screen.blit(desc_text, (SCREEN_WIDTH//2 - 120, y_pos + 50))
        
        # Для гранат
        if item["id"] == "grenade":
            # Всегда берем актуальное количество гранат из player_stats
            current_grenades = player_stats.get("grenades", 0)
            count_text = tiny_font.render(f"{current_grenades}", True, (255, 255, 255))
            screen.blit(count_text, (SCREEN_WIDTH//2 + 130, y_pos + 30))
            
            button_rect = pg.Rect(SCREEN_WIDTH//2 + 80, y_pos + 20, 100, 35)
            mouse_over = button_rect.collidepoint(mouse_pos)
            
            can_buy = coins >= item["price"]
            
            button_color = (100, 200, 100) if mouse_over and can_buy else (70, 160, 70)
            if not can_buy:
                button_color = (100, 100, 100)
                
            pg.draw.rect(screen, button_color, button_rect, border_radius=5)
            pg.draw.rect(screen, (200, 200, 200), button_rect, 2, border_radius=5)
            
            buy_text = tiny_font.render("Купить", True, (255, 255, 255))
            screen.blit(buy_text, (button_rect.centerx - buy_text.get_width()//2, 
                                button_rect.centery - buy_text.get_height()//2))
            
            if mouse_over and mouse_clicked and can_buy:
                coins -= item["price"]
                # Обновляем количество гранат через player_stats
                player_stats["grenades"] = player_stats.get("grenades", 0) + 1
                player.grenades = player_stats["grenades"]  # Синхронизируем с игроком
                player_stats["coins"] = coins
                save_player_stats()
                pg.time.delay(60)
            continue
        
        # Для оружия - кнопка "Купить" или "Надеть/Снять"
        if item["available"]:
            # Кнопка "Купить" для еще не купленного оружия
            button_rect = pg.Rect(SCREEN_WIDTH//2 + 80, y_pos + 20, 100, 35)
            mouse_over = button_rect.collidepoint(mouse_pos)
            
            button_color = (100, 200, 100) if mouse_over and coins >= item["price"] else (70, 160, 70)
            if coins < item["price"]:
                button_color = (160, 70, 70)
                
            pg.draw.rect(screen, button_color, button_rect, border_radius=5)
            pg.draw.rect(screen, (200, 200, 200), button_rect, 2, border_radius=5)
            
            buy_text = tiny_font.render("Купить", True, (255, 255, 255))
            screen.blit(buy_text, (button_rect.centerx - buy_text.get_width()//2, 
                                 button_rect.centery - buy_text.get_height()//2))
            
            if mouse_over and mouse_clicked and coins >= item["price"]:
                buy_sound.play()
                coins -= item["price"]
                setattr(player, f"has_{item['id']}", True)
                player_stats[f"has_{item['id']}"] = True
                
                # Автоматически надеваем купленное оружие
                player.equipment = item["id"]
                if item["id"] == "pistol":
                    player.damage = 15
                elif item["id"] == "rifle":
                    player.damage = 10
                elif item["id"] == "shotgun":
                    player.damage = 25
                elif item["id"] == "assault":
                    player.damage = 8
                
                player_stats["equipment"] = player.equipment
                player_stats["coins"] = coins
                save_player_stats()
                pg.time.delay(60)
        else:
            # Кнопка "Надеть/Снять" для уже купленного оружия
            button_rect = pg.Rect(SCREEN_WIDTH//2 + 80, y_pos + 20, 100, 35)
            mouse_over = button_rect.collidepoint(mouse_pos)
            
            # Определяем, надето ли это оружие сейчас
            is_equipped = (player.equipment == item["id"])
            
            button_color = (200, 200, 100) if mouse_over else (160, 160, 70)
            if is_equipped:
                button_color = (100, 200, 200) if mouse_over else (70, 160, 160)
                
            pg.draw.rect(screen, button_color, button_rect, border_radius=5)
            pg.draw.rect(screen, (200, 200, 200), button_rect, 2, border_radius=5)
            
            button_text = "Снять" if is_equipped else "Надеть"
            text = tiny_font.render(button_text, True, (255, 255, 255))
            screen.blit(text, (button_rect.centerx - text.get_width()//2, 
                           button_rect.centery - text.get_height()//2))
            
            if mouse_over and mouse_clicked:
                if is_equipped:
                    equip_sound.play()
                    # Снимаем оружие (переключаем на базовое)
                    player.equipment = "basic"
                    player.damage = 10  # Базовый урон
                else:
                    equip_sound.play()
                    # Надеваем это оружие
                    player.equipment = item["id"]
                    if item["id"] == "pistol":
                        player.damage = 15
                    elif item["id"] == "rifle":
                        player.damage = 10
                    elif item["id"] == "shotgun":
                        player.damage = 25
                    elif item["id"] == "assault":
                        player.damage = 8
                
                player_stats["equipment"] = player.equipment
                save_player_stats()
                pg.time.delay(60)
    
    # Инструкция по выходу
    exit_text = small_font.render("Нажмите TAB чтобы выйти", True, (255, 255, 255))
    screen.blit(exit_text, (SCREEN_WIDTH//2 - exit_text.get_width()//2, SCREEN_HEIGHT - 70))
    
    return coins
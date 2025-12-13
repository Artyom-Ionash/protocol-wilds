import pygame as pg
from settings import *
from window_settings import *
from game import *
from shop import draw_shop
from button import Button
from player import Player

# Зациклить фоновую музыку
volume = 1.0
background_music.play(-1)
background_music.set_volume(volume)

class MenuState:
    def __init__(self):
        self.buttons = []
        self.create_buttons()
        self.sound = [] 
        self.show_controls = False
        self.next_state = None
        
    def create_buttons(self):
        button_width, button_height = 200, 50
        start_y = SCREEN_HEIGHT // 2 - 150
        
        self.buttons = [
            Button(SCREEN_WIDTH//2 - button_width//2, start_y, button_width, button_height, "Играть", 
                  lambda: self.set_state("game")),
            Button(SCREEN_WIDTH//2 - button_width//2, start_y + 70, button_width, button_height, "Магазин", 
                  lambda: self.set_state("shop")),
            Button(SCREEN_WIDTH//2 - button_width//2, start_y + 140, button_width, button_height, "Настройки", 
                  lambda: self.set_state("settings")),
            Button(SCREEN_WIDTH//2 - button_width//2, start_y + 210, button_width, button_height, 
                  "Полный экран" if not FULLSCREEN else "Оконный режим", 
                  lambda: self.toggle_fullscreen()),
            Button(SCREEN_WIDTH//2 - button_width//2, start_y + 280, button_width, button_height, "Управление", 
                  lambda: self.toggle_controls()),
            Button(SCREEN_WIDTH//2 - button_width//2, start_y + 350, button_width, button_height, "Выход", 
                  lambda: self.set_state("quit"))
        ]
    
    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        # Переключаем режим
        from window_settings import toggle_fullscreen
        toggle_fullscreen()
        
        # ОБЯЗАТЕЛЬНО обновляем все фоны
        from settings import update_scaled_backgrounds
        update_scaled_backgrounds()
        
        # Пересоздаем кнопки с новыми позициями
        self.create_buttons()
    
    def adjust_volume(self, change):
        global volume
        volume += change
        volume = max(0.0, min(round(volume, 1), 1.0))
        pg.mixer.music.set_volume(volume)
        background_music.set_volume(volume)
    
    def toggle_controls(self):
        self.show_controls = not self.show_controls
        
    def set_state(self, new_state):
        self.next_state = new_state

    def update(self, mouse_pos, events):
        for button in self.buttons:
            button.check_hover(mouse_pos)

    def draw(self, surface):
        # Используем масштабированный фон меню
        surface.blit(menu_background_scaled, (0, 0))
        
        title = font.render("Future Game", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        warning = small_font.render("Внимание: при выходе в меню во время игры деньги не сохранятся!", True, (255, 0, 0))
        surface.blit(warning, (SCREEN_WIDTH//2 - warning.get_width()//2, 120))
        
        if self.next_state == "settings":
            self.draw_settings(surface)
        else:
            for button in self.buttons:
                button.draw(surface)
            
        if self.show_controls:
            self.draw_controls(surface)
    
    def draw_settings(self, surface):
        # Фон настроек
        settings_bg = pg.Surface((400, 250))
        settings_bg.fill((50, 50, 50))
        surface.blit(settings_bg, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 125))
        
        # Текст "Громкость" с кнопками
        vol_text = font.render(f"Громкость: {int(volume * 100)}%", True, WHITE)
        text_rect = vol_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        surface.blit(vol_text, text_rect)
        
        # Кнопки "+" и "-" для громкости
        plus_rect = pg.Rect(SCREEN_WIDTH//2 + 100, SCREEN_HEIGHT//2 - 100, 50, 50)
        minus_rect = pg.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 50, 50)
        
        pg.draw.rect(surface, (100, 100, 100), plus_rect)
        pg.draw.rect(surface, (100, 100, 100), minus_rect)
        
        plus_text = font.render("+", True, WHITE)
        minus_text = font.render("-", True, WHITE)
        
        surface.blit(plus_text, (plus_rect.centerx - plus_text.get_width()//2, plus_rect.centery - plus_text.get_height()//2))
        surface.blit(minus_text, (minus_rect.centerx - minus_text.get_width()//2, minus_rect.centery - minus_text.get_height()//2))
        
        # Кнопка полноэкранного режима
        fullscreen_text = "Выйти из полного экрана" if FULLSCREEN else "Полный экран"
        fullscreen_rect = pg.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 20, 200, 40)
        mouse_over_fullscreen = fullscreen_rect.collidepoint(pg.mouse.get_pos())
        
        fullscreen_color = (150, 150, 150) if mouse_over_fullscreen else (100, 100, 100)
        pg.draw.rect(surface, fullscreen_color, fullscreen_rect, border_radius=5)
        pg.draw.rect(surface, WHITE, fullscreen_rect, 2, border_radius=5)
        
        fs_text = small_font.render(fullscreen_text, True, WHITE)
        surface.blit(fs_text, (fullscreen_rect.centerx - fs_text.get_width()//2, 
                              fullscreen_rect.centery - fs_text.get_height()//2))
        
        # Обработка кликов
        mouse_pos = pg.mouse.get_pos()
        mouse_clicked = False
        
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
        
        if mouse_clicked:
            if plus_rect.collidepoint(mouse_pos):
                self.adjust_volume(0.1)
            elif minus_rect.collidepoint(mouse_pos):
                self.adjust_volume(-0.1)
            elif fullscreen_rect.collidepoint(mouse_pos):
                self.toggle_fullscreen()
    
        # Подсказка для выхода
        exit_text = small_font.render("Нажмите TAB чтобы выйти", True, WHITE)
        surface.blit(exit_text, (SCREEN_WIDTH//2 - exit_text.get_width()//2, SCREEN_HEIGHT//2 + 40))
    
    def draw_controls(self, surface):
        """Отрисовка окна управления"""
        controls_bg = pg.Surface((500, 300))
        controls_bg.fill((50, 50, 50))
        surface.blit(controls_bg, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//3))
        
        controls_title = font.render("Управление", True, WHITE)
        surface.blit(controls_title, (SCREEN_WIDTH//2 - controls_title.get_width()//2, SCREEN_HEIGHT//2 - 130))
        
        controls = [
            "Движение: W, A, S, D",
            "Стрельба: ЛКМ",
            "Поставить барьер: X",
            "Граната: ПКМ",
            "Пауза: ESC",
            "Полный экран: F11",
            "Выход в меню: TAB"
        ]
        
        for i, control in enumerate(controls):
            text = small_font.render(control, True, WHITE)
            surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 80 + i * 30))
            
        close_hint = small_font.render("Нажмите любую кнопку чтобы закрыть", True, WHITE)
        surface.blit(close_hint, (SCREEN_WIDTH//2 - close_hint.get_width()//2, SCREEN_HEIGHT//2 + 100))

def main_menu():
    load_player_stats()
    
    temp_player = Player(0, 0, 100, 0, 10, player_stats["equipment"])
    temp_player.grenades = player_stats["grenades"]
    temp_player.has_pistol = player_stats.get("has_pistol", False)
    temp_player.has_rifle = player_stats.get("has_rifle", False)
    temp_player.has_shotgun = player_stats.get("has_shotgun", False)
    temp_player.has_assault = player_stats.get("has_assault", False)
    
    menu_state = MenuState()
    current_state = "menu"
    running = True
    
    while running:
        mouse_pos = pg.mouse.get_pos()
        events = pg.event.get()
        
        # Update current state
        if current_state == "menu":
            menu_state.update(mouse_pos, events)
        elif current_state == "settings":
            # Обработка кликов по кнопкам громкости
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    # Получаем координаты кнопок из draw_settings
                    plus_rect = pg.Rect(SCREEN_WIDTH//2 + 100, SCREEN_HEIGHT//2 - 100, 50, 50)
                    minus_rect = pg.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 50, 50)
                    
                    if plus_rect.collidepoint(mouse_pos):
                        menu_state.adjust_volume(0.1)
                    elif minus_rect.collidepoint(mouse_pos):
                        menu_state.adjust_volume(-0.1)
        
        for event in events:
            if event.type == pg.QUIT:
                running = False
                
            if current_state == "menu":
                if menu_state.show_controls and event.type in (pg.MOUSEBUTTONDOWN, pg.KEYDOWN):
                    menu_state.show_controls = False
                else:
                    for button in menu_state.buttons:
                        if button.handle_event(event):
                            button.action()
                            if menu_state.next_state:
                                current_state = menu_state.next_state
                                menu_state.next_state = None
                            break
            
            # Handle settings exit
            elif current_state == "settings":
                if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                    current_state = "menu"
        
        # Draw current state
        screen.blit(menu_background_scaled, (0, 0))
        
        if current_state == "menu":
            menu_state.draw(screen)
        elif current_state == "game":
            game_loop()
            current_state = "menu"
            load_player_stats()
        elif current_state == "shop":
            coins = draw_shop(screen, temp_player, player_stats["coins"], player_stats)
            player_stats["coins"] = coins
            save_player_stats()
            
            if pg.key.get_pressed()[pg.K_TAB]:
                current_state = "menu"
        elif current_state == "settings":
            menu_state.draw_settings(screen)
        elif current_state == "quit":
            running = False
        
        pg.display.flip()
        clock.tick(FPS)
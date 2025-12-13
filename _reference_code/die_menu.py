from window_settings import *
from settings import *

def _show_game_over_screen(player, coins):
    """Отображение экрана поражения с опциями рестарта/выхода"""
    overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    game_over_text = font.render("ИГРА ОКОНЧЕНА", True, (255, 0, 0))
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//3))
    
    restart_text = font.render("Нажмите R для рестарта", True, (255, 255, 255))
    menu_text = font.render("Нажмите V для выхода в меню", True, (255, 255, 255))
    quit_text = font.render("Нажмите Q для выхода", True, (255, 255, 255))
    
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2))
    screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 100))
    
    pg.display.flip()
    
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit"
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:  # Рестарт
                    # Сохраняем ВСЕ параметры перед рестартом
                    player_stats.update({
                        "coins": coins,
                        "grenades": player.grenades,
                        "equipment": player.equipment,
                        "has_pistol": player.has_pistol,
                        "has_rifle": player.has_rifle,
                        "has_shotgun": player.has_shotgun,
                        'has_assault': player.has_assault
                    })
                    save_player_stats()
                    return "restart"
                
                elif event.key == pg.K_v:  # Меню
                    # Сохраняем ВСЕ параметры перед выходом в меню
                    player_stats.update({
                        "coins": coins,
                        "grenades": player.grenades,
                        "equipment": player.equipment,
                        "has_pistol": player.has_pistol,
                        "has_rifle": player.has_rifle,
                        "has_shotgun": player.has_shotgun,
                        'has_assault': player.has_assault
                    })
                    save_player_stats()
                    return "menu"
                
                elif event.key == pg.K_q:  # Выход
                    # Сохраняем ВСЕ параметры перед выходом
                    player_stats.update({
                        "coins": coins,
                        "grenades": player.grenades,
                        "equipment": player.equipment,
                        "has_pistol": player.has_pistol,
                        "has_rifle": player.has_rifle,
                        "has_shotgun": player.has_shotgun,
                        'has_assault': player.has_assault
                    })
                    save_player_stats()
                    # Выход из игры - возвращаем специальный код
                    return "quit_game"
        
        clock.tick(FPS)
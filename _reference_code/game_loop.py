import pygame as pg
import sys

def main():
    """Главная функция игры"""
    # Инициализация Pygame
    pg.init()
    
    try:
        # Импорты после инициализации Pygame
        from window_settings import screen, clock, FPS
        from menu import main_menu
        
        print("Запуск игры...")
        
        # Запуск главного меню
        main_menu()
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Завершение игры...")
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    main()
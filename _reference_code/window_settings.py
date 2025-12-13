import pygame as pg  

# Начальные настройки экрана
INITIAL_WIDTH = 822
INITIAL_HEIGHT = 562
SCREEN_WIDTH = INITIAL_WIDTH
SCREEN_HEIGHT = INITIAL_HEIGHT
FULLSCREEN = False

# Инициализация экрана
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Future Game")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Цвета кнопок
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 200)
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (100, 100, 100)
GOLD = (255, 215, 0)

# Частота кадров
clock = pg.time.Clock()
FPS = 60

def toggle_fullscreen():
    """Переключает между оконным и полноэкранным режимом"""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN
    
    if not FULLSCREEN:
        # Переход в полноэкранный режим
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
        FULLSCREEN = True
        print(f"Полноэкранный режим: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    else:
        # Возврат в оконный режим
        screen = pg.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT))
        SCREEN_WIDTH, SCREEN_HEIGHT = INITIAL_WIDTH, INITIAL_HEIGHT
        FULLSCREEN = False
        print(f"Оконный режим: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    
    # Возвращаем обновленные размеры
    return SCREEN_WIDTH, SCREEN_HEIGHT

def get_screen_center():
    """Возвращает центр экрана"""
    return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
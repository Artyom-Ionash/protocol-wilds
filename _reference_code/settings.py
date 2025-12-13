import pygame as pg
from window_settings import *
import json

# Инициализация звуковой системы
pg.mixer.init()

# Шрифты
font = pg.font.SysFont('arial', 24)
small_font = pg.font.SysFont('arial', 18)
tiny_font = pg.font.SysFont('arial', 14)

# ==================== ЗАГРУЗКА ЗВУКОВ ====================
shoot_player_sound   = pg.mixer.Sound("sounds/shoot_sounds/shoot_player.mp3")
shoot_enemy_sound    = pg.mixer.Sound("sounds/shoot_sounds/shoot_enemy.mp3")
background_music     = pg.mixer.Sound("sounds/other_sounds/background.mp3")
siren_sound          = pg.mixer.Sound("sounds/other_sounds/siren.mp3")
missile_sound        = pg.mixer.Sound("sounds/shoot_sounds/missile.mp3")
danger_missile_sound = pg.mixer.Sound("sounds/other_sounds/danger_missile.mp3")
explosion_sound      = pg.mixer.Sound("sounds/shoot_sounds/explosion.mp3")
buy_sound            = pg.mixer.Sound("sounds/other_sounds/buy_sound.mp3")
equip_sound          = pg.mixer.Sound("sounds/other_sounds/equip_sound.mp3")

# ==================== ЗАГРУЗКА СПРАЙТОВ ====================
_sprite_cache = {}

def load_sprite(path, scale=None):
    """Загружает спрайт с кэшированием"""
    cache_key = f"{path}_{scale}" if scale else path
    
    if cache_key not in _sprite_cache:
        sprite = pg.image.load(path).convert_alpha()
        if scale:
            sprite = pg.transform.scale(sprite, scale)
        _sprite_cache[cache_key] = sprite
    
    return _sprite_cache[cache_key]

def load_animation_frames(paths, scale=None):
    """Загружает анимацию с кэшированием"""
    frames = []
    for path in paths:
        frames.append(load_sprite(path, scale))
    return frames

# Спрайты игрока с разной экипировкой
player_sprites = {
    "basic": load_sprite("sprites/players/player_no_equip.png", (60, 45)),
    "pistol": load_sprite("sprites/players/player_pistol.png", (60, 45)),
    "rifle": load_sprite("sprites/players/player_machine_gun.png", (60, 45)),
    "shotgun": load_sprite("sprites/players/player_shotgun.png", (60, 45)),
    "assault": load_sprite("sprites/players/player_assault.png", (60, 45)),
    "grenade": load_sprite("sprites/for_player/grenade.png", (60, 60)),
}

# Фоновые изображения
background_sprite = pg.image.load("sprites/backgrounds/background_sprite.png")
menu_background = pg.image.load("sprites/backgrounds/menu_background.jpeg")
shop_background = pg.image.load("sprites/backgrounds/shop_background.png")

# Функция для обновления масштабированных фонов
def update_scaled_backgrounds():
    """Обновляет масштабированные фоновые изображения"""
    global background_sprite_scaled, menu_background_scaled, shop_background_scaled
    
    # Игровой фон всегда 1000x1000 (размер карты)
    background_sprite_scaled = pg.transform.scale(background_sprite, (1000, 1000))
    
    # Меню и магазин масштабируются под текущий размер экрана
    menu_background_scaled = pg.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    shop_background_scaled = pg.transform.scale(shop_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    print(f"Фоны обновлены. Размер экрана: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Инициализируем фоны при загрузке
update_scaled_backgrounds()

# Спрайты снарядов
bullet_sprite = pg.image.load("sprites/for_enemy/bullet.png")
boss_missile_sprite = pg.transform.scale(pg.image.load("sprites/for_enemy/missile.png"), (40, 40))
grenade_sprite = pg.transform.scale(pg.image.load("sprites/for_player/grenade.png"), (40, 40))

# Спрайты объектов
wall_sprite = pg.image.load("sprites/other/wall.png")
barrier_sprite = pg.transform.scale(pg.image.load("sprites/other/barrier.png"), (40, 40))
coin_sprite = pg.transform.scale(pg.image.load("sprites/other/coin_sprite.png"), (40, 40))

# Анимации роботов
robot_sprite_paths = {
    "up": ["sprites/robots/robot_up1.png", "sprites/robots/robot_up2.png", 
           "sprites/robots/robot_up1.png", "sprites/robots/robot_up3.png"],
    "down": ["sprites/robots/robot_down1.png", "sprites/robots/robot_down2.png",
             "sprites/robots/robot_down1.png", "sprites/robots/robot_down3.png"],
    "left": ["sprites/robots/robot_left1.png", "sprites/robots/robot_left2.png",
             "sprites/robots/robot_left1.png", "sprites/robots/robot_left3.png"],
    "right": ["sprites/robots/robot_right1.png", "sprites/robots/robot_right2.png",
              "sprites/robots/robot_right1.png", "sprites/robots/robot_right3.png"]
}
robot_sprites = {}
for direction, paths in robot_sprite_paths.items():
    robot_sprites[direction] = load_animation_frames(paths, (40, 40))

# Анимации босса
boss_sprites = {
    "up": [
        pg.image.load("sprites/bosses/boss_up1.png"),
        pg.image.load("sprites/bosses/boss_up2.png"),
        pg.image.load("sprites/bosses/boss_up3.png")
    ],
    "down": [
        pg.image.load("sprites/bosses/boss_down1.png"),
        pg.image.load("sprites/bosses/boss_down2.png"),
        pg.image.load("sprites/bosses/boss_down3.png")
    ],
    "left": [
        pg.image.load("sprites/bosses/boss_left1.png"),
        pg.image.load("sprites/bosses/boss_left2.png"),
        pg.image.load("sprites/bosses/boss_left3.png")
    ],
    "right": [
        pg.image.load("sprites/bosses/boss_right1.png"),
        pg.image.load("sprites/bosses/boss_right2.png"),
        pg.image.load("sprites/bosses/boss_right3.png")
    ]
}

# Глобальные игровые данные
player_stats = {
    "coins": 25,
    "equipment": "basic",
    "has_pistol": False,
    "has_rifle": False,
    "has_shotgun": False,
    "has_assault": False,
    "grenades": 0
}

def save_player_stats():
    """Сохраняет текущие данные игрока в файл"""
    try:
        with open('player_stats.json', 'w') as f:
            json.dump({
                "coins": player_stats["coins"],
                "equipment": player_stats["equipment"],
                "has_pistol": player_stats.get("has_pistol", False),
                "has_rifle": player_stats.get("has_rifle", False),
                "has_shotgun": player_stats.get("has_shotgun", False),
                "grenades": player_stats["grenades"]
            }, f, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def load_player_stats():
    """Загружает статистику игрока из файла"""
    try:
        with open('player_stats.json', 'r') as f:
            return json.load(f)
    except:
        return player_stats  # Возвращаем значения по умолчанию
from settings import *
# Класс стены
map_width = 1000
map_height = 1000
class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 100
        self.height = 100
        self.rect = pg.Rect(x, y, self.width, self.height)
        self.sprite = pg.transform.scale(wall_sprite, (self.width, self.height)) if wall_sprite else None
        
        # Если нет спрайта, создаем простую поверхность
        if not self.sprite:
            self.surface = pg.Surface((self.width, self.height))
            self.surface.fill((100, 100, 100))  # Серый цвет

    def draw(self, camera_x, camera_y):
        if self.sprite:
            screen.blit(self.sprite, (self.x - camera_x, self.y - camera_y))
        else:
            screen.blit(self.surface, (self.x - camera_x, self.y - camera_y))
# Генерация карты с порталом        
def generate_walls():
    walls = []
    cell_size = 100  # Размер ячейки

    # Создаем стены по границам карты
    for i in range(0, map_width, cell_size):
        walls.append(Wall(i, map_height - cell_size))  # Нижняя граница
    for j in range(0, map_height, cell_size):
        walls.append(Wall(0, j))  # Левая граница
        walls.append(Wall(map_width - cell_size, j))  # Правая граница
    return walls
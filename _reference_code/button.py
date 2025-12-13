from settings import *
# Класс кнопки-спрайта

class Button:
    def __init__(self, x, y, width, height, text, action, action_type="state_change"):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.action_type = action_type
        self.is_hovered = False
    
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False
    
    def draw(self, surface):
        color = (100, 100, 100) if not self.is_hovered else (150, 150, 150)
        pg.draw.rect(surface, color, self.rect)
        pg.draw.rect(surface, (0, 0, 0), self.rect, 2)
        
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
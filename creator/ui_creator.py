import pygame

ACCENT   = (100, 180, 255)
TEXT_COL = (220, 220, 220)
PANEL_BG = (30, 30, 45)

class Slider:
    def __init__(self, x, y, w, label, min_val, max_val, value, key):
        self.rect   = pygame.Rect(x, y, w, 8)
        self.label  = label
        self.min    = min_val
        self.max    = max_val
        self.value  = value
        self.key    = key
        self.active = False

    def draw(self, surf, font):
        surf.blit(
            font.render(f"{self.label}: {self.value:.2f}", True, TEXT_COL),
            (self.rect.x, self.rect.y-16))
        pygame.draw.rect(surf, (50,50,70), self.rect, border_radius=4)
        fw = int((self.value-self.min)/(self.max-self.min)*self.rect.w)
        pygame.draw.rect(surf, ACCENT,
            (self.rect.x, self.rect.y, fw, self.rect.h), border_radius=4)
        pygame.draw.circle(surf, ACCENT, (self.rect.x+fw, self.rect.y+4), 7)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            fw = int((self.value-self.min)/(self.max-self.min)*self.rect.w)
            if pygame.Rect(self.rect.x+fw-8, self.rect.y-4,
                           16, 16).collidepoint(event.pos):
                self.active = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.active = False
        if event.type == pygame.MOUSEMOTION and self.active:
            rel = (event.pos[0]-self.rect.x)/self.rect.w
            self.value = round(
                max(self.min, min(self.max,
                self.min+rel*(self.max-self.min))), 2)
            return True
        return False

class Button:
    def __init__(self, x, y, w, h, label):
        self.rect  = pygame.Rect(x, y, w, h)
        self.label = label

    def draw(self, surf, font):
        pygame.draw.rect(surf, PANEL_BG, self.rect, border_radius=6)
        pygame.draw.rect(surf, ACCENT,   self.rect, 1, border_radius=6)
        txt = font.render(self.label, True, ACCENT)
        surf.blit(txt, (
            self.rect.x+(self.rect.w-txt.get_width())//2,
            self.rect.y+(self.rect.h-txt.get_height())//2))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                self.rect.collidepoint(event.pos))

class ColorPicker:
    PALETTES = {
        "tono_piel":     [[255,220,185],[240,195,145],[200,150,110],
                          [160,110,80], [120,75,55],  [80,45,30]],
        "color_cabello": [[255,220,100],[180,100,30], [60,30,10],
                          [30,30,30],   [200,200,200],[180,60,60],
                          [60,100,200], [100,180,100]],
        "color_ropa":    [[74,124,63],  [60,80,160],  [160,60,60],
                          [160,130,60], [80,60,120],  [40,40,40],
                          [200,200,200],[160,100,60]],
    }

    def __init__(self, x, y, label, key):
        self.x = x; self.y = y
        self.label = label; self.key = key
        self.index  = 0
        self.colors = self.PALETTES[key]
        self.sw     = 18

    def draw(self, surf, font):
        surf.blit(font.render(self.label, True, TEXT_COL), (self.x, self.y-16))
        for i, c in enumerate(self.colors):
            r = pygame.Rect(self.x+i*(self.sw+2), self.y, self.sw, self.sw)
            pygame.draw.rect(surf, c, r, border_radius=3)
            if i == self.index:
                pygame.draw.rect(surf, ACCENT, r, 2, border_radius=3)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(self.colors)):
                r = pygame.Rect(self.x+i*(self.sw+2), self.y, self.sw, self.sw)
                if r.collidepoint(event.pos):
                    self.index = i; return True
        return False

    def get_color(self):
        return self.colors[self.index]
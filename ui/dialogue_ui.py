import pygame

class DialogueUI:
    def __init__(self, width, height):

        self.WIDTH = width
        self.HEIGHT = height

        # Cargar imagen
        self.ui_box = pygame.image.load(
            r"C:\Users\Rolando\OneDrive\Escritorio\Python\Hierarchical-NPC\assets\menu de interaccion\menu_npc_interaccion2.png"
        ).convert_alpha()

        self.ui_box = pygame.transform.scale(self.ui_box, (600, 400))

        # Rect (posición)
        self.ui_rect = self.ui_box.get_rect()
        self.ui_rect.midbottom = (self.WIDTH // 2, self.HEIGHT - 20)

        # Fuente
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen):

        # Dibujar fondo UI
        screen.blit(self.ui_box, self.ui_rect)

        # Texto principal
        dialogue = self.font.render("Hola, viajero...", True, (0, 0, 0))
        screen.blit(dialogue, (self.ui_rect.x + 300, self.ui_rect.y + 80))

        # Opciones
        text1 = self.font.render("1: Amistoso", True, (0, 0, 0))
        text2 = self.font.render("2: Hostil", True, (0, 0, 0))
        text3 = self.font.render("3: Conversar", True, (0, 0, 0))

        screen.blit(text1, (self.ui_rect.x + 80, self.ui_rect.y + 300))
        screen.blit(text2, (self.ui_rect.x + 260, self.ui_rect.y + 300))
        screen.blit(text3, (self.ui_rect.x + 440, self.ui_rect.y + 300))
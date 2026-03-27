import pygame
import sys

from ui.dialogue_ui import DialogueUI

# ==============================
# INICIALIZACIÓN
# ==============================

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hierarchical NPC - Demo")

clock = pygame.time.Clock()

# ==============================
# CONFIGURACIÓN DEL MUNDO
# ==============================

TILE_SIZE = 32

# ==============================
# CARGA DE ASSETS
# ==============================

ground = pygame.image.load(
    r"C:\Users\Rolando\OneDrive\Escritorio\Python\Hierarchical-NPC\assets\Tiles\Grass_Middle.png"
).convert_alpha()

ground = pygame.transform.scale(ground, (TILE_SIZE, TILE_SIZE))

# ==============================
# SPRITESHEET (PERSONAJES)
# ==============================

spritesheet = pygame.image.load(
    r"C:\Users\Rolando\OneDrive\Escritorio\Python\Hierarchical-NPC\assets\Player\Player.png"
).convert_alpha()

SPRITE_SIZE = 32

player_img = spritesheet.subsurface((0, 0, SPRITE_SIZE, SPRITE_SIZE))
npc_img = spritesheet.subsurface((32, 0, SPRITE_SIZE, SPRITE_SIZE))

player_img = pygame.transform.scale(player_img, (64, 64))
npc_img = pygame.transform.scale(npc_img, (64, 64))

# ==============================
# ENTIDADES
# ==============================

player_x, player_y = 100, 100
player_speed = 2

npc_x, npc_y = 400, 300

# ==============================
# UI
# ==============================

ui = DialogueUI(WIDTH, HEIGHT)

# ==============================
# ESTADO DEL JUEGO
# ==============================

interaction_mode = False

# ==============================
# LOOP PRINCIPAL
# ==============================

running = True
while running:

    # ==========================
    # 1. LÓGICA (ANTES DE EVENTOS)
    # ==========================

    dx = player_x - npc_x
    dy = player_y - npc_y
    distance = (dx**2 + dy**2) ** 0.5

    INTERACTION_DISTANCE = 80
    near_npc = distance < INTERACTION_DISTANCE

    # ==========================
    # 2. EVENTOS
    # ==========================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # Abrir interacción
            if event.key == pygame.K_e and near_npc:
                interaction_mode = True

            # Opciones del menú
            if interaction_mode:

                if event.key == pygame.K_1:
                    print({"category": "amistoso", "action": "conocer_mejor", "target": "Julius"})
                    interaction_mode = False

                if event.key == pygame.K_2:
                    print({"category": "hostil", "action": "provocar", "target": "Julius"})
                    interaction_mode = False

                if event.key == pygame.K_3:
                    print({"category": "conversar", "action": "hablar", "target": "Julius"})
                    interaction_mode = False

    # ==========================
    # 3. INPUT CONTINUO (MOVIMIENTO)
    # ==========================

    keys = pygame.key.get_pressed()

    if not interaction_mode:
        if keys[pygame.K_w]:
            player_y -= player_speed
        if keys[pygame.K_s]:
            player_y += player_speed
        if keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_d]:
            player_x += player_speed

    # ==========================
    # 4. RENDER
    # ==========================

    # Fondo (tileado)
    for x in range(0, WIDTH, TILE_SIZE):
        for y in range(0, HEIGHT, TILE_SIZE):
            screen.blit(ground, (x, y))

    # NPC
    screen.blit(npc_img, (npc_x, npc_y))

    # Player
    screen.blit(player_img, (player_x, player_y))

    # Texto de proximidad
    if near_npc and not interaction_mode:
        font = pygame.font.SysFont(None, 24)
        text = font.render("Presiona E para interactuar", True, (255, 255, 255))
        screen.blit(text, (npc_x - 40, npc_y - 20))

    # UI (separada correctamente)
    if interaction_mode:
        ui.draw(screen)

    pygame.display.flip()
    clock.tick(60)

# ==============================
# CIERRE
# ==============================

pygame.quit()
sys.exit()
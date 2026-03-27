import pygame
import json
from PIL import Image
from character import DEFAULT_CHAR
from render import render_to_surface, CANVAS_SIZE
from ui_creator import Slider, Button, ColorPicker

WINDOW_W, WINDOW_H = 900, 520
PREVIEW_SIZE = 300
BG       = (20, 20, 30)
PANEL_BG = (30, 30, 45)
ACCENT   = (100, 180, 255)
TEXT_COL = (220, 220, 220)
DATA_COL = (140, 220, 140)

def draw_data_panel(screen, font, char, x, y):
    h = char["altura"]
    c = char["complexion"]
    H = int(56 * h)

    lines = [
        "── GEOMETRÍA INTERNA ──",
        f"  H (total)  : {H} px",
        f"  cab_h      : {int(H*0.165)} px",
        f"  cuello_h   : {int(H*0.045)} px",
        f"  torso_h    : {int(H*0.285)} px",
        f"  cadera_h   : {int(H*0.085)} px",
        f"  pierna_h   : {int(H*0.360)} px",
        f"  pie_h      : {int(H*0.060)} px",
        "",
        "── PARÁMETROS ──",
        f"  altura     : {char['altura']:.2f}",
        f"  complexion : {char['complexion']:.2f}",
        "",
        "── COLOR ──",
        f"  piel  : {char['tono_piel']}",
        f"  ropa  : {char['color_ropa']}",
    ]
    for i, line in enumerate(lines):
        col = ACCENT if "──" in line else DATA_COL
        screen.blit(font.render(line, True, col), (x, y + i*17))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("NPC Character Creator — SDF v0.3")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont("monospace", 11)

    char  = dict(DEFAULT_CHAR)
    dirty = True
    preview_surf = None

    sliders = [
        Slider(30,  60, 180, "Altura",     0.4, 1.2, char["altura"],     "altura"),
        Slider(30, 110, 180, "Complexión", 0.2, 1.0, char["complexion"], "complexion"),
    ]
    pickers = [
        ColorPicker(30, 200, "Piel",    "tono_piel"),
        ColorPicker(30, 260, "Cabello", "color_cabello"),
        ColorPicker(30, 320, "Ropa",    "color_ropa"),
    ]
    btn_export = Button(30, 420, 100, 28, "Export PNG")
    btn_save   = Button(145, 420, 100, 28, "Save JSON")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            for s in sliders:
                if s.handle_event(event):
                    char[s.key] = s.value
                    dirty = True
            for p in pickers:
                if p.handle_event(event):
                    char[p.key] = p.get_color()
                    dirty = True

            if btn_export.clicked(event):
                raw  = render_to_surface(char)
                data = pygame.image.tostring(raw, "RGB")
                img  = Image.frombytes("RGB", (CANVAS_SIZE, CANVAS_SIZE), data)
                img.save("npc_export.png")
                print("Exportado: npc_export.png")

            if btn_save.clicked(event):
                with open("npc_data.json", "w") as f:
                    json.dump(char, f, indent=2)
                print("Guardado: npc_data.json")

        if dirty:
            preview_surf = pygame.transform.scale(
                render_to_surface(char), (PREVIEW_SIZE, PREVIEW_SIZE))
            dirty = False

        # ── Draw ─────────────────────────────────────────────
        screen.fill(BG)

        # Panel izquierdo — controles
        pygame.draw.rect(screen, PANEL_BG, (0, 0, 260, WINDOW_H))
        screen.blit(font.render("CONTROLES", True, ACCENT), (30, 20))
        for s in sliders: s.draw(screen, font)
        for p in pickers: p.draw(screen, font)
        btn_export.draw(screen, font)
        btn_save.draw(screen, font)

        # Centro — preview
        if preview_surf:
            px = 260 + (WINDOW_W - 260 - 620) // 2 + 20
            py = (WINDOW_H - PREVIEW_SIZE) // 2
            for gy in range(0, PREVIEW_SIZE, 16):
                for gx in range(0, PREVIEW_SIZE, 16):
                    col = (45,45,55) if (gx+gy)%32==0 else (35,35,45)
                    pygame.draw.rect(screen, col, (px+gx, py+gy, 16, 16))
            screen.blit(preview_surf, (px, py))
            pygame.draw.rect(screen, ACCENT,
                (px-1, py-1, PREVIEW_SIZE+2, PREVIEW_SIZE+2), 1)

        # Panel derecho — datos
        pygame.draw.rect(screen, PANEL_BG, (640, 0, 260, WINDOW_H))
        draw_data_panel(screen, font, char, 650, 20)

        screen.blit(
            font.render("NPC CHARACTER CREATOR — SDF v0.3", True, ACCENT),
            (270, 15))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
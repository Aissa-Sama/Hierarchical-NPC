# main_creator.py — Interfaz gráfica para crear NPCs con SDF
import pygame
import json
from PIL import Image
from character import DEFAULT_CHAR
from render  import (render_to_surface, export_sprite_sheet,
                       set_resolucion, RESOLUCIONES, CANVAS_SIZE)
from ui_creator import Slider, Button, ColorPicker

WINDOW_W, WINDOW_H = 950, 560
PREVIEW_SIZE = 320
BG       = (20, 20, 30)
PANEL_BG = (30, 30, 45)
ACCENT   = (100, 180, 255)
TEXT_COL = (220, 220, 220)
DATA_COL = (140, 220, 140)

def draw_data_panel(screen, font, char, angle_y, pose, res, x, y):
    h = char["altura"]
    H = int(res * 0.90 * h)
    lines = [
        "── GEOMETRÍA ──",
        f"  H (total)  : {H} px",
        f"  resolución : {res}x{res}",
        "",
        "── CÁMARA ──",
        f"  rotación Y : {angle_y:.1f}°",
        f"  pose       : {pose}",
        "",
        "── PARÁMETROS ──",
        f"  altura     : {char['altura']:.2f}",
        f"  complexion : {char['complexion']:.2f}",
        "",
        "── COLOR ──",
        f"  piel  : {char['tono_piel']}",
        f"  ropa  : {char['color_ropa']}",
        "",
        "── REGIONES ──",
        "  cabeza:      0.00-0.13",
        "  cuello:      0.13-0.17",
        "  hombros:     0.17-0.22",
        "  pecho:       0.22-0.32",
        "  cintura:     0.32-0.40",
        "  cadera:      0.40-0.50",
        "  piernas:     0.50-0.93",
        "  pies:        0.93-1.00",
    ]
    for i, line in enumerate(lines):
        col = ACCENT if "──" in line else DATA_COL
        screen.blit(font.render(line, True, col), (x, y + i*16))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("NPC Character Creator — SDF v0.5")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont("monospace", 11)

    char    = dict(DEFAULT_CHAR)
    angle_y = 0.0
    pose    = "A"
    res_idx = 2   # default 128x128
    res     = RESOLUCIONES[res_idx]
    set_resolucion(res)

    dirty        = True
    preview_surf = None

    sliders = [
        Slider(30,  60, 180, "Altura",     0.4, 1.2, char["altura"],     "altura"),
        Slider(30, 110, 180, "Complexión", 0.2, 1.0, char["complexion"], "complexion"),
        Slider(30, 160, 180, "Rotación Y", 0.0, 360.0, 0.0,             "rotacion_y"),
    ]
    pickers = [
        ColorPicker(30, 240, "Piel",    "tono_piel"),
        ColorPicker(30, 295, "Cabello", "color_cabello"),
        ColorPicker(30, 350, "Ropa",    "color_ropa"),
    ]

    btn_export      = Button(30,  410, 100, 26, "Export PNG")
    btn_save        = Button(145, 410, 100, 26, "Save JSON")
    btn_pose        = Button(30,  443, 100, 26, f"Pose: {pose}")
    btn_spritesheet = Button(145, 443, 100, 26, "Sprite Sheet")
    btn_res         = Button(30,  476, 215, 26, f"Res: {res}x{res}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            for s in sliders:
                if s.handle_event(event):
                    if s.key == "rotacion_y":
                        angle_y = s.value
                    else:
                        char[s.key] = s.value
                    dirty = True

            for p in pickers:
                if p.handle_event(event):
                    char[p.key] = p.get_color()
                    dirty = True

            if btn_export.clicked(event):
                raw  = render_to_surface(char, angle_y, pose)
                data = pygame.image.tostring(raw, "RGB")
                img  = Image.frombytes("RGB", (res, res), data)
                img.save(f"npc_export_{res}x{res}.png")
                print(f"Exportado: npc_export_{res}x{res}.png")

            if btn_save.clicked(event):
                with open("npc_data.json", "w") as f:
                    json.dump(char, f, indent=2)
                print("Guardado: npc_data.json")

            if btn_pose.clicked(event):
                pose = "T" if pose == "A" else "A"
                btn_pose.label = f"Pose: {pose}"
                dirty = True

            if btn_spritesheet.clicked(event):
                print(f"Generando sprite sheet {res}x{res} × 8 ángulos...")
                sheet = export_sprite_sheet(char, pose)
                sheet.save(f"npc_spritesheet_{res}.png")
                print(f"Exportado: npc_spritesheet_{res}.png")

            if btn_res.clicked(event):
                res_idx = (res_idx + 1) % len(RESOLUCIONES)
                res = RESOLUCIONES[res_idx]
                set_resolucion(res)
                btn_res.label = f"Res: {res}x{res}"
                dirty = True
                print(f"Resolución: {res}x{res}")

        if dirty:
            raw = render_to_surface(char, angle_y, pose)
            preview_surf = pygame.transform.scale(
                raw, (PREVIEW_SIZE, PREVIEW_SIZE))
            dirty = False

        # ── Draw ─────────────────────────────────────────────
        screen.fill(BG)
        pygame.draw.rect(screen, PANEL_BG, (0, 0, 260, WINDOW_H))
        screen.blit(font.render("CONTROLES", True, ACCENT), (30, 20))

        for s in sliders: s.draw(screen, font)
        for p in pickers: p.draw(screen, font)
        btn_export.draw(screen, font)
        btn_save.draw(screen, font)
        btn_pose.draw(screen, font)
        btn_spritesheet.draw(screen, font)
        btn_res.draw(screen, font)

        if preview_surf:
            px = 260 + (WINDOW_W - 260 - 670) // 2 + 20
            py = (WINDOW_H - PREVIEW_SIZE) // 2
            for gy in range(0, PREVIEW_SIZE, 16):
                for gx in range(0, PREVIEW_SIZE, 16):
                    col = (45,45,55) if (gx+gy)%32==0 else (35,35,45)
                    pygame.draw.rect(screen, col, (px+gx, py+gy, 16, 16))
            screen.blit(preview_surf, (px, py))
            pygame.draw.rect(screen, ACCENT,
                (px-1, py-1, PREVIEW_SIZE+2, PREVIEW_SIZE+2), 1)

        pygame.draw.rect(screen, PANEL_BG, (650, 0, 300, WINDOW_H))
        draw_data_panel(screen, font, char, angle_y, pose, res, 660, 15)

        screen.blit(
            font.render("NPC CHARACTER CREATOR — SDF v0.5", True, ACCENT),
            (270, 15))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

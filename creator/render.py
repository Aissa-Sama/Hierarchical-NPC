# render.py — Renderer volumétrico con proporciones anatómicas por consenso

import numpy as np
import pygame
from character import TABLA_ANATOMICA

# Resoluciones disponibles
RESOLUCIONES = [64, 96, 128, 192, 256]
VOX_RES      = 128   # default
CANVAS_SIZE  = 128

def set_resolucion(res):
    global VOX_RES, CANVAS_SIZE
    VOX_RES = res
    CANVAS_SIZE = res

def elipse_mask(size, cx, cz, rx, rz):
    if rx <= 0 or rz <= 0:
        return np.zeros((size, size), dtype=bool)
    x  = np.arange(size, dtype=np.float32)
    z  = np.arange(size, dtype=np.float32)
    xx, zz = np.meshgrid(x, z, indexing='ij')
    return ((xx-cx)/rx)**2 + ((zz-cz)/rz)**2 <= 1.0

def circulo_mask(size, cx, cz, r):
    return elipse_mask(size, cx, cz, r, r)

def lerp(a, b, t):
    return a + (b-a) * np.clip(t, 0, 1)

def build_volume(char, pose="A"):
    res = VOX_RES
    h   = char["altura"]
    c   = char["complexion"]
    mid = res / 2.0

    # Altura total en voxels
    H  = int(res * 0.90 * h)
    y0 = res - 1 - H   # top del personaje

    volume = np.zeros((res, res, res), dtype=bool)

    # Complejión modifica rx levemente
    c_mod = 1.0 + (c - 0.5) * 0.3

    def region_slices(nombre):
        """Genera slices para una región anatómica."""
        y_s, y_e, rx_max, rx_min, rz_max = TABLA_ANATOMICA[nombre]
        y_abs_s = y0 + int(H * y_s)
        y_abs_e = y0 + int(H * y_e)
        return y_abs_s, y_abs_e, rx_max, rx_min, rz_max

    # ── Torso y cabeza — slices centrales ────────────────────
    regiones_centrales = [
        "cabeza", "cuello", "hombros", "pecho",
        "cintura", "cadera"
    ]

    for nombre in regiones_centrales:
        y_s, y_e, rx_max, rx_min, rz_max = region_slices(nombre)
        for y in range(y_s, min(y_e, res)):
            if y < 0 or y >= res:
                continue
            t  = (y - y_s) / max(y_e - y_s, 1)
            rx = lerp(rx_max, rx_min, t) * H * c_mod
            rz = rz_max * H * (1.0 + (c - 0.5) * 0.15)
            if rx < 0.5 or rz < 0.5:
                continue
            volume[:, y, :] |= elipse_mask(res, mid, mid, rx, rz)

    # ── Piernas — dos columnas simétricas ─────────────────────
    regiones_pierna = ["muslo", "rodilla", "pantorrilla", "tobillo"]

    # Offset lateral de piernas — se deriva de la cadera
    _, _, cad_rx_max, _, _ = TABLA_ANATOMICA["cadera"]
    pier_off_top = cad_rx_max * H * 0.55
    pier_off_bot = pier_off_top * 0.70

    for nombre in regiones_pierna:
        y_s, y_e, rx_max, rx_min, rz_max = region_slices(nombre)
        _, _, _, _, cad_data = TABLA_ANATOMICA["cadera"]

        # Progreso global de la pierna (0=inicio muslo, 1=fin tobillo)
        y_muslo_s = y0 + int(H * TABLA_ANATOMICA["muslo"][0])
        y_tobillo_e = y0 + int(H * TABLA_ANATOMICA["tobillo"][1])
        pierna_total = max(y_tobillo_e - y_muslo_s, 1)

        for y in range(y_s, min(y_e, res)):
            if y < 0 or y >= res:
                continue
            t_seg  = (y - y_s) / max(y_e - y_s, 1)
            t_glob = (y - y_muslo_s) / pierna_total

            # A-pose: piernas en V leve
            if pose == "A":
                pier_off = lerp(pier_off_top, pier_off_bot, t_glob)
            else:
                pier_off = pier_off_top * 0.85

            rx = lerp(rx_max, rx_min, t_seg) * H * c_mod
            rz = rz_max * H * (1.0 + (c - 0.5) * 0.15)
            if rx < 0.5 or rz < 0.5:
                continue

            mask  = elipse_mask(res, mid - pier_off, mid, rx, rz)
            mask |= elipse_mask(res, mid + pier_off, mid, rx, rz)
            volume[:, y, :] |= mask

    # ── Pies ──────────────────────────────────────────────────
    y_s, y_e, rx_max, rx_min, rz_max = region_slices("pie")
    for y in range(y_s, min(y_e, res)):
        if y < 0 or y >= res:
            continue
        t       = (y - y_s) / max(y_e - y_s, 1)
        rx      = lerp(rx_max, rx_min, t) * H * c_mod
        rz      = rz_max * H * 1.4   # pies más profundos (hacia adelante)
        pie_off = pier_off_bot
        cz_pie  = mid + rz * 0.25
        if rx < 0.5 or rz < 0.5:
            continue
        mask  = elipse_mask(res, mid - pie_off, cz_pie, rx, rz)
        mask |= elipse_mask(res, mid + pie_off, cz_pie, rx, rz)
        volume[:, y, :] |= mask

    # ── Brazos — A-pose o T-pose ──────────────────────────────
    # Brazos arrancan en hombros y terminan al nivel de la cadera
    _, _, hom_rx_max, _, _ = TABLA_ANATOMICA["hombros"]
    y_hom_s = y0 + int(H * TABLA_ANATOMICA["hombros"][0])
    y_cad_e = y0 + int(H * TABLA_ANATOMICA["cadera"][1])
    brazo_h = y_cad_e - y_hom_s

    # Radios del brazo: grueso arriba (deltoides), delgado abajo (muñeca)
    brazo_r_top = hom_rx_max * H * 0.32 * c_mod
    brazo_r_bot = brazo_r_top * 0.55

    # Posición base X del brazo (en el hombro)
    brazo_x_base = hom_rx_max * H * c_mod

    for y in range(y_hom_s, min(y_cad_e, res)):
        if y < 0 or y >= res:
            continue
        t = (y - y_hom_s) / max(brazo_h, 1)
        r = lerp(brazo_r_top, brazo_r_bot, t)

        if pose == "T":
            # Brazos horizontales — offset X crece linealmente
            bx = brazo_x_base + t * brazo_x_base * 0.8
            bz = 0.0
        else:
            # A-pose — brazos bajan con inclinación ~30°
            bx = brazo_x_base + t * brazo_x_base * 0.25
            bz = t * r * 0.5   # leve hacia adelante

        if r < 0.5:
            continue
        mask  = circulo_mask(res, mid - bx, mid + bz, r)
        mask |= circulo_mask(res, mid + bx, mid + bz, r)
        volume[:, y, :] |= mask

    return volume

def rotation_matrix_y(angle_deg):
    a = np.radians(angle_deg)
    return np.array([
        [ np.cos(a), 0, np.sin(a)],
        [ 0,         1, 0        ],
        [-np.sin(a), 0, np.cos(a)],
    ], dtype=np.float32)

def project_rotated(volume, char, angle_y=0.0):
    res = VOX_RES
    h   = char["altura"]
    H   = int(res * 0.90 * h)
    y0  = res - 1 - H

    piel = np.array(char["tono_piel"],  dtype=np.float32)
    ropa = np.array(char["color_ropa"], dtype=np.float32)

    # Límites de color por región
    y_cab_end  = y0 + int(H * 0.17)
    y_tor_end  = y0 + int(H * 0.50)

    mid = res / 2.0
    R   = rotation_matrix_y(angle_y)

    img       = np.zeros((res, res, 4), dtype=np.uint8)
    depth     = np.full((res, res), -1, dtype=np.int32)
    color_buf = np.zeros((res, res, 3), dtype=np.float32)

    px_arr = np.arange(res, dtype=np.float32)
    py_arr = np.arange(res, dtype=np.float32)
    px_grid, py_grid = np.meshgrid(px_arr, py_arr, indexing='ij')

    steps   = res * 2
    z_start = -res

    for step in range(steps):
        z_cam = z_start + step
        cx = px_grid - mid
        cy = py_grid - mid
        cz = np.full_like(cx, z_cam)

        wx = R[0,0]*cx + R[0,2]*cz + mid
        wy = cy + mid
        wz = R[2,0]*cx + R[2,2]*cz + mid

        xi = np.round(wx).astype(np.int32)
        yi = np.round(wy).astype(np.int32)
        zi = np.round(wz).astype(np.int32)

        valid = (
            (xi >= 0) & (xi < res) &
            (yi >= 0) & (yi < res) &
            (zi >= 0) & (zi < res) &
            (depth == -1)
        )

        xi_c = np.clip(xi, 0, res-1)
        yi_c = np.clip(yi, 0, res-1)
        zi_c = np.clip(zi, 0, res-1)
        occupied = volume[xi_c, yi_c, zi_c]

        hit_mask = valid & occupied
        depth[hit_mask] = step

        y_world = wy[hit_mask].astype(int)
        colors  = np.where(
            (y_world < y_cab_end)[:, None], piel,
            np.where(
            (y_world < y_tor_end)[:, None], ropa,
            piel))
        color_buf[hit_mask] = colors

    hit = depth >= 0

    shade = np.ones((res, res), dtype=np.float32)
    if hit.any():
        d  = depth.astype(np.float32)
        gx = np.zeros_like(d)
        gy = np.zeros_like(d)
        gx[1:-1, :] = (d[2:,  :] - d[:-2, :]) * 0.5
        gy[:, 1:-1] = (d[:,  2:] - d[:, :-2]) * 0.5

        lx, ly, lz = -0.4, -0.6, 1.0
        ln = np.sqrt(lx**2+ly**2+lz**2)
        lx /= ln; ly /= ln; lz /= ln

        nz  = np.ones_like(d) * 0.6
        nx  = -gx * 0.35
        ny  = -gy * 0.35
        nln = np.sqrt(nx**2+ny**2+nz**2) + 1e-8
        nx /= nln; ny /= nln; nz /= nln

        diffuse = np.clip(nx*lx + ny*ly + nz*lz, 0, 1)
        ao      = np.clip(depth.astype(np.float32) / (res*2), 0, 1)
        shade   = np.clip(0.25 + 0.55*diffuse + 0.20*ao, 0, 1)

    for xi in range(res):
        for yi in range(res):
            if not hit[xi, yi]:
                continue
            s = shade[xi, yi]
            img[yi, xi, :3] = np.clip(color_buf[xi, yi] * s, 0, 255).astype(np.uint8)
            img[yi, xi,  3] = 255

    return img

def render_to_surface(char, angle_y=0.0, pose="A"):
    vol  = build_volume(char, pose)
    img  = project_rotated(vol, char, angle_y)
    surf = pygame.surfarray.make_surface(img[:, :, :3].swapaxes(0, 1))
    surf.set_colorkey((0, 0, 0))
    return surf

def export_sprite_sheet(char, pose="A"):
    from PIL import Image as PILImage
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    res    = VOX_RES
    vol    = build_volume(char, pose)
    frames = []

    for angle in angles:
        img_arr = project_rotated(vol, char, angle)
        pil_img = PILImage.frombytes("RGBA", (res, res), img_arr.tobytes())
        frames.append(pil_img)

    sheet = PILImage.new("RGBA", (res * 8, res), (0,0,0,0))
    for i, frame in enumerate(frames):
        sheet.paste(frame, (i * res, 0))

    return sheet

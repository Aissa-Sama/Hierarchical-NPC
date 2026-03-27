# renderer.py — Modelo volumétrico por slices Y

import numpy as np
import pygame

VOX_RES     = 64
CANVAS_SIZE = 64

# ─── Generador de máscaras 2D ─────────────────────────────────

def elipse_mask(size, cx, cz, rx, rz):
    """Máscara bool [size x size] — elipse centrada en (cx, cz)."""
    x = np.arange(size, dtype=np.float32)
    z = np.arange(size, dtype=np.float32)
    xx, zz = np.meshgrid(x, z, indexing='ij')
    return ((xx-cx)/rx)**2 + ((zz-cz)/rz)**2 <= 1.0

def circulo_mask(size, cx, cz, r):
    return elipse_mask(size, cx, cz, r, r)

def union_mask(a, b):
    return a | b

def lerp(a, b, t):
    return a + (b-a) * np.clip(t, 0, 1)

# ─── Definición de secciones por región Y ────────────────────

def build_volume(char):
    """
    Construye volumen [X, Y, Z] slice por slice en Y.
    Cada slice Y es una máscara 64x64 en plano XZ.
    """
    h  = char["altura"]
    c  = char["complexion"]
    mid = VOX_RES / 2.0

    # Altura total del personaje en slices
    H  = int(56 * h)
    # Posición Y donde empieza el personaje (desde arriba)
    y0 = VOX_RES - 2 - H

    volume = np.zeros((VOX_RES, VOX_RES, VOX_RES), dtype=bool)

    # ── Proporciones en slices ────────────────────────────────
    cab_h    = int(H * 0.165)   # cabeza
    cuello_h = int(H * 0.045)   # cuello
    torso_h  = int(H * 0.285)   # torso (hombros→cintura)
    cadera_h = int(H * 0.085)   # cadera
    pierna_h = int(H * 0.360)   # piernas
    pie_h    = int(H * 0.060)   # pies

    # ── Radios base ───────────────────────────────────────────
    # Cabeza
    cab_rx0  = 3.2 + c*0.5   # radio X top cabeza
    cab_rx1  = 4.2 + c*0.6   # radio X mid cabeza (más ancha)
    cab_rx2  = 3.5 + c*0.4   # radio X bot cabeza
    cab_rz0  = 2.8 + c*0.4
    cab_rz1  = 3.6 + c*0.5
    cab_rz2  = 3.0 + c*0.3

    # Cuello
    cue_rx   = 1.6 + c*0.4
    cue_rz   = 1.4 + c*0.3

    # Torso — interpola entre 3 puntos
    tor_rx_top = 6.5 + c*1.5   # hombros
    tor_rx_mid = 4.0 + c*1.0   # cintura
    tor_rx_bot = 5.5 + c*1.2   # base torso
    tor_rz_top = 4.5 + c*0.8
    tor_rz_mid = 3.2 + c*0.6
    tor_rz_bot = 3.8 + c*0.7

    # Brazos — posición X y radio
    brazo_cx   = mid - (tor_rx_top + 2.2 + c*0.5)
    brazo_cx_d = mid + (tor_rx_top + 2.2 + c*0.5)
    brazo_rx0  = 2.0 + c*0.5   # radio arriba
    brazo_rx1  = 1.5 + c*0.4   # radio abajo
    brazo_h    = int(H * 0.380)

    # Manos
    mano_r     = 1.8 + c*0.4
    mano_h     = int(H * 0.055)

    # Cadera
    cad_rx0    = 5.8 + c*1.4
    cad_rx1    = 5.2 + c*1.2
    cad_rz0    = 4.0 + c*0.8
    cad_rz1    = 3.6 + c*0.7

    # Piernas
    pier_off   = 3.0 + c*0.8   # offset del centro
    pier_rx0   = 3.2 + c*0.8   # muslo
    pier_rx1   = 2.0 + c*0.5   # pantorrilla
    pier_rz0   = 2.8 + c*0.6
    pier_rz1   = 1.8 + c*0.4

    # Pies
    pie_rx_v   = 3.5 + c*0.6
    pie_rz_v   = 2.2 + c*0.4
    pie_off_z  = 1.5   # pies ligeramente hacia adelante

    # ── Posiciones Y absolutas ────────────────────────────────
    y_cab_start   = y0
    y_cab_end     = y0 + cab_h
    y_cue_start   = y_cab_end
    y_cue_end     = y_cue_start + cuello_h
    y_tor_start   = y_cue_end
    y_tor_end     = y_tor_start + torso_h
    y_bra_start   = y_tor_start
    y_bra_end     = y_bra_start + brazo_h
    y_mano_start  = y_bra_end
    y_mano_end    = y_mano_start + mano_h
    y_cad_start   = y_tor_end
    y_cad_end     = y_cad_start + cadera_h
    y_pier_start  = y_cad_end
    y_pier_end    = y_pier_start + pierna_h
    y_pie_start   = y_pier_end
    y_pie_end     = y_pie_start + pie_h

    # ── Slice por slice ───────────────────────────────────────
    for y in range(VOX_RES):

        mask = np.zeros((VOX_RES, VOX_RES), dtype=bool)

        # ── CABEZA ────────────────────────────────────────────
        if y_cab_start <= y < y_cab_end:
            t = (y - y_cab_start) / max(y_cab_end - y_cab_start, 1)
            # Forma de cabeza: estrecha arriba, ancha en medio, estrecha abajo
            # Usando Bézier cuadrático: top→mid→bot
            if t < 0.5:
                t2 = t * 2
                rx = lerp(cab_rx0, cab_rx1, t2)
                rz = lerp(cab_rz0, cab_rz1, t2)
            else:
                t2 = (t - 0.5) * 2
                rx = lerp(cab_rx1, cab_rx2, t2)
                rz = lerp(cab_rz1, cab_rz2, t2)
            mask |= elipse_mask(VOX_RES, mid, mid, rx, rz)

        # ── CUELLO ────────────────────────────────────────────
        elif y_cue_start <= y < y_cue_end:
            t = (y - y_cue_start) / max(y_cue_end - y_cue_start, 1)
            rx = lerp(cab_rx2, cue_rx, t)
            rz = lerp(cab_rz2, cue_rz, t)
            mask |= elipse_mask(VOX_RES, mid, mid, rx, rz)

        # ── TORSO ─────────────────────────────────────────────
        if y_tor_start <= y < y_tor_end:
            t = (y - y_tor_start) / max(y_tor_end - y_tor_start, 1)
            # Bézier cuadrático: hombros → cintura → base
            if t < 0.5:
                t2 = t * 2
                rx = lerp(tor_rx_top, tor_rx_mid, t2)
                rz = lerp(tor_rz_top, tor_rz_mid, t2)
            else:
                t2 = (t - 0.5) * 2
                rx = lerp(tor_rx_mid, tor_rx_bot, t2)
                rz = lerp(tor_rz_mid, tor_rz_bot, t2)
            mask |= elipse_mask(VOX_RES, mid, mid, rx, rz)

        # ── BRAZOS ────────────────────────────────────────────
        if y_bra_start <= y < y_bra_end:
            t  = (y - y_bra_start) / max(y_bra_end - y_bra_start, 1)
            br = lerp(brazo_rx0, brazo_rx1, t)
            # Brazo izquierdo
            mask |= circulo_mask(VOX_RES, brazo_cx, mid, br)
            # Brazo derecho
            mask |= circulo_mask(VOX_RES, brazo_cx_d, mid, br)

        # ── MANOS ─────────────────────────────────────────────
        if y_mano_start <= y < y_mano_end:
            mask |= circulo_mask(VOX_RES, brazo_cx,   mid, mano_r)
            mask |= circulo_mask(VOX_RES, brazo_cx_d, mid, mano_r)

        # ── CADERA ────────────────────────────────────────────
        if y_cad_start <= y < y_cad_end:
            t  = (y - y_cad_start) / max(y_cad_end - y_cad_start, 1)
            rx = lerp(cad_rx0, cad_rx1, t)
            rz = lerp(cad_rz0, cad_rz1, t)
            mask |= elipse_mask(VOX_RES, mid, mid, rx, rz)

        # ── PIERNAS ───────────────────────────────────────────
        if y_pier_start <= y < y_pier_end:
            t  = (y - y_pier_start) / max(y_pier_end - y_pier_start, 1)
            rx = lerp(pier_rx0, pier_rx1, t)
            rz = lerp(pier_rz0, pier_rz1, t)
            cx_i = mid - pier_off
            cx_d = mid + pier_off
            mask |= elipse_mask(VOX_RES, cx_i, mid, rx, rz)
            mask |= elipse_mask(VOX_RES, cx_d, mid, rx, rz)

        # ── PIES ──────────────────────────────────────────────
        if y_pie_start <= y < y_pie_end:
            cz_pie = mid + pie_off_z
            mask |= elipse_mask(VOX_RES, mid - pier_off, cz_pie,
                                pie_rx_v, pie_rz_v)
            mask |= elipse_mask(VOX_RES, mid + pier_off, cz_pie,
                                pie_rx_v, pie_rz_v)

        volume[:, y, :] = mask

    return volume

# ─── Proyección y sombreado ───────────────────────────────────

def project_and_shade(volume, char):
    piel = np.array(char["tono_piel"],  dtype=np.float32)
    ropa = np.array(char["color_ropa"], dtype=np.float32)

    h  = char["altura"]
    H  = int(56 * h)
    y0 = VOX_RES - 2 - H

    cab_h    = int(H * 0.165)
    cuello_h = int(H * 0.045)
    torso_h  = int(H * 0.285)
    cadera_h = int(H * 0.085)
    pierna_h = int(H * 0.360)

    y_cab_end  = y0 + cab_h
    y_cue_end  = y_cab_end + cuello_h
    y_tor_end  = y_cue_end + torso_h
    y_cad_end  = y_tor_end + cadera_h
    y_pier_end = y_cad_end + pierna_h

    # Depth buffer
    depth = np.full((VOX_RES, VOX_RES), -1, dtype=np.int32)
    for z in range(VOX_RES-1, -1, -1):
        mask = volume[:, :, z] & (depth == -1)
        depth[mask] = z
    hit = depth >= 0

    # Sombreado
    shade = np.ones((VOX_RES, VOX_RES), dtype=np.float32)
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
        ao      = np.clip(depth.astype(np.float32) / VOX_RES, 0, 1)
        shade   = np.clip(0.25 + 0.55*diffuse + 0.20*ao, 0, 1)

    # Colorear
    img = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
    for xi in range(VOX_RES):
        for yi in range(VOX_RES):
            if not hit[xi, yi]:
                continue
            y = yi
            if y < y_cab_end:
                color = piel
            elif y < y_cue_end:
                color = piel
            elif y < y_tor_end:
                color = ropa
            elif y < y_cad_end:
                color = ropa
            else:
                color = piel

            s = shade[xi, yi]
            img[yi, xi, :3] = np.clip(color * s, 0, 255).astype(np.uint8)
            img[yi, xi,  3] = 255

    return img

def render_to_surface(char):
    vol  = build_volume(char)
    img  = project_and_shade(vol, char)
    surf = pygame.surfarray.make_surface(img[:, :, :3].swapaxes(0, 1))
    surf.set_colorkey((0, 0, 0))
    return surf
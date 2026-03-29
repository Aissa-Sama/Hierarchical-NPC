#character.py — Definición de la estructura de datos para el personaje y sus atributos
DEFAULT_CHAR = {
    "altura":        1.0,
    "complexion":    0.5,
    "tono_piel":     [245, 197, 163],
    "color_cabello": [59,  31,  10],
    "color_ropa":    [74,  124, 63],
}

# Valores ajustados — Grok era el más cercano a la realidad
TABLA_ANATOMICA = {
    "cabeza":      (0.00, 0.13, 0.050, 0.040, 0.044),
    "cuello":      (0.13, 0.17, 0.030, 0.022, 0.025),
    "hombros":     (0.17, 0.22, 0.130, 0.110, 0.080),
    "pecho":       (0.22, 0.32, 0.110, 0.090, 0.075),
    "cintura":     (0.32, 0.40, 0.080, 0.070, 0.055),
    "cadera":      (0.40, 0.50, 0.100, 0.090, 0.065),
    "muslo":       (0.50, 0.68, 0.065, 0.045, 0.050),
    "rodilla":     (0.68, 0.73, 0.045, 0.038, 0.038),
    "pantorrilla": (0.73, 0.88, 0.050, 0.030, 0.040),
    "tobillo":     (0.88, 0.93, 0.025, 0.020, 0.020),
    "pie":         (0.93, 1.00, 0.060, 0.045, 0.065),
}


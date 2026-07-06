# ============================
# MOTOR DE RECOMENDACIÓN AFP
# ============================
# Este módulo evalúa reglas de negocio y produce
# una recomendación estructurada lista para consumir
# desde la UI (Streamlit) o desde una API futura (MAIA).
# ============================

from datos import RENTABILIDAD, PARAMS
from calculos import valor_futuro, apv_optimo, cobertura


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def recomendar(brecha, ingreso, apv, años, fondo, rentabilidad=None):
    """
    Motor de recomendación principal.

    Parámetros
    ----------
    brecha : float
        Brecha previsional total en CLP (valor presente).
    ingreso : float
        Ingreso mensual del cliente en CLP.
    apv : float
        APV mensual que el cliente está dispuesto/puede aportar.
    años : int
        Horizonte hasta el retiro.
    fondo : str
        Fondo actual del cliente ("A"–"E").
    rentabilidad : float, opcional
        Rentabilidad esperada anual. Si es None se toma de datos.py.

    Retorna
    -------
    dict con recomendación estructurada y auditable.
    """

    # -----------------------------------------
    # 1. Preparar variables base
    # -----------------------------------------
    if rentabilidad is None:
        rentabilidad = RENTABILIDAD.get(fondo, 0.040)

    # Cálculos financieros clave
    vf = valor_futuro(apv, rentabilidad, años)
    cov = cobertura(vf, brecha)
    apv_opt = apv_optimo(brecha, rentabilidad, años)
    pct_ingreso = apv_opt / ingreso if ingreso > 0 else 0

    # Lista de reglas activadas (auditable)
    reglas_activadas = []

    # -----------------------------------------
    # 2. Reglas de CAPACIDAD DE PAGO
    # -----------------------------------------
    horizonte_recomendado = años
    esfuerzo = "Bajo"

    if pct_ingreso > PARAMS["TOPE_APV_PCT"]:
        # R1: APV óptimo > 10% del ingreso
        reglas_activadas.append(
            "R1: APV requerido supera el 10% del ingreso → extender horizonte +5 años"
        )
        horizonte_recomendado = años + 5
        esfuerzo = "Alto"

    elif pct_ingreso > PARAMS["APV_MODERADO"]:
        # R2: APV óptimo entre 5% y 10%
        reglas_activadas.append(
            "R2: APV requerido entre 5% y 10% del ingreso → esfuerzo moderado"
        )
        esfuerzo = "Moderado"

    # -----------------------------------------
    # 3. Reglas de HORIZONTE / FONDO
    # -----------------------------------------
    if años < 10:
        # R3: Horizonte corto → maximizar rentabilidad
        reglas_activadas.append(
            "R3: Horizonte corto (<10 años) → recomendar Fondo A para maximizar rentabilidad"
        )
        fondo_recomendado = "A"

    elif años >= 20:
        # R4: Horizonte largo → aprovechar interés compuesto
        reglas_activadas.append(
            "R4: Horizonte largo (≥20 años) → Fondo A aprovecha el interés compuesto"
        )
        fondo_recomendado = "A"

    else:
        # Caso intermedio: mantener fondo actual o Fondo C
        fondo_recomendado = fondo if fondo in ("A", "B", "C") else "C"

    # -----------------------------------------
    # 4. Reglas de BRECHA / CANAL
    # -----------------------------------------
    if brecha > PARAMS["BRECHA_ALTA"]:
        # R5: Brecha alta
        reglas_activadas.append(
            "R5: Brecha alta (>30M) → Prioridad P1 · canal WhatsApp + CAT out"
        )
        prioridad = "P1 · Alta"
        canal = "WhatsApp + CAT out"

    elif brecha > PARAMS["BRECHA_MEDIA"]:
        # R6: Brecha media
        reglas_activadas.append(
            "R6: Brecha media (5M–30M) → Prioridad P2 · canal App + Mail"
        )
        prioridad = "P2 · Media"
        canal = "App + Mail"

    else:
        # R7: Brecha baja
        reglas_activadas.append(
            "R7: Brecha baja (<5M) → Prioridad P3 · canal Notificación App"
        )
        prioridad = "P3 · Baja"
        canal = "Notificación App"

    # -----------------------------------------
    # 5. Regla de COBERTURA
    # -----------------------------------------
    if cov < PARAMS["COBERTURA_OBJETIVO"]:
        # R8: Cobertura insuficiente
        reglas_activadas.append(
            "R8: Cobertura <80% → ajustar APV o extender horizonte"
        )

    # -----------------------------------------
    # 6. Calcular APV recomendado final
    # -----------------------------------------
    # Recalculamos el APV óptimo con el fondo y horizonte finales
    rent_final = RENTABILIDAD.get(fondo_recomendado, rentabilidad)
    apv_recomendado = apv_optimo(brecha, rent_final, horizonte_recomendado)

    # -----------------------------------------
    # 7. SCORE 0–100
    # -----------------------------------------
    # Componente 1: Cobertura (máx 50 pts)
    score_cobertura = min(cov, 1) * 50

    # Componente 2: Capacidad de pago (máx 25 pts)
    # Menor % ingreso = mayor puntaje
    if pct_ingreso <= PARAMS["APV_MODERADO"]:
        score_capacidad = 25
    elif pct_ingreso <= PARAMS["TOPE_APV_PCT"]:
        score_capacidad = 15
    else:
        score_capacidad = 5

    # Componente 3: Horizonte (máx 25 pts)
    # Horizonte >20 = ideal, <10 = penalizado
    if años >= 20:
        score_horizonte = 25
    elif años >= 10:
        score_horizonte = 15
    else:
        score_horizonte = 5

    score_total = int(round(score_cobertura + score_capacidad + score_horizonte))

    # -----------------------------------------
    # 8. Output estructurado
    # -----------------------------------------
    return {
        "brecha": brecha,
        "cobertura_actual": round(cov, 4),
        "apv_optimo": round(apv_opt, 0),
        "pct_ingreso": round(pct_ingreso, 4),
        "fondo_recomendado": fondo_recomendado,
        "apv_recomendado": round(apv_recomendado, 0),
        "horizonte_recomendado": horizonte_recomendado,
        "esfuerzo": esfuerzo,
        "prioridad": prioridad,
        "canal": canal,
        "score": score_total,
        "score_desglose": {
            "cobertura": round(score_cobertura, 1),
            "capacidad": score_capacidad,
            "horizonte": score_horizonte,
        },
        "reglas_activadas": reglas_activadas,
        "human_in_the_loop": True,
        "validacion_requerida": True,
    }


# ============================================================
# TEST RÁPIDO (solo si se ejecuta directo)
# ============================================================
if __name__ == "__main__":
    resultado = recomendar(
        brecha=15_000_000,
        ingreso=1_200_000,
        apv=25_000,
        años=15,
        fondo="C",
    )

    print("=== RECOMENDACIÓN ===")
    for k, v in resultado.items():
        print(f"{k}: {v}")
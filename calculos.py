# ============================
# FUNCIONES MATEMÁTICAS
# ============================

def valor_futuro(apv, rent, años):
    """
    Calcula el valor futuro de una anualidad (APV mensual)
    """
    i = rent / 12
    n = años * 12

    if i == 0:
        return apv * n

    return apv * ((1 + i)**n - 1) / i


def apv_optimo(brecha, rent, años):
    """
    Calcula el APV necesario para cerrar una brecha
    """
    i = rent / 12
    n = años * 12

    if i == 0:
        return brecha / n

    return brecha * i / ((1 + i)**n - 1)


def cobertura(valor_futuro, brecha):
    """
    % de cobertura de la brecha
    """
    if brecha == 0:
        return 1

    return valor_futuro / brecha


def brecha_laguna(meses, cotizacion_mensual, vc_hist, vc_actual):
    """
    Calcula brecha por laguna previsional
    """
    cot_total = meses * cotizacion_mensual

    if vc_hist == 0:
        return 0

    cuotas = cot_total / vc_hist
    valor_hoy = cuotas * vc_actual

    return valor_hoy
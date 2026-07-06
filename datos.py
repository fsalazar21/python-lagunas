# ============================
# DATOS BASE DEL MODELO
# ============================

# Valor cuota actual (referencial)
VC_ACTUAL = {
    "A": 98000,
    "B": 82000,
    "C": 85000,
    "D": 60000,
    "E": 70000,
}

# Rentabilidad esperada anual
RENTABILIDAD = {
    "A": 0.053,
    "B": 0.047,
    "C": 0.040,
    "D": 0.035,
    "E": 0.029,
}

# Perfil de riesgo
RIESGO = {
    "A": "Agresivo",
    "B": "Riesgoso",
    "C": "Moderado",
    "D": "Conservador",
    "E": "Muy conservador",
}

# Parámetros de negocio
PARAMS = {
    "TOPE_APV_PCT": 0.10,      # 10% ingreso
    "APV_MODERADO": 0.05,      # 5%
    "BRECHA_ALTA": 30000000,
    "BRECHA_MEDIA": 5000000,
    "COBERTURA_OBJETIVO": 0.8,
}
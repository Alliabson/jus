from datetime import datetime, timedelta

def calculate_legal_dates(start_date, area):
    """Calcula prazos processuais conforme área jurídica"""
    if area == "Criminal":
        return {
            "Resposta": start_date + timedelta(days=10),
            "Recurso": start_date + timedelta(days=5)
        }
    elif area == "Civil":
        return {
            "Resposta": start_date + timedelta(days=15),
            "Recurso": start_date + timedelta(days=10)
        }
    else:  # Previdenciário
        return {
            "Resposta": start_date + timedelta(days=20),
            "Recurso": start_date + timedelta(days=15)
        }

def calculate_penalty_risk(score):
    """Calcula risco penal baseado em score"""
    if score > 80:
        return "Alto risco"
    elif score > 50:
        return "Médio risco"
    return "Baixo risco"

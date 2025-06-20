import requests

def fetch_jurisprudence(search_term: str, area: str) -> dict:
    """Simulação de API jurídica (substitua por API real)"""
    mock_data = {
        "termo": search_term,
        "area": area,
        "resultados": [
            {
                "processo": "AP 9999999-99.9999.999.9999",
                "relator": "Ministro Fulano",
                "ementa": f"Recurso sobre {search_term} na área {area}...",
                "decisao": "Provido"
            }
        ]
    }
    return mock_data

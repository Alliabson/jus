import requests

def fetch_jurisprudence(search_term: str, area: str) -> dict:
    """Busca jurisprudência em APIs oficiais"""
    # Exemplo com API do STF (simplificado)
    base_url = "https://portal.stf.jus.br/jurisprudencia/"
    params = {
        "classe": area,
        "termo": search_term,
        "pagina": 1
    }
    
    try:
        response = requests.get(base_url + "api/search", params=params)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

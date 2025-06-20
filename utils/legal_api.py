# utils/legal_api.py

import requests
import json
import os # Importar para usar os.getenv para chaves de APIs externas

# ⚠️ IMPORTANTE: URL de API Real para BUSCA GERAL e ATUALIZADA.
# Para uma busca GERAL ROBUSTA E COM EMENTAS COMPLETAS DE TODOS OS TJs,
# uma API PAGA de Lawtech (como Jusbrasil API, Legal One, etc.) é ALTAMENTE RECOMENDADA.
#
# Se a intenção é buscar METADADOS GERAIS GRATUITOS (sem ementas completas diretas),
# a API Pública do CNJ DataJud é a opção mais próxima.
#
# URL_API_JURISPRUDENCIA_GERAL = "https://api.nomedaapi.com/v1/jurisprudencia/geral" # Exemplo de Lawtech API
# URL_API_CNJ_DATAJUD = "https://www.cnj.jus.br/datajud/api/v1/public" # Exemplo CNJ (metadados)

# Por enquanto, mantenha este placeholder, ele NÃO FAZ REQUISIÇÃO REAL!
# Ele serve apenas para indicar onde você colocaria a URL de uma API real no futuro.
URL_API_REAL_PARA_FUTURO = "https://api.sua-api-juridica-geral-real.com/v1/busca"


def fetch_jurisprudence(search_term: str, area: str = None) -> dict:
    """
    Busca jurisprudência (simulada por enquanto) que representaria uma busca geral e atualizada.

    Args:
        search_term (str): O termo de busca (palavras-chave, número de processo, etc.).
        area (str, optional): A área jurídica para filtrar (e.g., "Civil", "Criminal", "Previdenciário").
                              Pode ser usado no mock ou em APIs reais que suportem.

    Returns:
        dict: Um dicionário contendo os resultados da jurisprudência simulada, formatados para o app.
              Retorna {"error": "mensagem de erro", "resultados": []} em caso de falha.
    """
    print(f"DEBUG: Buscando jurisprudência GERAL e ATUAL (simulado) para '{search_term}' na área '{area}'...")

    try:
        # --- LÓGICA DE CHAMADA À API REAL ---
        # ⚠️ PASSO 1: OBTENHA UMA CHAVE DE API, SE A API REAL EXIGIR.
        # Configure-a como 'EXTERNAL_LEGAL_API_KEY' no Streamlit Secrets (Cloud) ou no seu .env (local).
        # external_api_key = os.getenv("EXTERNAL_LEGAL_API_KEY")
        # headers = {"Authorization": f"Bearer {external_api_key}"} if external_api_key else {}

        # ⚠️ PASSO 2: CONFIGURE OS PARÂMETROS CONFORME A DOCUMENTAÇÃO DA SUA API REAL ESCOLHIDA!
        # Estes são parâmetros genéricos. A API real terá os seus próprios nomes (ex: 'query', 'q', 'search').
        params = {
            "query": search_term,
            "limit": 3, # Limita o número de resultados para este exemplo
            # "domain": area, # Se a API real permitir filtrar por área
            # "sort_by": "date_desc", # Para buscar a mais atual (se a API real suportar)
        }

        # ⚠️ PASSO 3: DESCOMENTE AS LINHAS ABAIXO QUANDO TIVER A URL REAL E AUTENTICAÇÃO!
        # response = requests.get(URL_API_REAL_PARA_FUTURO, headers=headers, params=params)
        # response.raise_for_status() # Lança um erro para status de erro HTTP (4xx, 5xx)
        # data = response.json() # Pega a resposta JSON da API real
        # print(f"DEBUG: Resposta da API real recebida: {json.dumps(data, indent=2)}")

        # --- FIM DA LÓGICA DE CHAMADA À API REAL ---


        # --- CÓDIGO TEMPORÁRIO: MOCK DE RESPOSTA PARA BUSCA GERAL E ATUALIZADA ---
        # Este mock simula resultados de diferentes TJs e com datas mais recentes.
        mock_data = {
            "termo": search_term,
            "area": area,
            "resultados": [
                {
                    "processo": f"TJSP {hash(search_term) % 100000}-99.2024.8.26.0001",
                    "relator": "Des. Maria Silva (TJSP)",
                    "ementa": (
                        f"**EMENTA ATUALIZADA (TJSP)**: Processo sobre **{search_term}** na área **{area}**. "
                        "Jurisprudência recente de [mês/ano atual]. A decisão ressalta "
                        "a interpretação contemporânea da matéria. Recurso conhecido e provido. (Acórdão de 15/05/2024)"
                    ),
                    "decisao": "Provido (Acórdão de 15/05/2024)"
                },
                {
                    "processo": f"TJRJ {hash(search_term + 'a') % 100000}-99.2024.8.19.0001",
                    "relator": "Des. João Santos (TJRJ)",
                    "ementa": (
                        f"**JURISPRUDÊNCIA RECENTE (TJRJ)**: Agravo de instrumento sobre **{search_term}** na área **{area}**. "
                        "Decisão unânime. A Corte reiterou a aplicação da tese jurídica "
                        "em casos análogos. Negado provimento. (Julgado em 01/06/2024)"
                    ),
                    "decisao": "Não Provido (Julgado em 01/06/2024)"
                },
                {
                    "processo": f"TJMG {hash(search_term + 'b') % 100000}-99.2024.8.13.0001",
                    "relator": "Des. Pedro Almeida (TJMG)",
                    "ementa": (
                        f"**PRECEDENTE ATUAL (TJMG)**: Apelação Cível em tema de **{search_term}** ({area}). "
                        "Análise sobre [ponto específico]. A jurisprudência mineira tem se consolidado "
                        "nesse sentido. Sentença mantida. (Data: 20/05/2024)"
                    ),
                    "decisao": "Sentença Mantida (Data: 20/05/2024)"
                }
            ]
        }
        return mock_data
        # --- FIM DO CÓDIGO TEMPORÁRIO ---


        # ----------------------------------------------------------------------
        # ⚠️ PASSO 4: QUANDO VOCÊ INTEGRAR UMA API REAL, VOCÊ VAI ADAPTAR ESTE BLOCO!
        # Você precisará mapear a resposta real da API (a variável 'data' da requisição)
        # para o formato que seu 'app.py' espera (com 'processo', 'relator', 'ementa', 'decisao').
        #
        # processed_results = []
        # if 'data' in data and 'jurisprudences' in data['data']: # Exemplo de estrutura de resposta de API real
        #     for doc in data['data']['jurisprudences']:
        #         processed_results.append({
        #             "processo": doc.get('numero_processo_completo', 'N/A'), # Adapte para os nomes de campo da sua API real
        #             "relator": doc.get('nome_do_relator', 'N/A'),
        #             "ementa": doc.get('texto_da_ementa_completa', 'N/A'),
        #             "decisao": doc.get('tipo_da_decisao_final', 'N/A')
        #         })
        # return {
        #     "termo": search_term,
        #     "area": area,
        #     "resultados": processed_results
        # }
        # ----------------------------------------------------------------------

    except requests.exceptions.RequestException as e:
        print(f"ERRO: Erro de conexão ou requisição com a API jurídica externa: {e}")
        return {"error": f"Erro de conexão com a API jurídica: {e}", "resultados": []}
    except json.JSONDecodeError:
        print(f"ERRO: Resposta inválida da API (não é JSON).")
        return {"error": "Resposta da API não é um JSON válido.", "resultados": []}
    except Exception as e:
        print(f"ERRO: Ocorreu um erro inesperado na busca de jurisprudência: {e}")
        return {"error": f"Erro inesperado: {e}", "resultados": []}

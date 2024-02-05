import httpx
from fastapi import HTTPException

SERP_API_URL = 'https://gateway.apiserpro.serpro.gov.br/consulta-nfe-df-trial/api/v1/nfe'

@staticmethod
def obter_dados_nfe(chave_nfe: str, authorization: str):
    url = f"{SERP_API_URL}/{chave_nfe}"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': authorization
    }

    with httpx.Client() as client:
        try:
            response = client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Erro na requisição HTTP: {str(e)}")

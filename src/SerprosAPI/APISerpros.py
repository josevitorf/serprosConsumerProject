import httpx
from fastapi import HTTPException

SERP_API_URL_NFS = 'https://gateway.apiserpro.serpro.gov.br/consulta-nfe-df-trial/api/v1/nfe'
SERP_API_URL_OCPJP = 'https://gateway.apiserpro.serpro.gov.br/consulta-cnpj-df-trial/v2/basica'
SERP_API_URL_CPF = 'https://gateway.apiserpro.serpro.gov.br/consulta-cpf-df-trial/v1/cpf'


class SerprosAPI:
    @staticmethod
    def obter_dados_nfe(chave_nfe: str):
        url = f"{SERP_API_URL_NFS}/{chave_nfe}"
        authorization = "Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e"
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

    @staticmethod
    def obter_dados_cpf(chave_cpf: str, authorization: str):
        url = f"{SERP_API_URL_CPF}/{chave_cpf}"

        authorization = "Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e"
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

    @staticmethod
    def obter_dados_cnpj(chave_cnpj: str, authorization: str):
        url = f"{SERP_API_URL_OCPJP}/{chave_cnpj}"

        authorization = "Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e"
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

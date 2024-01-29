import os

from fastapi import APIRouter, Header, HTTPException, UploadFile, File
import json
from fastapi.responses import JSONResponse

from src.services.serpros_services import SerprosServices

router = APIRouter(prefix="/serpros")

class SerprosController:


    @router.get("/message")
    def read_users():
        return {"Bem Vindo ao projeto Serpros"}

    @router.get("/dados-nfe-local/{chave_nfe}")
    async def obter_dados_nfe_endpoint_Local(chave_nfe: str,
                                             accept: str = Header("application/json, application/xml"),
                                             authorization: str = Header(
                                                 "Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")):
        try:
            dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe, authorization)

            # Salvar os dados em um arquivo JSON local (opcional)
            with open(f"{chave_nfe}.json", 'w') as json_file:
                json.dump(dados_nfe, json_file, indent=2)

            return dados_nfe
        except HTTPException as e:
            raise e

    @router.get("/dados-nfe-online/{chave_nfe}")
    async def obter_dados_nfe_endpoint_online(chave_nfe: str,
                                              accept: str = Header("application/json, application/xml"),
                                              authorization: str = Header(
                                                  "Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")):
        try:
            dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe, authorization)
            return dados_nfe
        except HTTPException as e:
            raise e

    @router.post("/processar-codigos")
    async def processar_codigos(codigos: str,
                                accept: str = Header("application/json, application/xml"),
                                authorization: str = Header("Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")):
        # Verifica se os códigos foram fornecidos
        if not codigos:
            raise HTTPException(status_code=422, detail="Códigos não fornecidos")

        # Divide os códigos separados por vírgula
        codigos_lista = codigos.split(',')

        # Lista para armazenar os resultados
        resultados = []

        # Processa cada código
        for chave_nfe in codigos_lista:
            try:
                # Obtém os dados da NF-e para cada código
                dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe, authorization)
                resultados.append({"chave_nfe": chave_nfe, "dados_nfe": dados_nfe})
            except HTTPException as e:
                # Adiciona detalhes sobre qualquer erro
                resultados.append({"chave_nfe": chave_nfe, "erro": f"Erro na requisição para {chave_nfe}: {str(e)}"})

        return resultados


    @router.get("/files-convert/")
    async def convert_file_to_json():
        try:
            file_path = 'docs/NFs.txt'
            file_type = 'txt'
            result = SerprosServices.read_and_convert_to_json(file_path, file_type)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")



################################## MULTI LOTES CODIGOS #######################################

    @router.get("/dados-nfe-local/{chave_nfe}")
    async def obter_dados_nfe_endpoint_local(chave_nfe: str,
                                             accept: str = Header("application/json, application/xml"),
                                             authorization: str = Header("Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")):
        try:
            dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe, authorization)
            return dados_nfe
        except HTTPException as e:
            raise e

    @router.get("/dados-nfe-local-from-file/")
    async def obter_dados_nfe_from_file(
            accept: str = Header("application/json, application/xml"),
            authorization: str = Header("Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")
    ):
        try:
            # Caminho fixo do arquivo
            file_path = 'docs/NFs.txt'

            # Lê os códigos do arquivo
            codigos_nfe = SerprosServices._read_codes_from_txt(file_path)

            # Pasta para salvar os resultados JSON
            result_folder = 'jsonResults'

            # Certifica-se de que a pasta exista
            os.makedirs(result_folder, exist_ok=True)

            # Para cada código, faz a chamada ao endpoint Serpros
            resultados = {}
            for chave_nfe in codigos_nfe:
                try:
                    dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe, authorization)

                    # Salvar os dados em um arquivo JSON local na pasta 'jsonResults'
                    with open(os.path.join(result_folder, f"{chave_nfe}.json"), 'w') as json_file:
                        json.dump(dados_nfe, json_file, indent=2)

                    # Adiciona o resultado ao dicionário de resultados
                    resultados[chave_nfe] = dados_nfe
                except HTTPException as e:
                    # Se ocorrer um erro, adiciona um valor nulo ao dicionário de resultados
                    resultados[chave_nfe] = None

            return resultados
        except HTTPException as e:
            raise e

    @router.get("/dados-nfe-online/")
    async def obter_dados_nfe_online(
            accept: str = Header("application/json, application/xml"),
            authorization: str = Header("Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")
    ):
        try:
            # Caminho fixo do arquivo
            file_path = 'docs/NFs.txt'

            # Lê os códigos do arquivo
            codigos_nfe = SerprosServices._read_codes_from_txt(file_path)

            # Resultado para armazenar os dados
            resultados = {}

            # Para cada código, faz a chamada ao endpoint Serpros
            for chave_nfe in codigos_nfe:
                try:
                    dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe, authorization)

                    # Adiciona o resultado ao dicionário de resultados
                    resultados[chave_nfe] = dados_nfe
                except HTTPException as e:
                    # Se ocorrer um erro, adiciona um valor nulo ao dicionário de resultados
                    resultados[chave_nfe] = None

            return resultados
        except HTTPException as e:
            raise e



################################################Upload DE ARQUIVOS ##################################################################
    @router.post("/processar-arquivo/")
    async def processar_arquivo(
            file: UploadFile = File(...),
            authorization: str = Header("Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")
    ):
        try:
            print("Recebendo solicitação para processar arquivo.")
            result = SerprosServices.read_and_convert_to_json_auto(file, authorization, language='pt')
            print("Arquivo processado com sucesso.")
            return JSONResponse(content={"result": result}, status_code=200)
        except HTTPException as e:
            print(f"Erro HTTP: {e}")
            raise e
        except FileNotFoundError as e:
            print(f"Erro ao ler o arquivo: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {str(e)}")
        except Exception as e:
            print(f"Erro durante o processamento do arquivo: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro durante o processamento do arquivo: {str(e)}")


import os

import datetime
from typing import List, Dict

from fastapi import APIRouter, Header, UploadFile, File, FastAPI, Request, HTTPException, Form, Request
import json
from fastapi.responses import JSONResponse

from src.services.serpros_services import SerprosServices
from src.SerprosAPI.APISerpros import SerprosAPI

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

#router = APIRouter(prefix="/serpros")
router = APIRouter()

templates = Jinja2Templates(
    directory="templates")  # Crie uma pasta 'templates' no mesmo diretório do seu código e coloque seus arquivos HTML lá


class SerprosController:

    @router.get("/message")
    def read_users():
        return {"Bem Vindo ao projeto Serpros"}

    @router.get("/", response_class=HTMLResponse)
    async def read_item(request: Request):
        return templates.TemplateResponse("home.html", {"request": request})

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
                                             authorization: str = Header(
                                                 "Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")):
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

    ####################################################################################################################################
    ####################################################################################################################################
    ####################################################################################################################################
    # @router.route("/processar-nota-fiscal-front2", methods=["GET", "POST"], response_class=HTMLResponse)
    # async def processar_nota_fiscal(request: Request, chave_nfe: str = Form(...), authorization: str = Form(...)):
    #     if request.method == "POST":
    #         if not chave_nfe:
    #             error_message = "Chave NFe não fornecida."
    #             return templates.TemplateResponse("index.html", {"request": request, "error_message": error_message})
    #
    #         dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe, authorization)
    #
    #         if not dados_nfe:
    #             error_message = "Erro ao obter os dados da nota fiscal."
    #             return templates.TemplateResponse("index.html", {"request": request, "error_message": error_message})
    #
    #         return templates.TemplateResponse("index.html", {"request": request, "dados_nfe": dados_nfe})
    #
    #     # Se o método for GET, retorne uma página com o formulário
    #     dados_nfe = {
    #         "nProt": "Default nProt",
    #         "Id": "Default Id",
    #         "emit": {
    #             "xNome": "Default Emitente",
    #             "enderEmit": {
    #                 "xLgr": "Default Endereço",
    #                 "nro": "Default 123",
    #                 "xMun": "Default Cidade",
    #                 "UF": "Default UF"
    #             }
    #         },
    #         "dest": {
    #             "xNome": "Default Destinatário",
    #             "enderDest": {
    #                 "xLgr": "Default Endereço",
    #                 "nro": "Default 456",
    #                 "xMun": "Default Cidade",
    #                 "UF": "Default UF"
    #             }
    #         }
    #     }
    #     return templates.TemplateResponse("index.html", {"request": request, "dados_nfe": dados_nfe})

    # @router.get("/processar-nota-fiscal-front2", response_class=HTMLResponse)
    # async def processar_nota_fiscal(request: Request):
    #     dados_nfe = None
    #     error_message = None
    #     return templates.TemplateResponse("index.html",
    #                                       {"request": request, "dados_nfe": dados_nfe, "error_message": error_message})
    #
    # @router.post("/processar-nota-fiscal-front2", response_class=HTMLResponse)
    # async def processar_nota_fiscal(request: Request, chave_nfe: str = Form(...), authorization: str = Form(...)):
    #     if not chave_nfe:
    #         error_message = "Chave NFe não fornecida."
    #         return templates.TemplateResponse("index.html", {"request": request, "error_message": error_message})
    #
    #     dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe, authorization)
    #
    #     if not dados_nfe:
    #         error_message = "Erro ao obter os dados da nota fiscal."
    #         return templates.TemplateResponse("index.html", {"request": request, "error_message": error_message})
    #
    #     return templates.TemplateResponse("index.html", {"request": request, "dados_nfe": dados_nfe})

    #     @router.get("/", response_class=HTMLResponse)
    #     async def read_item():
    #         return """
    #         <html lang="en">
    # <head>
    #     <meta charset="UTF-8">
    #     <meta name="viewport" content="width=device-width, initial-scale=1.0">
    #     <title>Processar Nota Fiscal</title>
    # </head>
    # <body>
    #     <h1>Processar Nota Fiscal</h1>
    #     <form id="form" action="/serpros/dados-nfe-online2" method="get">
    #         <label for="chave_nfe">Chave NFe:</label>
    #         <input type="text" id="chave_nfe" name="chave_nfe" required>
    #         <button type="button" onclick="submitForm()">Processar</button>
    #     </form>
    #     <div id="result"></div>
    #     <script>
    #         async function submitForm() {
    #             const chaveNFe = document.getElementById("chave_nfe").value;
    #             const response = await fetch(`/serpros/dados-nfe-online2/${chaveNFe}`);
    #             const htmlData = await response.text(); // Receber a resposta como texto
    #             const resultDiv = document.getElementById("result");
    #             resultDiv.innerHTML = htmlData; // Inserir o HTML retornado na div de resultado
    #         }
    #     </script>
    # </body>
    # </html>
    #         """
    #
    #     @router.get("/dados-nfe-online2/{chave_nfe}", response_class=HTMLResponse)
    #     async def obter_dados_nfe_endpoint_online(chave_nfe: str,
    #                                               accept: str = Header("application/json, application/xml"),
    #                                               authorization: str = Header(
    #                                                   "Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")):
    #         try:
    #             # Aqui você chamaria sua função para obter os dados da nota fiscal
    #             # Substitua isso com sua lógica real para obter os dados da nota fiscal
    #             dados_nfe = {
    #                 "nProt": "123456",
    #                 "Id": "NFe123",
    #                 "emit": {"xNome": "Empresa Emitente",
    #                          "enderEmit": {"xLgr": "Rua A", "nro": "123", "xMun": "Cidade", "UF": "UF"}},
    #                 "dest": {"xNome": "Destinatário",
    #                          "enderDest": {"xLgr": "Rua B", "nro": "456", "xMun": "Cidade B", "UF": "UF B"}}
    #             }
    #             return dados_nfe
    #         except HTTPException as e:
    #             raise e



    @router.get("/dados-nfe-online/{chave_nfe}", response_class=JSONResponse)
    async def obter_dados_nfe_endpoint_online(chave_nfe: str,
                                              accept: str = Header("application/json, application/xml"),
                                              authorization: str = Header(
                                                  "Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e"),
                                              request: Request = None):
        try:
            dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe,
                                                        authorization)  # Supondo que SerprosServices.obter_dados_nfe seja uma função que retorna os dados da nota fiscal
            return dados_nfe
        except HTTPException as e:
            raise e

    ########################################################################################################################
    @router.get("/dados-nfe-online-alguns/{chave_nfe}")
    async def obter_dados_nfe_endpoint_online_especific(chave_nfe: str):
        try:

            # Obter os dados da NF-e da Serpros API
            dados_nfe = SerprosAPI.obter_dados_nfe(chave_nfe)
            #print(dados_nfe)

            # Extrair o CNPJ do emitente da NF-e
            cnpj_emitente = dados_nfe.get("nfeProc", {}).get("NFe", {}).get("infNFe", {}).get("emit", {}).get("CNPJ", None)
            #print(cnpj_emitente)

            cnpj_mock = 34238864000168

            #Chamar a API da Serpros para obter dados do CNPJ
            dados_cnpj = SerprosAPI.obter_dados_cnpj(cnpj_mock, authorization="Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")
            #print(dados_cnpj)

            # Extrair o campo "CPF" do payload da NF-e
            nfe_data = dados_nfe.get("nfeProc", {}).get("protNFe", {}).get("infProt", {})
            cpf = dados_nfe.get("nfeProc", {}).get("NFe", {}).get("infNFe", {}).get("dest", {}).get("CPF", None)
            dhRecbto = nfe_data.get("dhRecbto", None)

            # Extrair os produtos
            produtos = []
            det = dados_nfe.get("nfeProc", {}).get("NFe", {}).get("infNFe", {}).get("det", [])
            for item in det:
                produto = item.get("prod", {}).get("xProd", None)
                if produto:
                    produtos.append({"xProd": produto})

            payload = {
                "CPF": cpf,
                "dhRecbto": dhRecbto,
                "produtos": produtos,
                "cnpj_emitente": cnpj_emitente,
                #"AQUI COMECA OS DADOS CNPJ": "DADOS CNPJ",
                #"dados_cnpj": dados_cnpj
            }

            return payload

            #return {"CPF": cpf, "dhRecbto": dhRecbto, "produtos": produtos, "cnpj_emitente": cnpj_emitente}
        except HTTPException as e:
            raise e

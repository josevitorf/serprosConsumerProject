import tempfile
from datetime import datetime
from tempfile import SpooledTemporaryFile
from typing import List, Union
from fastapi import UploadFile
import os
from zxing import BarCodeReader, BarCode, BarCodeReaderException
from fastapi import HTTPException
import httpx
import csv
import easyocr

SERP_API_URL = 'https://gateway.apiserpro.serpro.gov.br/consulta-nfe-df-trial/api/v1/nfe'


class SerprosServices:
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


############################################# ETL ######################################################
    @staticmethod
    def read_and_convert_to_json(file_path: str, file_type: str = "txt") -> dict:
        try:
            if file_type == "txt":
                codes = SerprosServices._read_codes_from_txt(file_path)
            elif file_type == "csv":
                codes = SerprosServices._read_codes_from_csv(file_path)
            elif file_type == "image":
                codes = SerprosServices._read_text_from_image(file_path)
            else:
                raise Exception("Tipo de arquivo não suportado.")

            result = {
                "codes": codes,
                "conversion_date": datetime.utcnow().isoformat()
            }

            return result
        except Exception as e:
            raise Exception(f"Erro ao ler e converter arquivo para JSON: {str(e)}")


####################################### funcoes de extraçao de codigo de arquivos locais ##############################################################
    @staticmethod
    def _read_codes_from_txt(file_path: str) -> List[str]:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return [code.strip() for code in content.split(',') if code.strip()]
        except Exception as e:
            raise Exception(f"Erro ao ler códigos do arquivo TXT: {str(e)}")

    @staticmethod
    def _read_codes_from_csv(file_path: str) -> List[str]:
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                codes = [code.strip() for row in reader for code in row if code.strip()]
            return codes
        except Exception as e:
            raise Exception(f"Erro ao ler códigos do arquivo CSV: {str(e)}")

    @staticmethod
    def _read_codes_from_image(upload_file, language='pt'):
        try:
            file_content = upload_file.file.read()
            reader = easyocr.Reader([language])
            result = reader.readtext(file_content)
            extracted_text = ' '.join([item[1] for item in result])
            return extracted_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao extrair texto da imagem: {str(e)}")

################################################Upload DE ARQUIVOS ##################################################################

    def read_and_convert_to_json_auto(file: UploadFile, authorization: str, language='pt') -> dict:
        try:
            _, file_extension = os.path.splitext(file.filename)
            file_extension = file_extension.lower()

            if file_extension == ".txt":
                codes = SerprosServices._read_codes_from_txt_online_upload(file.file)
            elif file_extension == ".csv":
                codes = SerprosServices._read_codes_from_csv_online_upload(file.file)
            elif file_extension in (".jpg", ".jpeg", ".png", ".gif"):
                # Extrair código de barras da imagem
                extracted_text = SerprosServices._read_codes_from_image_Barcode_online_upload(file.file)

                if extracted_text:
                    # Chamar a API do Serpros com o código de barras extraído
                    serpros_response = SerprosServices.obter_dados_nfe(extracted_text, authorization)

                    # Retornar os resultados da API do Serpros
                    return {
                        "codes": extracted_text,
                        "serpros_response": serpros_response,
                        "conversion_date": datetime.utcnow().isoformat()
                    }
                else:
                    raise HTTPException(status_code=400, detail="Código de barras não detectado.")
            else:
                raise Exception("Extensão de arquivo não suportada.")

            result = {
                # "codes": codes,
                # "conversion_date": datetime.utcnow().isoformat()
            }

            # Para cada código, faz a chamada ao endpoint Serpros
            for chave_nfe in codes:
                try:
                    dados_nfe = SerprosServices.obter_dados_nfe(chave_nfe, authorization)

                    # Adiciona o resultado ao dicionário de resultados
                    result[chave_nfe] = dados_nfe
                except HTTPException as e:
                    # Se ocorrer um erro, adiciona um valor nulo ao dicionário de resultados
                    result[chave_nfe] = None

            return result
        except FileNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Erro ao ler e converter arquivos para JSON funcao read_and_convert_to_json_auto: {str(e)}")


    @staticmethod
    def _read_codes_from_txt_online_upload(file: SpooledTemporaryFile) -> List[str]:
        try:
            content = file.read().decode('utf-8')
            return [code.strip() for code in content.split(',') if code.strip()]
        except Exception as e:
            raise Exception(f"Erro ao ler códigos do arquivo TXT: {str(e)}")

    @staticmethod
    def _read_codes_from_csv_online_upload(file: SpooledTemporaryFile) -> List[str]:
        try:
            content = file.read().decode('utf-8')
            reader = csv.reader(content.splitlines())
            codes = [code.strip() for row in reader for code in row if code.strip()]
            return codes
        except Exception as e:
            raise Exception(f"Erro ao ler códigos do arquivo CSV: {str(e)}")

    @staticmethod
    def _read_codes_from_image_Barcode_online_upload(file: tempfile.SpooledTemporaryFile) -> Union[str, None]:
        try:
            print("Recebendo solicitação para processar arquivo.")

            temp_file_path = os.path.join(tempfile.gettempdir(), "temp_image.png")
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file.read())
            reader = BarCodeReader()
            barcode = reader.decode(temp_file_path)
            os.remove(temp_file_path)

            if barcode:
                print("Tipo:", barcode.format)
                print("Dados:", barcode.raw)

                return barcode.raw
            else:
                print("Código de barras não detectado.")
                return None

        except Exception as e:
            print(f"Erro durante o processamento do arquivo: {str(e)}")
            return None
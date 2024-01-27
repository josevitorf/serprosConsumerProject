from datetime import datetime
from typing import List
from pathlib import Path
import os

from PIL import Image
import pytesseract
from fastapi import HTTPException
import httpx
import csv

from pytesseract import pytesseract
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

    @staticmethod
    def read_and_convert_to_json_auto(file_path: str, authorization: str,language='pt') -> dict:
        try:
            # Obter a extensão do arquivo
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()

            if file_extension == ".txt":
                codes = SerprosServices._read_codes_from_txt(file_path)
            elif file_extension == ".csv":
                codes = SerprosServices._read_codes_from_csv(file_path)
            elif file_extension in (".jpg", ".jpeg", ".png", ".gif"):
                # Extrair texto da imagem
                extracted_text = SerprosServices.extract_text_from_image(file_path, language)

                # Chamar a API do Serpros com os códigos extraídos
                serpros_response = SerprosServices.obter_dados_nfe(extracted_text, authorization)

                # Retornar os resultados da API do Serpros
                return {
                    "codes": extracted_text,
                    "serpros_response": serpros_response,
                    "conversion_date": datetime.utcnow().isoformat()
                }
            else:
                raise Exception("Extensão de arquivo não suportada.")

            result = {
                "codes": codes,
                "conversion_date": datetime.utcnow().isoformat()
            }

            return result
        except Exception as e:
            raise Exception(f"Erro ao ler e converter arquivo para JSON: {str(e)}")




####################################### funcoes de extraçao de codigo ##############################################################

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

import json
from datetime import datetime
from typing import Dict, List

from PIL import Image
import pytesseract
from fastapi import FastAPI, HTTPException, Header
import httpx
import json
import csv

from pytesseract import pytesseract

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


######################################UPLOAD DE ARQUIVOS#############################
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
    def _read_text_from_image(file_path: str) -> List[str]:
        try:
            # Abrir a imagem
            image = Image.open(file_path)

            # Converta a imagem para escala de cinza
            image = image.convert('L')

            # Use o pytesseract para extrair o texto
            contents = pytesseract.image_to_string(image)

            return [code.strip() for code in contents.split(',') if code.strip()]
        except Exception as e:
            raise Exception(f"Erro ao ler texto da imagem: {str(e)}")
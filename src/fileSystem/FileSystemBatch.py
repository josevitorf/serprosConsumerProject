import datetime
import os
import csv
from typing import List, Union
import tempfile

from fastapi import FastAPI
import schedule
import time

app = FastAPI()


def processar_lote():
    # Lógica para consumir o sistema de arquivos em lote
    print("Consumindo o sistema de arquivos em lote...")
    diretorio = "/caminho/para/seu/diretorio"
    authorization = "sua_autorizacao"

    for nome_arquivo in os.listdir(diretorio):
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)
        if os.path.isfile(caminho_arquivo):
            _, extensao_arquivo = os.path.splitext(nome_arquivo.lower())
            if extensao_arquivo in ['.txt', '.csv']:
                with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                    if extensao_arquivo == '.txt':
                        codes = _read_codes_from_txt_online_upload(arquivo)
                    elif extensao_arquivo == '.csv':
                        codes = _read_codes_from_csv_online_upload(arquivo)

                    for chave_nfe in codes:
                        try:
                            dados_nfe = obter_dados_nfe(chave_nfe, authorization)
                            # Faça algo com os dados da NF-e...
                        except Exception as e:
                            print(f"Erro ao obter dados da NF-e {chave_nfe}: {str(e)}")
            elif extensao_arquivo in ['.jpg', '.jpeg', '.png', '.gif']:
                with open(caminho_arquivo, 'rb') as arquivo:
                    extracted_text = _read_codes_from_image_Barcode_online_upload(arquivo)
                    if extracted_text:
                        serpros_response = obter_dados_nfe(extracted_text, authorization)
                        # Faça algo com os dados da NF-e...
                    else:
                        print("Código de barras não detectado.")


def _read_codes_from_txt_online_upload(arquivo) -> List[str]:
    try:
        content = arquivo.read().decode('utf-8')
        return [code.strip() for code in content.split(',') if code.strip()]
    except Exception as e:
        raise Exception(f"Erro ao ler códigos do arquivo TXT: {str(e)}")

def _read_codes_from_csv_online_upload(arquivo) -> List[str]:
    try:
        content = arquivo.read().decode('utf-8')
        reader = csv.reader(content.splitlines())
        codes = [code.strip() for row in reader for code in row if code.strip()]
        return codes
    except Exception as e:
        raise Exception(f"Erro ao ler códigos do arquivo CSV: {str(e)}")

def obter_dados_nfe(chave_nfe: str, authorization: str):
    try:
        # Lógica para obter dados da NF-e com base na chave
        return {"dados": f"Dados da NF-e com chave {chave_nfe}"}
    except Exception as e:
        raise Exception(f"Erro ao obter dados da NF-e {chave_nfe}: {str(e)}")

def _read_codes_from_image_Barcode_online_upload(arquivo) -> Union[str, None]:
    try:
        print("Recebendo solicitação para processar arquivo.")

        temp_file_path = os.path.join(tempfile.gettempdir(), "temp_image.png")
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(arquivo.read())

        # Aqui você deve ter a lógica para extrair o código de barras da imagem
        # Por exemplo, usar uma biblioteca como OpenCV para processar a imagem
        extracted_text = "1234567890"  # Exemplo de código de barras extraído

        os.remove(temp_file_path)

        if extracted_text:
            print("Código de barras detectado:", extracted_text)
            return extracted_text
        else:
            print("Código de barras não detectado.")
            return None

    except Exception as e:
        print(f"Erro durante o processamento do arquivo: {str(e)}")
        return None



# Rota para acionar o processamento em lotes
@app.get("/processar-lote")
def trigger_batch_processing():
    processar_lote()
    return {"message": "Processamento em lote iniciado"}


# Agendar a execução da função diariamente às 00:00h
schedule.every().day.at("00:00").do(processar_lote)


# Agendar a execução da função nas segundas, quartas e sextas-feiras às 00:00h
def schedule_batch_processing():
    hoje = datetime.datetime.now()
    dia_semana = hoje.weekday()
    if dia_semana in [0, 2, 4]:  # Segunda-feira (0), Quarta-feira (2), Sexta-feira (4)
        schedule.every().monday.at("00:00").do(processar_lote)


# Função para rodar o agendador
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Rodar o agendador em uma thread separada
import threading

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

# Iniciar o agendamento imediatamente após a inicialização do aplicativo
schedule_batch_processing()

import os
import shutil
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import List, Union
from zxing import BarCodeReader
import requests
import json

class FileHandler(FileSystemEventHandler):
    def __init__(self, input_dir, process_dir, output_dir, authorization):
        self.input_dir = input_dir
        self.process_dir = process_dir
        self.output_dir = output_dir
        self.authorization = authorization

    def on_created(self, event):
        if event.is_directory:
            return

        file_name = os.path.basename(event.src_path)
        _, file_extension = os.path.splitext(file_name)

        if file_extension.lower() in (".txt", ".csv", ".jpg", ".jpeg", ".png", ".gif"):
            self.process_file(event.src_path)

    def process_file(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            _, file_extension = os.path.splitext(file_name)

            if file_extension.lower() == ".txt":
                codes = self._read_codes_from_txt_online_upload(file_path)
            elif file_extension.lower() == ".csv":
                codes = self._read_codes_from_csv_online_upload(file_path)
            elif file_extension.lower() in (".jpg", ".jpeg", ".png", ".gif"):
                codes = self._read_codes_from_image_Barcode_online_upload(file_path)
                self._call_serpros_api_and_save_results(codes, file_name)
            else:
                raise Exception("Extensão de arquivo não suportada.")

            # Move o arquivo para a pasta de processamento com o nome alterado
            destination = os.path.join(self.process_dir, f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file_name}")
            shutil.move(file_path, destination)
            print(f"Arquivo movido para {destination}")

        except FileNotFoundError:
            raise
        except Exception as e:
            print(f"Erro ao processar o arquivo: {str(e)}")

    def _read_codes_from_txt_online_upload(self, file_path) -> List[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return [code.strip() for code in content.split(',') if code.strip()]
        except Exception as e:
            raise Exception(f"Erro ao ler códigos do arquivo TXT: {str(e)}")

    def _read_codes_from_csv_online_upload(self, file_path) -> List[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                codes = [code.strip() for row in reader for code in row if code.strip()]
            return codes
        except Exception as e:
            raise Exception(f"Erro ao ler códigos do arquivo CSV: {str(e)}")

    def _read_codes_from_image_Barcode_online_upload(self, file_path) -> Union[str, None]:
        try:
            print("Recebendo solicitação para processar arquivo.")
            reader = BarCodeReader()
            barcode = reader.decode(file_path)

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

    def _call_serpros_api_and_save_results(self, codes, file_name):
        try:
            for code in codes:
                url = f"https://gateway.apiserpro.serpro.gov.br/consulta-nfe-df-trial/api/v1/nfe/{code}"

                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': self.authorization
                }

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    json_response = response.json()

                    # Salva a resposta JSON no diretório de output
                    output_file_path = os.path.join(self.output_dir, f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{code}_response.json")
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        json.dump(json_response, output_file, ensure_ascii=False, indent=2)

                    print(f"Resposta JSON salva em {output_file_path}")
                else:
                    raise Exception(f"Erro ao chamar a API do Serpros - Status Code: {response.status_code}, Detalhes: {response.text}")

        except Exception as e:
            raise Exception(f"Erro ao chamar a API do Serpros: {str(e)}")

def monitor_directory(input_dir, process_dir, output_dir, authorization):
    event_handler = FileHandler(input_dir, process_dir, output_dir, authorization)
    observer = Observer()
    observer.schedule(event_handler, path=input_dir, recursive=False)
    observer.start()

    try:
        print(f"Monitorando o diretório: {input_dir}")
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    input_directory = "C:\\Users\\Josev\\OneDrive\\Documentos\\docs"
    process_directory = "C:\\Users\\Josev\\OneDrive\\Documentos\\process"
    output_directory = "C:\\Users\\Josev\\OneDrive\\Documentos\\output"
    authorization_token = "your_authorization_token"

    # Certifique-se de que os diretórios de processamento e output existam
    for directory in [process_directory, output_directory]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    monitor_directory(input_directory, process_directory, output_directory, authorization_token)

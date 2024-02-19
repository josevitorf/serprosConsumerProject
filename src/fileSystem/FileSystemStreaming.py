import asyncio
import os
from fastapi import FastAPI
from typing import List

app = FastAPI()

async def ler_arquivos_em_tempo_real(diretorio: str) -> List[str]:
    while True:
        arquivos = os.listdir(diretorio)
        print("Arquivos no diretório:", arquivos)
        # Lógica para processar os arquivos conforme necessário
        await asyncio.sleep(10)  # Espera por 10 segundos antes de verificar novamente

@app.on_event("startup")
async def startup_event():
    diretorio = "/caminho/para/seu/diretorio"
    # Inicia a tarefa assíncrona de leitura de arquivos em tempo real
    asyncio.create_task(ler_arquivos_em_tempo_real(diretorio))

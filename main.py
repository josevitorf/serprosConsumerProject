# main.py
from fastapi import FastAPI
from src.controllers.serpros_controller import router as serpros_router  # Ajuste na importação

app = FastAPI()

#https://apicenter.estaleiro.serpro.gov.br/documentacao/consulta-nfe/pt/chamadas/demonstracao/

app.include_router(serpros_router, prefix="/nfs", tags=["nfs"])

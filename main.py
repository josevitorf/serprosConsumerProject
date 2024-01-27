# main.py
from fastapi import FastAPI
from src.controllers.serpros_controller import router as serpros_router  # Ajuste na importação
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Configuração CORS para permitir chamadas a partir de qualquer origem
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#https://apicenter.estaleiro.serpro.gov.br/documentacao/consulta-nfe/pt/chamadas/demonstracao/

# Adicione o middleware CORS ao aplicativo principal (app)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


app.include_router(serpros_router, prefix="/nfs", tags=["nfs"])

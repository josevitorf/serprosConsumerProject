from fastapi import FastAPI

from src.controllers.serpros_controller import router as serpros_router

from src.controllers.SerprosCNPJ_Controller import router as SerprosCNPJ_router
from src.controllers.SerprosNFEs_Controller import router as SerprosNFE_router
from src.controllers.SerprosCPF_Controller import router as SerprosCPF_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# https://apicenter.estaleiro.serpro.gov.br/documentacao/consulta-nfe/pt/chamadas/demonstracao/
# https://apicenter.estaleiro.serpro.gov.br/documentacao/


app.include_router(serpros_router, tags=["nfs"])
app.include_router(SerprosCNPJ_router, tags=["cnpj"])
app.include_router(SerprosNFE_router, tags=["nfe"])
app.include_router(SerprosCPF_router, tags=["cpf"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

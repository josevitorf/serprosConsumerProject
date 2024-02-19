from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Crie uma pasta 'templates' no mesmo diretório do seu código e coloque seus arquivos HTML lá

@app.get("/message2")
def read_users2():
    return {"Bem Vindo ao projeto Serpros"}

@app.get("/processar-nota-fiscal-front", methods=["GET", "POST"], response_class=HTMLResponse)
async def processar_nota_fiscal(request: Request):
    if request.method == "POST":
        form_data = await request.form()
        chave_nfe = form_data["chave_nfe"]
        # Aqui você pode processar a chave da nota fiscal, fazer chamadas a serviços externos, etc.
        # Por enquanto, vamos apenas passar os dados recebidos de volta para o HTML
        dados_nfe = {
            "nProt": "123456",
            "Id": "789",
            "emit": {
                "xNome": "Emitente",
                "enderEmit": {
                    "xLgr": "Endereço",
                    "nro": "123",
                    "xMun": "Cidade",
                    "UF": "UF"
                }
            },
            "dest": {
                "xNome": "Destinatário",
                "enderDest": {
                    "xLgr": "Endereço",
                    "nro": "456",
                    "xMun": "Cidade",
                    "UF": "UF"
                }
            }
        }
        return templates.TemplateResponse("resultado.html", {"request": request, "chave_nfe": chave_nfe, "dados_nfe": dados_nfe})
    else:
        # Se o método for GET, retorne uma página com o formulário
        return templates.TemplateResponse("index.html", {"request": request})
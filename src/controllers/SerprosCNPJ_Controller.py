from fastapi import APIRouter, Header, UploadFile, File, FastAPI, Request, HTTPException, Form, Request
import json
from fastapi.responses import JSONResponse
from src.SerprosAPI.APISerpros import SerprosAPI

router = APIRouter()


class SerprosCNPJ_Controller:

    @router.get("/dados-cnpj-online/{chave_cnpj}")
    async def obter_dados_nfe_endpoint_online(chave_cnpj: str,
                                              authorization: str = Header("Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")):
        try:
            dados_nfe = SerprosAPI.obter_dados_cnpj(chave_cnpj, authorization)
            return dados_nfe
        except HTTPException as e:
            raise e

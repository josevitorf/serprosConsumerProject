from fastapi import APIRouter, Header, UploadFile, File, FastAPI, Request, HTTPException, Form, Request
import json
from fastapi.responses import JSONResponse
from src.SerprosAPI.APISerpros import SerprosAPI

router = APIRouter()


class SerprosCPF_Controller:

    @router.get("/dados-cpf-online/{chave_cpf}")
    async def obter_dados_cpf_endpoint_online(chave_cpf: str,
                                              authorization: str = Header("Bearer 06aef429-a981-3ec5-a1f8-71d38d86481e")):
        try:
            dados_nfe = SerprosAPI.obter_dados_cpf(chave_cpf, authorization)
            return dados_nfe
        except HTTPException as e:
            raise e

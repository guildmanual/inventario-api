from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import asyncpg
import os
from typing import Optional

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

class ComputadorData(BaseModel):
    hostname: str
    sistema_operacional: str

@app.post("/api/inventario")
async def receber_dados(dados: ComputadorData, authorization: Optional[str] = Header(None)):
    if not authorization or authorization != "Bearer seu_token_aqui":
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute('''
            INSERT INTO computadores (hostname, sistema_operacional, ultima_coleta)
            VALUES ($1, $2, NOW())
            ON CONFLICT (hostname) DO UPDATE SET
            sistema_operacional = EXCLUDED.sistema_operacional,
            ultima_coleta = NOW()
        ''', dados.hostname, dados.sistema_operacional)
        await conn.close()
        return {"status": "sucesso", "mensagem": "Dados recebidos"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/")
async def root():
    return {"mensagem": "API Inventário Tech365 - BACEN"}

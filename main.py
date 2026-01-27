from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import asyncpg
import os
from typing import Optional

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

# Token fixo - SUBSTITUA pelo token correto (o que está no banco)
VALID_TOKEN = os.environ.get("VALID_TOKEN")  # Seguro!

class ComputadorData(BaseModel):
    hostname: str
    sistema_operacional: str
    usuario: Optional[str] = None
    memoria_gb: Optional[float] = None
    processador: Optional[str] = None

@app.post("/api/inventario")
async def receber_dados(dados: ComputadorData, authorization: Optional[str] = Header(None)):
    # Verificação simples do token
    if not authorization or authorization != f"Bearer {VALID_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute('''
            INSERT INTO computadores 
            (hostname, sistema_operacional, usuario, memoria_gb, processador, ultima_coleta)
            VALUES ($1, $2, $3, $4, $5, NOW())
            ON CONFLICT (hostname) DO UPDATE SET
            sistema_operacional = EXCLUDED.sistema_operacional,
            usuario = EXCLUDED.usuario,
            memoria_gb = EXCLUDED.memoria_gb,
            processador = EXCLUDED.processador,
            ultima_coleta = NOW()
        ''', 
        dados.hostname, dados.sistema_operacional, dados.usuario,
        dados.memoria_gb, dados.processador)
        
        await conn.close()
        return {"status": "sucesso", "mensagem": "Dados recebidos"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/api/computadores")
async def listar_computadores(authorization: Optional[str] = Header(None)):
    if not authorization or authorization != f"Bearer {VALID_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        computadores = await conn.fetch("SELECT * FROM computadores ORDER BY ultima_coleta DESC")
        await conn.close()
        return {"computadores": computadores}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/")
async def root():
    return {"mensagem": "API Inventário Tech365 - BACEN"}

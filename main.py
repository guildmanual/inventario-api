from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://guildmanual.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
VALID_TOKEN = os.environ.get("VALID_TOKEN")

class ComputadorData(BaseModel):
    hostname: str
    sistema_operacional: str
    usuario: Optional[str] = None
    memoria_gb: Optional[float] = None
    processador: Optional[str] = None

@app.post("/api/inventario")
async def receber_dados(dados: ComputadorData, authorization: Optional[str] = Header(None)):
    if not authorization or authorization != f"Bearer {VALID_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO computadores 
            (hostname, sistema_operacional, memoria_gb, processador, ultima_coleta)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (hostname) DO UPDATE SET
            sistema_operacional = EXCLUDED.sistema_operacional,
            memoria_gb = EXCLUDED.memoria_gb,
            processador = EXCLUDED.processador,
            ultima_coleta = NOW()
        ''', 
        (dados.hostname, dados.sistema_operacional,
         dados.memoria_gb, dados.processador))
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "sucesso", "mensagem": "Dados recebidos"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/api/computadores")
async def listar_computadores(authorization: Optional[str] = Header(None)):
    if not authorization or authorization != f"Bearer {VALID_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM computadores ORDER BY ultima_coleta DESC")
        computadores = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"computadores": computadores}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
# ========== NOVAS ROTAS ==========

@app.get("/api/historico")
def get_historico(authorization: Optional[str] = Header(None)):
    if not authorization or authorization != f"Bearer {VALID_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM computadores ORDER BY ultima_coleta DESC")
        historico = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"historico": historico}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/api/ativos")
def get_ativos(authorization: Optional[str] = Header(None)):
    if not authorization or authorization != f"Bearer {VALID_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT DISTINCT ON (hostname) *
            FROM computadores 
            ORDER BY hostname, ultima_coleta DESC
        """)
        ativos = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"ativos": ativos}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
        
@app.get("/")
async def root():
    return {"mensagem": "API Inventário Tech365 - BACEN"}

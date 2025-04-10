from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import os

app = FastAPI(
    title="API de Contratos por E-mail",
    description="Recebe uma lista de contratos com até 4 e-mails e devolve os contratos agrupados por e-mail.",
    version="1.0.0"
)

class Contrato(BaseModel):
    titulo: str
    email1: Optional[str] = None
    email2: Optional[str] = None
    email3: Optional[str] = None
    email4: Optional[str] = None
    termo: Optional[str] = None
    fornecedor: Optional[str] = None

@app.post("/agrupar-por-email")
def agrupar_por_email(contratos: List[Contrato]) -> Dict[str, List[dict]]:
    resultado = {}
    for contrato in contratos:
        contrato_data = {
            "titulo": contrato.titulo,
            "termo": contrato.termo,
            "fornecedor": contrato.fornecedor
        }
        for email in [contrato.email1, contrato.email2, contrato.email3, contrato.email4]:
            if email:
                if email not in resultado:
                    resultado[email] = []
                resultado[email].append(contrato_data)
    return resultado

# Root endpoint to confirm the API is running
@app.get("/")
def read_root():
    return {"status": "online", "message": "API de Contratos está em execução"}

# Only run the server when executing locally
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
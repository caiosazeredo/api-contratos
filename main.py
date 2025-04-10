from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import io
from datetime import datetime
import xlsxwriter  # You'll need to add this to requirements.txt

app = FastAPI(
    title="API de Contratos por E-mail com Geração de Excel",
    description="Recebe uma lista de contratos e devolve um arquivo Excel com os contratos agrupados por e-mail.",
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
    dataVencimento: Optional[str] = None  # Add this field for vencimento date

@app.post("/agrupar-por-email")
def agrupar_por_email(contratos: List[Contrato]) -> Dict[str, List[dict]]:
    resultado = {}
    for contrato in contratos:
        contrato_data = {
            "titulo": contrato.titulo,
            "termo": contrato.termo,
            "fornecedor": contrato.fornecedor,
            "dataVencimento": contrato.dataVencimento
        }
        for email in [contrato.email1, contrato.email2, contrato.email3, contrato.email4]:
            if email:
                if email not in resultado:
                    resultado[email] = []
                resultado[email].append(contrato_data)
    return resultado

@app.post("/gerar-excel")
def gerar_excel(contratos: List[Contrato]) -> Response:
    # First, group the contracts by email
    resultado = {}
    for contrato in contratos:
        contrato_data = {
            "titulo": contrato.titulo,
            "termo": contrato.termo,
            "fornecedor": contrato.fornecedor,
            "dataVencimento": contrato.dataVencimento
        }
        for email in [contrato.email1, contrato.email2, contrato.email3, contrato.email4]:
            if email:
                if email not in resultado:
                    resultado[email] = []
                resultado[email].append(contrato_data)
    
    # Create an in-memory Excel file
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Contratos")
    
    # Add headers with formatting
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1
    })
    
    headers = ['Email', 'Número de Contratos', 'Contratos', 'Termos', 
               'Fornecedores', 'Data de Vencimento', 'Status']
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Add data rows
    row = 1
    for email, contratos in resultado.items():
        worksheet.write(row, 0, email)
        worksheet.write(row, 1, len(contratos))
        
        # Join the contract titles, terms, and vendors
        contratos_titulos = ", ".join([c["titulo"] for c in contratos])
        worksheet.write(row, 2, contratos_titulos)
        
        termos = ", ".join([c["termo"] for c in contratos if c["termo"]])
        worksheet.write(row, 3, termos)
        
        fornecedores = ", ".join([c["fornecedor"] for c in contratos if c["fornecedor"]])
        worksheet.write(row, 4, fornecedores)
        
        # Add vencimento dates if available, otherwise leave blank
        datas_vencimento = ", ".join([c["dataVencimento"] for c in contratos if c.get("dataVencimento")])
        worksheet.write(row, 5, datas_vencimento)
        
        # Status column - can be customized based on your logic
        # For example, if date is past due, mark as "Vencido", otherwise "Pendente"
        status = "Pendente"  # Default status
        worksheet.write(row, 6, status)
        
        row += 1
    
    # Auto-adjust column widths
    for i, header in enumerate(headers):
        worksheet.set_column(i, i, max(len(header) + 2, 15))
    
    workbook.close()
    
    # Prepare the response with the Excel file
    output.seek(0)
    
    # Generate a filename with the current date
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"Contratos_Vencimentos_{today}.xlsx"
    
    # Return the Excel file as a response
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

# 🚀 Inicia o servidor automaticamente ao rodar o script
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
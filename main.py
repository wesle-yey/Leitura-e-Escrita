from fastapi import FastAPI, File, UploadFile, HTTPException
from io import BytesIO
from fastapi.responses import HTMLResponse
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return HTMLResponse(content=open("static/home.html", "r").read(), status_code=200)

@app.post("/upload")
async def upload_excel(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        # Verifica se é Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            results.append({"filename": file.filename, "error": "Não é arquivo Excel"})
            continue
        
        try:
            # Lê o arquivo
            contents = await file.read()
            df = pd.read_excel(BytesIO(contents))
            
            # Limpa NaN e converte para dict
            df = df.fillna('')
            data = df.to_dict('records')
            
            results.append({"filename": file.filename, "data": data})
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})
    
    return {"results": results}

@app.post("/uploadtest")
async def upload_excel(files: List[UploadFile] = File(...)):
    results = []
    linhas_para_pular_leitura = [0, 1, 2, 3, 4, 5, 12, 17, 20, 21, 22, *range(23, 45)]
    cols_leitura= list(range(0, 14))

    columns_leitura=[
    "ano",
    "total alunos",
    "nl",
    "%",
    "ls",
    "%",
    "lp",
    "%",
    "lf",
    "%",
    "lsf",
    "%",
    "lcf",
    "%"
]
    linhas_para_pular_escrita = [*range(0, 27), 33, 38, 41, 42, 43, 44]
    cols_escrita= list(range(0, 12))

    columns_escrita=[
    "ano",
    "total alunos",
    "p",
    "%",
    "s",
    "%",
    "s.a.",
    "%",
    "a",
    "%",
    "o",
    "%"
]
    for file in files:
        # Verifica se é Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            results.append({"filename": file.filename, "error": "Não é arquivo Excel"})
            continue
        #leitura
        try:
            contents = await file.read()
            df = pd.read_excel(BytesIO(contents),
                               skiprows=linhas_para_pular_leitura,
                               usecols=cols_leitura,)
            df.columns= columns_leitura
            
            # Limpa NaN e converte para dict
            df = df.fillna('')
            data = df.to_dict('records')
            
            results.append({"filename": file.filename, "tipo": "Leitura", "data": data})
            
        #escrita
            df = pd.read_excel(BytesIO(contents),
                               skiprows=linhas_para_pular_escrita,
                               usecols=cols_escrita,)
            df.columns= columns_escrita
            
            # Limpa NaN e converte para dict
            df = df.fillna('')
            data = df.to_dict('records')
            
            results.append({"filename": file.filename, "tipo": "Escrita", "data": data})
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})
    
    return {"results": results,}
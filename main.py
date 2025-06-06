from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from operations import operations as op

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
    for file in files:
        # Verifica se é Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            return {"error": f"Envie apenas arquivos excel (xlsx ou xls): {str(e)}"}
    try:
        results = await op.gerar_tabela(files)
        return {"results": results}
    except Exception as e:
        return {"error": f"Erro no processamento: {str(e)}"}
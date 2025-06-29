
from fastapi import UploadFile
from typing import List
from io import BytesIO
import pandas as pd

async def gerar_tabela_do_polo(files: List[UploadFile]):
    results = []
    all_leitura_dfs = []
    all_escrita_dfs = []
    linhas_para_pular_leitura = [0, 1, 2, 3, 4, 5, 12, 17, 20, 21, 22, *range(23, 45)]
    linhas_para_pular_escrita = [*range(0, 27), 33, 38, 41, 42, 43, 44]
    cols_leitura = list(range(0, 14))
    cols_escrita = list(range(0, 12))
    columns_leitura = ["ano", "total alunos", "nl", "nl%", "ls", "ls%", "lp", "lp%", "lf", "lf%", "lsf", "lsf%", "lcf", "lcf%"]
    columns_escrita = ["ano", "total alunos", "p", "p%", "s", "s%", "s.a.", "s.a%", "a", "a%", "o", "o%"]
    
    for file in files:
        # Verifica se é Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            results.append({"filename": file.filename, "error": "Não é arquivo Excel"})
            continue
            
        try:
            # Lê o conteúdo do arquivo
            contents = await file.read()
            
            # Processamento de Leitura
            df_leitura= criar_dataframe(arquivo_em_bytes=contents, linhas_a_serem_puladas=linhas_para_pular_leitura, colunas_a_serem_usadas=cols_leitura)
            df_leitura.columns = columns_leitura
            df_leitura = df_leitura.fillna(0)  # Mudei para 0 para permitir soma
            df_leitura['arquivo_origem'] = file.filename
            all_leitura_dfs.append(df_leitura)
            
            # Processamento de Escrita
            df_escrita= criar_dataframe(arquivo_em_bytes=contents, linhas_a_serem_puladas=linhas_para_pular_escrita, colunas_a_serem_usadas=cols_escrita)
            df_escrita.columns = columns_escrita
            df_escrita = df_escrita.fillna(0)
            df_escrita['arquivo_origem'] = file.filename
            all_escrita_dfs.append(df_escrita)
            
        except Exception as e:
            results.append({
                "filename": file.filename, 
                "error": f"Erro ao processar arquivo: {str(e)}"
            })
    
    # Concatena todos os DataFrames
    if all_leitura_dfs:
        df_leitura_consolidado = pd.concat(all_leitura_dfs, ignore_index=True)
        
        # Soma por ano (ou outro critério que você precisar)
        df_leitura_soma = df_leitura_consolidado.groupby('ano').agg({
            'total alunos': 'sum',
            'nl': 'sum',
            'ls': 'sum', 
            'lp': 'sum',
            'lf': 'sum',
            'lsf': 'sum',
            'lcf': 'sum'
        }).reset_index()
        
        # Recalcula percentuais (evitando divisão por zero)
        total_col = df_leitura_soma['total alunos'] 
        df_leitura_soma['nl_%'] = (df_leitura_soma['nl'] / total_col * 100).fillna(0).round(2)
        df_leitura_soma['ls_%'] = (df_leitura_soma['ls'] / total_col * 100).fillna(0).round(2)
        df_leitura_soma['lp_%'] = (df_leitura_soma['lp'] / total_col * 100).fillna(0).round(2)
        df_leitura_soma['lf_%'] = (df_leitura_soma['lf'] / total_col * 100).fillna(0).round(2)
        df_leitura_soma['lsf_%'] = (df_leitura_soma['lsf'] / total_col * 100).fillna(0).round(2)
        df_leitura_soma['lcf_%'] = (df_leitura_soma['lcf'] / total_col * 100).fillna(0).round(2)
        
        # Remove qualquer NaN restante
        df_leitura_soma = df_leitura_soma.fillna(0)
        
        results.append({
            "tipo": "Leitura",
            "data": df_leitura_soma.to_dict('records')
        })
    
    if all_escrita_dfs:
        df_escrita_consolidado = pd.concat(all_escrita_dfs, ignore_index=True)
        
        # Soma por ano
        df_escrita_soma = df_escrita_consolidado.groupby('ano').agg({
            'total alunos': 'sum',
            'p': 'sum',
            's': 'sum',
            's.a.': 'sum',
            'a': 'sum',
            'o': 'sum'
        }).reset_index()
        
        # Recalcula percentuais (evitando divisão por zero)
        total_col = df_escrita_soma['total alunos']
        df_escrita_soma['p_%'] = (df_escrita_soma['p'] / total_col * 100).fillna(0).round(2)
        df_escrita_soma['s_%'] = (df_escrita_soma['s'] / total_col * 100).fillna(0).round(2)
        df_escrita_soma['s.a._%'] = (df_escrita_soma['s.a.'] / total_col * 100).fillna(0).round(2)
        df_escrita_soma['a_%'] = (df_escrita_soma['a'] / total_col * 100).fillna(0).round(2)
        df_escrita_soma['o_%'] = (df_escrita_soma['o'] / total_col * 100).fillna(0).round(2)
        
        # Remove qualquer NaN restante
        df_escrita_soma = df_escrita_soma.fillna(0)
        
        results.append({
            "tipo": "Escrita Escrita", 
            "data": df_escrita_soma.to_dict('records')
        })
    return results

##### TODO
#JUNTAR LEITURA E ESCRITA
#GERAR TABELA EXCEL
#ENVIAR VIA JSON TABELA EXCEL PARA O FRONT/BAIXAR

def criar_dataframe(arquivo_em_bytes, linhas_a_serem_puladas, colunas_a_serem_usadas):
    df = pd.read_excel(BytesIO(arquivo_em_bytes), 
                       skiprows=linhas_a_serem_puladas,
                       usecols=colunas_a_serem_usadas)
    return df
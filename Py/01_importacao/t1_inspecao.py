import pandas as pd
import numpy as np
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Tarefa 1 — Importação e inspeção
arquivos = {
    "Tabela_CIDagrupado" : "CID_agrupado.csv", 
    "Tabela_MunicipioIBGE" : "municipios_ibge.csv", 
    "Tabela_SIM23" : "sim_2023_sp_ba_sc.csv", 
    "Tabela_Dicionario" : "vars_label.csv", 
    "Tabela_Geografico" : "geos.csv",
    "Tabela_CID" : "CID.csv" 
    }
    
def analisar_tabela(nome_tabela, caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, encoding='utf-8')
    
    print("-" * 50)
    print(f"ANÁLISE DA TABELA: {nome_tabela.upper()}")
    print("-" * 50)
    
    linhas, colunas = df.shape
    print(f"• Número de linhas: {linhas}")
    print(f"• Número de colunas: {colunas}\n")
    
    print("• Detalhes das Variáveis ausentes:")
    
    info_df = pd.DataFrame({
        'Tipo': df.dtypes,
        '% Ausentes': (df.isnull().sum() / linhas) * 100
    })
    
    info_df['Classificação'] = np.where(
        info_df['Tipo'].isin([np.dtype('int64'), np.dtype('float64'), np.dtype('int32'), np.dtype('float32')]), 
        'Numérica', 
        'Categórica'
    )
    
    info_df['% Ausentes'] = info_df['% Ausentes'].map("{:.2f}%".format)
    print(info_df)
    print("\n" + "="*50 + "\n")

for nome, caminho in arquivos.items():
    try:
        analisar_tabela(nome, caminho)
    except Exception as e:
        print(f"Erro ao processar a {nome}: {e}")

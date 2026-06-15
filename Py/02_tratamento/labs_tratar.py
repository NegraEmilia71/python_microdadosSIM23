import pandas as pd
import numpy as np
import os

caminho_base_sim = "dado/cru/sim_2023_sp_ba_sc.csv"
caminho_vars_label = "dado/cru/vars_label.csv"

def construir_dicionarios_mapeamento(caminho_vars_label):
    df_labels = pd.read_csv(caminho_vars_label)
    
    dict_raca = {"1": "Branca", "2": "Preta", "3": "Amarela", "4": "Parda", "5": "Indígena", "9": "Ignorado"}
    dict_uf = {"29": "Bahia", "42": "Santa Catarina", "35": "São Paulo"}
    
    mapas_completos = {
        "RACACOR": dict_raca,
        "CODMUNRES": dict_uf  
    }
    return mapas_completos

def pipeline_tratamento_rotulos(caminho_sim, caminho_vars_label):
    mapas_traducao = construir_dicionarios_mapeamento(caminho_vars_label)
    
    chunks = pd.read_csv(caminho_sim, low_memory=False, chunksize=100000)
    primeiro_bloco = True
    
    for idx, chunk in enumerate(chunks, start=1):
        for col_alvo, dicionario in mapas_traducao.items():
            if col_alvo in chunk.columns:
                chunk[f'{col_alvo}_limpa'] = chunk[col_alvo].astype(str).str.split('.').str[0].str.strip()
                chunk[f'{col_alvo}_DESC'] = chunk[f'{col_alvo}_limpa'].map(dicionario)
                chunk[f'{col_alvo}_DESC'] = chunk[f'{col_alvo}_DESC'].fillna('Não Declarado')
                chunk.drop(columns=[f'{col_alvo}_limpa'], inplace=True)
        
        diretorio_saida = "dado/processado/sim_2023_base.csv"
        os.makedirs(os.path.dirname(diretorio_saida), exist_ok=True)
        
        if primeiro_bloco:
            chunk.to_csv(diretorio_saida, index=False, mode='w', encoding='utf-8')
            primeiro_bloco = False
        else:
            chunk.to_csv(diretorio_saida, index=False, mode='a', header=False, encoding='utf-8')
        
try:
    pipeline_tratamento_rotulos(caminho_base_sim, caminho_vars_label)
except Exception as e:
    print(f"Erro no pipeline de tradução: {e}")
    
# Tarefa 3 — Tratamento da idade: Faixa Etária

import pandas as pd
import numpy as np
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def processar_idade_por_pedacos(caminho_arquivo, coluna_idade='IDADE'):
    bins = [-1, 1, 5, 15, 60, 200]
    labels = ['Menor de 1 ano', '1 a 4 anos', '5 a 14 anos', '15 a 59 anos', '60 anos ou mais']
    contagem_total_faixas = pd.Series(0, index=labels)
    pedacos = pd.read_csv(caminho_arquivo, low_memory=False, chunksize=100000)
    
    for i, chunk in enumerate(pedacos, start=1):
            
        idade_str = chunk[coluna_idade].astype(str).str.split('.').str[0].str.zfill(3)
        idade_anos = pd.Series(np.nan, index=chunk.index)
        
        for idx, cod in idade_str.items():
            if cod in ['000', '999', 'nan']:
                continue
                
            cod_int = int(cod)
            
            # Minutos
            if 1 <= cod_int <= 60:
                idade_anos.loc[idx] = cod_int / (60 * 24 * 365)
            elif cod_int == 100:
                idade_anos.loc[idx] = 30 / (60 * 24 * 365) 
                
            # Horas
            elif 101 <= cod_int <= 123:
                idade_anos.loc[idx] = (cod_int - 100) / (24 * 365)
            elif cod_int == 200:
                idade_anos.loc[idx] = 12 / (24 * 365) 
                
            # Dias
            elif 201 <= cod_int <= 229:
                idade_anos.loc[idx] = (cod_int - 200) / 365
            elif cod_int == 300:
                idade_anos.loc[idx] = 15 / 365 
                
            # Meses
            elif 301 <= cod_int <= 311:
                idade_anos.loc[idx] = (cod_int - 300) / 12
            elif cod_int == 400:
                idade_anos.loc[idx] = 0.5 
                
            # Anos
            elif 401 <= cod_int <= 599:
                idade_anos.loc[idx] = float(cod_int - 400)
        
        faixas_bloco = pd.cut(idade_anos, bins=bins, labels=labels, right=False)
             
        contagem_total_faixas = contagem_total_faixas.add(faixas_bloco.value_counts(), fill_value=0)
    
    print("\n" + "="*50)
    print("DISTRIBUIÇÃO POR FAIXA ETÁRIA (CONTAGEM REAL)")
    print("="*50)
    print(contagem_total_faixas.astype(int))
    
    print("\n" + "="*50)
    print("PROPORÇÃO POR FAIXA ETÁRIA (PERCENTUAL GLOBAL)")
    print("="*50)
    proporcao = (contagem_total_faixas / contagem_total_faixas.sum()) * 100
    print(proporcao.map("{:.2f}%".format))
    print("="*50 + "\n")

arquivo_alvo = "sim_2023_sp_ba_sc.csv"
try:
    processar_idade_por_pedacos(arquivo_alvo)
except Exception as e:
    print(f"Ocorreu um erro ao rodar o script: {e}")
    
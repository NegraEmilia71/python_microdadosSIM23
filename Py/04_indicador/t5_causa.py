# Tarefa 5 - Causas externas, mortes não naturais e circunstâncias do óbito

import pandas as pd
import numpy as np
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

caminho_base_sim = "dado/processado/sim_2023_base.csv"
def gerar_arquivo_causas_externas(caminho_sim):
    total_registros_salvos = 0
    total_com_acidtrab = 0
    casos_divergentes = 0
    
    primeiro_bloco = True
    chunks = pd.read_csv(caminho_sim, low_memory=False, chunksize=100000)
    
    for idx, chunk in enumerate(chunks, start=1):
        chunk['cid_inicial'] = chunk['CAUSABAS'].astype(str).str.strip().str[:1].str.upper()
        chunk['circ_limpa'] = chunk['CIRCOBITO'].astype(str).str.split('.').str[0].str.strip()
        chunk['acid_limpa'] = chunk['ACIDTRAB'].astype(str).str.split('.').str[0].str.strip()
        
        condicao_cid = chunk['cid_inicial'].isin(['V', 'W', 'X', 'Y'])
        
        condicao_circ = chunk['circ_limpa'].isin(['1', '2', '3', '4'])
        
        condicao_trabalho = chunk['acid_limpa'] == '1'
        
        df_externas_bloco = chunk[condicao_cid | condicao_circ | condicao_trabalho].copy()
        
        total_registros_salvos += len(df_externas_bloco)
        total_com_acidtrab += condicao_trabalho.sum()
        
        divergencias_bloco = chunk[(~condicao_cid) & condicao_circ]
        casos_divergentes += len(divergencias_bloco)
        
        os.makedirs("output/resultado", exist_ok=True)
        caminho_saida = os.path.join("output/resultado/causas_externas.csv")
        
        if primeiro_bloco:
            df_externas_bloco.to_csv(caminho_saida, index=False, mode='w', encoding='utf-8')
            primeiro_bloco = False
        else:
            df_externas_bloco.to_csv(caminho_saida, index=False, mode='a', header=False, encoding='utf-8')
                    
    print("\n" + "="*60)
    print("RELATÓRIO FINAL DE MÉTRICAS — TAREFA 5")
    print("="*60)
    print(f"• Total de registros salvos em 'causas_externas.csv': {total_registros_salvos:,}")
    print(f"• Quantidade de registros com ACIDTRAB ativo (1):     {total_com_acidtrab:,}")
    print(f"• Casos de divergência detectados (CID vs CIRCOBITO): {casos_divergentes:,}")
    print("="*60)
    print(f" Arquivo gerado perfeitamente em: {caminho_saida}\n")

try:
    gerar_arquivo_causas_externas(caminho_base_sim)
except Exception as e:
    print(f"Erro ao gerar o arquivo de causas externas: {e}")
    
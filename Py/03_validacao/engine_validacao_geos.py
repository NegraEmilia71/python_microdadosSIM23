# Tarefa 6 — Análise comparativa entre UFs

import pandas as pd
import numpy as np

def calcular_estatisticas_geos(caminho_sim, ufs_desafio):
    volumetria_uf = {uf: 0 for uf in ufs_desafio}
    municipios_por_uf = {uf: set() for uf in ufs_desafio}
    inconsistencias_por_uf = {uf: 0 for uf in ufs_desafio}
    
    chunks = pd.read_csv(caminho_sim, low_memory=False, chunksize=100000)
    
    for chunk in chunks:
        if 'NO_UF' in chunk.columns:
            col_uf = 'NO_UF'
        elif 'UF' in chunk.columns:
            col_uf = 'UF'
        else:
            col_uf = chunk.columns[0]
            
        chunk[col_uf] = chunk[col_uf].fillna('IGNORADO').astype(str).str.strip().str.upper()
        
        if 'CODMUNRES' in chunk.columns:
            chunk['CODMUNRES_str'] = chunk['CODMUNRES'].astype(str).str.split('.').str[0].str.strip().str.zfill(6)
        else:
            chunk['CODMUNRES_str'] = '000000'
        
        for _, row in chunk.iterrows():
            uf_linha = row[col_uf]
            cod_mun = row['CODMUNRES_str']
            
            if uf_linha in volumetria_uf:
                volumetria_uf[uf_linha] += 1
                municipios_por_uf[uf_linha].add(cod_mun)
                
                prefixos_uf = {'SP': '35', 'BA': '29', 'SC': '42'}
                if not cod_mun.startswith(prefixos_uf[uf_linha]):
                    inconsistencias_por_uf[uf_linha] += 1
                    
    return volumetria_uf, municipios_por_uf, inconsistencias_por_uf

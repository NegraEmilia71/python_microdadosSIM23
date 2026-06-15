# Tarefa 4 — Classificação das causas de morte

import pandas as pd
import numpy as np
import os

caminho_base_sim = "dado/processado/sim_2023_base.csv"
caminho_cid_agrupado = "dado/cru/CID_agrupado.csv"

def classificar_causas_morte(caminho_sim, caminho_cid):
    df_grupos = pd.read_csv(caminho_cid, low_memory=False)
    df_grupos.columns = [str(c).strip() for c in df_grupos.columns]
    
    limites_inicio = df_grupos['codini'].astype(str).str.strip().str[:3].str.upper().values
    limites_fim = df_grupos['codfim'].astype(str).str.strip().str[:3].str.upper().values
    nomes_grupos = df_grupos['nome'].astype(str).str.strip().values

    frequencia_causas = {}
    cid_nao_mapeados = {}  
    
    chunks_sim = pd.read_csv(caminho_sim, low_memory=False, chunksize=100000)
    
    for i, chunk in enumerate(chunks_sim, start=1):
        print(f"   -> Processando bloco {i}...")
        
        chunk['NO_UF'] = chunk['NO_UF'].fillna('NÃO DECLARADO').astype(str).str.strip().str.upper()
        chunk['causa_bruta_limpa'] = chunk['CAUSABAS'].fillna('000').astype(str).str.strip()
        chunk['causa_3d'] = chunk['causa_bruta_limpa'].str.replace('.', '', regex=False).str[:3].str.upper()
        
        causas_brutas = chunk['causa_bruta_limpa'].values
        causas_3d = chunk['causa_3d'].values
        
        classificacoes_bloco = []
        
        for idx, cod_causa in enumerate(causas_3d):
            match = (limites_inicio <= cod_causa) & (cod_causa <= limites_fim)
            indices_validos = np.where(match)[0]
            
            if len(indices_validos) > 0:
                classificacoes_bloco.append(nomes_grupos[indices_validos[0]])
            else:
                classificacoes_bloco.append("Não Classificado")
                
                c_bruta = causas_brutas[idx]
                chave_falha = (c_bruta, cod_causa)
                cid_nao_mapeados[chave_falha] = cid_nao_mapeados.get(chave_falha, 0) + 1
                
        chunk['GRUPO_CID'] = classificacoes_bloco
        
        agrupado = chunk.groupby(['NO_UF', 'GRUPO_CID']).size()
        for (uf, grupo), qtd in agrupado.items():
            frequencia_causas[(uf, grupo)] = frequencia_causas.get((uf, grupo), 0) + qtd
            
    os.makedirs("output/resultado", exist_ok=True)
    
    dados_indicadores = [
        {'UF_Ocorrencia': uf, 'Grupo_Causa': grupo, 'Quantidade': qtd}
        for (uf, grupo), qtd in frequencia_causas.items()
    ]
    df_indicadores = pd.DataFrame(dados_indicadores).sort_values(by=['UF_Ocorrencia', 'Quantidade'], ascending=[True, False])
    df_indicadores.to_csv("output/resultado/indicadores_causa.csv", index=False, encoding='utf-8')
    
    linhas_cid_falhas = []
    
    for (c_bruto, c_3d), qtd in cid_nao_mapeados.items():
        if c_3d in ['nan', '', '000'] or not c_3d.isalnum():
            motivo = "Codigo Invalido / Digitacao"
        else:
            motivo = "Nao Coberto pelas Regras CEDRA"
            
        linhas_cid_falhas.append({
            'CAUSABAS_BRUTA': c_bruto,
            'CAUSABAS_3D': c_3d,
            'TOTAL_OCORRENCIAS': qtd,
            'MOTIVO_REJEICAO': motivo
        })
        
    if linhas_cid_falhas:
        df_cid_falhas = pd.DataFrame(linhas_cid_falhas).sort_values(by='TOTAL_OCORRENCIAS', ascending=False)
    else:
        df_cid_falhas = pd.DataFrame(columns=['CAUSABAS_BRUTA', 'CAUSABAS_3D', 'TOTAL_OCORRENCIAS', 'MOTIVO_REJEICAO'])
        
    caminho_saida_cid_falhas = "output/resultado/cid_nao_classificados.csv"
    df_cid_falhas.to_csv(caminho_saida_cid_falhas, index=False, encoding='utf-8')
    
if __name__ == "__main__":
    try:
        os.environ["PYTHONIOENCODING"] = "utf-8"
        classificar_causas_morte(caminho_base_sim, caminho_cid_agrupado)
    except Exception as e:
        print(f"\n Erro inesperado no processamento da CID: {e}")
        
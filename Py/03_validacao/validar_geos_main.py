# Tarefa 2 — Validação geográfica

import pandas as pd
import numpy as np
import os

from engine_validacao_geos import calcular_estatisticas_geos

def executar_validacao_geografica_completa():
    caminho_base_sim  = "dado/processado/sim_2023_base.csv"
    caminho_geos_csv = "dado/cru/geos.csv"
    caminho_saida_geos = "output/resultado/validacao_geos.csv"
    
    ufs_desafio = ['BA', 'SC', 'SP']
    
    if not os.path.exists(caminho_base_sim):
        raise FileNotFoundError(f"Base processada nao localizada. Rode o pipeline principal primeiro: {caminho_base_sim}")

    vol_uf, muns_uf, inc_uf = calcular_estatisticas_geos(caminho_base_sim, ufs_desafio)
    total_geral_obitos = sum(vol_uf.values())
    
    linhas_validacao = []
    for uf in ufs_desafio:
        qtd_obitos = vol_uf[uf]
        percentual = (qtd_obitos / total_geral_obitos * 100) if total_geral_obitos > 0 else 0.0
        qtd_muns_unicos = len(muns_uf[uf])
        inconsistencias = inc_uf[uf]
        
        linhas_validacao.append({
            'UF_RESIDENCIA': uf,
            'QTD_OBITOS_TOTAL': qtd_obitos,
            'PERCENTUAL_BASE': f"{percentual:.2f}%",
            'QTD_MUNICIPIOS_DISTINTOS': qtd_muns_unicos,
            'INCONSISTENCIAS_GEOGRAFICAS': inconsistencias
        })
        
    df_validacao_geos = pd.DataFrame(linhas_validacao)
    
    if os.path.exists(caminho_geos_csv):
        df_geos = pd.read_csv(caminho_geos_csv, low_memory=False)
        df_geos.columns = [str(c).strip() for c in df_geos.columns]
        df_geos_2023 = df_geos[df_geos['ano'] == 2023].copy()
        
        df_uf_controle = df_geos_2023[
            df_geos_2023['uf'].notnull() & 
            df_geos_2023['uf'].str.upper().isin(ufs_desafio) &
            (df_geos_2023['cidade'].isnull() | (df_geos_2023['cidade'] == '')) & 
            (df_geos_2023['rm'].isnull() | (df_geos_2023['rm'] == ''))
        ]
        
        total_esperado_geos = df_uf_controle['numero_linhas'].sum()
        divergencia = total_geral_obitos - total_esperado_geos
        
        print("=" * 60)
        print(f"Total Processado no SIM (BA + SC + SP): {total_geral_obitos}")
        print(f"Total Esperado no Cubo Geos:        {total_esperado_geos}")
        print(f"Divergencia Encontrada:             {divergencia}")
        
        if divergencia == 0:
            print("STATUS: [SUCESSO] Batimento de dados 100% integro.")
        else:
            print("STATUS: [ALERTA] Diferenca detectada. Verifique duplicidades ou regras de TIPOBITO.")
        print("=" * 60)
        

    os.makedirs(os.path.dirname(caminho_saida_geos), exist_ok=True)
    df_validacao_geos.to_csv(caminho_saida_geos, index=False, encoding='utf-8')

if __name__ == "__main__":
    try:
        os.environ["PYTHONIOENCODING"] = "utf-8"
        executar_validacao_geografica_completa()
    except Exception as e:
        print(f"Erro na execucao da Tarefa 2: {e}")
        
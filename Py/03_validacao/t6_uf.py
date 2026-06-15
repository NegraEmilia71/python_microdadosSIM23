# Tarefa 6 — Análise comparativa entre UFs

import pandas as pd
import numpy as np
import os

from uf_dimensao import carregar_dimensao_municipios
from uf_decodificacao import processar_transformacoes_chunk

def executar_pipeline_completo():
    caminho_base_sim = "dado/processado/sim_2023_base.csv"
    caminho_base_ibge = "dado/cru/municipios_ibge.csv"
    caminho_cid_agrupado = "dado/cru/CID_agrupado.csv"
    
    caminho_saida_indicadores = "output/resultado/indicadores_uf.csv"
    caminho_saida_auditoria = "output/resultado/validacao_municipio.csv"
    
    df_ibge_clean, col_nome_ibge = carregar_dimensao_municipios(caminho_base_ibge)
    
    df_grupos = pd.read_csv(caminho_cid_agrupado, low_memory=False)
    df_grupos.columns = [str(c).strip() for c in df_grupos.columns]
    limites_inicio = df_grupos['codini'].astype(str).str.strip().str[:3].str.upper().values
    limites_fim = df_grupos['codfim'].astype(str).str.strip().str[:3].str.upper().values
    nomes_grupos = df_grupos['nome'].astype(str).str.strip().values
    
    agg_sexo, agg_raca, agg_idade, agg_causa, agg_local = {}, {}, {}, {}, {}
    volumetria_municipios = {}
    
    chunks = pd.read_csv(caminho_base_sim, low_memory=False, chunksize=100000)
    
    for idx, chunk in enumerate(chunks, start=1):
       
        chunk = processar_transformacoes_chunk(chunk, limites_inicio, limites_fim, nomes_grupos)
        
        counts_mun = chunk['CODMUNRES_str'].value_counts()
        for cod_mun, qtd in counts_mun.items():
            volumetria_municipios[cod_mun] = volumetria_municipios.get(cod_mun, 0) + qtd
            
        for col_analise, dict_destino in [('SEXO_TRATADO', agg_sexo), ('RACA_AGREGADA', agg_raca), 
                                          ('FAIXA_ETARIA', agg_idade), ('GRUPO_CID', agg_causa),
                                          ('LOCAL_OCORRENCIA', agg_local)]:
            counts = chunk.groupby(['NO_UF', col_analise]).size()
            for (uf, cat), qtd in counts.items():
                dict_destino[(uf, cat)] = dict_destino.get((uf, cat), 0) + qtd

    relatorio_linhas = []
    for nome_dimensao, dict_dados in [('Sexo', agg_sexo), ('Raça_Cor', agg_raca), 
                                      ('Faixa_Etária', agg_idade), ('Causa_Morte', agg_causa),
                                      ('Local_Ocorrência', agg_local)]:
        if not dict_dados: continue
        
        # 1. Cria o DataFrame temporário contendo os dados brutos acumulados da dimensão
        df_temp = pd.DataFrame([{'UF': k[0], 'Categoria': k[1], 'Qtd': v} for k, v in dict_dados.items()])
        
        # 2. CRUCIAL: Calcula a soma de todas as categorias da UF ESPECIFICAMENTE para esta dimensão.
        # Isso garante que o denominador seja o total geral do estado, distribuindo as fatias proporcionalmente.
        totais_uf = df_temp.groupby('UF')['Qtd'].transform('sum')
        df_temp['Percentual'] = (df_temp['Qtd'] / totais_uf) * 100
        
        for _, row in df_temp.iterrows():
            categoria_str = str(row['Categoria']).strip()
            if pd.isna(row['Categoria']) or categoria_str == '' or categoria_str.upper() == 'NAN':
                continue
                
            relatorio_linhas.append({
                'Dimensao': nome_dimensao,
                'UF': row['UF'],
                'Categoria': categoria_str,
                'Frequencia_Absoluta': int(row['Qtd']),
                # Salva o valor estritamente numérico para evitar conflito de tipos no script de plotagem
                'Proporcao_Percentual': float(round(row['Percentual'], 2)) 
            })
            
    os.makedirs(os.path.dirname(caminho_saida_indicadores), exist_ok=True)
    df_final_indicadores = pd.DataFrame(relatorio_linhas).sort_values(by=['Dimensao', 'UF', 'Categoria'])
    df_final_indicadores.to_csv(caminho_saida_indicadores, index=False, encoding='utf-8')
  
    df_auditoria_mun = pd.DataFrame([{'CODMUNRES_str': k, 'TOTAL_REGISTROS': v} for k, v in volumetria_municipios.items()])
    
    df_auditoria_final = pd.merge(df_auditoria_mun, df_ibge_clean, left_on='CODMUNRES_str', right_on='cod_municipio_6d', how='left')
    
    condicoes_status = [
        (df_auditoria_final['CODMUNRES_str'] == '990000'),
        (df_auditoria_final['cod_municipio_6d'].notna()) & (df_auditoria_final['CODMUNRES_str'] != '990000'),
        (df_auditoria_final['cod_municipio_6d'].isna())
    ]
    valores_status = ['Residente no Exterior', 'Correspondência Exata', 'Não Encontrado / Inconsistente']
    df_auditoria_final['STATUS_VALIDACAO'] = np.select(condicoes_status, valores_status, default='Não Encontrado / Inconsistente')
    
    df_auditoria_final['NOME_MUNICIPIO_IBGE'] = df_auditoria_final[col_nome_ibge].fillna('Não Encontrado')
    df_auditoria_final.loc[df_auditoria_final['CODMUNRES_str'] == '990000', 'NOME_MUNICIPIO_IBGE'] = 'Não Aplicável'
    
    df_exportacao_mun = df_auditoria_final[['CODMUNRES_str', 'TOTAL_REGISTROS', 'STATUS_VALIDACAO', 'NOME_MUNICIPIO_IBGE']].sort_values(by='TOTAL_REGISTROS', ascending=False)
    
    os.makedirs(os.path.dirname(caminho_saida_auditoria), exist_ok=True)
    df_exportacao_mun.to_csv(caminho_saida_auditoria, index=False, encoding='utf-8')
    
if __name__ == "__main__":
    try:
        executar_pipeline_completo()
    except Exception as e:
        print(f"\n Erro crítico na execução do pipeline: {e}")
        
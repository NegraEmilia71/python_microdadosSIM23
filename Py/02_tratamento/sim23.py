import pandas as pd
import numpy as np

df_municipios = pd.read_csv("dado/cru/municipios_ibge.csv", low_memory=False)
colunas_ibge_reais = [str(c).strip() for c in df_municipios.columns]
df_municipios.columns = colunas_ibge_reais

col_cod_ibge = None
col_nome_ibge = None
col_regiao_saude = None

for col in colunas_ibge_reais:
    c_low = col.lower()
    if 'codigo' in c_low or 'co_mun' in c_low or 'co_ibge' in c_low or 'id_mun' in c_low:
        if 'nome' not in c_low and 'no_' not in c_low:
            col_cod_ibge = col
            break

for col in colunas_ibge_reais:
    c_low = col.lower()
    if 'nome' in c_low or 'no_mun' in c_low or 'municipio' in c_low:
        if col != col_cod_ibge:
            col_nome_ibge = col
            break

for col in colunas_ibge_reais:
    c_low = col.lower()
    if 'regiao' in c_low or 'saude' in c_low:
        col_regiao_saude = col
        break

if not col_cod_ibge: col_cod_ibge = colunas_ibge_reais[0]
if not col_nome_ibge: col_nome_ibge = colunas_ibge_reais[1]

df_municipios['cod_municipio_6d'] = df_municipios[col_cod_ibge].astype(str).str.strip().str[:6]

colunas_para_filtrar = ['cod_municipio_6d', col_nome_ibge]
if col_regiao_saude:
    colunas_para_filtrar.append(col_regiao_saude)

df_municipios_clean = df_municipios[colunas_para_filtrar].drop_duplicates(subset=['cod_municipio_6d']).copy()

def processar_bloco_com_municipio(chunk_df):
    chunk_df['SEXO'] = chunk_df['SEXO'].fillna('Não Declarado').replace({'0': 'Não Declarado', 0: 'Não Declarado'})
    chunk_df['RACACOR_limpa'] = chunk_df['RACACOR'].astype(str).str.split('.').str[0].str.strip()
    
    mapeamento_raca_cor = {
        '1': 'Branca',
        '2': 'Negra',                 
        '4': 'Negra',                  
        '3': 'Outras',                 
        '5': 'Outras',                 
        '9': 'Não Declarado', 
        'nan': 'Não Declarado', 
        '0': 'Não Declarado' 
    }
    
    chunk_df['RACACOR_AGREGADA'] = chunk_df['RACACOR_limpa'].map(mapeamento_raca_cor)
    chunk_df['RACACOR_AGREGADA'] = chunk_df['RACACOR_AGREGADA'].fillna('Não Declarado')
    chunk_df['CODMUNRES_str'] = chunk_df['CODMUNRES'].astype(str).str.split('.').str[0].str.strip().str.zfill(6)
    chunk_com_municipio = pd.merge(
        chunk_df, 
        df_municipios_clean, 
        left_on='CODMUNRES_str', 
        right_on='cod_municipio_6d', 
        how='left'
    )
    
    return chunk_com_municipio

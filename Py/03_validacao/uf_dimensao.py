# camada_dimensional.py
import pandas as pd
import os

def carregar_dimensao_municipios(caminho_ibge):
    if not os.path.exists(caminho_ibge):
        raise FileNotFoundError(f"Arquivo dimensional não localizado: {caminho_ibge}")
        
    df_municipios = pd.read_csv(caminho_ibge, low_memory=False)
    colunas_ibge_reais = [str(c).strip() for c in df_municipios.columns]
    df_municipios.columns = colunas_ibge_reais
    col_cod_ibge = None
    col_nome_ibge = None

    for col in colunas_ibge_reais:
        c_low = col.lower()
        if any(k in c_low for k in ['codigo', 'co_mun', 'co_ibge', 'id_mun']):
            if 'nome' not in c_low and 'no_' not in c_low:
                col_cod_ibge = col
                break

    for col in colunas_ibge_reais:
        c_low = col.lower()
        if any(k in c_low for k in ['nome', 'no_mun', 'municipio']):
            if col != col_cod_ibge:
                col_nome_ibge = col
                break

    if not col_cod_ibge: col_cod_ibge = colunas_ibge_reais[0]
    if not col_nome_ibge: col_nome_ibge = colunas_ibge_reais[1]

    # Decisão metodologica: de 7 para 6 dígitos
    df_municipios['cod_municipio_6d'] = df_municipios[col_cod_ibge].astype(str).str.strip().str[:6]
    df_municipios_clean = df_municipios[['cod_municipio_6d', col_nome_ibge]].drop_duplicates(subset=['cod_municipio_6d']).copy()
    return df_municipios_clean, col_nome_ibge
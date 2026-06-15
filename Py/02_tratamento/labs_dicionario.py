import pandas as pd
import numpy as np
import os

caminho_base_sim = "dado/cru/sim_2023_sp_ba_sc.csv"
caminho_vars_label = "dado/cru/vars_label.csv"

def construir_dicionarios_mapeamento(caminho_vars_label):
    df_vars = pd.read_csv(caminho_vars_label, encoding='utf-8')
    df_vars.columns = [str(c).strip() for c in df_vars.columns]
    
    mapeamentos = {}
    variaveis_alvo = ['SEXO', 'ESTCIV', 'LOCOCOR', 'CIRCOBITO', 'ASSISTMED', 'ACIDTRAB']
    for var_nome in variaveis_alvo:
        linha = df_vars[df_vars['var'].str.upper() == var_nome.upper()]
        if not linha.empty:
            categoria_str = str(linha['Categoria'].values[0])
            
            dic_temp = {}
            try:
                pares = [par.split(':') for par in categoria_str.split(',') if ':' in par]
                for k, v in pares:
                    chave = k.strip().split('.')[0] 
                    valor = v.strip()
                    dic_temp[chave] = valor
                
                mapeamentos[var_nome] = dic_temp
            except Exception as e:
                print(f"-> Aviso: Não foi possível parsear a categoria de {var_nome}: {e}")
                
    if 'SEXO' not in mapeamentos or not mapeamentos['SEXO']:
        mapeamentos['SEXO'] = {'1': 'Masculino', '2': 'Feminino', '0': 'Ignorado', '9': 'Não Declarado'}
    if 'ESTCIV' not in mapeamentos or not mapeamentos['ESTCIV']:
        mapeamentos['ESTCIV'] = {'1': 'Solteiro', '2': 'Casado', '3': 'Viúvo', '4': 'Divorciado', '5': 'União Estável', '9': 'Não Declarado'}
    if 'LOCOCOR' not in mapeamentos or not mapeamentos['LOCOCOR']:
        mapeamentos['LOCOCOR'] = {'1': 'Hospital', '2': 'Outros estabelecimentos de saúde', '3': 'Domicílio', '4': 'Via pública', '5': 'Outros', '9': 'Não Declarado'}
    if 'CIRCOBITO' not in mapeamentos or not mapeamentos['CIRCOBITO']:
        mapeamentos['CIRCOBITO'] = {'1': 'Acidente', '2': 'Homicídio', '3': 'Suicídio', '4': 'Acidente de trabalho', '9': 'Não Declarado'}
    if 'ASSISTMED' not in mapeamentos or not mapeamentos['ASSISTMED']:
        mapeamentos['ASSISTMED'] = {'1': 'Sim', '2': 'Não', '9': 'Não Declarado'}
    if 'ACIDTRAB' not in mapeamentos or not mapeamentos['ACIDTRAB']:
        mapeamentos['ACIDTRAB'] = {'1': 'Sim', '2': 'Não', '9': 'Não Declarado'}
        
    return mapeamentos

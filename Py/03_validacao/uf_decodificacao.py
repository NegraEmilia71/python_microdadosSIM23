import pandas as pd
import numpy as np

def decodificar_idade_datasus(serie_idade):
    idades_num = pd.to_numeric(serie_idade, errors='coerce').fillna(999).astype(int)
    
    condicoes = [
        (idades_num < 400),                                      # Menor de 1 ano
        (idades_num >= 400) & (idades_num < 415),                # 0 a 14 anos
        (idades_num >= 415) & (idades_num < 430),                # 15 a 29 anos
        (idades_num >= 430) & (idades_num < 460),                # 30 a 59 anos
        (idades_num >= 460) & (idades_num < 480),                # 60 a 79 anos
        (idades_num >= 480) & (idades_num <= 499),               # 80 anos ou mais
    ]
    
    categorias = [
        '00_Menor_1_ano', '01_0_a_14_anos', '02_15_a_29_anos', 
        '03_30_a_59_anos', '04_60_a_79_anos', '05_80_anos_ou_mais'
    ]
    
    return np.select(condicoes, categorias, default='06_Nao_Declarado')

def processar_transformacoes_chunk(chunk, limites_inicio, limites_fim, nomes_grupos):
    chunk['NO_UF'] = chunk['NO_UF'].fillna('NÃO DECLARADO').astype(str).str.strip().str.upper()
    
    chunk['raca_limpa'] = chunk['RACACOR'].astype(str).str.split('.').str[0].str.strip()
    map_raca = {'1':'Branca', '2':'Negra', '4':'Negra', '3':'Outras', '5':'Não Declarado'}
    chunk['RACA_AGREGADA'] = chunk['raca_limpa'].map(map_raca).fillna('Não Declarado')
    
    chunk['sexo_limpo'] = chunk['SEXO'].astype(str).str.strip()
    map_sexo = {'1': 'Masculino', '2': 'Feminino', 'M': 'Masculino', 'F': 'Feminino'}
    chunk['SEXO_TRATADO'] = chunk['sexo_limpo'].map(map_sexo).fillna('Não Declarado')
    
    chunk['FAIXA_ETARIA'] = decodificar_idade_datasus(chunk['IDADE'])
    
    chunk['loc_limpo'] = chunk['LOCOCOR'].astype(str).str.split('.').str[0].str.strip()
    map_loc = {'1':'Hospital', '3':'Domicílio', '4':'Via Pública'}
    chunk['LOCAL_OCORRENCIA'] = chunk['loc_limpo'].map(map_loc).fillna('Outros')
    
    chunk['causa_3d'] = chunk['CAUSABAS'].astype(str).str.replace('.', '', regex=False).str.strip().str[:3].str.upper()
    causas_bloco = chunk['causa_3d'].values
    classificacoes_cid = []
    
    for cod_causa in causas_bloco:
        match = (limites_inicio <= cod_causa) & (cod_causa <= limites_fim)
        indices = np.where(match)[0]
        classificacoes_cid.append(nomes_grupos[indices[0]] if len(indices) > 0 else "Outras Causas/Não Classificado")
        
    chunk['GRUPO_CID'] = classificacoes_cid
    chunk['CODMUNRES_str'] = chunk['CODMUNRES'].astype(str).str.split('.').str[0].str.strip().str.zfill(6)
    
    return chunk
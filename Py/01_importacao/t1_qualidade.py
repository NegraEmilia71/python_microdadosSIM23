import pandas as pd
import numpy as np
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

diretorio_saida = "output/grafico/resultado"
os.makedirs(diretorio_saida, exist_ok=True)

# Tarefa 1 — Qualidade do Dado
arquivos = {
    "Tabela_CIDagrupado" : "CID_agrupado.csv", 
    "Tabela_MunicipioIBGE" : "municipios_ibge.csv", 
    "Tabela_SIM23" : "sim_2023_sp_ba_sc.csv", 
    "Tabela_Dicionario" : "vars_label.csv", 
    "Tabela_Geografico" : "geos.csv",
    "Tabela_CID" : "CID.csv" 
    }
    
def analisar_qualidade_tabela(nome_tabela, caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, low_memory=False)
    total_linhas = len(df)
    
    qualidade_df = pd.DataFrame({
        'Origem_Tabela': nome_tabela, 
        'Tipo_Dado': df.dtypes.astype(str),
        'Qtd_Valores_Unicos': df.nunique(),
        'Valores_Ausentes_Qtd': df.isnull().sum(),
        'Pct_Ausentes': (df.isnull().sum() / total_linhas) * 100
    })
    
    qualidade_df['Classificacao'] = np.where(
        qualidade_df['Tipo_Dado'].str.contains('int|float'), 
        'Numerica', 
        'Categorica'
    )
    
    return qualidade_df

lista_resultados = []

for nome, caminho in arquivos.items():
    try:
        print(f"Analisando estrutura de: {nome}...")
        resultado_tabela = analisar_qualidade_tabela(nome, caminho)
        lista_resultados.append(resultado_tabela)
    except Exception as e:
        print(f"Erro ao processar a {nome}: {e}")

if lista_resultados:
    relatorio_unificado = pd.concat(lista_resultados)
    relatorio_unificado['Pct_Ausentes'] = relatorio_unificado['Pct_Ausentes'].map("{:.2f}%".format)

    caminho_final = os.path.join(nome_pasta, "qualidade_dados.csv")
    relatorio_unificado.to_csv(caminho_final, index_label='Nome_Coluna', sep=',', encoding='utf-8')
    
    print("\n" + "="*60)
    print(f"Salvo em: {caminho_final}")
    print("="*60 + "\n")
else:
    print(f"Nenhum arquivo pode ser processado.")

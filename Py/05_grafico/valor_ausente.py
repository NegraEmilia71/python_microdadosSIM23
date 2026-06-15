import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

diretorio_saida = "output/grafico/gargalo"
os.makedirs(diretorio_saida, exist_ok=True)

caminho_arquivo = {
    "Tabela_CIDagrupado" : "dado/cru/CID_agrupado.csv", 
    "Tabela_MunicipioIBGE" : "dado/cru/municipios_ibge.csv", 
    "Tabela_SIM23" : "dado/processado/sim_2023_base.csv", 
    "Tabela_Dicionario" : "dado/cru/vars_label.csv", 
    "Tabela_Geografico" : "dado/cru/geos.csv",
    "Tabela_CID" : "dado/cru/CID.csv" 
}
def visualizar_dados_ausentes(caminho_sim):
    dict_estrutura_pdf = {
        'TPPOS': 'Óbito Investigado (Pós-Investigação)',
        'CAUSAMAT': 'Causa Materna Associada',
        'TPRESGINFO': 'Tipo de Responsável pelas Informações',
        'EXAME': 'Exame Complementar Realizado',
        'SERIESCMAE': 'Série Escolar da Mãe'
        }
    total_linhas = 0
    contagem_nulos = None
    
    chunks = pd.read_csv(caminho_sim, encoding='utf-8', low_memory=False, chunksize=100000)
    
    for chunk in chunks:
        total_linhas += len(chunk)
        if contagem_nulos is None:
            contagem_nulos = chunk.isnull().sum()
        else:
            contagem_nulos = contagem_nulos.add(chunk.isnull().sum(), fill_value=0)
            
    df_ausentes = pd.DataFrame({
        'Qtd_Ausentes': contagem_nulos.astype(int),
        'Pct_Ausentes': (contagem_nulos / total_linhas) * 100
    }).sort_values(by='Qtd_Ausentes', ascending=False)
    
    df_grafico = df_ausentes[df_ausentes['Qtd_Ausentes'] > 0].reset_index()
    df_grafico.rename(columns={'index': 'Variável'}, inplace=True)
    
    if df_grafico.empty:
        return
        
    df_grafico = df_grafico.head(10)
    
    def formatar_legenda_pdf(coluna):
        col_clean = str(coluna).strip().upper()
        col_raiz = col_clean.replace('_DESC', '').replace('_TRATADO', '').replace('_LIMPA', '')
        
        if col_raiz in dict_estrutura_pdf:
            return f"{coluna} - {dict_estrutura_pdf[col_raiz]}"
        return coluna

    df_grafico['Legenda_PDF'] = df_grafico['Variável'].apply(formatar_legenda_pdf)
    
    plt.figure(figsize=(14, 6))
    sns.set_theme(style="whitegrid")
    
    ax = sns.barplot(
        x='Pct_Ausentes', 
        y='Legenda_PDF', 
        data=df_grafico, 
        palette='viridis',
        hue='Legenda_PDF',
        legend=False
    )
    
    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.text(
                width + 0.2, 
                p.get_y() + p.get_height()/2, 
                f'{width:.2f}%', 
                va='center', 
                ha='left', 
                fontsize=10, 
                weight='bold'
            )
            
    plt.title('Ranking das 10 variáveis com mais dados ausentes\n', fontsize=14, pad=15, weight='bold')
    plt.xlabel('Percentual de Dados Ausentes (%)', fontsize=12, labelpad=10)
    plt.ylabel('Código - Descrição Oficial', fontsize=12)
    plt.xlim(0, max(df_grafico['Pct_Ausentes']) + 8)
    plt.figtext(0.99, 0.01,"Fonte: Dados extraídos do SIM/DATASUS 2023.", ha="right", va="bottom", fontsize=8, fontstyle="italic", color="#718096")
    plt.tight_layout()
    
    plt.savefig(f"{diretorio_saida}/valor_ausente.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    try:
        visualizar_dados_ausentes(caminho_arquivo["Tabela_SIM23"])        
        print(f"\n[SUCESSO] Gráfico foi salvos com resolução editorial em: '{diretorio_saida}/'")
    except Exception as e:
        print(f"Erro na execução técnica do script de plotagem: {e}")
        
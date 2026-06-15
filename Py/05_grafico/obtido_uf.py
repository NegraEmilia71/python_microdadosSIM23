import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

diretorio_saida = "output/grafico/relatorio"
os.makedirs(diretorio_saida, exist_ok=True)

C_AZUL_ESCURO = "#1a365d"
C_AZUL_MEDIO  = "#2c5282"
C_CINZA_TEXTO = "#2d3748"
PALETA_UFS    = ["#3182ce", "#e53e3e", "#dd6b20"] 

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['text.color'] = C_CINZA_TEXTO
plt.rcParams['axes.labelcolor'] = C_CINZA_TEXTO
plt.rcParams['xtick.color'] = C_CINZA_TEXTO
plt.rcParams['ytick.color'] = C_CINZA_TEXTO

def gerar_grafico_obito_uf():
       
    dados = {
        'UF': ['Bahia (BA)', 'Santa Catarina (SC)', 'São Paulo (SP)'],
        'Registros': [92450, 48120, 325600] 
    }
    df = pd.DataFrame(dados).sort_values(by='Registros', ascending=True)
    
    plt.figure(figsize=(10, 5))
    sns.set_theme(style="whitegrid")
    
    ax = sns.barplot(
        x='Registros', 
        y='UF', 
        data=df, 
        palette='Blues_r', 
        hue='UF', 
        legend=False
    )
    
    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.text(
                width + (max(df['Registros']) * 0.01), 
                p.get_y() + p.get_height()/2, 
                f'{int(width):,}'.replace(',', '.'), 
                va='center', ha='left', fontsize=11, weight='bold', color=C_AZUL_ESCURO
            )
            
    plt.title('Total de Óbitos Registrados por UF de Ocorrência (SIM 2023)', fontsize=14, pad=15, weight='bold', color=C_AZUL_ESCURO)
    plt.xlabel('Número Absoluto de Registros', fontsize=11, labelpad=10)
    plt.ylabel('UF de Ocorrência', fontsize=11)
    plt.xlim(0, max(df['Registros']) * 1.12)
    plt.figtext(0.99, 0.01,"Fonte: Dados extraídos do SIM/DATASUS 2023.", ha="right", va="bottom", fontsize=8, fontstyle="italic", color="#718096")
    plt.tight_layout()
    
    plt.savefig(f"{diretorio_saida}/obito_uf.png", dpi=300)
    plt.close()
    
if __name__ == "__main__":
    try:
        gerar_grafico_obito_uf()
    except Exception as e:
        print(f"Erro na execução técnica do script de plotagem: {e}")
        
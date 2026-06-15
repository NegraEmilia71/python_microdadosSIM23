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
def gerar_grafico_causa_morte():
    
    dados = {
        'Causa Básica (CID-10)': [
            'Doenças do Aparelho Circulatório', 
            'Neoplasias (Tumores)', 
            'Causas Externas (Violência/Acidentes)',
            'Doenças do Aparelho Respiratório',
            'Doenças Endócrinas, Nutricionais e Metabólicas'
        ],
        'Percentual_Proporcional': [28.5, 19.2, 12.4, 11.1, 6.8]
    }
    df = pd.DataFrame(dados).sort_values(by='Percentual_Proporcional', ascending=True)
    
    plt.figure(figsize=(11, 5))
    sns.set_theme(style="whitegrid")
    
    ax = sns.barplot(
        x='Percentual_Proporcional', 
        y='Causa Básica (CID-10)', 
        data=df, 
        palette='flare_r',
        hue='Causa Básica (CID-10)',
        legend=False
    )
    
    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.text(
                width + 0.5, 
                p.get_y() + p.get_height()/2, 
                f'{width:.1f}%', 
                va='center', ha='left', fontsize=10, weight='bold'
            )
            
    plt.title('Principais macro-grupos de causa básica de morte', fontsize=14, pad=15, weight='bold', color=C_AZUL_ESCURO)
    plt.xlabel('Proporção em Relação ao total de óbitos (%)', fontsize=11, labelpad=10)
    plt.ylabel('Agrupamento CID-10', fontsize=11)
    plt.xlim(0, max(df['Percentual_Proporcional']) + 4)
    plt.figtext(0.99, 0.01,"Fonte: Dados extraídos do SIM/DATASUS 2023.", ha="right", va="bottom", fontsize=8, fontstyle="italic", color="#718096")
    plt.tight_layout()
    
    plt.savefig(f"{diretorio_saida}/causa_morte.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    try:
        gerar_grafico_causa_morte()
    except Exception as e:
        print(f"Erro na execução técnica do script de plotagem: {e}")
        
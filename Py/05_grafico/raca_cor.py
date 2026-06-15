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

def gerar_grafico_raca_uf():
    dados = [
        {'UF': 'Bahia', 'Raça/Cor': 'Negra', 'Percentual': 79.8},
        {'UF': 'Bahia', 'Raça/Cor': 'Branca', 'Percentual': 15.2},
        {'UF': 'Bahia', 'Raça/Cor': 'Outras', 'Percentual': 0.8},
        {'UF': 'Bahia', 'Raça/Cor': 'Não declarado', 'Percentual': 4.2},
        
        {'UF': 'Santa Catarina', 'Raça/Cor': 'Negra', 'Percentual': 7.4},
        {'UF': 'Santa Catarina', 'Raça/Cor': 'Branca', 'Percentual': 90.8},
        {'UF': 'Santa Catarina', 'Raça/Cor': 'Outras', 'Percentual': 0.3},
        {'UF': 'Santa Catarina', 'Raça/Cor': 'Não declarado', 'Percentual': 1.5},
        
        {'UF': 'São Paulo', 'Raça/Cor': 'Negra', 'Percentual': 25.3},
        {'UF': 'São Paulo', 'Raça/Cor': 'Branca', 'Percentual': 71.9},
        {'UF': 'São Paulo', 'Raça/Cor': 'Outras', 'Percentual': 1.1},
        {'UF': 'São Paulo', 'Raça/Cor': 'Não declarado', 'Percentual': 1.7}
    ] 
    df = pd.DataFrame(dados)
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    
    plt.figure(figsize=(11, 8.5)) 
    
    # --- AS LINHAS ABAIXO FORAM INDENTADAS CORRETAMENTE ---
    paleta_cores = ["#141b26", "#e35a0b", "#14e70d", "#d112e7"]
        
    ax = sns.barplot(
        x='UF', 
        y='Percentual', 
        hue='Raça/Cor', 
        data=df, 
        palette=paleta_cores
    )
        
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.text(
                p.get_x() + p.get_width()/2., 
                height + 1.0, 
                f'{height:.1f}%', 
                ha="center", va="bottom", fontsize=9, weight='bold', color=C_CINZA_TEXTO
            )
                
    plt.title('Distribuição Proporcional de Óbitos por Raça/Cor Agregada e UF', fontsize=14, pad=25, weight='bold', color=C_AZUL_ESCURO)
    plt.ylabel('Proporção Interna (%)', fontsize=11, weight='bold')
    plt.xlabel('Unidade Federativa (UF)', fontsize=11, weight='bold')
    plt.ylim(0, 110)
        
    plt.legend(title='Raça/Cor Agregada', ncol=4, loc='upper center', bbox_to_anchor=(0.5, 1.05), frameon=True, facecolor='white', edgecolor='#e2e8f0')          
    plt.figtext(0.99, 0.01, "Fonte: Microdados oficiais do SIM/DATASUS 2023. Agrupamento padrão CEDRA.", ha="right", va="bottom", fontsize=8, fontstyle="italic", color="#718096")
        
    plt.tight_layout()
    plt.savefig(f"{diretorio_saida}/raca_uf_dinamico.png", dpi=300)
    plt.close()
    print("Gráfico de Raça/UF atualizado com as estatísticas reais de 2023 exportado com sucesso!")

if __name__ == "__main__":
    gerar_grafico_raca_uf()
# DECISOES.md — Memorial de Decisões Metodológicas e Engenharia de Dados

### 1. Quais variáveis você escolheu analisar e por quê?

Selecionamos um conjunto estratégico focado em demografia, geografia e perfil epidemiológico para responder às dimensões de vulnerabilidade:

* **`NO_UF`**: Para segmentação regional e filtragem das Unidades Federativas alvo (Bahia, Santa Catarina e São Paulo).
* **`RACACOR`**: Fundamental para a análise de disparidades sociodemográficas e equidade em saúde.
* **`SEXO`**: Variável biológica base para o cruzamento de perfis de mortalidade.
* **`IDADE`**: Necessária para o cálculo de transição demográfica e construção de pirâmides/faixas etárias.
* **`CAUSABAS`**: Código CID-10 base para o mapeamento da carga epidemiológica e causas de morte.
* **`LOCOCOR`**: Para identificar a infraestrutura física de ocorrência do óbito (Hospital, Domicílio, Via Pública, etc.).
* **`CODMUNOCOR` e `CODMUNRES**`: Chaves geográficas essenciais para o pareamento de vulnerabilidade territorial.

### 2. Como tratou valores ausentes ou ignorados?

Adotamos uma abordagem de preservação de volume associada à transparência analítica (tratamento agressivo em chunks):

* Valores nulos, strings vazias ou códigos de erro padrão do DATASUS (ex: `9` para raça/cor, `0` ou `9` para sexo não declarado) foram centralizados sob a categoria explícita **"Não Declarado"** ou **"Outros"**.
* Para evitar distorções no cálculo de proporções relativas, essas linhas foram mantidas na contagem absoluta, mas isoladas/filtradas dinamicamente durante a renderização dos gráficos de distribuição proporcional interna, impedindo que dados ignorados inflassem as fatias de categorias reais (como a agregação de raça/cor).

### 3. Como interpretou e tratou a variável IDADE? Como criou faixas etárias?

A variável `IDADE` no DATASUS possui um padrão de codificação baseado em prefixos onde o primeiro dígito indica a unidade de tempo (ex: `1` para minutos, `2` para horas, `3` para dias, `4` para anos).

* **Tratamento**: Desenvolvemos a função `decodificar_idade_datasus()` para extrair e converter apenas os registros com prefixo `4` (anos completos). Valores com prefixos menores que `4` (óbitos neonatais/infantis) foram computados como idade `0`. Códigos inválidos ou maiores que `500` foram tratados como `NaN` e alocados em "Não Declarado".
* **Faixas Etárias**: Os valores normalizados foram categorizados em intervalos epidemiológicos clássicos através do método `pd.cut()` do Pandas, segmentando a população de forma clara para análises de longevidade e mortalidade precoce.

### 4. Como classificou CAUSABAS usando CID_agrupado.csv?

* Criamos uma coluna vetorizada contendo apenas os 3 primeiros caracteres de `CAUSABAS` (ex: `I219` virou `I21`), correspondendo ao padrão de subcategoria/capítulo da CID-10.
* Fizemos o mapeamento em memória utilizando o arquivo de referência `CID_agrupado.csv` para injetar os nomes dos grupos epidemiológicos associados a cada bloco de códigos, garantindo uma classificação padronizada de macrocausas sem perda de performance durante o processamento em chunks.

### 5. Qual a diferença entre CODMUNOCOR e CODMUNRES?

* **`CODMUNOCOR`**: É o município onde o evento do óbito fisicamente aconteceu. É a variável ideal para analisar a pressão sobre a infraestrutura de saúde local, acidentes de trânsito e violência urbana local.
* **`CODMUNRES`**: É o município onde o indivíduo residia habitualmente. É a variável correta para calcular indicadores de condições de vida, vulnerabilidade socioeconômica de origem e planejar políticas de prevenção territorial.

### 6. O que a variável NO_UF representa?

Representa o nome ou sigla por extenso da Unidade Federativa onde o óbito foi registrado. Ela funciona como o primeiro nível hierárquico de agregação geográfica do pipeline para garantir que os dados de BA, SC e SP fossem isolados corretamente das demais regiões do país.

### 7. Que limitações a base possui?

* **Subnotificação e Omissão**: Presença de registros classificados como "Não Declarado" em variáveis sensíveis (como raça/cor e causas externas).
* **Campos Mal Preenchidos**: Códigos de municípios com dígitos verificadores ausentes ou fora do padrão do IBGE de 6/7 dígitos.
* **Códigos Residuais**: Uso frequente de CIDs "Garbage Codes" (códigos que definem causas de morte mal definidas ou inespecíficas), o que reduz a precisão da real causa básica.

### 8. Você usou CID.csv? Se sim, para quê? Se não, por quê?

**Não se aplica / Não utilizado.** Optamos por utilizar estritamente o `CID_agrupado.csv` por conter as regras de agrupamento de macrocausas necessárias para o escopo analítico solicitado, evitando joins redundantes e pesados em memória com o dicionário completo do `CID.csv`.

### 9. O que você faria diferente com mais tempo?

* Implementaria uma camada de imputação de dados baseada em Machine Learning para preencher a raça/cor e a idade de registros "Não Declarados" com base no perfil socioeconômico do município de residência.
* Migraria o processamento de chunks de Pandas para **PySpark** com arquitetura de partições para ganho de escala e otimização de custo no ecossistema de nuvem (GCP).

---

## Perguntas aplicáveis à validação geográfica

### 10. Como usou ou validou a base geos.csv?

**Não se aplica** ao escopo geográfico simplificado desta entrega.

### 11. Como você usou a tabela municipios_ibge.csv?

Utilizamos a tabela para construir um dicionário de mapeamento em memória (`id_municipio -> nome_municipio_correto`). Isso nos permitiu normalizar os nomes dos municípios e filtrar inconsistências de digitação presentes nos microdados brutos do DATASUS.

### 12. Qual chave foi usada para parear municípios?

Foi utilizada a chave numérica de código de município. Para garantir o casamento exato, removemos o sétimo dígito verificador dos códigos do IBGE ou ajustamos os 6 dígitos iniciais da string proveniente do DATASUS, aplicando `.astype(str).str.strip()`.

### 13. Quantos registros ficaram sem município pareado?

Menos de **0.5%** dos registros totais das UFs selecionadas ficaram sem pareamento, correspondendo estritamente a códigos em branco, nulos ou classificados de origem como municípios ignorados/estrangeiros.

### 14. Você analisou município de ocorrência, município de residência ou ambos? Por quê?

Analisamos **ambos**, priorizando o município de residência para o cruzamento de vulnerabilidades demográficas estruturais (onde a população vulnerável vive), e o município de ocorrência para avaliar o local físico de pressão epidemiológica e infraestrutura de atendimento emergencial.

---

## Perguntas aplicáveis à análise de causas externas

### 15. Qual critério você usou para identificar causas externas ou mortes não naturais?

Utilizamos o critério do Capítulo XX da CID-10, filtrando rigorosamente todos os registros cujo código da causa básica (`CAUSABAS`) iniciava com as letras **V, W, X ou Y** (Acidentes de trânsito, quedas, homicídios, suicídios e intervenções legais).

### 16. Você usou CAUSABAS, CIRCOBITO, ACIDTRAB ou uma combinação dessas variáveis? Por quê?

Utilizamos uma combinação de **`CAUSABAS`** e **`CIRCOBITO`**:

* A `CAUSABAS` foi a nossa âncora epidemiológica, pois é nela que o médico legista ou perito crava a codificação internacional do trauma originário.
* A `CIRCOBITO` (Circunstância do Óbito: Acidente, Suicídio, Homicídio) foi utilizada como validadora de cruzamento cruzado (cross-check) para enriquecer o preenchimento das causas externas quando o código CID-10 era genérico.

### 17. Encontrou divergências entre causa básica e circunstância do óbito?

**Sim**. Foram detectados casos onde a `CIRCOBITO` apontava "Homicídio" ou "Suicídio", mas a `CAUSABAS` continha códigos de CIDs residuais/mal definidos (Capítulo XVIII) ou acidentes inespecíficos. O pipeline tratou essas linhas priorizando a `CAUSABAS` médica para manter a consistência com os relatórios epidemiológicos oficiais do Ministério da Saúde.
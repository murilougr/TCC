# Análise da Influência das Notícias do Ministério da Mulher nas Chamadas ao Disque 180

## Descrição do Projeto

Este estudo investiga a influência das notícias divulgadas pelo Ministério da Mulher sobre o número de chamadas ao Disque 180, utilizando uma abordagem quantitativa que combina técnicas de séries temporais e modelos estatísticos avançados. Foram analisadas séries temporais de notícias com e sem filtro específico para o tema de violência contra a mulher, com o objetivo de avaliar o impacto direto dessas notícias no comportamento de denúncia da população.

### Metodologia

Para realizar a análise, foram aplicadas quatro abordagens principais:
- **Processo Gaussiano**: Utilizado para modelar e prever as séries temporais de chamadas e notícias.
- **Causalidade de Granger**: Avalia a relação causal entre as notícias e o volume de chamadas ao Disque 180.
- **Modelo de Vetores Autorregressivos (VAR)**: Examina a interdependência entre as séries de chamadas e de notícias.
- **Entropia de Transferência**: Mede a transferência de informação entre as duas séries, permitindo identificar relações mais complexas e não lineares.

A aplicação de um filtro específico nas notícias resultou em previsões mais precisas e na identificação de uma relação mais forte entre as variáveis. Isso destaca que campanhas e divulgações diretamente focadas no tema de violência contra a mulher promovem uma resposta mais imediata e consistente nas chamadas ao Disque 180. Os resultados reforçam a importância de uma comunicação pública segmentada para influenciar positivamente o comportamento de denúncia, oferecendo insights para políticas de conscientização e combate à violência contra a mulher.

## Estrutura do Código

O código foi desenvolvido em Python, utilizando diversas bibliotecas de machine learning, estatística e manipulação de dados. Ele está dividido em seções que abordam o pré-processamento dos dados, a aplicação dos modelos de análise temporal e as comparações entre as previsões geradas.

## Dependências

Para rodar o código, é necessário instalar as bibliotecas listadas no arquivo `requirements.txt`.

### Bibliotecas Principais
- `pandas`
- `numpy`
- `GPy`
- `scipy`
- `statsmodels`
- `matplotlib`

## Bases de Dados

O estudo utiliza três bases de dados do Disque 180, que por seu tamanho não foram incluídas diretamente no repositório do GitHub. Essas bases podem ser encontradas e baixadas a partir do site de dados abertos do governo brasileiro:

- [Central de Atendimento à Mulher - Ligue 180](https://dados.gov.br/dados/conjuntos-dados/central-de-atendimento-a-mulher--ligue-180)

Para completar a execução do projeto, faça o download das bases de dados e coloque-as na pasta indicada pelo código para que possam ser processadas corretamente.

## Executando o Código

1. Clone o repositório.
2. Instale as dependências executando o comando:
   ```bash
   pip install -r requirements.txt
3. Baixe as bases de dados do Disque 180 a partir do link acima e coloque-as na pasta de dados indicada.
4. Execute o script principal para realizar as análises e visualizar os resultados.

## Resultados
O código gera saídas que incluem previsões das chamadas ao Disque 180 com e sem filtro aplicado nas notícias, além de tabelas e gráficos que mostram as relações identificadas pelos modelos aplicados.

## Conclusões
Os resultados deste estudo sugerem que campanhas focadas em temas específicos de violência contra a mulher têm uma influência mais forte e direta nas chamadas ao Disque 180, reforçando a importância de uma comunicação segmentada para mobilizar e apoiar a denúncia de casos de violência.

import pandas as pd
import matplotlib.pyplot as plt

# Carregar o arquivo JSON
df = pd.read_json('../0_Dados_Ligue_180/mulheres.json')

# Converter a coluna de data para o tipo datetime, assumindo que a coluna 'data' está no formato de data
df['data'] = pd.to_datetime(df['data'], errors='coerce', dayfirst=True)

# Criar uma coluna de semana e ano usando a função isocalendar
df['ano'] = df['data'].dt.isocalendar().year
df['semana'] = df['data'].dt.isocalendar().week

# Contar o número de ocorrências por semana
ocorrencias_por_semana = df.groupby(['ano', 'semana']).size().reset_index(name='ocorrencias')

# Criar uma coluna com a data da última ocorrência de cada semana
ocorrencias_por_semana['data_final_semana'] = ocorrencias_por_semana.apply(
    lambda row: f"{row['ano']}-W{int(row['semana']):02d}-1", axis=1
)
ocorrencias_por_semana['data_final_semana'] = pd.to_datetime(ocorrencias_por_semana['data_final_semana'], format="%Y-W%W-%w")

# Filtrar os dados entre 1 de abril de 2023 e 1 de março de 2024
inicio_periodo = pd.to_datetime('2023-03-20')
fim_periodo = pd.to_datetime('2024-05-26')
ocorrencias_periodo = ocorrencias_por_semana[
    (ocorrencias_por_semana['data_final_semana'] >= inicio_periodo) &
    (ocorrencias_por_semana['data_final_semana'] <= fim_periodo)
]

# Plotar a série temporal filtrada por semana
plt.figure(figsize=(12, 6))
plt.plot(ocorrencias_periodo['data_final_semana'], ocorrencias_periodo['ocorrencias'], marker='o')
plt.title('')
plt.xlabel('Semana')
plt.ylabel('Número de Ocorrências')
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.show()

# Adicionar colunas de data inicial e final da semana
ocorrencias_periodo['data_inicial_semana'] = ocorrencias_periodo['data_final_semana'] - pd.to_timedelta(ocorrencias_periodo['data_final_semana'].dt.weekday, unit='d')
ocorrencias_periodo['data_final_semana_real'] = ocorrencias_periodo['data_inicial_semana'] + pd.DateOffset(days=6)

# Mostrar todas as semanas com data inicial e final
print("Semanas analisadas com datas iniciais e finais:")
print(ocorrencias_periodo[['ano', 'semana', 'data_inicial_semana', 'data_final_semana_real']])

# Encontrar a data mais recente no dataframe df_final
data_mais_recente = ocorrencias_por_semana['data_final_semana'].max()

# Exibir a data mais recente
print(f"A data mais recente nos dados é: {data_mais_recente}")

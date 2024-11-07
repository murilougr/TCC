import pandas as pd
import matplotlib.pyplot as plt

# Função para processar cada arquivo e retornar o dataframe formatado por semana
def processar_arquivo_por_semana(file_path, genero_col, data_col, genero='FEMININO', delimiter=';'):
    df = pd.read_csv(file_path, delimiter=delimiter)

    # Filtrar por gênero
    df_filtered = df[df[genero_col].str.upper() == genero].copy()

    # Converter a coluna de data para datetime
    df_filtered[data_col] = pd.to_datetime(df_filtered[data_col], errors='coerce')
    
    # Criar uma coluna de semana (usando a função isocalendar para obter semana e ano)
    df_filtered['ano'] = df_filtered[data_col].dt.isocalendar().year
    df_filtered['semana'] = df_filtered[data_col].dt.isocalendar().week

    # Contar as ocorrências por semana
    ocorrencias_por_semana = df_filtered.groupby(['ano', 'semana']).size().reset_index(name='ocorrencias')
    return ocorrencias_por_semana

# Arquivos e suas respectivas colunas de dados
arquivos = [
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-segundo-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2024.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
]

# Processar cada arquivo e armazenar os dataframes em uma lista
dataframes = []
for arquivo in arquivos:
    df_temp = processar_arquivo_por_semana(arquivo['file'], arquivo['genero_col'], arquivo['data_col'], delimiter=arquivo['delimiter'])
    dataframes.append(df_temp)

# Concatenar todos os dataframes
df_final = pd.concat(dataframes)

# Agrupar por ano e semana e somar as ocorrências
df_final = df_final.groupby(['ano', 'semana']).sum().reset_index()

# Criar uma coluna de "data" baseada na semana (a data da última ocorrência da semana)
df_final['data_final_semana'] = df_final.apply(
    lambda row: f"{row['ano']}-W{int(row['semana']):02d}-1", axis=1
)
df_final['data_final_semana'] = pd.to_datetime(df_final['data_final_semana'], format="%Y-W%W-%w")

# Filtrar os dados entre 1 de abril de 2023 e 1 de março de 2024
inicio_periodo = pd.to_datetime('2023-03-20')
fim_periodo = pd.to_datetime('2024-05-26')
df_periodo = df_final[(df_final['data_final_semana'] >= inicio_periodo) & (df_final['data_final_semana'] <= fim_periodo)]

# Plotar a série temporal filtrada por semana
plt.figure(figsize=(12, 6))
plt.plot(df_periodo['data_final_semana'], df_periodo['ocorrencias'], marker='o')
plt.title('')
plt.xlabel('Semana')
plt.ylabel('Número de Chamadas')
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.show()

# Adicionar colunas de data inicial e final da semana
df_periodo['data_inicial_semana'] = df_periodo['data_final_semana'] - pd.to_timedelta(df_periodo['data_final_semana'].dt.weekday, unit='d')
df_periodo['data_final_semana_real'] = df_periodo['data_inicial_semana'] + pd.DateOffset(days=6)

# Mostrar todas as semanas com data inicial e final
print("Semanas analisadas com datas iniciais e finais:")
print(df_periodo[['ano', 'semana', 'data_inicial_semana', 'data_final_semana_real']])


# Encontrar a data mais recente no dataframe df_final
data_mais_recente = df_final['data_final_semana'].max()

# Exibir a data mais recente
print(f"A data mais recente nos dados é: {data_mais_recente}")

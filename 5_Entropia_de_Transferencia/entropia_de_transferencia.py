import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pyinform
from sklearn.preprocessing import StandardScaler

# Função para processar os dados e retornar a série temporal formatada por semana
def processar_arquivo_por_semana(file_path, genero_col, data_col, genero='FEMININO', delimiter=';'):
    df = pd.read_csv(file_path, delimiter=delimiter, low_memory=False)
    # Filtrar por gênero
    df_filtered = df[df[genero_col].str.upper() == genero].copy()
    # Converter a coluna de data para datetime com dayfirst=True
    df_filtered[data_col] = pd.to_datetime(df_filtered[data_col], errors='coerce', dayfirst=True)
    # Criar uma coluna de semana (usando a função isocalendar para obter semana e ano)
    df_filtered['ano'] = df_filtered[data_col].dt.isocalendar().year
    df_filtered['semana'] = df_filtered[data_col].dt.isocalendar().week
    # Contar as ocorrências por semana
    ocorrencias_por_semana = df_filtered.groupby(['ano', 'semana']).size().reset_index(name='ocorrencias')
    return ocorrencias_por_semana

# Função para quantizar as séries temporais
def quantize_series(series, num_bins=10):
    series_min = np.min(series)
    series_max = np.max(series)
    bins = np.linspace(series_min, series_max, num_bins)
    return np.digitize(series, bins) - 1  # Retorna os índices dos bins

# Função para calcular a Entropia de Transferência
def calcular_entropia_transferencia(X, Y, k=1):
    te = pyinform.transferentropy.transfer_entropy(X, Y, k)
    return te

# Definir o período de análise
inicio_periodo = pd.to_datetime('2023-03-20')
fim_periodo = pd.to_datetime('2024-05-26')

# Processar os arquivos do Disque 180
arquivos_disque180 = [
    {'file': '../0_Dados_Ligue_180/ligue180-2019.csv', 'genero_col': 'vitima_sexo', 'data_col': 'data_atendimento', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2020.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_da_denúncia', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-segundo-semestre-2020.csv', 'genero_col': 'Gênero da vítima', 'data_col': 'Data de cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2021.csv', 'genero_col': 'Gênero da vítima', 'data_col': 'Data de cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-segundo-semestre-2021.csv', 'genero_col': 'Gênero da vítima', 'data_col': 'Data de cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2022.csv', 'genero_col': 'Gênero da vítima', 'data_col': 'Data de cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-segundo-semestre-2022.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-segundo-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2024.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
]

# Processar cada arquivo e armazenar os dataframes em uma lista
dataframes_disque180 = []
for arquivo in arquivos_disque180:
    df_temp = processar_arquivo_por_semana(arquivo['file'], arquivo['genero_col'], arquivo['data_col'], delimiter=arquivo['delimiter'])
    dataframes_disque180.append(df_temp)

# Concatenar todos os dataframes do Disque 180
df_disque180 = pd.concat(dataframes_disque180)

# Agrupar por ano e semana e somar as ocorrências
df_disque180 = df_disque180.groupby(['ano', 'semana']).sum().reset_index()

# Filtrar o período definido
df_disque180['data_final_semana'] = pd.to_datetime(df_disque180['ano'].astype(str) + '-W' + df_disque180['semana'].astype(str) + '-1', format="%Y-W%W-%w")
df_disque180 = df_disque180[(df_disque180['data_final_semana'] >= inicio_periodo) & (df_disque180['data_final_semana'] <= fim_periodo)]

# Carregar o arquivo JSON das notícias do Ministério da Mulher
df_mulher = pd.read_json('../0_Dados_Ligue_180/noticias_nova_filtradas_mulheres.json')

# Converter a coluna de data para o tipo datetime
df_mulher['data'] = pd.to_datetime(df_mulher['data'], errors='coerce', dayfirst=True)

# Criar uma coluna de semana e ano usando a função isocalendar
df_mulher['ano'] = df_mulher['data'].dt.isocalendar().year
df_mulher['semana'] = df_mulher['data'].dt.isocalendar().week

# Contar o número de ocorrências por semana
df_mulher = df_mulher.groupby(['ano', 'semana']).size().reset_index(name='ocorrencias')

# Filtrar o período definido
df_mulher['data_final_semana'] = pd.to_datetime(df_mulher['ano'].astype(str) + '-W' + df_mulher['semana'].astype(str) + '-1', format="%Y-W%W-%w")
df_mulher = df_mulher[(df_mulher['data_final_semana'] >= inicio_periodo) & (df_mulher['data_final_semana'] <= fim_periodo)]

# Padronizar ambas as séries temporais
scaler_disque = StandardScaler()
scaler_mulher = StandardScaler()

df_disque180['ocorrencias_normalizadas'] = scaler_disque.fit_transform(df_disque180[['ocorrencias']])
df_mulher['ocorrencias_normalizadas'] = scaler_mulher.fit_transform(df_mulher[['ocorrencias']])

# Sincronizar as duas séries temporais
df_disque180.set_index(['ano', 'semana'], inplace=True)
df_mulher.set_index(['ano', 'semana'], inplace=True)
df_concatenado = pd.concat([df_disque180['ocorrencias_normalizadas'], df_mulher['ocorrencias_normalizadas']], axis=1, join='inner')
df_concatenado.columns = ['disque180', 'mulher']

# Certificar que os índices estão corretos (numericamente sequenciais)
df_concatenado = df_concatenado.reset_index(drop=True)

# Quantizar as séries de chamadas e notícias
quantized_chamadas = quantize_series(df_concatenado['disque180'].values, num_bins=10)
quantized_mulher = quantize_series(df_concatenado['mulher'].values, num_bins=10)

# Calcular a Entropia de Transferência
te_chamadas_para_mulher = calcular_entropia_transferencia(quantized_chamadas, quantized_mulher)
te_mulher_para_chamadas = calcular_entropia_transferencia(quantized_mulher, quantized_chamadas)

# Exibir os resultados
print(f"Entropia de Transferência (Chamadas -> Notícias): {te_chamadas_para_mulher}")
print(f"Entropia de Transferência (Notícias -> Chamadas): {te_mulher_para_chamadas}")

# Comparar as direções
if te_chamadas_para_mulher > te_mulher_para_chamadas:
    print("A transferência de informação é maior das Chamadas para as Notícias.")
elif te_mulher_para_chamadas > te_chamadas_para_mulher:
    print("A transferência de informação é maior das Notícias para as Chamadas.")
else:
    print("Não há diferença significativa na transferência de informação entre as duas direções.")

# Plotar as séries temporais para visualização
plt.figure(figsize=(10, 5))
plt.plot(df_concatenado.index, df_concatenado['disque180'], label='Chamadas ao Disque 180 (Padronizado)')
plt.plot(df_concatenado.index, df_concatenado['mulher'], label='Notícias Ministério da Mulher (Padronizado)')
plt.title('')
plt.xlabel('Semanas')
plt.ylabel('Ocorrências Padronizadas')
plt.legend()
plt.grid()
plt.show()

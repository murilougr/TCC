import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.vector_ar.var_model import VAR
from scipy.stats import chi2
import matplotlib.pyplot as plt

# Função para processar os dados e retornar a série temporal formatada por semana
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

# Processar os dados dos arquivos do Disque 180 (vários arquivos)
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
df_disque180 = pd.concat(dataframes)

# Agrupar por ano e semana e somar as ocorrências
df_disque180 = df_disque180.groupby(['ano', 'semana']).sum().reset_index()

# Carregar os dados das notícias do Ministério da Mulher
df_mulher = pd.read_json('../0_Dados_Ligue_180/mulheres.json')

# Converter a coluna de data para o tipo datetime
df_mulher['data'] = pd.to_datetime(df_mulher['data'], errors='coerce', dayfirst=True)

# Criar uma coluna de semana e ano usando a função isocalendar
df_mulher['ano'] = df_mulher['data'].dt.isocalendar().year
df_mulher['semana'] = df_mulher['data'].dt.isocalendar().week

# Contar o número de ocorrências por semana
df_mulher = df_mulher.groupby(['ano', 'semana']).size().reset_index(name='ocorrencias')

# Filtrar o período de análise (20 de março de 2023 até 26 de maio de 2024)
inicio_periodo = pd.to_datetime('2023-03-20')
fim_periodo = pd.to_datetime('2024-05-26')

# Filtrar o período para ambas as séries
df_disque180 = df_disque180[(df_disque180['ano'] >= inicio_periodo.year) & (df_disque180['ano'] <= fim_periodo.year)]
df_mulher = df_mulher[(df_mulher['ano'] >= inicio_periodo.year) & (df_mulher['ano'] <= fim_periodo.year)]

# Padronizar os dados (Disque 180 e Ministério da Mulher) para o mesmo período
scaler_disque = StandardScaler()
scaler_mulher = StandardScaler()

# Normalizar as ocorrências do Disque 180 e das notícias
df_disque180['ocorrencias_normalizadas'] = scaler_disque.fit_transform(df_disque180[['ocorrencias']])
df_mulher['ocorrencias_normalizadas'] = scaler_mulher.fit_transform(df_mulher[['ocorrencias']])

# Alinhar as duas séries temporais pelo mesmo período (usando semanas em comum)
df_disque180.set_index(['ano', 'semana'], inplace=True)
df_mulher.set_index(['ano', 'semana'], inplace=True)

# Concatenar as séries temporais
df_concatenado = pd.concat([df_disque180['ocorrencias_normalizadas'], df_mulher['ocorrencias_normalizadas']], axis=1, join='inner')
df_concatenado.columns = ['disque180', 'mulher']

# Ajustar o modelo VAR com lag = 3
print("\nAjustando o modelo VAR com lag = 3:")
var_model = VAR(df_concatenado)
var_result = var_model.fit(maxlags=3)

# Exibir sumário dos resultados
print(var_result.summary())

# Fazer previsões com o modelo ajustado (tanto para Disque 180 quanto para as notícias)
forecast_values = var_result.forecast(df_concatenado.values[-3:], steps=5)

# Desnormalizando as previsões (tirar a padronização/normalização)
forecast_values_denormalized = np.column_stack([
    scaler_disque.inverse_transform(forecast_values[:, [0]]),
    scaler_mulher.inverse_transform(forecast_values[:, [1]])
])

# Exibir previsões desnormalizadas para as próximas 5 semanas (tanto Disque 180 quanto notícias)
print("\nPrevisão para as próximas 5 semanas (valores reais):")
print(forecast_values_denormalized)

# Comparação entre previsão e valores reais para as próximas 5 semanas
real_values = df_concatenado.tail(5)
real_values_denormalized = pd.DataFrame({
    'Semana': real_values.index,
    'Previsão (Disque 180)': forecast_values_denormalized[:, 0],
    'Valor Real (Disque 180)': scaler_disque.inverse_transform(real_values[['disque180']]).flatten(),
    'Previsão (Notícias)': forecast_values_denormalized[:, 1],
    'Valor Real (Notícias)': scaler_mulher.inverse_transform(real_values[['mulher']]).flatten()
})

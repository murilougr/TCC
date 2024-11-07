from sklearn.preprocessing import StandardScaler
import numpy as np
import GPy
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import mean_absolute_error

# Função para processar os arquivos do Disque 180 e retornar a série temporal formatada por semana
def processar_arquivo_disque180(file_path, genero_col, data_col, genero='FEMININO', delimiter=';'):
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

# Processar os arquivos do Disque 180 (vários arquivos)
arquivos_disque = [
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-segundo-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2024.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
]

# Processar cada arquivo e armazenar os dataframes em uma lista
dataframes_disque = []
for arquivo in arquivos_disque:
    df_temp = processar_arquivo_disque180(arquivo['file'], arquivo['genero_col'], arquivo['data_col'], delimiter=arquivo['delimiter'])
    dataframes_disque.append(df_temp)

# Concatenar todos os dataframes do Disque 180
df_disque180 = pd.concat(dataframes_disque)

# Agrupar por ano e semana e somar as ocorrências
df_disque180 = df_disque180.groupby(['ano', 'semana']).sum().reset_index()

# Carregar o arquivo JSON das notícias do Ministério da Mulher
df_mulher = pd.read_json('../0_Dados_Ligue_180/mulheres.json')

# Converter a coluna de data para o tipo datetime
df_mulher['data'] = pd.to_datetime(df_mulher['data'], errors='coerce', dayfirst=True)

# Criar uma coluna de semana e ano usando a função isocalendar
df_mulher['ano'] = df_mulher['data'].dt.isocalendar().year
df_mulher['semana'] = df_mulher['data'].dt.isocalendar().week

# Contar o número de ocorrências por semana
df_mulher = df_mulher.groupby(['ano', 'semana']).size().reset_index(name='ocorrencias')

# Ajustar período de análise para ambas as séries
inicio_periodo = pd.to_datetime('2023-03-20')
fim_periodo = pd.to_datetime('2024-05-05')

# Filtrar o período para ambas as séries
df_disque180 = df_disque180[(df_disque180['ano'] >= inicio_periodo.year) & (df_disque180['ano'] <= fim_periodo.year)]
df_mulher = df_mulher[(df_mulher['ano'] >= inicio_periodo.year) & (df_mulher['ano'] <= fim_periodo.year)]

# Padronizar ambas as séries
scaler_disque = StandardScaler()
scaler_mulher = StandardScaler()

df_disque180['ocorrencias_normalizadas'] = scaler_disque.fit_transform(df_disque180[['ocorrencias']])
df_mulher['ocorrencias_normalizadas'] = scaler_mulher.fit_transform(df_mulher[['ocorrencias']])

# Alinhar as séries temporais para o mesmo período
df_disque180.set_index(['ano', 'semana'], inplace=True)
df_mulher.set_index(['ano', 'semana'], inplace=True)

# Concatenar as duas séries temporais baseadas nas semanas em comum
df_concatenado = pd.concat([df_disque180['ocorrencias_normalizadas'], df_mulher['ocorrencias_normalizadas']], axis=1, join='inner')
df_concatenado.columns = ['disque180', 'mulher']

# Variável `dias`: número de semanas
dias = np.array([[i] for i in range(len(df_concatenado))])

# Variáveis `disque180` e `mulher`
disque180 = df_concatenado['disque180'].values.reshape(-1, 1)
mulher = df_concatenado['mulher'].values.reshape(-1, 1)

# Kernel para o processo gaussiano multi-output
kernel = GPy.kern.Matern52(input_dim=2, variance=1., lengthscale=10.)

# Criar o modelo de regressão gaussiana de saída múltipla (Multi-output GP)
m = GPy.models.GPCoregionalizedRegression([dias, dias], [disque180, mulher], kernel)

# Otimizar o modelo para encontrar os melhores hiperparâmetros
m.optimize(messages=True)

# Gerar novos dados de semanas (previsão para as próximas 5 semanas)
semanas_futuras = np.array([[i] for i in range(len(df_concatenado), len(df_concatenado) + 5)])
output_index_futuros_disque180 = np.zeros_like(semanas_futuras)
output_index_futuros_mulher = np.ones_like(semanas_futuras)

# Concatenar as novas entradas com os índices de saída
X_futuro_disque180 = np.hstack([semanas_futuras, output_index_futuros_disque180])
X_futuro_mulher = np.hstack([semanas_futuras, output_index_futuros_mulher])

# Criar o Y_metadata para especificar a saída (0 = disque180, 1 = mulher)
Y_metadata_disque180 = {'output_index': output_index_futuros_disque180}
Y_metadata_mulher = {'output_index': output_index_futuros_mulher}

# Predição para disque180 e mulher separadamente
mean_disque180, variance_disque180 = m.predict(X_futuro_disque180, Y_metadata=Y_metadata_disque180)
mean_mulher, variance_mulher = m.predict(X_futuro_mulher, Y_metadata=Y_metadata_mulher)

# Criar datas futuras para exibição das previsões
futuras_datas = pd.date_range(start=fim_periodo, periods=6, freq='W')[1:]

# Reverter a padronização para o formato original dos dados
previsao_disque180 = scaler_disque.inverse_transform(mean_disque180).ravel()
intervalo_inferior_disque180 = scaler_disque.inverse_transform(mean_disque180 - 1.96 * np.sqrt(variance_disque180)).ravel()
intervalo_superior_disque180 = scaler_disque.inverse_transform(mean_disque180 + 1.96 * np.sqrt(variance_disque180)).ravel()

previsao_mulher = scaler_mulher.inverse_transform(mean_mulher).ravel()
intervalo_inferior_mulher = scaler_mulher.inverse_transform(mean_mulher - 1.96 * np.sqrt(variance_mulher)).ravel()
intervalo_superior_mulher = scaler_mulher.inverse_transform(mean_mulher + 1.96 * np.sqrt(variance_mulher)).ravel()

# Adicionar os valores reais das semanas previstas para as tabelas
valores_reais_disque180 = df_disque180.tail(5)['ocorrencias'].values
valores_reais_mulher = df_mulher.tail(5)['ocorrencias'].values

# Criar datas futuras para exibição das previsões
futuras_datas = pd.date_range(start=fim_periodo, periods=6, freq='W')[1:]

# **Adicionar esta seção para calcular 'data_final_semana' em df_mulher**
# Resetar o índice para facilitar o manuseio
df_mulher = df_mulher.reset_index()

# Criar 'data_final_semana' para df_mulher
df_mulher['data_final_semana'] = df_mulher.apply(
    lambda row: f"{int(row['ano'])}-W{int(row['semana']):02d}-1", axis=1
)
df_mulher['data_final_semana'] = pd.to_datetime(df_mulher['data_final_semana'], format="%Y-W%W-%w")

# Filtrar as 5 semanas reais para comparação
df_teste_mulher = df_mulher[df_mulher['data_final_semana'] > fim_periodo]
df_teste_mulher = df_teste_mulher.sort_values('data_final_semana')

# Garantir que temos pelo menos 5 semanas de dados reais
valores_reais_mulher = df_teste_mulher['ocorrencias'].values[:5]

# **Fazer o mesmo para df_disque180**
df_disque180 = df_disque180.reset_index()

df_disque180['data_final_semana'] = df_disque180.apply(
    lambda row: f"{int(row['ano'])}-W{int(row['semana']):02d}-1", axis=1
)
df_disque180['data_final_semana'] = pd.to_datetime(df_disque180['data_final_semana'], format="%Y-W%W-%w")

df_teste_disque180 = df_disque180[df_disque180['data_final_semana'] > fim_periodo]
df_teste_disque180 = df_teste_disque180.sort_values('data_final_semana')

valores_reais_disque180 = df_teste_disque180['ocorrencias'].values[:5]

# Criar tabela para o Disque 180
tabela_disque180 = pd.DataFrame({
    'Data Inicial Semana': (futuras_datas - pd.to_timedelta(futuras_datas.weekday, unit='d')),
    'Previsão': previsao_disque180,
    'Int. Inferior': intervalo_inferior_disque180,
    'Int. Superior': intervalo_superior_disque180,
    'Valor Real': valores_reais_disque180,
    'Erro': np.abs(previsao_disque180 - valores_reais_disque180)
})

# Criar tabela para o Ministério da Mulher
tabela_mulher = pd.DataFrame({
    'Data Inicial Semana': (futuras_datas - pd.to_timedelta(futuras_datas.weekday, unit='d')),
    'Previsão': previsao_mulher,
    'Int. Inferior': intervalo_inferior_mulher,
    'Int. Superior': intervalo_superior_mulher,
    'Valor Real': valores_reais_mulher,
    'Erro': np.abs(previsao_mulher - valores_reais_mulher)
})

# Print das tabelas finais
print("Tabela Disque 180:")
print(tabela_disque180)

print("\nTabela Ministério da Mulher:")
print(tabela_mulher)

# Transformando o índice em numérico (caso esteja causando problemas)
df_concatenado = df_concatenado.reset_index()

# Visualização dos dados e das previsões
plt.figure(figsize=(10,6))

# Dados originais
plt.plot(df_concatenado.index, df_concatenado['disque180'].values, 'b', label="Disque 180 (Normalizado)")
plt.plot(df_concatenado.index, df_concatenado['mulher'].values, 'r', label="Ministério da Mulher (Normalizado)")

# Previsão
plt.plot(futuras_datas, mean_disque180.ravel(), 'b--', label="Previsão Disque 180")
plt.plot(futuras_datas, mean_mulher.ravel(), 'r--', label="Previsão Ministério da Mulher")

# Intervalos de confiança para Disque 180
plt.fill_between(futuras_datas, 
                 mean_disque180.ravel() - 1.96 * np.sqrt(variance_disque180.ravel()),
                 mean_disque180.ravel() + 1.96 * np.sqrt(variance_disque180.ravel()),
                 color='blue', alpha=0.2)

# Intervalos de confiança para Ministério da Mulher
plt.fill_between(futuras_datas, 
                 mean_mulher.ravel() - 1.96 * np.sqrt(variance_mulher.ravel()),
                 mean_mulher.ravel() + 1.96 * np.sqrt(variance_mulher.ravel()),
                 color='red', alpha=0.2)

plt.legend()
plt.title("Previsão de Chamadas (Disque 180) e Ocorrências (Ministério da Mulher)")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.show()
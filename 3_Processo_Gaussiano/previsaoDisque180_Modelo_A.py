import numpy as np
import GPy
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import mean_absolute_error

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

# Filtrar os dados até 26 de maio de 2024 (sem utilizar as últimas 5 semanas)
inicio_periodo = pd.to_datetime('2023-03-20')
fim_periodo = pd.to_datetime('2024-05-26')
df_treino = df_final[(df_final['data_final_semana'] >= inicio_periodo) & (df_final['data_final_semana'] <= fim_periodo)]

# Variável `dias`: número de semanas
dias = np.array([[i] for i in range(len(df_treino))])

# Variável `chamadas`: número de ocorrências por semana
chamadas = df_treino['ocorrencias'].values.reshape(-1, 1)

# Kernel para o processo gaussiano
kernel = GPy.kern.Matern52(input_dim=1, variance=1., lengthscale=10.)

# Criar o modelo de regressão gaussiana (GP) com saída única
m = GPy.models.GPRegression(dias, chamadas, kernel)

# Otimizar o modelo para encontrar os melhores hiperparâmetros
m.optimize(messages=True)

# Gerar novos dados de semanas (previsão para as próximas 5 semanas)
semanas_futuras = np.array([[i] for i in range(len(df_treino), len(df_treino) + 5)])

# Fazer a previsão
mean_chamadas, variance_chamadas = m.predict(semanas_futuras)

# Criar datas futuras para exibição das previsões
futuras_datas = pd.date_range(start=df_treino['data_final_semana'].iloc[-1], periods=6, freq='W')[1:]

# Filtrar as 5 semanas reais para comparação
df_teste = df_final[(df_final['data_final_semana'] > fim_periodo)]

# Exibir as previsões em forma de tabela com intervalo e valor real
previsoes_df = pd.DataFrame({
    'Data Inicial Semana': futuras_datas - pd.to_timedelta(futuras_datas.weekday, unit='d'),
    'Data Final Semana': futuras_datas - pd.to_timedelta(futuras_datas.weekday, unit='d') + pd.DateOffset(days=6),
    'Previsão de Chamadas': mean_chamadas[:, 0],
    'Intervalo Inferior': mean_chamadas[:, 0] - 1.96 * np.sqrt(variance_chamadas[:, 0]),
    'Intervalo Superior': mean_chamadas[:, 0] + 1.96 * np.sqrt(variance_chamadas[:, 0]),
    'Valor Real': df_teste['ocorrencias'].values[:5],
    'Erro Absoluto': np.abs(df_teste['ocorrencias'].values[:5] - mean_chamadas[:, 0])
})

# Print da tabela final
print(previsoes_df)

# Visualização dos dados e das previsões
plt.figure(figsize=(10,6))

# Dados originais
plt.plot(df_treino['data_final_semana'], chamadas, 'b', label="Número de Chamadas")

# Previsão
plt.plot(futuras_datas, mean_chamadas, 'b--', label="Previsão de Chamadas")

# Intervalo de confiança para chamadas
plt.fill_between(futuras_datas, 
                 mean_chamadas[:, 0] - 1.96 * np.sqrt(variance_chamadas[:, 0]),
                 mean_chamadas[:, 0] + 1.96 * np.sqrt(variance_chamadas[:, 0]),
                color='blue', alpha=0.2)

plt.legend()
plt.title("")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.show()

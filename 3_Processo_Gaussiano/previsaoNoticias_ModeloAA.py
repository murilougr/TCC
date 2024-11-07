import numpy as np
import GPy
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import mean_absolute_error

# Carregar o arquivo JSON
df = pd.read_json('../0_Dados_Ligue_180/mulheres.json')

# Converter a coluna de data para o tipo datetime
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

# Filtrar os dados entre 1 de abril de 2023 e 1 de maio de 2024 (ou seja, até a 5ª semana antes do final)
inicio_periodo = pd.to_datetime('2023-03-20')
fim_periodo = pd.to_datetime('2024-05-26')
ocorrencias_periodo = ocorrencias_por_semana[
    (ocorrencias_por_semana['data_final_semana'] >= inicio_periodo) & 
    (ocorrencias_por_semana['data_final_semana'] <= fim_periodo)
]

# Variável `dias`: número de semanas
dias = np.array([[i] for i in range(len(ocorrencias_periodo))])

# Variável `ocorrencias`: número de ocorrências por semana
ocorrencias = ocorrencias_periodo['ocorrencias'].values.reshape(-1, 1)

# Kernel para o processo gaussiano
kernel = GPy.kern.Matern52(input_dim=1, variance=1., lengthscale=10.)

# Criar o modelo de regressão gaussiana (GP) com saída única
m = GPy.models.GPRegression(dias, ocorrencias, kernel)

# Otimizar o modelo para encontrar os melhores hiperparâmetros
m.optimize(messages=True)

# Gerar novos dados de semanas (previsão para as próximas 5 semanas)
semanas_futuras = np.array([[i] for i in range(len(ocorrencias_periodo), len(ocorrencias_periodo) + 5)])

# Fazer a previsão
mean_ocorrencias, variance_ocorrencias = m.predict(semanas_futuras)

# Criar datas futuras para exibição das previsões
futuras_datas = pd.date_range(start=ocorrencias_periodo['data_final_semana'].iloc[-1], periods=6, freq='W')[1:]

# Filtrar as 5 semanas reais para comparação (caso já tenham sido coletadas)
df_teste = ocorrencias_por_semana[(ocorrencias_por_semana['data_final_semana'] > fim_periodo)]

# Exibir as previsões em forma de tabela com intervalo e valor real
previsoes_df = pd.DataFrame({
    'Data Inicial Semana': futuras_datas - pd.to_timedelta(futuras_datas.weekday, unit='d'),
    'Data Final Semana': futuras_datas - pd.to_timedelta(futuras_datas.weekday, unit='d') + pd.DateOffset(days=6),
    'Previsão de Ocorrências': mean_ocorrencias[:, 0],
    'Intervalo Inferior': mean_ocorrencias[:, 0] - 1.96 * np.sqrt(variance_ocorrencias[:, 0]),
    'Intervalo Superior': mean_ocorrencias[:, 0] + 1.96 * np.sqrt(variance_ocorrencias[:, 0]),
    'Valor Real': df_teste['ocorrencias'].values[:5],
    'Erro Absoluto': np.abs(df_teste['ocorrencias'].values[:5] - mean_ocorrencias[:, 0])
})

# Print da tabela final
print(previsoes_df)

# Visualização dos dados e das previsões
plt.figure(figsize=(10,6))

# Dados originais
plt.plot(ocorrencias_periodo['data_final_semana'], ocorrencias, 'b', label="Número de Ocorrências")

# Previsão
plt.plot(futuras_datas, mean_ocorrencias, 'b--', label="Previsão de Ocorrências")

# Intervalo de confiança para ocorrências
plt.fill_between(futuras_datas, 
                 mean_ocorrencias[:, 0] - 1.96 * np.sqrt(variance_ocorrencias[:, 0]),
                 mean_ocorrencias[:, 0] + 1.96 * np.sqrt(variance_ocorrencias[:, 0]),
                 color='blue', alpha=0.2)

plt.legend()
plt.title("")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.show()

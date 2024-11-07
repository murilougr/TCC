import pandas as pd
import matplotlib.pyplot as plt

# Função para processar cada arquivo e retornar o dataframe formatado
def processar_arquivo(file_path, genero_col, data_col, genero='FEMININO', delimiter=';'):
    df = pd.read_csv(file_path, delimiter=delimiter)

    # Filtrar por gênero
    df_filtered = df[df[genero_col].str.upper() == genero].copy()

    # Converter a coluna de data para datetime
    df_filtered[data_col] = pd.to_datetime(df_filtered[data_col], errors='coerce')
    df_filtered.loc[:, 'mes'] = df_filtered[data_col].dt.to_period('M')

    # Contar as ocorrências por mês
    ocorrencias_por_mes = df_filtered.groupby(['mes']).size().reset_index(name='ocorrencias')
    return ocorrencias_por_mes

# Arquivos e suas respectivas colunas de dados
arquivos = [
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-segundo-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2024.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
]

# Processar cada arquivo e armazenar os dataframes em uma lista
dataframes = []
for arquivo in arquivos:
    df_temp = processar_arquivo(arquivo['file'], arquivo['genero_col'], arquivo['data_col'], delimiter=arquivo['delimiter'])
    dataframes.append(df_temp)

# Concatenar todos os dataframes
df_final = pd.concat(dataframes)

# Agrupar por mês e somar as ocorrências
df_final = df_final.groupby('mes').sum().reset_index()

# Converter o período para string para facilitar o plot
df_final['mes'] = df_final['mes'].dt.strftime('%m/%Y')

# Plotar a série temporal unificada
plt.figure(figsize=(12, 6))
plt.plot(df_final['mes'], df_final['ocorrencias'], marker='o')
plt.title('')
plt.xlabel('Mês')
plt.ylabel('Número de Ocorrências')
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.show()

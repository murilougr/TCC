import pandas as pd
import matplotlib.pyplot as plt

# Função para processar cada arquivo e retornar o dataframe formatado por dia
def processar_arquivo_por_dia(file_path, genero_col, data_col, genero='FEMININO', delimiter=';'):
    df = pd.read_csv(file_path, delimiter=delimiter)

    # Filtrar por gênero
    df_filtered = df[df[genero_col].str.upper() == genero].copy()

    # Converter a coluna de data para datetime
    df_filtered[data_col] = pd.to_datetime(df_filtered[data_col], errors='coerce')
    
    # Criar uma coluna de data (dia)
    df_filtered['data'] = df_filtered[data_col].dt.date

    # Contar as ocorrências por dia
    ocorrencias_por_dia = df_filtered.groupby(['data']).size().reset_index(name='ocorrencias')
    return ocorrencias_por_dia

# Arquivos e suas respectivas colunas de dados
arquivos = [
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-segundo-semestre-2023.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
    {'file': '../0_Dados_Ligue_180/ligue180-primeiro-semestre-2024.csv', 'genero_col': 'Gênero_da_vítima', 'data_col': 'Data_de_cadastro', 'delimiter': ';'},
]

# Processar cada arquivo e armazenar os dataframes em uma lista
dataframes = []
for arquivo in arquivos:
    df_temp = processar_arquivo_por_dia(arquivo['file'], arquivo['genero_col'], arquivo['data_col'], delimiter=arquivo['delimiter'])
    dataframes.append(df_temp)

# Concatenar todos os dataframes
df_final = pd.concat(dataframes)

# Agrupar por data e somar as ocorrências
df_final = df_final.groupby(['data']).sum().reset_index()

# Plotar a série temporal unificada por dia
plt.figure(figsize=(12, 6))
plt.plot(df_final['data'], df_final['ocorrencias'], marker='o')
plt.title('')
plt.xlabel('Dia')
plt.ylabel('Número de Ocorrências')
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.show()

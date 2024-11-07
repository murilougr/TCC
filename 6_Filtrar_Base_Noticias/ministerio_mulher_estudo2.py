import re
import json
from collections import Counter

# Função para carregar o arquivo JSON
def carregar_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

# Carregar os arquivos JSON
bases_de_dados = [
    '../0_Dados_Ligue_180/mulheres.json',
]

# Lista de radicais para a primeira análise (uma palavra)
radicais_uma_palavra = [
    r'\bfeminis',        # Feminismo
    r'\bmachism',      # Machismo
    r'\bmisogin',      # Misoginia
    r'\bsexismo',      # Sexismo
    r'\bviolenc',      # Violência
    r'\bviolent',      # Violento
    r'\bassed',        # Assédio
    r'\basséd',        # Assédio
    r'\babus',         # Abuso
    r'\bagress',       # Agressão
    r'\bestupro',      # Estupro
    r'\bfeminic',      # Feminicídio
    r'\bpatriarc',     # Patriarcado
    r'\bdesiguald',    # Desigualdade
    r'\bopress',       # Opressão
    r'\bexplor',        # Exploração
    r'\bdiscrimin',    # Discriminação
    r'\bpreconceit',   # Preconceito
    r'\bdenúnc',       # Denúncia
    r'\bdenunc',       # Denúncia
    r'\bcrueld',       # Crueldade
    r'\bopress',       # Crueldade
    r'\bigual',       # Crueldade
    r'\bequidad',       # Crueldade
]


# Lista de pares de radicais para a segunda análise (duas palavras no mesmo título)
radicais_duas_palavras = [
    # LEIS
    (r'\bmaria', r'\bpenha'),         # Lei Maria da Penha
    (r'\bligue', r'\b180'),           # Ligue 180 (denúncia)
    (r'\bminuto', r'\bseguinte'),     # Minuto seguinte (ligado ao combate à violência)
    (r'\blei', r'\bimportuna'),     # Lei de Importunação Sexual
    (r'\bcasa', r'\bmulher'),      # Casa da Mulher Brasileira (abrigo e proteção)

    (r'\blei', r'\bproteç'),          # Leis de proteção
    (r'\blei', r'\bcombat'),          # Leis de proteção
    (r'\blei', r'\bjustiça'),          # Leis de proteção
    (r'\blei', r'\bseguran'),          # Leis de proteção

    (r'\bpolit', r'\bproteç'),          # Leis de proteção
    (r'\bpolit', r'\bcombat'),          # Leis de proteção
    (r'\bpolit', r'\bjustiça'),          # Leis de proteção
    (r'\bpolit', r'\bseguran'),          # Leis de proteção

    (r'\bnorma', r'\bproteç'),          # Leis de proteção
    (r'\bnorma', r'\bcombat'),          # Leis de proteção
    (r'\bnorma', r'\bjustiça'),          # Leis de proteção
    (r'\bnorma', r'\bseguran'),          # Leis de proteção

    (r'\bregulam', r'\bproteç'),          # Leis de proteção
    (r'\bregulam', r'\bcombat'),          # Leis de proteção
    (r'\bregulam', r'\bjustiça'),          # Leis de proteção
    (r'\bregulam', r'\bseguran'),          # Leis de proteção

    (r'\bestatut', r'\bproteç'),          # Leis de proteção
    (r'\bestatut', r'\bcombat'),          # Leis de proteção
    (r'\bestatut', r'\bjustiça'),          # Leis de proteção
    (r'\bestatut', r'\bseguran'),          # Leis de proteção

    (r'\bdecret', r'\bproteç'),          # Leis de proteção
    (r'\bdecret', r'\bcombat'),          # Leis de proteção
    (r'\bdecret', r'\bjustiça'),          # Leis de proteção
    (r'\bdecret', r'\bseguran'),          # Leis de proteção

    (r'\bdireit', r'\bproteç'),          # Leis de proteção
    (r'\bdireit', r'\bcombat'),          # Leis de proteção
    (r'\bdireit', r'\bjustiça'),          # Leis de proteção
    (r'\bdireit', r'\bseguran'),          # Leis de proteção

    (r'\bcod', r'\bproteç'),          # Leis de proteção
    (r'\bcod', r'\bcombat'),          # Leis de proteção
    (r'\bcod', r'\bjustiça'),          # Leis de proteção
    (r'\bcod', r'\bseguran'),          # Leis de proteção

    (r'\bplan', r'\bproteç'),          # Leis de proteção
    (r'\bplan', r'\bcombat'),          # Leis de proteção
    (r'\bplan', r'\bjustiça'),          # Leis de proteção
    (r'\bplan', r'\bseguran'),          # Leis de proteção

    (r'\bpropost', r'\bproteç'),          # Leis de proteção
    (r'\bpropost', r'\bcombat'),          # Leis de proteção
    (r'\bpropost', r'\bjustiça'),          # Leis de proteção
    (r'\bpropost', r'\bseguran'),          # Leis de proteção

    (r'\bprojet', r'\bproteç'),          # Leis de proteção
    (r'\bprojet', r'\bcombat'),          # Leis de proteção
    (r'\bprojet', r'\bjustiça'),          # Leis de proteção
    (r'\bprojet', r'\bseguran'),          # Leis de proteção

    # MULHER | FEMIN | GENER
    (r'\bmulher', r'\bproteç'),        # Igualdade para mulheres
    (r'\bmulher', r'\bcombat'),      # Equidade para mulheres
    (r'\bmulher', r'\bjustiça'),      # Justiça para mulheres
    (r'\bmulher', r'\bseguran'),      # Segurança para mulheres
    (r'\bmulher', r'\bcrime'),       # Crimes de feminicídio
    (r'\bmulher', r'\blei'),       # Crimes de feminicídio
    (r'\bmulher', r'\bpolit'),       # Crimes de feminicídio
    (r'\bmulher', r'\bnorma'),       # Crimes de feminicídio
    (r'\bmulher', r'\bregulam'),       # Crimes de feminicídio
    (r'\bmulher', r'\bestatut'),       # Crimes de feminicídio
    (r'\bmulher', r'\bdecret'),       # Crimes de feminicídio
    (r'\bmulher', r'\bdireit'),       # Crimes de feminicídio
    (r'\bmulher', r'\bplan'),       # Crimes de feminicídio
    (r'\bmulher', r'\bpropost'),       # Crimes de feminicídio
    (r'\bmulher', r'\bprojet'),       # Crimes de feminicídio
    (r'\bmulher', r'\bconflit'),       # Crimes de feminicídio
    (r'\bmulher', r'\bdireit'),       # Crimes de feminicídio

    (r'\bgêner', r'\bproteç'),        # Igualdade para mulheres
    (r'\bgêner', r'\bcombat'),      # Equidade para mulheres
    (r'\bgêner', r'\bjustiça'),      # Justiça para mulheres
    (r'\bgêner', r'\bseguran'),      # Segurança para mulheres
    (r'\bgêner', r'\bcrime'),       # Crimes de feminicídio
    (r'\bgêner', r'\blei'),       # Crimes de feminicídio
    (r'\bgêner', r'\bpolit'),       # Crimes de feminicídio
    (r'\bgêner', r'\bnorma'),       # Crimes de feminicídio
    (r'\bgêner', r'\bregulam'),       # Crimes de feminicídio
    (r'\bgêner', r'\bestatut'),       # Crimes de feminicídio
    (r'\bgêner', r'\bdecret'),       # Crimes de feminicídio
    (r'\bgêner', r'\bdireit'),       # Crimes de feminicídio
    (r'\bgêner', r'\bplan'),       # Crimes de feminicídio
    (r'\bgêner', r'\bpropost'),       # Crimes de feminicídio
    (r'\bgêner', r'\bprojet'),       # Crimes de feminicídio
    (r'\bgêner', r'\bconflit'),       # Crimes de feminicídio
    (r'\bgêner', r'\bdireit'),       # Crimes de feminicídio

    (r'\bfemin', r'\bproteç'),        # Igualdade para mulheres
    (r'\bfemin', r'\bcombat'),      # Equidade para mulheres
    (r'\bfemin', r'\bjustiça'),      # Justiça para mulheres
    (r'\bfemin', r'\bseguran'),      # Segurança para mulheres
    (r'\bfemin', r'\bcrime'),       # Crimes de feminicídio
    (r'\bfemin', r'\blei'),       # Crimes de feminicídio
    (r'\bfemin', r'\bpolit'),       # Crimes de feminicídio
    (r'\bfemin', r'\bnorma'),       # Crimes de feminicídio
    (r'\bfemin', r'\bregulam'),       # Crimes de feminicídio
    (r'\bfemin', r'\bestatut'),       # Crimes de feminicídio
    (r'\bfemin', r'\bdecret'),       # Crimes de feminicídio
    (r'\bfemin', r'\bdireit'),       # Crimes de feminicídio
    (r'\bfemin', r'\bplan'),       # Crimes de feminicídio
    (r'\bfemin', r'\bpropost'),       # Crimes de feminicídio
    (r'\bfemin', r'\bprojet'),       # Crimes de feminicídio
    (r'\bfemin', r'\bconflit'),       # Crimes de feminicídio
    (r'\bfemin', r'\bdireit'),       # Crimes de feminicídio
]

# Função para verificar se qualquer radical está presente no título (uma palavra)
def verificar_radical_uma_palavra(titulo, radicais):
    for radical in radicais:
        if re.search(radical, titulo, re.IGNORECASE):
            return True
    return False

# Função para verificar se dois radicais estão presentes no mesmo título
def verificar_radicais_duas_palavras(titulo, pares_radicais):
    for radical1, radical2 in pares_radicais:
        if re.search(radical1, titulo, re.IGNORECASE) and re.search(radical2, titulo, re.IGNORECASE):
            return True
    return False

# Função para contar o número de notícias em cada categoria
def contar_categorias(noticias):
    categorias = [item['categoria'] for item in noticias if 'categoria' in item and item['categoria']]
    contador_categorias = Counter(categorias)
    return contador_categorias

# Analisar notícias em múltiplos arquivos e armazenar notícias filtradas
noticias_uma_palavra = []
noticias_duas_palavras = []

for base in bases_de_dados:
    data = carregar_json(base)

    for noticia in data:
        titulo = noticia.get('title', '')

        # Verificar a primeira análise (uma palavra)
        if verificar_radical_uma_palavra(titulo, radicais_uma_palavra):
            noticias_uma_palavra.append(noticia)

        # Verificar a segunda análise (duas palavras no mesmo título)
        if verificar_radicais_duas_palavras(titulo, radicais_duas_palavras):
            noticias_duas_palavras.append(noticia)

# Contar o número de notícias em cada categoria para as notícias filtradas
contador_uma_palavra = contar_categorias(noticias_uma_palavra)
contador_duas_palavras = contar_categorias(noticias_duas_palavras)

# Exibir os resultados
print(f"Número de notícias que correspondem à primeira análise (uma palavra): {len(noticias_uma_palavra)}")
print("Número de notícias por categoria (uma palavra):")
for categoria, count in contador_uma_palavra.items():
    print(f"{categoria}: {count}")

print(f"\nNúmero de notícias que correspondem à segunda análise (duas palavras): {len(noticias_duas_palavras)}")
print("Número de notícias por categoria (duas palavras):")
for categoria, count in contador_duas_palavras.items():
    print(f"{categoria}: {count}")

# Montar o JSON final com as notícias que passaram nos filtros
noticias_filtradas = {
    'noticias_uma_palavra': noticias_uma_palavra,
    'noticias_duas_palavras': noticias_duas_palavras
}

# Salvar o JSON filtrado em um novo arquivo
with open('../0_Dados_Ligue_180/noticias_nova_filtradas_mulheres_direitos.json', 'w', encoding='utf-8') as file:
    json.dump(noticias_filtradas, file, ensure_ascii=False, indent=4)

print("Notícias filtradas foram salvas no arquivo 'noticias_filtradas.json'.")

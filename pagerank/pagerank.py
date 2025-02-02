import os
import random
import re
import sys

# Definição de constantes
DAMPING = 0.85  # Fator de amortecimento para o algoritmo de PageRank
SAMPLES = 10000  # Número de amostras para o método de amostragem


def main():
    """
    Função principal que executa o algoritmo PageRank.
    """
    if len(sys.argv) != 2:
        # Verifica se o usuário forneceu um diretório como argumento
        sys.exit("Usage: python pagerank.py corpus")  
    # Realiza a leitura do corpus (conjunto de páginas e seus links)
    corpus = crawl(sys.argv[1])

    # Calcula o PageRank usando o método de amostragem
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

    # Calcula o PageRank usando o método iterativo
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Lê um diretório de arquivos HTML e extrai links para outras páginas.
    Retorna um dicionário onde cada chave é uma página e os valores são 
    um conjunto de páginas que são referenciadas por ela.
    """
    pages = dict()

    # Percorre todos os arquivos no diretório fornecido
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):  # Apenas processa arquivos HTML
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            # Expressão regular para encontrar links dentro de <a href="...">
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            # Remove auto-referências e adiciona ao dicionário
            pages[filename] = set(links) - {filename}

    # Filtra os links para garantir que apenas páginas dentro do corpus sejam consideradas
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename] if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Retorna um modelo de transição que define a distribuição de probabilidade de qual página visitar a seguir.
    
    - Com probabilidade `damping_factor`, escolhe um link aleatório a partir da página atual.
    - Com probabilidade `1 - damping_factor`, escolhe qualquer página do corpus aleatoriamente.
    """
    probabilidades = {chave: 0 for chave in corpus}  # Inicializa o dicionário de probabilidades

    # Se a página tiver links, usa-os. Caso contrário, considera todas as páginas do corpus.
    links = corpus[page] if corpus[page] else corpus.keys()

    for pagina in probabilidades:
        probabilidades[pagina] = (1 - damping_factor) / len(corpus)  # Distribuição uniforme
        if pagina in links:
            # Adiciona a probabilidade proporcional aos links
            probabilidades[pagina] += damping_factor / len(links)  

    return probabilidades


def sample_pagerank(corpus, damping_factor, n):
    """
    Retorna os valores de PageRank estimados por meio de amostragem de `n` páginas.
    
    - Escolhe uma página inicial aleatória.
    - Usa o modelo de transição para determinar a próxima página a ser visitada.
    - Repete esse processo `n` vezes e calcula a frequência relativa das visitas.
    """
    rank = {pagina: 0 for pagina in corpus}  # Inicializa as contagens de visita para cada página

    pagina = random.choice(list(corpus.keys()))  # Escolhe uma página inicial aleatória

    for _ in range(n):
        rank[pagina] += 1  # Conta a visita à página atual
        model = transition_model(corpus, pagina, damping_factor)  # Obtém o modelo de transição
        paginas = list(model.keys())
        probabilidades = list(model.values())

        if not paginas or not probabilidades:  # Caso não haja páginas válidas, encerra o loop
            break

        # Escolhe a próxima página baseada nas probabilidades
        pagina = random.choices(paginas, probabilidades)[0]  

    # Normaliza os valores para que a soma seja 1
    total = sum(rank.values())
    for pagina in rank:
        rank[pagina] /= total
    
    return rank


def iterate_pagerank(corpus, damping_factor):
    """
    Retorna os valores de PageRank por meio de um processo iterativo até convergência.
    
    - Começa atribuindo valores iniciais iguais a todas as páginas.
    - Atualiza os valores de PageRank iterativamente até que a variação seja menor que um limite `threshold`.
    """
    # Inicializa com valores iguais para todas as páginas
    rank = {page: 1 / len(corpus) for page in corpus}  
    threshold = 0.001  # Define o critério de convergência

    while True:
        new_rank = {}  # Novo dicionário para armazenar os valores atualizados
        for pagina in corpus:
            total = (1 - damping_factor) / len(corpus)  # Parcela fixa do cálculo

            for link_page in corpus:
                if pagina in corpus[link_page]:  # Se a página recebe links de outra
                    total += damping_factor * (rank[link_page] / len(corpus[link_page]))

                if not corpus[link_page]:  # Caso uma página não tenha links, considera link para todas
                    total += damping_factor * (rank[link_page] / len(corpus))

            new_rank[pagina] = total  # Atualiza o novo valor de PageRank

        # Verifica se houve convergência (mudanças pequenas o suficiente)
        if all(abs(new_rank[p] - rank[p]) < threshold for p in rank):
            break

        rank = new_rank.copy()  # Atualiza os valores para a próxima iteração

    return rank  # Retorna os valores finais de PageRank


if __name__ == "__main__":
    main()

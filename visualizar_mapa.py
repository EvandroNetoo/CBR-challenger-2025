import json
from time import sleep

import httpx
import matplotlib.image as mpimg
import networkx as nx
from matplotlib import pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from networkx import Graph
from networkx.readwrite import json_graph
from scipy.ndimage import rotate

IP_BRICK = '192.168.101.132'


def print_mapa(grafo: Graph, pos_atual: tuple[int, int], direcao: int):
    plt.clf()
    pos = {(i, j): (j, -i) for i in range(5) for j in range(6)}
    pos[(-1, -1)] = (-1, -2)

    cores_arestas = [conhecimento['cor'] for u, v, conhecimento in grafo.edges.data('conhecimento')]
    labels_arestas = {(u, v): conhecimento['peso'] for u, v, conhecimento in grafo.edges.data('conhecimento')}

    nx.draw(
        grafo,
        pos=pos,
        with_labels=True,
        node_size=500,
        node_color='lightblue',
        edge_color=cores_arestas,
        width=5,
        font_size=8,
        font_color='black',
    )
    nx.draw_networkx_edge_labels(grafo, pos, edge_labels=labels_arestas)

    img = mpimg.imread('robo.jpg')
    img_rotated = rotate(img, angle=direcao * -90, reshape=True)
    imagebox = OffsetImage(img_rotated, zoom=0.6)
    ab = AnnotationBbox(imagebox, (pos_atual[1], -pos_atual[0]), frameon=False)

    plt.gca().add_artist(ab)

    plt.draw()


def main():
    URL = f'http://{IP_BRICK}:8080/mapa'
    plt.ion()
    plt.figure()

    while True:
        try:
            response = httpx.get(URL)
            response.raise_for_status()
        except httpx.HTTPError as e:
            print(f'Erro na requisição: {e}')
            sleep(0.1)
            continue

        data = json.loads(response.text)

        grafo = json_graph.node_link_graph(data['grafo'], edges='edges')
        pos_atual = tuple(data['pos_atual'])
        direcao = data['direcao']
        print_mapa(grafo, pos_atual, direcao)

        plt.pause(0.1)


if __name__ == '__main__':
    main()

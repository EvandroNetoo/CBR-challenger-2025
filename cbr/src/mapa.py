from typing import Iterable

import matplotlib.pyplot as plt
import networkx as nx


class OpçõesConhecimentoAresta:
    INICIO = {'peso': 50, 'cor': 'blue'}
    VAZIO = {'peso': 1, 'cor': 'green'}
    DESCONHECIDA = {'peso': 2, 'cor': 'gray'}
    BLOCO = {'peso': None, 'cor': 'yellow'}
    BLOCO_BRANCO = {'peso': None, 'cor': 'red'}


class Mapa:
    AREA_VERDE = (-1, -1)

    def __init__(self, altura: int = 5, largura: int = 6):
        self.altura = altura
        self.largura = largura
        self.grafo: nx.Graph = nx.grid_2d_graph(altura, largura)

        for aresta in self.grafo.edges:
            self.grafo.edges[aresta]['conhecimento'] = OpçõesConhecimentoAresta.DESCONHECIDA

        self.grafo.add_node(self.AREA_VERDE)
        for node in self.grafo.nodes:
            if node[1] == 0:
                self.grafo.add_edge(
                    self.AREA_VERDE,
                    node,
                    conhecimento=OpçõesConhecimentoAresta.INICIO,
                )

    def caminho_saida(self, origem):
        """Calcula o caminho mais curto do nó de origem até a área verde (0, -1) usando Dijkstra."""
        return nx.dijkstra_path(
            self.grafo,
            source=origem,
            target=self.AREA_VERDE,
            weight=lambda u, v, a: a['conhecimento']['peso'],
        )

    def nos_com_bloco(self) -> set[tuple[int, int]]:
        """Retorna um conjunto de nós que possuem arestas com conhecimento de bloco."""
        nos_com_bloco = set()
        for u, v, conhecimento in self.grafo.edges.data('conhecimento'):
            if conhecimento == OpçõesConhecimentoAresta.BLOCO:
                nos_com_bloco.add(u)
                nos_com_bloco.add(v)
        return nos_com_bloco

    def nos_com_arestas_desconhecidas(self) -> list[tuple[int, int]]:
        """Retorna uma lista de nós que possuem arestas com conhecimento desconhecido."""
        nos_com_arestas_desconhecidas = set()
        for u, v, conhecimento in self.grafo.edges.data('conhecimento'):
            if conhecimento == OpçõesConhecimentoAresta.DESCONHECIDA:
                nos_com_arestas_desconhecidas.add(u)
                nos_com_arestas_desconhecidas.add(v)
        nos_com_arestas_desconhecidas = list(nos_com_arestas_desconhecidas)

        # Ordena os nós por prioridade baseada na quantidade de vizinhos desconhecidos
        def contar_vizinhos_desconhecidos(no):
            vizinhos_desconhecidos = set()
            # Conta vizinhos diretos com arestas desconhecidas
            for vizinho in self.grafo.neighbors(no):
                if self.grafo.edges[no, vizinho]['conhecimento'] == OpçõesConhecimentoAresta.DESCONHECIDA:
                    vizinhos_desconhecidos.add(vizinho)

                # Conta vizinhos indiretos com arestas desconhecidas
                # Considera o vizinho como um ponto de referência para encontrar vizinhos indiretos
                # que estão na mesma direção do nó atual
                # Exemplo: se o nó atual é (2, 2) e o vizinho é (3, 2),
                # então o vizinho vizinho seria (4, 2)
                diferenca = (vizinho[0] - no[0], vizinho[1] - no[1])
                vizinho_vizinho = (vizinho[0] + diferenca[0], vizinho[1] + diferenca[1])

                if (
                    self.grafo.has_edge(vizinho, vizinho_vizinho)
                    and self.grafo.edges[vizinho, vizinho_vizinho]['conhecimento']
                    == OpçõesConhecimentoAresta.DESCONHECIDA
                ):
                    vizinhos_desconhecidos.add(vizinho_vizinho)

            return len(vizinhos_desconhecidos)

        # A ordenação garante que, em caso de empate, o nó com maior potencial de descoberta de vizinhos desconhecidos seja priorizado na próxima ação.
        # o algoritmo vai escolher o nó mais próximo que estiver mais no final da lista
        # por isso, invertemos a lista para que os nós com mais vizinhos desconhecidos fiquem no final
        nos_com_arestas_desconhecidas.sort(key=contar_vizinhos_desconhecidos, reverse=True)
        return nos_com_arestas_desconhecidas

    def dijkstra_multiplos_destinos(
        self, origem: tuple[int, int], destinos: Iterable[tuple[int, int]]
    ) -> list[tuple[int, int]] | None:
        """Calcula o caminho mais curto do nó de origem até qualquer um dos nós de destino usando Dijkstra."""
        try:
            _, caminho = nx.multi_source_dijkstra(
                self.grafo,
                sources=destinos,
                target=origem,
                weight=lambda u, v, a: a['conhecimento']['peso'],
            )
        except nx.NetworkXNoPath:
            return None

        # Inverte pois a lib retorna do destino para a origem
        return list(reversed(caminho))

    def print(self):
        """Desenha o grafo usando Matplotlib."""
        pos = {(i, j): (j, -i) for i in range(5) for j in range(6)}
        pos[self.AREA_VERDE] = (-1, -2)
        cores_arestas = [conhecimento['cor'] for u, v, conhecimento in self.grafo.edges.data('conhecimento')]
        labels_arestas = {
            (u, v): conhecimento['peso'] for u, v, conhecimento in self.grafo.edges.data('conhecimento')
        }
        nx.draw(
            self.grafo,
            pos=pos,
            with_labels=True,
            node_size=500,
            node_color='lightblue',
            edge_color=cores_arestas,
            width=5,
            font_size=8,
            font_color='black',
        )
        nx.draw_networkx_edge_labels(self.grafo, pos, edge_labels=labels_arestas)
        plt.show()

    def zerar(self):
        """Zera o mapa, removendo todas as informações de conhecimento."""
        for u, v in self.grafo.edges:
            if self.grafo.edges[u, v]['conhecimento'] not in (  # noqa
                OpçõesConhecimentoAresta.INICIO,
                OpçõesConhecimentoAresta.BLOCO_BRANCO,
            ):
                self.grafo.edges[u, v]['conhecimento'] = OpçõesConhecimentoAresta.DESCONHECIDA


if __name__ == '__main__':
    mapa = Mapa()
    # mapa.print()

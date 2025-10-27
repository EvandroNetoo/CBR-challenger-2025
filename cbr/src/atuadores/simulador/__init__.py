import random
from enum import Enum
from pathlib import Path

import matplotlib.image as mpimg
import networkx as nx
from matplotlib import pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from scipy.ndimage import rotate

from ..interface_atuador import InterfaceAtuador


class Simulador(InterfaceAtuador):
    class OpçõesLixos(Enum):
        AZUL = {'cor': 'blue'}
        VERMELHO = {'cor': 'red'}
        VERDE = {'cor': 'green'}
        AMARELO = {'cor': 'yellow'}
        PRETO = {'cor': 'purple'}
        BRANCO = {'cor': 'gray'}
        MARROM = {'cor': 'maroon'}
        VAZIO = {'cor': 'black'}

        def __getitem__(self, key):
            return self.value[key]

    class Direcoes:
        CIMA = 0
        DIREITA = 1
        BAIXO = 2
        ESQUERDA = 3
        DESCONHECIDA = 4

    def __init__(self, qtd_blocos=21, seed=None, altura=5, largura=6):
        self.altura = altura
        self.largura = largura
        self.qtd_blocos = qtd_blocos
        self.grafo: nx.Graph = nx.grid_2d_graph(altura, largura)
        self.imagem_robo = Path(__file__).parent / 'robo.jpg'

        self.pos_anterior = (4, -1)
        self.pos_atual = (4, 0)

        if self._é_par(len(self.grafo.edges)) and not self._é_par(qtd_blocos):
            raise ValueError(
                'Não é possível gerar um mapa espelhado com um número ímpar de blocos com quantidade par de arestas.'
            )

        for aresta in self.grafo.edges:
            self.grafo[aresta[0]][aresta[1]]['lixo'] = self.OpçõesLixos.VAZIO

        if seed is not None:
            random.seed(seed)

        opções = list(self.OpçõesLixos)
        opções.remove(self.OpçõesLixos.VAZIO)

        arestas = list(self.grafo.edges)

        if not self._é_par(qtd_blocos):
            aresta_central = (
                ((altura - 1) // 2, (largura - 1) // 2),
                (altura // 2, largura // 2),
            )
            self.grafo[aresta_central[0]][aresta_central[1]]['lixo'] = random.choice(opções)
            arestas.remove(aresta_central)

        elif self._é_par(qtd_blocos) and not self._é_par(len(self.grafo.edges)):
            aresta_central = (
                ((altura - 1) // 2, (largura - 1) // 2),
                (altura // 2, largura // 2),
            )
            arestas.remove(aresta_central)

        for _ in range(qtd_blocos // 2):
            selecionada = random.choice(arestas)
            u_selecionada, v_selecionada = selecionada
            u_espelho = (
                abs(altura - u_selecionada[0] - 1),
                abs(largura - u_selecionada[1] - 1),
            )
            v_espelho = (
                abs(altura - v_selecionada[0] - 1),
                abs(largura - v_selecionada[1] - 1),
            )

            lixo_selecionado = random.choice(opções)
            self.grafo[u_selecionada][v_selecionada]['lixo'] = lixo_selecionado
            self.grafo[u_espelho][v_espelho]['lixo'] = lixo_selecionado

            arestas.remove(selecionada)
            arestas.remove((v_espelho, u_espelho))

        plt.ion()

    @staticmethod
    def _é_par(numero: int | float) -> bool:
        return numero % 2 == 0

    def print(self):
        plt.clf()

        pos = {(i, j): (j, -i) for i in range(self.altura) for j in range(self.largura)}
        cores_arestas = [self.grafo[u][v]['lixo']['cor'] for u, v in self.grafo.edges]

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
        img = mpimg.imread(self.imagem_robo)
        print(f'Posição atual do robô: {self.pos_atual}, Direção: {self.direcao}')
        img_rotated = rotate(img, angle=self.direcao * -90, reshape=True)
        imagebox = OffsetImage(img_rotated, zoom=0.6)
        ab = AnnotationBbox(imagebox, (self.pos_atual[1], -self.pos_atual[0]), frameon=False)

        plt.gca().add_artist(ab)

        plt.draw()

        plt.show(block=False)

    def ir_para_0_0(self):
        self.pos_anterior = (0, -1)
        self.pos_atual = (0, 0)
        self.print()

    def calcular_direcao(self, pos_anterior: tuple[int, int], pos_atual: tuple[int, int]):
        valor = (pos_atual[0] - pos_anterior[0], pos_atual[1] - pos_anterior[1])
        match valor:
            case (0, 1):
                return self.Direcoes.DIREITA
            case (0, -1):
                return self.Direcoes.ESQUERDA
            case (1, 0):
                return self.Direcoes.BAIXO
            case (-1, 0):
                return self.Direcoes.CIMA
            case _:
                return self.Direcoes.DESCONHECIDA

    @property
    def direcao(self) -> str:
        return self.calcular_direcao(self.pos_anterior, self.pos_atual)

    @property
    def nos_visinhos(self):
        # Arestas vizinhas com base na direcao do robo sendo CIMA
        no_frente = (self.pos_atual[0] - 1, self.pos_atual[1])
        no_direita = (self.pos_atual[0], self.pos_atual[1] + 1)
        no_atras = (self.pos_atual[0] + 1, self.pos_atual[1])
        no_esquerda = (self.pos_atual[0], self.pos_atual[1] - 1)

        qtd_rotacoes = self.direcao

        for _ in range(qtd_rotacoes):
            no_frente, no_direita, no_atras, no_esquerda = no_direita, no_atras, no_esquerda, no_frente

        return no_frente, no_direita, no_atras, no_esquerda

    @property
    def sensores_laterais(self):
        no_frente, no_direita, no_atras, no_esquerda = self.nos_visinhos

        nos_com_sensores = [
            no_esquerda,
            no_frente,
            no_direita,
        ]

        sensores = []
        for no in nos_com_sensores:
            try:
                if self.grafo[self.pos_atual][no]['lixo'] != self.OpçõesLixos.VAZIO:
                    sensores.append(200)
                    continue
                no_vizinho_vizinho = (
                    no[0] + (no[0] - self.pos_atual[0]),
                    no[1] + (no[1] - self.pos_atual[1]),
                )
                if self.grafo[no][no_vizinho_vizinho]['lixo'] != self.OpçõesLixos.VAZIO:
                    sensores.append(500)
                    continue
                sensores.append(1000)
            except KeyError:
                sensores.append(1000)

        return sensores

    def ande_certa_distancia(self, distancia: int, velocidade: int): ...

    def gire_graus(self, graus: int, velocidade: int):
        no_frente, no_direita, no_atras, no_esquerda = self.nos_visinhos
        if graus == 90:
            self.pos_anterior = no_esquerda
        if graus == -90:
            self.pos_anterior = no_direita
        if graus in {-180, 180}:
            self.pos_anterior = no_frente
        self.print()

    def seguir_ate_encruzilhada(self, velocidade: int):
        no_frente, no_direita, no_atras, no_esquerda = self.nos_visinhos
        self.pos_anterior, self.pos_atual = self.pos_atual, no_frente
        self.print()

    def voltar_encruzilhada(self):
        pass

    def pegar_bloco(self) -> bool:
        no_frente, no_direita, no_atras, no_esquerda = self.nos_visinhos
        pegou = False
        if self.grafo.has_edge(self.pos_atual, no_frente):
            self.grafo[self.pos_atual][no_frente]['lixo'] = self.OpçõesLixos.VAZIO
            pegou = True

        self.print()
        return pegou

    def seguir_linha(self):
        pass

    def pare(self):
        pass

    def escreve_posicao(self, posicao: tuple[int, int]):
        pass

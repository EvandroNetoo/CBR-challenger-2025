"""Implementa a classe base para todas as estratégias de navegação do robô.

Este módulo define a estrutura fundamental para as estratégias de navegação,
provendo métodos para manipulação e atualização do mapa, classificação de
distâncias, cálculo de direções, e determinação dos próximos movimentos.

A classe EstrategiaBase serve como uma classe abstrata que outras estratégias
devem herdar e implementar, garantindo um comportamento consistente em todas
as estratégias de navegação do robô.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict

import settings
from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha
from src.mapa import Mapa, OpçõesConhecimentoAresta
from src.servico_web import ServicoWeb


class EstrategiaBase(ABC):
    """Classe abstrata base para implementação de estratégias de navegação do robô.

    Esta classe define a estrutura comum para todas as estratégias de navegação,
    fornecendo métodos para interação com o mapa, cálculo de direções, classificação
    de distâncias, e determinação do próximo movimento do robô.

    Todas as estratégias específicas devem herdar desta classe e implementar o método abstrato 'iniciar'.
    """

    class Distancia:
        """Constantes para classificação de distâncias detectadas pelos sensores."""

        NAO_ENCONTRADO = 0
        PERTO = 1
        MEDIO = 2

    class Direcoes:
        """Constantes para as possíveis direções do robô no mapa."""

        CIMA = 0
        DIREITA = 1
        BAIXO = 2
        ESQUERDA = 3
        DESCONHECIDA = 4

    def __init__(self, robo: RoboSeguidorDeLinha, mapa: Mapa):
        self.robo = robo
        self.mapa = mapa

        self.posicoes_lixeiras_depositadas = defaultdict(int)

        print(f'Posições lixeira: {self.posicoes_lixeiras}')
        print(f'Cubos pegos: {self.posicoes_lixeiras_depositadas}')

        self.pos_anterior = (0, -1)  # Posição inicial anterior (fora do mapa)
        self.pos_atual = (0, 0)  # Posição inicial atual (origem do mapa)

        # Inicia o serviço web para visualização em modo debug
        if settings.DEBUG:
            ServicoWeb.estrategia = self
            ServicoWeb.iniciar()

    # ==========================================================================
    # MÉTODOS DE PROCESSAMENTO DE SENSORES E DISTÂNCIAS
    # ==========================================================================

    def classificar_distancia(self, distancia_mm: int) -> str:
        """Classifica a distância em categorias: PERTO, MEDIO ou NAO_ENCONTRADO"""
        if distancia_mm <= 0:
            return self.Distancia.NAO_ENCONTRADO
        if distancia_mm <= 250:
            return self.Distancia.PERTO
        elif distancia_mm <= 700:
            return self.Distancia.MEDIO
        else:
            return self.Distancia.NAO_ENCONTRADO

    def calcular_direcao(self, pos_anterior: tuple[int, int], pos_atual: tuple[int, int]) -> str:
        """Calcula a direção do robô com base na posição anterior e atual"""
        valor = (pos_atual[0] - pos_anterior[0], pos_atual[1] - pos_anterior[1])
        match valor:
            case (0, 1):
                return self.Direcoes.DIREITA
            case (0, -1):
                return self.Direcoes.ESQUERDA
            case (1, 0):
                return self.Direcoes.BAIXO
            case (-1, 0):
                return self.Direcoes.CIMA  # nao mudarrrrrrrrrr
            case _:
                return self.Direcoes.DESCONHECIDA

    def atualizacao_dinamica_mapa(self):
        """Atualiza o mapa com as distâncias medidas pelos sensores laterais do robô."""
        QTD_LEITURAS = 3

        distancias = zip(*[self.robo.sensores_laterais for _ in range(QTD_LEITURAS)], strict=False)
        distancia_max_esquerda, distancia_max_frontal, distancia_max_direita = map(max, distancias)
        print(
            f'Distâncias medidas - Esquerda: {distancia_max_esquerda} mm, Frontal: {distancia_max_frontal} mm, Direita: {distancia_max_direita} mm'
        )
        print(f'Posição atual: {self.pos_atual}, Nós vizinhos: {self.nos_vizinhos}')

        classificacao_esquerda = self.classificar_distancia(distancia_max_esquerda)
        classificacao_frontal = self.classificar_distancia(distancia_max_frontal)
        classificacao_direita = self.classificar_distancia(distancia_max_direita)

        no_frente, no_direita, _, no_esquerda = self.nos_vizinhos

        self.atualizacao_dinamica_aresta(no_frente, classificacao_frontal)
        self.atualizacao_dinamica_aresta(no_direita, classificacao_direita)
        self.atualizacao_dinamica_aresta(no_esquerda, classificacao_esquerda)

    def atualizacao_dinamica_aresta(
        self, no_vizinho: tuple[int, int], classificacao: int, zerar_branco: bool = False
    ):
        """Atualiza o conhecimento do mapa com base na classificação da distância para o nó vizinho."""

        def atualizar_conhecimento(no1, no2, novo_valor):
            """Tenta atualizar o conhecimento da aresta, respeitando a regra do BLOCO_BRANCO."""
            try:
                if (
                    not zerar_branco
                    and self.mapa.grafo[no1][no2]['conhecimento'] == OpçõesConhecimentoAresta.BLOCO_BRANCO
                ):
                    return
                self.mapa.grafo[no1][no2]['conhecimento'] = novo_valor
            except KeyError:
                pass  # Nó ou aresta inexistente

        # Calcula o "vizinho do vizinho" (linha reta)
        no_vizinho_vizinho = (
            no_vizinho[0] + (no_vizinho[0] - self.pos_atual[0]),
            no_vizinho[1] + (no_vizinho[1] - self.pos_atual[1]),
        )

        # Regras de atualização por classificação
        match classificacao:
            case self.Distancia.PERTO:
                atualizar_conhecimento(self.pos_atual, no_vizinho, OpçõesConhecimentoAresta.BLOCO)

            case self.Distancia.MEDIO:
                atualizar_conhecimento(self.pos_atual, no_vizinho, OpçõesConhecimentoAresta.VAZIO)
                atualizar_conhecimento(no_vizinho, no_vizinho_vizinho, OpçõesConhecimentoAresta.BLOCO)

            case self.Distancia.NAO_ENCONTRADO:
                atualizar_conhecimento(self.pos_atual, no_vizinho, OpçõesConhecimentoAresta.VAZIO)
                atualizar_conhecimento(no_vizinho, no_vizinho_vizinho, OpçõesConhecimentoAresta.VAZIO)

    # ==========================================================================
    # MÉTODOS DE NAVEGAÇÃO E PLANEJAMENTO DE CAMINHOS
    # ==========================================================================

    def proximo_no(self) -> tuple[int, int] | None:
        """Determina o próximo nó para o robô se mover, priorizando blocos conhecidos ou nós desconhecidos."""
        return self.no_para_bloco_mais_proximo() or self.no_para_no_desconhecido_mais_proximo()

    def no_para_bloco_mais_proximo(self) -> tuple[int, int] | None:
        """Encontra o próximo nó que leva ao bloco mais próximo."""
        nos_com_bloco = self.mapa.nos_com_bloco()
        if not nos_com_bloco:
            return None

        caminho = self.mapa.dijkstra_multiplos_destinos(self.pos_atual, nos_com_bloco)
        print('caminho proximo_no_para_bloco_mais_proximo: ', caminho)

        return None if caminho is None else caminho[1]

    def no_para_no_desconhecido_mais_proximo(self) -> tuple[int, int] | None:
        """Encontra o próximo nó que leva ao nó desconhecido mais próximo."""
        nos_com_arestas_desconhecidas = self.mapa.nos_com_arestas_desconhecidas()
        if not nos_com_arestas_desconhecidas:
            return None

        caminho = self.mapa.dijkstra_multiplos_destinos(self.pos_atual, nos_com_arestas_desconhecidas)
        print('caminho proximo_no_para_no_desconhecido_mais_proximo: ', caminho)
        return None if caminho is None else caminho[1]

    def graus_para_no_vizinho(self, no_vizinho: tuple[int, int]) -> int:
        """Calcula os graus que o robô deve girar para se orientar na direção do próximo nó."""
        direcao_no_vizinho = self.calcular_direcao(self.pos_atual, no_vizinho)
        quant_giro = (direcao_no_vizinho - self.direcao + 2) % 4 - 2
        graus = quant_giro * 90
        return graus

    # ==========================================================================
    # PROPRIEDADES E MÉTODOS AUXILIARES
    # ==========================================================================

    @property
    def nos_vizinhos(self) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]:
        """Retorna os nós vizinhos com base na direção e posição atual do robô"""
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
    def direcao(self) -> str:
        """Retorna a direção atual do robô com base na posição anterior e atual"""
        return self.calcular_direcao(self.pos_anterior, self.pos_atual)

    @abstractmethod
    def iniciar(self):
        pass

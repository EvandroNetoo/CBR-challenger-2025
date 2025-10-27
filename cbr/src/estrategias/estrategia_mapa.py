"""Implementa a estratégia de navegação do robô para o mapa principal.

Este módulo define a estratégia para exploração do mapa principal, incluindo:
- Navegação entre as encruzilhadas do mapa
- Detecção e coleta de blocos
- Retorno para a área verde quando um bloco é coletado
- Exploração otimizada do mapa usando informações dos sensores

A estratégia coordena o comportamento do robô para mapear eficientemente o ambiente
e coletar blocos para serem depositados na área verde.
"""

from time import sleep

from settings import VELOCIDADE_BAIXA, VELOCIDADE_MAXIMA, VELOCIDADE_PADRAO
from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha
from src.definicao_cores import Cores, DefinicaoCoresLinha
from src.mapa import Mapa, OpçõesConhecimentoAresta

from .estrategia_base import EstrategiaBase


class EstrategiaMapa(EstrategiaBase):
    """Implementa a estratégia de navegação e exploração do mapa principal.

    Gerencia a navegação no mapa, incluindo detecção e coleta de blocos,
    atualização do mapa baseada em sensores, e retorno à área verde.
    """

    def __init__(self, robo: RoboSeguidorDeLinha, mapa: Mapa):
        super().__init__(robo, mapa)

    def iniciar(self) -> tuple[Cores, int]:
        """Inicia a execução da estratégia para o mapa principal.

        Este método implementa a lógica principal de exploração do mapa e coleta de blocos.
        O robô navega pelo mapa, atualiza seu conhecimento do ambiente e tenta encontrar
        blocos para coletar. Quando um bloco válido é coletado, o robô retorna à área verde.
        """
        self.robo.ande_certa_distancia(40, velocidade=VELOCIDADE_BAIXA)

        while True:
            self.atualizacao_dinamica_mapa()
            self.robo.tela_teclado.escreve_posicao(self.pos_atual)

            # Verifica se há blocos próximos e tenta pegá-los
            if self.girar_para_bloco_vizinho_se_houver(velocidade=VELOCIDADE_BAIXA):
                cor_pega = self.pegar_bloco()

                if cor_pega != Cores.BRANCO and cor_pega in self.posicoes_lixeiras and cor_pega is not None:
                    self.retornar_para_area_verde()
                    return cor_pega, self.pos_atual[0]

                continue

            proximo_no = self.proximo_no()

            if proximo_no == self.mapa.AREA_VERDE:
                self.area_verde_e_retorno()
                continue

            if not proximo_no:
                print('Nenhum próximo nó encontrado, exploração completa.')
                self.mapa.zerar()

                # Usado para não bugar a função para o próximo nó
                # Ele tenta ir para o nó em que ele já está
                if self.mapa.grafo.has_edge(self.pos_atual, self.nos_vizinhos[2]):
                    self.mapa.grafo[self.pos_atual][self.nos_vizinhos[2]]['conhecimento'] = (
                        OpçõesConhecimentoAresta.VAZIO
                    )
                continue

            self.rotacionar_para_no(proximo_no)
            self.seguir_ate_encruzilhada(tempo_minimo=0.2)

    def area_verde_e_retorno(self):
        """
        Navega até a área verde e retorna para a próxima linha.
        Esta função é chamada quando o há um bloqueio no caminho da cidade
        """
        self.robo.voltar_encruzilhada(velocidade=VELOCIDADE_BAIXA)
        self.rotacionar_para_no((self.pos_atual[0], -1), distancia=20)
        self.robo.seguir_linha_ate_cor(
            DefinicaoCoresLinha.e_verde,
            velocidade=VELOCIDADE_BAIXA,
            modo=self.robo.ModoMotor.VELOCIDADE,
        )
        self.robo.ande_certa_distancia(90, velocidade=VELOCIDADE_PADRAO)
        sleep(0.1)
        self.robo.gire_graus_giroscopio(-90, velocidade=VELOCIDADE_PADRAO)
        sleep(0.1)
        self.robo.ande_certa_distancia(280, velocidade=VELOCIDADE_PADRAO)
        sleep(0.1)
        self.robo.gire_graus_giroscopio(-90, velocidade=VELOCIDADE_PADRAO)

        self.robo.ande_ate_deixar_de_ver_cor(DefinicaoCoresLinha.e_verde, velocidade=VELOCIDADE_PADRAO)
        sleep(0.1)
        self.robo.ande_certa_distancia(20, velocidade=VELOCIDADE_BAIXA)
        self.robo.encontrar_linha_preta(velocidade=VELOCIDADE_PADRAO)

        self.robo.seguir_ate_encruzilhada(
            velocidade=VELOCIDADE_BAIXA, modo=self.robo.ModoMotor.VELOCIDADE, tempo_minimo=0.2
        )

        nova_aresta = self.pos_atual[0] + 1
        self.pos_anterior = (nova_aresta, -1)
        self.pos_atual = (nova_aresta, 0)

    def pegar_bloco(self) -> Cores:
        """Pega um bloco à frente do robô.
        Ajusta a distância conforme necessário e atualiza o mapa.
        """
        cor_pega = False
        distancia = 45  # Distância inicial para tentar pegar o bloco

        while not cor_pega:
            cor_pega = self.robo.pegar_bloco(distancia=distancia, posicoes_lixeiras=self.posicoes_lixeiras)
            print(f'Cor pega: {cor_pega}')

            self.robo.voltar_encruzilhada()

            if (cor_pega == Cores.BRANCO or cor_pega not in self.posicoes_lixeiras) and cor_pega is not None:
                no_frente, _, _, _ = self.nos_vizinhos
                self.mapa.grafo[self.pos_atual][no_frente]['conhecimento'] = (
                    OpçõesConhecimentoAresta.BLOCO_BRANCO
                )

                return Cores.BRANCO

            self.robo.ande_certa_distancia(20, velocidade=VELOCIDADE_PADRAO)
            self.atualizacao_dinamica_mapa()
            no_frente, _, _, _ = self.nos_vizinhos

            if self.mapa.grafo[self.pos_atual][no_frente]['conhecimento'] == OpçõesConhecimentoAresta.BLOCO:
                cor_pega = False
                distancia += 5
            else:
                print('Bloco não encontrado mais, parando tentativa de pegar bloco.')
                return cor_pega

        return cor_pega

    def rotacionar_para_no(
        self,
        proximo_no: tuple[int, int],
        *,
        andar_para_frente: bool = True,
        distancia=0,
        velocidade=VELOCIDADE_PADRAO,
        girar_com_giroscopio=False,
    ):
        """Rotaciona o robô para ficar orientado na direção do próximo nó.

        Args:
            proximo_no: Coordenadas (linha, coluna) do próximo nó
            andar_para_frente: Se True, anda um pouco para frente antes de girar
            distancia: Distância a andar para frente em mm
            velocidade: Velocidade do movimento
            girar_com_giroscopio: Se True, usa o giroscópio para girar com mais precisão
        """
        graus_giro = self.graus_para_no_vizinho(proximo_no)

        if andar_para_frente and graus_giro != 0:
            self.robo.ande_certa_distancia(distancia, velocidade=velocidade)

        if girar_com_giroscopio:
            self.robo.gire_graus_giroscopio(graus_giro, velocidade=VELOCIDADE_PADRAO)
        else:
            self.robo.gire_graus(graus_giro, velocidade=VELOCIDADE_MAXIMA)

        # atualiza a posição anterior do robô para atualizar a direção
        diferenca = (self.pos_atual[0] - proximo_no[0], self.pos_atual[1] - proximo_no[1])
        self.pos_anterior = (self.pos_atual[0] + diferenca[0], self.pos_atual[1] + diferenca[1])

    def seguir_ate_encruzilhada(self, tempo_minimo: int = 0, com_cubo: bool = False) -> bool:
        """Faz o robô seguir até a próxima encruzilhada e atualiza a posição.

        O robô segue a linha até encontrar uma encruzilhada, e então atualiza
        sua posição anterior e atual no mapa.

        Args:
            tempo_minimo: Tempo mínimo em segundos para seguir a linha
        """
        achou_encruzilhada = self.robo.seguir_ate_encruzilhada(tempo_minimo=tempo_minimo, com_cubo=com_cubo)

        # Atualiza a posição anterior e atual do robô
        no_frente, no_direita, no_atras, no_esquerda = self.nos_vizinhos
        self.pos_anterior, self.pos_atual = self.pos_atual, no_frente

        return achou_encruzilhada

    def girar_para_bloco_vizinho_se_houver(self, velocidade: int = VELOCIDADE_PADRAO) -> bool:
        """Detecta e gira para cubos nas proximidades, retorna True se um cubo foi coletado"""
        no_frente, no_direita, no_atras, no_esquerda = self.nos_vizinhos
        nos_possiveis = [
            no_frente,
            no_direita,
            no_esquerda,
            no_atras,
        ]

        for no in nos_possiveis:
            try:
                if self.mapa.grafo[self.pos_atual][no]['conhecimento'] == OpçõesConhecimentoAresta.BLOCO:
                    self.robo.voltar_encruzilhada(velocidade=velocidade)
                    self.rotacionar_para_no(
                        no, girar_com_giroscopio=True, velocidade=velocidade, distancia=25
                    )
                    self.robo.pare()
                    return True
            except KeyError:
                continue

        return False

    def retornar_para_area_verde(self):
        # Comentário sobre código removido
        # self.robo.voltar_encruzilhada(velocidade=VELOCIDADE_PADRAO) # TIREI - PRCISA VER SE DA PROBLEMA - BANANA

        # O len é 2 quando chegar na saída pois a área verde é (0, -1)
        # então, quando chegar na saída, o caminho terá 2 nós:
        # 1. o nó atual (0, 0)
        # 2. o nó da área verde (0, -1)
        # Se o caminho tiver mais de 2 nós, significa que ainda não chegou na área verde
        # e o robô deve continuar seguindo o caminho até chegar lá.
        # Se o caminho tiver exatamente 2 nós, significa que já chegou na área verde
        LEN_QUANDO_CHEGAR = 2

        # Navega pelo caminho mais curto até chegar próximo à área verde
        while len(caminho := self.mapa.caminho_saida(self.pos_atual)) > LEN_QUANDO_CHEGAR:
            proximo_no = caminho[1]
            self.rotacionar_para_no(proximo_no)
            if not self.seguir_ate_encruzilhada(tempo_minimo=0.2, com_cubo=True):
                print('Erro: não encontrou encruzilhada ao retornar para área verde.')
                return
            self.atualizacao_dinamica_mapa()
            self.robo.tela_teclado.escreve_posicao(self.pos_atual)
            # self.robo.ande_certa_distancia(20, velocidade=VELOCIDADE_PADRAO)

        # Rotaciona para ficar de frente para a entrada da área verde
        self.rotacionar_para_no((self.pos_atual[0], -1), andar_para_frente=True)

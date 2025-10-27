"""
Módulo responsável pelo controle do robô.
Implementa funções para movimentação básica, giros, alinhamentos e interação com sensores.
Inclui métodos para navegação autônoma e manipulação de blocos.
"""

from typing import Callable

from libs.giroscopio import Giroscopio
from libs.motores import Motores
from libs.portas import Portas
from libs.sensorCorReflexao import CorReflexao
from libs.tcs34725 import TCS34725
from libs.vl53 import VL53L0X
from settings import (
    CHAVE_SENSOR_COR_ESQUERDO,
    PORTA_SENSOR_COR_ESQUERDO,
    PORTA_SENSOR_COR_LINHA,
    VALOR_ENCRUZILHADA,
    VELOCIDADE_PADRAO,
)
from src.atuadores.robo.garra import Garra
from src.atuadores.robo.tela_teclado import TelaTeclado
from src.definicao_cores import ValorAlinhamentoSeguidor


class Robo:
    """
    Classe que implementa o controle do robô.

    O robô possui:
    - Dois motores para controle de movimentação (esquerdo e direito)
    - Uma garra para manipulação de objetos
    - Sensores de distância nas laterais e frente
    - Sensores de cor para detecção de linhas e objetos
    - Giroscópio para controle de orientação
    """

    # Constantes de conversão
    DISTANCIA_PARA_GRAUS = 800 / 300 * 1.6  # Fator de conversão de distância para graus do motor
    GRAUS_PARA_GRAUS_ANGULAR_ESQUERDA = 6.67
    GRAUS_PARA_GRAUS_ANGULAR_DIREITA = 7.15

    # Índices dos motores
    MOTOR_DIREITO = 1
    MOTOR_ESQUERDO = 2

    # Índices dos sensores
    SENSOR_COR_ESQUERDO = 1
    SENSOR_COR_CENTRO = 2
    SENSOR_COR_DIREITO = 3

    class ModoMotor:
        VELOCIDADE = 0
        POTENCIA = 1

    def __init__(self):
        """
        Inicializa o robô configurando os motores, a garra e os sensores.
        Define a direção dos motores e o modo de freio.
        """
        super().__init__()

        # Inicialização dos motores
        self.motores = Motores(True)
        self.motores.direcao_motor(self.MOTOR_ESQUERDO, self.motores.NORMAL)
        self.motores.direcao_motor(self.MOTOR_DIREITO, self.motores.INVERTIDO)
        self.motores.set_modo_freio(self.motores.HOLD)

        # Inicialização da garra
        self.garra = Garra()

        # Inicialização dos sensores de distância
        self.sensor_distancia_direito = VL53L0X(Portas.I2C4)
        self.sensor_distancia_esquerdo = VL53L0X(Portas.I2C2)
        self.sensor_distancia_frontal = VL53L0X(Portas.I2C8)

        # Inicialização do giroscópio
        self.giroscopio = Giroscopio(Portas.SERIAL1)

        # Inicialização dos sensores de cor
        self.sensor_de_linha = CorReflexao(PORTA_SENSOR_COR_LINHA)
        self.sensor_cor_esquerdo = TCS34725(
            PORTA_SENSOR_COR_ESQUERDO,
            chave_sensor=CHAVE_SENSOR_COR_ESQUERDO,
        )

        # inicializa tele e teclado
        self.tela_teclado = TelaTeclado()

    # -----------------------------------------------------------
    # Movimentação básica
    # -----------------------------------------------------------

    def ande_reto(
        self, velocidade: int = VELOCIDADE_PADRAO, modo: int = ModoMotor.VELOCIDADE, delta: int = 0
    ):
        # direita, esquerda
        if modo == self.ModoMotor.VELOCIDADE:
            if velocidade > 0:
                self.motores.velocidade_motores(velocidade * 0.92 + delta, velocidade - delta)
            else:
                self.motores.velocidade_motores(velocidade + delta, velocidade * 0.92 - delta)
        else:
            self.motores.potencia_motores(velocidade, velocidade)

    def pare(self):
        self.motores.para_motores()

    def pare_suave(self):
        self.motores.velocidade_motores(3, 3)

    # -----------------------------------------------------------
    # Giros
    # -----------------------------------------------------------

    def gire_graus(self, graus: int, *, velocidade: int = VELOCIDADE_PADRAO, pare_apos_girar: bool = True):
        if not graus:
            return

        # Converte graus para valores do encoder
        graus_para_graus_angular = (
            self.GRAUS_PARA_GRAUS_ANGULAR_ESQUERDA if graus < 0 else self.GRAUS_PARA_GRAUS_ANGULAR_DIREITA
        )
        graus = int(graus * graus_para_graus_angular)
        direcao = graus // abs(graus)

        self.motores.move_motores(velocidade * (-direcao), graus, velocidade * direcao, graus)

        while (
            self.motores.estado_motor(self.MOTOR_DIREITO),
            self.motores.estado_motor(self.MOTOR_ESQUERDO),
        ) != (self.motores.PARADO, self.motores.PARADO):
            self.motores.estado()

        if pare_apos_girar:
            self.pare()

    def gire_graus_giroscopio(self, graus: int, velocidade: int = VELOCIDADE_PADRAO):
        if not graus:
            return

        direcao = 1 if graus > 0 else -1
        angulo_inicial = self.giroscopio.le_angulo_z()
        angulo_atual = angulo_inicial

        while abs(angulo_atual - angulo_inicial) < abs(graus):
            angulo_atual = self.giroscopio.le_angulo_z()

            # Reduz velocidade ao se aproximar do alvo para maior precisão
            if abs(angulo_atual - angulo_inicial) > abs(graus * 0.7):
                self.motores.velocidade_motores(-direcao * velocidade // 3, direcao * velocidade // 3)
            else:
                self.motores.velocidade_motores(-direcao * velocidade, direcao * velocidade)

        self.pare()

    def calcular_angulo_para_rotacao(self, angulo_alvo: int) -> int:
        """
        Calcula a diferença angular entre o ângulo atual e o alvo.
        Encontra o caminho mais curto (direita ou esquerda) para atingir o alvo.
        """
        angulo_atual = (self.giroscopio.le_angulo_z() + 360) % 360
        angulo_alvo %= 360

        diferenca = angulo_alvo - angulo_atual

        # Encontra o caminho mais curto
        if diferenca > 180:
            diferenca -= 360
        elif diferenca < -180:
            diferenca += 360

        return diferenca

    def girar_para_angulo(self, angulo_alvo: int, velocidade: int = VELOCIDADE_PADRAO):
        diferenca = self.calcular_angulo_para_rotacao(angulo_alvo)
        if abs(diferenca) < 2:
            return

        direcao = 1 if diferenca > 0 else -1

        while abs(self.calcular_angulo_para_rotacao(angulo_alvo)) > 15:
            self.motores.velocidade_motores(-direcao * velocidade, direcao * velocidade)

        while abs(self.calcular_angulo_para_rotacao(angulo_alvo)) > 2:
            self.motores.velocidade_motores(-direcao * velocidade // 3, direcao * velocidade // 3)

        self.pare()

    # -----------------------------------------------------------
    # Movimento com sensores
    # -----------------------------------------------------------

    def ande_certa_distancia(self, distancia: int, *, velocidade: int = VELOCIDADE_PADRAO):
        # Converte distância em milímetros para graus do motor
        self.pare()
        graus = distancia * self.DISTANCIA_PARA_GRAUS
        angulo_motor_inicial = self.motores.angulo_motor(self.MOTOR_DIREITO)
        angulo_motor = angulo_motor_inicial

        valor_giroscopio_inicial = self.giroscopio.le_angulo_z()

        while angulo_motor_inicial - graus < angulo_motor < angulo_motor_inicial + graus:
            angulo_motor = self.motores.angulo_motor(self.MOTOR_DIREITO)
            valor_giroscopio_atual = self.giroscopio.le_angulo_z()
            self.ande_reto(velocidade=velocidade, delta=(valor_giroscopio_atual - valor_giroscopio_inicial))

        self.pare()

    def encontrar_linha_preta(self, *, velocidade: int = VELOCIDADE_PADRAO, valor: int = 70):
        """
        Gira o robô em zigue-zague até encontrar uma linha preta.
        """
        graus_acumulado = 15  # Ângulo inicial de busca
        graus = graus_acumulado  # Incremento de ângulo a cada ciclo

        while True:
            graus_para_graus_angular = (
                self.GRAUS_PARA_GRAUS_ANGULAR_ESQUERDA
                if graus_acumulado < 0
                else self.GRAUS_PARA_GRAUS_ANGULAR_DIREITA
            )
            graus_angular = int(graus_acumulado * graus_para_graus_angular)
            direcao = graus_angular // abs(graus_angular)

            self.motores.move_motores(
                velocidade * (-direcao), graus_angular, velocidade * direcao, graus_angular
            )

            while (
                self.motores.estado_motor(self.MOTOR_DIREITO),
                self.motores.estado_motor(self.MOTOR_ESQUERDO),
            ) != (self.motores.PARADO, self.motores.PARADO):
                self.motores.estado()

                direito_extremo, direita, esquerda, esquerdo_extremo = self.sensor_de_linha.le_reflexao()
                media = (direita + esquerda + direito_extremo + esquerdo_extremo) // 4

                if media < valor:
                    return

            # Aumenta o ângulo e inverte a direção para o próximo ciclo
            graus_acumulado = (abs(graus_acumulado) + graus) * -direcao

    def voltar_encruzilhada(
        self, *, velocidade: int = VELOCIDADE_PADRAO, valor_encruzilhada: int = VALOR_ENCRUZILHADA
    ):
        while True:
            extrema_direita, direita, esquerda, extrema_esquerda = self.sensor_de_linha.le_reflexao()
            media = (extrema_esquerda + esquerda + direita + extrema_direita) / 4

            if media < valor_encruzilhada:
                break

            self.motores.velocidade_motores(-velocidade, -velocidade)

        self.pare()

    # -----------------------------------------------------------
    # Funções de cor e alinhamento
    # -----------------------------------------------------------

    def ande_ate_cor(
        self, funcao_cor: Callable[[tuple[int, int, int]], bool], *, velocidade: int = VELOCIDADE_PADRAO
    ):
        valor_giroscopio_inicial = self.giroscopio.le_angulo_z()
        while True:
            valor1 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_ESQUERDO)
            valor2 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_CENTRO)
            valor3 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_DIREITO)

            if funcao_cor(valor1) or funcao_cor(valor2) or funcao_cor(valor3):
                break

            valor_giroscopio_atual = self.giroscopio.le_angulo_z()
            self.ande_reto(
                velocidade,
                modo=self.ModoMotor.VELOCIDADE,
                delta=(valor_giroscopio_atual - valor_giroscopio_inicial),
            )

        self.pare()

    def ande_ate_deixar_de_ver_cor(
        self,
        funcao_cor: Callable[[tuple[int, int, int]], bool],
        *,
        velocidade: int = VELOCIDADE_PADRAO,
    ):
        valor_giroscopio_inicial = self.giroscopio.le_angulo_z()
        while True:
            valor1 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_ESQUERDO)
            valor2 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_CENTRO)
            valor3 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_DIREITO)

            if not (funcao_cor(valor1) or funcao_cor(valor2) or funcao_cor(valor3)):
                break

            valor_giroscopio_atual = self.giroscopio.le_angulo_z()
            self.ande_reto(
                velocidade,
                modo=self.ModoMotor.VELOCIDADE,
                delta=(valor_giroscopio_atual - valor_giroscopio_inicial),
            )

        self.pare()

    def alinhe_entre_linhas(
        self,
        dados_alinhamento: tuple[int, int] = ValorAlinhamentoSeguidor.VERDE_AMARELO,
        tolerancia: int = 5,
        *,
        velocidade: int = VELOCIDADE_PADRAO,
    ) -> bool:
        """
        Alinha o robô entre duas linhas coloridas ajustando cada lado independentemente.
        """
        lado_esquerdo_alinhado = False
        lado_direito_alinhado = False

        # Extrai os parâmetros de alinhamento
        indice_rgb, valor_alinhamento = dados_alinhamento

        # Lê valores iniciais dos sensores
        direito = self.sensor_de_linha.le_rgbc(self.SENSOR_COR_DIREITO)[indice_rgb]
        esquerdo = self.sensor_de_linha.le_rgbc(self.SENSOR_COR_ESQUERDO)[indice_rgb]

        while not (lado_esquerdo_alinhado and lado_direito_alinhado):
            # Alinha o sensor esquerdo primeiro
            while not lado_esquerdo_alinhado:
                if esquerdo < valor_alinhamento:
                    self.motores.velocidade_motores(0, velocidade)
                if esquerdo > valor_alinhamento:
                    self.motores.velocidade_motores(0, -velocidade)

                esquerdo = self.sensor_de_linha.le_rgbc(self.SENSOR_COR_ESQUERDO)[indice_rgb]
                lado_esquerdo_alinhado = (
                    valor_alinhamento - tolerancia < esquerdo < valor_alinhamento + tolerancia
                )

            # Em seguida, alinha o sensor direito
            while not lado_direito_alinhado:
                if direito < valor_alinhamento:
                    self.motores.velocidade_motores(velocidade, 0)
                if direito > valor_alinhamento:
                    self.motores.velocidade_motores(-velocidade, 0)

                direito = self.sensor_de_linha.le_rgbc(self.SENSOR_COR_DIREITO)[indice_rgb]
                lado_direito_alinhado = (
                    valor_alinhamento - tolerancia < direito < valor_alinhamento + tolerancia
                )

            # Verifica novamente se ambos os lados permanecem alinhados
            esquerdo = self.sensor_de_linha.le_rgbc(self.SENSOR_COR_ESQUERDO)[indice_rgb]
            lado_esquerdo_alinhado = (
                valor_alinhamento - tolerancia < esquerdo < valor_alinhamento + tolerancia
            )

            direito = self.sensor_de_linha.le_rgbc(self.SENSOR_COR_DIREITO)[indice_rgb]
            lado_direito_alinhado = valor_alinhamento - tolerancia < direito < valor_alinhamento + tolerancia

        self.pare()

    # -----------------------------------------------------------
    # Manipulação de blocos
    # -----------------------------------------------------------

    # método sobrescrito na classe RoboSeguidorDeLinha
    def pegar_bloco(self, posicoes_lixeiras: list[tuple[int, int]], distancia: int = 40) -> bool:
        self.voltar_encruzilhada()
        self.ande_certa_distancia(30)
        self.garra.pegar_bloco()
        return True

    # -----------------------------------------------------------
    # Leitura de sensores
    # -----------------------------------------------------------

    @property
    def sensores_laterais(self) -> tuple[int, int, int]:
        """
        Lê os valores dos sensores de distância laterais e frontal.

        Returns:
            tuple[int, int, int]: Distâncias em milímetros na ordem (esquerdo, frontal, direito)
        """
        # Solicita leitura de todos os sensores
        self.sensor_distancia_esquerdo.solicita_leitura()
        self.sensor_distancia_frontal.solicita_leitura()
        self.sensor_distancia_direito.solicita_leitura()

        # Obtém as distâncias em milímetros
        distancia_esquerdo = self.sensor_distancia_esquerdo.read_range_continuous_millimeters()
        distancia_frontal = self.sensor_distancia_frontal.read_range_continuous_millimeters()
        distancia_direito = self.sensor_distancia_direito.read_range_continuous_millimeters()

        return distancia_esquerdo, distancia_frontal, distancia_direito

"""
Módulo responsável pelo controle da garra do robô.

Fornece a classe `Garra`, que gerencia os servos da garra, alavanca e porta,
além de métodos para ações como pegar, depositar e identificar blocos.
"""

from time import sleep

from libs.motores import Motores
from libs.portas import Portas
from libs.tcs34725 import TCS34725
from src.definicao_cores import Cores, DefinicaoCoresBloco


class Garra:
    """
    Classe que implementa o controle da garra do robô.

    A garra possui 3 servos motores:
    - Servo da garra: controla a abertura e fechamento da garra
    - Servo da alavanca: controla a altura da garra
    - Servo da porta: controla a abertura e fechamento da porta para depósito

    Também possui um sensor de cor para identificar a cor dos blocos.
    """

    # Constantes de configuração
    INDICE_SERVO_GARRA = 1
    INDICE_SERVO_ALAVANCA = 4
    INDICE_SERVO_PORTA = 3
    PORTA_SENSOR_COR = Portas.I2C1
    CHAVE_SENSOR_COR = 'sensor_cor_garra'

    # Posições dos servos (em graus)
    POSICAO_ALAVANCA_SUBIDA = 40
    POSICAO_ALAVANCA_DESCIDA_TOTAL = 170
    POSICAO_ALAVANCA_DESCIDA_PEGAR = 145
    POSICAO_ALAVANCA_DESCIDA_DEPOSITAR = 115  # 115 padrao

    POSICAO_GARRA_FECHADA = 70
    POSICAO_GARRA_ABERTA = 180
    POSICAO_GARRA_PARCIAL = 180

    POSICAO_PORTA_ABERTA = 83
    POSICAO_PORTA_FECHADA = 180

    def __init__(self):
        """
        Inicializa a garra, configurando os motores e o sensor de cor.
        Define a posição inicial da garra (subida, aberta e com porta fechada).
        """
        self.motores = Motores(True)
        self.sensor_cor = TCS34725(self.PORTA_SENSOR_COR, chave_sensor=self.CHAVE_SENSOR_COR)

        # Configuração inicial da garra
        self.subir()
        self.abrir()
        self.fechar_porta()
        sleep(1)

    # =========== Controle da alavanca ===========
    def subir(self, *, tempo: float = 0):
        self.motores.move_servo(self.INDICE_SERVO_ALAVANCA, self.POSICAO_ALAVANCA_SUBIDA, tempo)

    def abaixar_total(self, *, tempo: float = 0):
        self.motores.move_servo(self.INDICE_SERVO_ALAVANCA, self.POSICAO_ALAVANCA_DESCIDA_TOTAL, tempo)

    def abaixar_parcial_pegar(self, *, tempo: float = 0):
        self.motores.move_servo(self.INDICE_SERVO_ALAVANCA, self.POSICAO_ALAVANCA_DESCIDA_PEGAR, tempo)

    def abaixar_parcial_depositar(self, *, tempo: float = 0):
        self.motores.move_servo(self.INDICE_SERVO_ALAVANCA, self.POSICAO_ALAVANCA_DESCIDA_DEPOSITAR, tempo)

    # =========== Controle da garra ===========
    def fechar(self, *, tempo: float = 0):
        self.motores.move_servo(self.INDICE_SERVO_GARRA, self.POSICAO_GARRA_FECHADA, tempo)

    def abrir(self, *, tempo: float = 0):
        self.motores.move_servo(self.INDICE_SERVO_GARRA, self.POSICAO_GARRA_ABERTA, tempo)

    def abrir_parcial(self, *, tempo: float = 0):
        self.motores.move_servo(self.INDICE_SERVO_GARRA, self.POSICAO_GARRA_PARCIAL, tempo)

    # =========== Controle da porta ===========
    def abrir_porta(self, *, tempo: float = 0):
        self.motores.move_servo(self.INDICE_SERVO_PORTA, self.POSICAO_PORTA_ABERTA, tempo)

    def fechar_porta(self, *, tempo: float = 0):
        self.motores.move_servo(self.INDICE_SERVO_PORTA, self.POSICAO_PORTA_FECHADA, tempo)

    # =========== Ações compostas ===========
    def pegar_bloco(self):
        self.abaixar_total(tempo=0.2)
        self.fechar()

    def abrir_e_abaixar_parcial_depositar(self, abrir_porta: bool = True):
        if abrir_porta:
            self.abrir_porta(tempo=0.2)
        self.abaixar_parcial_depositar(tempo=0.2)

    def depositar_bloco(self, abrir_porta: bool = True):
        self.abrir_e_abaixar_parcial_depositar(abrir_porta=abrir_porta)
        self.abrir_parcial(tempo=0.5)
        sleep(0.2)
        self.abrir()
        self.subir()
        self.fechar_porta()
        sleep(0.5)

    def ler_cor_bloco(self) -> Cores:
        rgbc = self.sensor_cor.le_rgbc(usar_calibracao=False)
        rgb = self.sensor_cor.rgbc_to_rgb255(rgbc)
        hsv = self.sensor_cor.rgb_to_hsv(rgb)
        print('Leitura do cubo - RGBC:', rgbc, 'RGB:', rgb, 'HSV:', hsv)
        return DefinicaoCoresBloco.cor(hsv, rgbc)

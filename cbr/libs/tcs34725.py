from colorsys import rgb_to_hsv
from time import sleep
from smbus2 import SMBus

from libs.configuracao import Configuracao

"""Classe para controlar os sensores i2c TCS34725 nas portas I2C do MariolaZero.
Precisamos passar como parametro qual porta ele I2C está usando"""


class TCS34725:
    MUX_ADDR = 0x70  # Endereço do TCA9548A
    TCS_ADDR = 0x29  # Endereço do sensor TCS34725
    COMMAND_BIT = 0x80
    ENABLE = 0x00
    ATIME = 0x01
    CONTROL = 0x0F
    ID = 0x12
    CDATAL = 0x14
    bus = None
    I2C_BUS = 1  # Verifique qual /dev/i2c-X você está usando

    def __init__(self, porta_mux=None, chave_sensor: str | None = None):
        self.bus = SMBus(self.I2C_BUS)
        self.porta_mux = porta_mux
        if self.porta_mux > 7 or self.porta_mux < 0:
            raise ValueError('Canal inválido (deve ser 0 a 7)')
        self._select_channel()
        # Ativa o sensor (PON + AEN)
        self.bus.write_byte_data(self.TCS_ADDR, self.COMMAND_BIT | self.ENABLE, 0x03)

        # Tempo de integração (2.4ms × (256 - ATIME)) → ATIME = 0xC0 → ~60ms
        self.bus.write_byte_data(self.TCS_ADDR, self.COMMAND_BIT | self.ATIME, 0xC0)

        # Ganho (1x, 4x, 16x, 60x) → 0x01 = 4x
        self.bus.write_byte_data(self.TCS_ADDR, self.COMMAND_BIT | self.CONTROL, 0x01)


        self.configuracao = None
        self.arquivo_calibracao = '/home/banana/cbr/calibracao_sensor_tcs34725'
        if chave_sensor:
            self.CHAVE_CALIBRACAO_BRANCO = f'{chave_sensor}_branco'
            self.CHAVE_CALIBRACAO_PRETO = f'{chave_sensor}_preto'
            self.configuracao = Configuracao(self.arquivo_calibracao)
        self.valor_menor = None
        self.valor_maior = None

        self._carregar_calibracao()



    # Função para selecionar canal no TCA9548A
    def _select_channel(self):
        self.bus.write_byte(self.MUX_ADDR, 1 << self.porta_mux)

    # Função para ler ID do TCS34725 (deve retornar 0x44 ou 0x10)
    def _read_tcs_id(self):
        TCS34725_ID = 0x12
        return self.bus.read_byte_data(self.TCS_ADDR, TCS34725_ID)

    # Funções auxiliares
    def _read_word(self, reg):
        low = self.bus.read_byte_data(self.TCS_ADDR, self.COMMAND_BIT | reg)
        high = self.bus.read_byte_data(self.TCS_ADDR, self.COMMAND_BIT | (reg + 1))
        return (high << 8) | low

    def le_rgbc(self, usar_calibracao: bool=True):
        # Lê os valores
        self._select_channel()
        self._select_channel()
        clear = self._read_word(self.CDATAL)
        red = self._read_word(self.CDATAL + 2)
        green = self._read_word(self.CDATAL + 4)
        blue = self._read_word(self.CDATAL + 6)
        rgbc = (red, green, blue, clear)

        if usar_calibracao and self.valor_menor and self.valor_maior:
            return self.rgbc_to_rgb255(rgbc)
        return rgbc

    def rgb_to_hsv(self, valor_rgb: tuple[int, int, int]) -> tuple[float, float, float]:
        valor_hsv = rgb_to_hsv(*map(lambda x: x / 255, valor_rgb[0:3]))
        return (int(valor_hsv[0] * 360), int(valor_hsv[1] * 255), int(valor_hsv[2] * 255))

    def le_hsv(self, calibrado: bool=True) -> tuple[float, float, float]:
        valor_rgb = self.le_rgbc(usar_calibracao=calibrado)
        return self.rgb_to_hsv(valor_rgb)

    def rgbc_to_rgb255(
            self, 
            valor: tuple[int, int, int, int],
        ): 
        try:
            red_calibrado = self.__normalizar_valor(valor[0], self.valor_menor[0], self.valor_maior[0])
            green_calibrado = self.__normalizar_valor(valor[1], self.valor_menor[1], self.valor_maior[1])
            blue_calibrado = self.__normalizar_valor(valor[2], self.valor_menor[2], self.valor_maior[2])
            return (red_calibrado, green_calibrado, blue_calibrado)
        except Exception as e:
            print(f"Erro ao calibrar valores RGB: {e}")
            return valor

    def __normalizar_valor(self, valor, valor_min, valor_max):
            """Normaliza um valor para escala 0-255 com base nos limites calibrados"""
            normalized = 255 * (valor - valor_min) / (valor_max - valor_min)
            return max(0, min(255, int(normalized)))

    def media_sensor(self, n: int = 100):
        """Faz N leituras do sensor de cor e calcula a média RGBA"""
        soma_r = soma_g = soma_b = soma_a = 0

        for _ in range(n):
            r, g, b, c = self.le_rgbc(usar_calibracao=False)
            print(f'Leitura: R={r}, G={g}, B={b}, C={c}')
            soma_r += r
            soma_g += g
            soma_b += b
            soma_a += c

            sleep(0.01)

        return (soma_r / n, soma_g / n, soma_b / n, soma_a / n)

    def _carregar_calibracao(self):
        self.valor_menor = None
        self.valor_maior = None

        if self.configuracao:
            self.configuracao.carrega()
            self.valor_menor = self.configuracao.obtem(self.CHAVE_CALIBRACAO_PRETO)
            self.valor_maior = self.configuracao.obtem(self.CHAVE_CALIBRACAO_BRANCO)

    def _calibrar(self, chave: str):
        valor_media = self.media_sensor()
        self.configuracao.insere(chave, [int(v) for v in valor_media])
        self._carregar_calibracao()


    def calibrar_branco(self):
        if not self.configuracao:
            raise ValueError("Chave do sensor não definida para calibrar.")

        self._calibrar(self.CHAVE_CALIBRACAO_BRANCO)

    def calibrar_preto(self):
        if not self.configuracao:
            raise ValueError("Chave do sensor não definida para calibrar.")

        self._calibrar(self.CHAVE_CALIBRACAO_PRETO)
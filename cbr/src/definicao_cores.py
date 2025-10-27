from enum import Enum

# =========================
# ENUMS E CONSTANTES
# =========================


class Cores(Enum):
    """Enum que representa as cores detectáveis pelo robô."""

    VERMELHO = 0
    VERDE = 1
    AZUL = 2
    AMARELO = 3
    PRETO = 4
    BRANCO = 5
    MARROM = 6
    VAZIO = 7


class HSV:
    H, S, V = 0, 1, 2


class RGBC:
    R, G, B, C = 0, 1, 2, 3


class ValorAlinhamentoSeguidor:
    """
    Valores de alinhamento do seguidor de linha.
    Cada constante contém:
    (índice do sensor RGBC utilizado, valor de alinhamento).
    """

    VERDE_AMARELO = (0, 55)
    VERDE_VERMELHO = (0, 40)


class DefinicaoCoresLinha:
    """Define as cores detectáveis na linha com base em valores HSV."""

    @staticmethod
    def e_preto(valor: int) -> bool:
        return valor < 20

    @staticmethod
    def e_azul(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        return 65 <= h <= 90 and 30 <= s <= 60 and 35 <= v <= 55

    @staticmethod
    def e_verde(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        return 35 <= h <= 55 and 25 <= s <= 60 and 30 <= v <= 55

    @staticmethod
    def e_amarelo(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        return 12 <= h <= 25 and 45 <= s <= 80 and 60 <= v <= 127

    @staticmethod
    def e_vermelho(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        return ((0 <= h <= 10) or (110 <= h <= 127)) and 40 <= s <= 90 and 55 <= v <= 95

    @staticmethod
    def e_vermelho_ou_azul_ou_amarelo(hsv: tuple[int, int, int]) -> tuple[bool, bool, bool]:
        """Retorna uma tupla indicando (vermelho, azul, amarelo)."""
        return (
            DefinicaoCoresLinha.e_vermelho(hsv),
            DefinicaoCoresLinha.e_azul(hsv),
            DefinicaoCoresLinha.e_amarelo(hsv),
        )

    @staticmethod
    def cor(hsv: tuple[int, int, int]) -> Cores | None:
        """Identifica e retorna a cor detectada na linha."""
        if DefinicaoCoresLinha.e_vermelho(hsv):
            return Cores.VERMELHO
        if DefinicaoCoresLinha.e_azul(hsv):
            return Cores.AZUL
        if DefinicaoCoresLinha.e_amarelo(hsv):
            return Cores.AMARELO
        if DefinicaoCoresLinha.e_verde(hsv):
            return Cores.VERDE
        if DefinicaoCoresLinha.e_preto(hsv[HSV.V]):
            return Cores.PRETO
        return None


class DefinicaoCoresLixeira:
    """Define as cores das lixeiras com base em valores HSV."""

    @staticmethod
    def e_preto(hsv: tuple[int, int, int]) -> bool:
        h, _, v = hsv
        return ((0 <= h <= 30 or 190 <= h <= 360) and v <= 30) or v <= 15

    @staticmethod
    def e_azul(hsv: tuple[int, int, int]) -> bool:  # OK
        h, s, v = hsv
        return 180 <= h <= 255 and (155 <= s <= 255 and 35 <= v <= 160)

    @staticmethod
    def e_vermelho(hsv: tuple[int, int, int]) -> bool:  # ok
        h, s, v = hsv
        return ((0 <= h <= 25) or (320 <= h <= 360)) and 140 <= s <= 255 and 31 <= v <= 255

    @staticmethod
    def e_verde(hsv: tuple[int, int, int]) -> bool:  # OK
        h, s, v = hsv
        return 80 <= h <= 170 and 130 <= s <= 255 and 5 <= v <= 70

    @staticmethod
    def e_amarelo(hsv: tuple[int, int, int]) -> bool:  # OK
        h, s, v = hsv
        return 30 <= h <= 75 and 90 <= s <= 255 and 100 <= v <= 255

    @staticmethod
    def e_marrom(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        # return ((0 <= h <= 55) or (320 <= h <= 360)) and 20 <= s <= 255 and 3 <= v <= 60
        # return ((0 <= h <= 40) or (160 <= h <= 360)) and (h*1.5 <= s or s*1.5 <= h) and v < 30
        return (h * 1.5 <= s or s * 1.5 <= h or s == 255) and v < 30 and (0, 0) != (h, s)

    @staticmethod
    def cor(hsv: tuple[int, int, int]) -> Cores | None:
        """Identifica e retorna a cor detectada."""
        if DefinicaoCoresLixeira.e_azul(hsv):
            return Cores.AZUL
        if DefinicaoCoresLixeira.e_vermelho(hsv):
            return Cores.VERMELHO
        if DefinicaoCoresLixeira.e_verde(hsv):
            return Cores.VERDE
        if DefinicaoCoresLixeira.e_amarelo(hsv):
            return Cores.AMARELO
            # if DefinicaoCoresLixeira.e_marrom(hsv):
            #     return Cores.MARROM
        if DefinicaoCoresLixeira.e_preto(hsv):
            return Cores.PRETO
        return None


class DefinicaoCoresBloco:
    """Define as cores dos blocos com base em valores RGB e HSV."""

    @staticmethod
    def e_preto(rgbc: tuple[int, int, int, int]) -> bool:
        return 1400 < rgbc[RGBC.C] < 3500

    @staticmethod
    def e_branco(rgbc: tuple[int, int, int, int]) -> bool:
        return rgbc[RGBC.C] > 20000

    @staticmethod
    def e_azul(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        return 135 <= h <= 255 and 200 <= s <= 255 and 30 <= v <= 255

    @staticmethod
    def e_vermelho(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        return ((0 <= h <= 10) or (300 <= h <= 360)) and 130 <= s <= 255 and 31 <= v <= 255

    @staticmethod
    def e_verde(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        return 90 <= h <= 175 and 65 <= s <= 255 and v > 5

    @staticmethod
    def e_amarelo(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        return 20 <= h <= 60 and 120 <= s <= 200 and 120 <= v <= 255

    @staticmethod
    def e_marrom(hsv: tuple[int, int, int]) -> bool:
        h, s, v = hsv
        return ((0 <= h <= 55) or (140 <= h <= 300)) and 10 <= s <= 255
        # return (0 <= h <= 55) or (140 <= h <= 300)

    @staticmethod
    def cor(hsv: tuple[int, int, int], rgbc: tuple[int, int, int, int]) -> Cores | None:
        """Identifica e retorna a cor do bloco."""
        if DefinicaoCoresBloco.e_amarelo(hsv):
            return Cores.AMARELO
        if DefinicaoCoresBloco.e_branco(rgbc):
            return Cores.BRANCO
        if DefinicaoCoresBloco.e_vermelho(hsv):
            return Cores.VERMELHO
        if DefinicaoCoresBloco.e_verde(hsv):
            return Cores.VERDE
        if DefinicaoCoresBloco.e_azul(hsv):
            return Cores.AZUL
        # if DefinicaoCoresBloco.e_marrom(hsv):
        #     return Cores.MARROM
        if DefinicaoCoresBloco.e_preto(rgbc):
            return Cores.PRETO
        return None

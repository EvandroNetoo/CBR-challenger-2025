import threading
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont


class Tela:
    def __init__(self, i2c_bus=0, i2c_address=0x3C):
        self.width = 128
        self.height = 64
        self.TAMANHO_TELA = 4
        self._TAMANHO_FONTE = 12

        # Inicializa o display
        self.serial = i2c(port=i2c_bus, address=i2c_address)
        self.display = ssd1306(self.serial, width=self.width, height=self.height, rotate=0)

        # Fonte
        self.font = ImageFont.truetype(
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            self._TAMANHO_FONTE
        )

        # Limpa a tela inicialmente
        with canvas(self.display) as draw:
            draw.rectangle(self.display.bounding_box, outline='black', fill='black')

        self.linhas = [''] * self.TAMANHO_TELA

    def escreve(self, texto, linha=0):
        """Escreve texto em uma linha específica da tela."""
        if not (0 <= linha < self.TAMANHO_TELA):
            raise ValueError(f"Linha inválida. Deve ser entre 0 e {self.TAMANHO_TELA - 1}.")
        self.linhas[linha] = texto
        self._desenha()

    def escreve_assincrono(self, texto, linha=0):
        """Escreve sem travar o robô."""
        thread = threading.Thread(target=self.escreve, args=(texto, linha))
        thread.daemon = True
        thread.start()

    def limpa(self, linha=-1):
        """Limpa uma linha específica ou toda a tela."""
        if linha == -1:
            self.linhas = [''] * self.TAMANHO_TELA
        elif 0 <= linha < self.TAMANHO_TELA:
            self.linhas[linha] = ''
        else:
            raise ValueError(f"Linha inválida. Deve ser entre 0 e {self.TAMANHO_TELA - 1}.")
        self._desenha()

    def _desenha(self):
        """Desenha o conteúdo atual na tela OLED."""
        with canvas(self.display) as draw:
            for i, linha in enumerate(self.linhas):
                y = i * (self._TAMANHO_FONTE)  # espaçamento entre linhas
                draw.text((0, y), linha, font=self.font, fill='white')

    @property
    def tamanho_fonte(self):
        return self._TAMANHO_FONTE
    
    @tamanho_fonte.setter
    def tamanho_fonte(self, tamanho):
        self._TAMANHO_FONTE = tamanho
        self.font = ImageFont.truetype(
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            self._TAMANHO_FONTE
        )

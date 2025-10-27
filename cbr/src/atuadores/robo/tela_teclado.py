from libs.teclado import Teclado
from libs.tela import Tela
from src.definicao_cores import Cores


class TelaTeclado:
    def __init__(self):
        self.tela = Tela()
        self.teclado = Teclado()
        self.teclado.botao_para_encerrar_programa(4)
        # self.tela.limpa()

    def escreve_cor(self, cor: Cores):
        # self.tela.limpa()
        self.tela.tamanho_fonte = 60
        if cor == Cores.VERDE:
            self.tela.escreve_assincrono('VD')
        elif cor == Cores.VERMELHO:
            self.tela.escreve_assincrono('VM')
        elif cor == Cores.AMARELO:
            self.tela.escreve_assincrono('AM')
        elif cor == Cores.AZUL:
            self.tela.escreve_assincrono('AZ')
        elif cor == Cores.MARROM:
            self.tela.escreve_assincrono('MR')
        elif cor == Cores.PRETO:
            self.tela.escreve_assincrono('PT')
        elif cor == Cores.BRANCO:
            self.sinaliza_cubo_branco()
        else:
            self.tela.escreve_assincrono('NUL')

    def sinaliza_cubo_branco(self):
        self.tela.limpa()
        self.tela.tamanho_fonte = 500
        self.tela.escreve_assincrono('▉')

    def escreve_posicao(self, posicao: tuple[int, int]):
        self.tela.tamanho_fonte = 55
        self.tela.escreve_assincrono(f'({posicao[0]},{posicao[1]})')

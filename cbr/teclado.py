from libs.teclado import Teclado
from libs.tela import Tela

teclado = Teclado()
tela = Tela()

teclado.botao_para_encerrar_programa(4)
tela.escreve('▉▉▉▉▉▉▉▉', 0)


while True:
    if teclado.botao_pressionado(1):
        print('1')
    if teclado.botao_pressionado(2):
        print('2')

    if teclado.botao_pressionado(1) and teclado.botao_pressionado(2):
        print('1 e 2')

    print('\n')

from libs.teclado import Teclado
from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha
from src.estrategias.estrategia_area_verde import EstrategiaAreaVerde
from src.mapa import Mapa

teclado = Teclado()

teclado.botao_para_encerrar_programa(4)

robo = RoboSeguidorDeLinha()
estrategia = EstrategiaAreaVerde(robo, Mapa())

try:
    estrategia.iniciar()
except KeyboardInterrupt:
    robo.pare()
    print('Processo interrompido.')

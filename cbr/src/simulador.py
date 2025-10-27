from src.atuadores import Simulador
from src.estrategias.estrategia_mapa import EstrategiaMapa
from src.mapa import Mapa

mapa = Mapa()
robo = Simulador()
estrategia = EstrategiaMapa(robo, mapa)
while True:
    robo.ir_para_0_0()
    estrategia.iniciar()

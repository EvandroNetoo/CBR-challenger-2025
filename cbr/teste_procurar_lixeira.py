from settings import VELOCIDADE_PADRAO
from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha
from src.definicao_cores import Cores
from src.estrategias.estrategia_area_verde import EstrategiaAreaVerde
from src.mapa import Mapa

robo = RoboSeguidorDeLinha()
estrategia = EstrategiaAreaVerde(robo, Mapa())
estrategia.posicoes_lixeiras = [Cores.AMARELO, Cores.VERMELHO, Cores.MARROM, Cores.VERDE, Cores.PRETO]
# cor_bloco_pego, aresta_saida = Cores.VERDE, 2

i = 0
cor_bloco_pego = estrategia.posicoes_lixeiras[i]
while True:
    estrategia.retornar_para_mapa(cor_bloco_pego=cor_bloco_pego, velocidade=VELOCIDADE_PADRAO)
    input('Aperte Enter para continuar...')
    i = (i + 1) % len(estrategia.posicoes_lixeiras)
    cor_bloco_pego = estrategia.posicoes_lixeiras[i]

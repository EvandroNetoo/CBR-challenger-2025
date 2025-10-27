from settings import VELOCIDADE_BAIXA
from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha
from src.definicao_cores import Cores
from src.estrategias.estrategia_mapa import EstrategiaMapa
from src.mapa import Mapa

robo = RoboSeguidorDeLinha()
estrategia = EstrategiaMapa(robo, Mapa())
estrategia.posicoes_lixeiras = [
    Cores.VERMELHO,
    Cores.AMARELO,
    Cores.MARROM,
    Cores.VERDE,
    Cores.AZUL,
    Cores.PRETO,
]

try:
    estrategia.robo.seguir_ate_encruzilhada(velocidade=VELOCIDADE_BAIXA, modo=robo.ModoMotor.VELOCIDADE)
    # estrategia.robo.voltar_encruzilhada()
    # estrategia.robo.ande_certa_distancia(35, velocidade=VELOCIDADE_BAIXA)
    estrategia.iniciar()
    # robo.sensor_de_linha.le_reflexao()
    # sleep(1)
    # robo.sensor_de_linha.calibra_preto()
    # print('Calibração de branco concluída.')
except KeyboardInterrupt:
    robo.pare()
    print('Processo interrompido.')

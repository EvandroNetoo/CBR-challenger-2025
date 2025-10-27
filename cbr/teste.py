from settings import VELOCIDADE_MAXIMA
from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha

robo = RoboSeguidorDeLinha()


try:
    velocidade = 50
    distancia = 300
    while True:
        robo.ande_certa_distancia(distancia, velocidade=VELOCIDADE_MAXIMA)

        robo.pare()
        input('Pressione Enter para seguir até a encruzilhada...')


except KeyboardInterrupt:
    robo.pare()
    print('Processo interrompido.')

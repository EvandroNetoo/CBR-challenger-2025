from time import sleep

from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha
from src.definicao_cores import DefinicaoCoresLinha

robo = RoboSeguidorDeLinha()

try:
    while True:
        valor1 = robo.sensor_de_linha.le_hsv(robo.SENSOR_COR_ESQUERDO)
        valor2 = robo.sensor_de_linha.le_hsv(robo.SENSOR_COR_CENTRO)
        valor3 = robo.sensor_de_linha.le_hsv(robo.SENSOR_COR_DIREITO)

        print(f'Esquerdo: {valor1} - Centro: {valor2} - Direito: {valor3}')
        print(
            DefinicaoCoresLinha.cor(valor1),
            DefinicaoCoresLinha.cor(valor2),
            DefinicaoCoresLinha.cor(valor3),
        )
        sleep(0.2)

except KeyboardInterrupt:
    robo.pare()
    print('Processo interrompido.')

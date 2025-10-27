from time import sleep

from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha

robo = RoboSeguidorDeLinha()

try:
    while True:
        leitura = robo.sensor_de_linha.le_reflexao()
        print(leitura, int(sum(leitura) / len(leitura)))
        esquerdo = robo.sensor_de_linha.le_rgbc(robo.SENSOR_COR_ESQUERDO)
        centro = robo.sensor_de_linha.le_rgbc(robo.SENSOR_COR_CENTRO)
        direito = robo.sensor_de_linha.le_rgbc(robo.SENSOR_COR_DIREITO)

        print(f'Esquerdo: {esquerdo} - Centro: {centro} - Direito: {direito}')
        sleep(0.02)
except KeyboardInterrupt:
    robo.pare()
    print('Processo interrompido.')

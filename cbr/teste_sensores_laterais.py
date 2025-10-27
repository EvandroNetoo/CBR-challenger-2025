from time import sleep

from libs.motores import Motores
from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha

robo = RoboSeguidorDeLinha()

motores = Motores(True)

try:
    while True:
        print('Esquerdo: ', robo.sensor_distancia_esquerdo.read_range_single_millimeters())
        print('Frontal: ', robo.sensor_distancia_frontal.read_range_single_millimeters())
        print('Direito: ', robo.sensor_distancia_direito.read_range_single_millimeters())
        # rgbc = robo.sensor_cor_esquerdo.le_rgbc(usar_calibracao=False)
        # rgb = robo.sensor_cor_esquerdo.rgbc_to_rgb255(rgbc)
        # hsv = robo.sensor_cor_esquerdo.rgb_to_hsv(rgb)
        # cor = DefinicaoCoresLixeira.cor(hsv)

        # print(f'RGBC: {rgbc}')
        # print(f'RGB: {rgb}')
        # print(f'HSV: {hsv}')
        # print(f'Cor detectada: {cor}')
        print('---')
        sleep(0.5)
except KeyboardInterrupt:
    robo.pare()
    print('Processo interrompido.')

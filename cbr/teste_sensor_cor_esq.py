from time import sleep

from libs.tcs34725 import TCS34725
from settings import CHAVE_SENSOR_COR_ESQUERDO, PORTA_SENSOR_COR_ESQUERDO
from src.definicao_cores import DefinicaoCoresLixeira

sensor = TCS34725(PORTA_SENSOR_COR_ESQUERDO, chave_sensor=CHAVE_SENSOR_COR_ESQUERDO)

while True:
    rgbc = sensor.le_rgbc(usar_calibracao=False)
    rgb = sensor.rgbc_to_rgb255(rgbc)
    hsv = sensor.rgb_to_hsv(rgb)
    cor = DefinicaoCoresLixeira.cor(hsv)

    print(f'RGBC: {rgbc}')
    print(f'RGB: {rgb}')
    print(f'HSV: {hsv}')
    print(f'Cor detectada: {cor}')
    print('---')
    sleep(0.2)

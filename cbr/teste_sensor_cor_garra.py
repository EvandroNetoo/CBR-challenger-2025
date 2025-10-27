from time import sleep

from libs.tcs34725 import TCS34725
from src.atuadores.robo.garra import Garra
from src.definicao_cores import DefinicaoCoresBloco

sensor = TCS34725(Garra.PORTA_SENSOR_COR, chave_sensor=Garra.CHAVE_SENSOR_COR)

while True:
    rgbc = sensor.le_rgbc(usar_calibracao=False)
    rgb = sensor.rgbc_to_rgb255(rgbc)
    hsv = sensor.rgb_to_hsv(rgb)
    cor = DefinicaoCoresBloco.cor(hsv, rgbc)

    print(f'RGBC: {rgbc}')
    print(f'RGB: {rgb}')
    print(f'HSV: {hsv}')
    print(f'Cor detectada: {cor}')
    print('---')
    sleep(0.2)

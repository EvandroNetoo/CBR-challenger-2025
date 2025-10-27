from time import sleep

from libs.tcs34725 import TCS34725
from src.atuadores.robo.garra import Garra
from src.definicao_cores import DefinicaoCoresBloco

sensor = TCS34725(Garra.PORTA_SENSOR_COR, chave_sensor=Garra.CHAVE_SENSOR_COR)
garra = Garra()
# garra.abrir()
# input("Pressione Enter para continuar...")

while True:
    x = input('Digite o ângulo da alavanca (0 a 180): ')
    garra.motores.move_servo(garra.INDICE_SERVO_GARRA, int(x), 1)

    for _ in range(10):
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

    # sleep(0.2)
    # garra.abaixar_parcial()
    # input("Pressione Enter para pegar o cubo novamente...")
    # garra.pegar_bloco()
    # input("Pressione Enter para soltar o cubo...")

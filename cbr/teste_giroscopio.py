from time import sleep

from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha

robo = RoboSeguidorDeLinha()
robo.giroscopio.calibra()

while True:
    # robo.giroscopio.reseta_z()
    print(robo.giroscopio.le_angulo_z())
    print(robo.giroscopio.le_angulo_z() % 360)
    robo.gire_graus_giroscopio(90)
    sleep(0.5)

    # print(robo.giroscopio.le_angulo_z())
    # print(robo.giroscopio.le_angulo_z() % 360)

    input('Pressione Enter para girar 90 graus...')

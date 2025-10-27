from libs.tcs34725 import TCS34725
from src.atuadores.robo.garra import Garra

sensor = TCS34725(Garra.PORTA_SENSOR_COR, chave_sensor=Garra.CHAVE_SENSOR_COR)

input('Pressione Enter para iniciar a calibração do sensor de cor da garra na cor BRANCA...')
sensor.calibrar_branco()
input('Pressione Enter para iniciar a calibração do sensor de cor da garra na cor PRETA...')
sensor.calibrar_preto()
print('Calibração concluída!')

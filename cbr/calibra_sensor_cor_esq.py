from libs.tcs34725 import TCS34725
from settings import CHAVE_SENSOR_COR_ESQUERDO, PORTA_SENSOR_COR_ESQUERDO

sensor = TCS34725(PORTA_SENSOR_COR_ESQUERDO, chave_sensor=CHAVE_SENSOR_COR_ESQUERDO)

input('Pressione Enter para iniciar a calibração do sensor de cor esquerdo na cor BRANCA...')
sensor.calibrar_branco()
input('Pressione Enter para iniciar a calibração do sensor de cor esquerdo na cor PRETA...')
sensor.calibrar_preto()
print('Calibração concluída!')

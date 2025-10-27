from time import sleep

from settings import PORTA_SENSOR_COR_LINHA
from src.atuadores.robo import CorReflexao

sensor_cor_linha = CorReflexao(PORTA_SENSOR_COR_LINHA)

sensor_cor_linha.le_reflexao()
sleep(1)
print('iniciando calibração de branco...')
sensor_cor_linha.calibra_branco()
print('Calibração de branco concluída.')

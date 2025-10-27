from settings import VELOCIDADE_PADRAO
from src.atuadores.robo import Robo
from src.atuadores.robo.seguidor_linha import DirecaoSeguirLinhaSimples, RoboSeguidorDeLinha
from src.definicao_cores import DefinicaoCoresLinha

robo = RoboSeguidorDeLinha()

try:
    direcao = DirecaoSeguirLinhaSimples.NORTE
    while True:
        while not (
            robo.seguir_linha_simples_e_analisar_cor(
                DefinicaoCoresLinha.e_vermelho,
                indice_sensor=robo.SENSOR_COR_CENTRO,
                direcao=direcao,
                velocidade=80,
                modo=Robo.ModoMotor.POTENCIA,
            )
        ):
            pass
        robo.pare()
        input('Aperte Enter para iniciar a próxima lixeira...')
        robo.gire_graus(180, velocidade=VELOCIDADE_PADRAO)

        direcao *= -1  # Inverte a direção para a próxima busca


except KeyboardInterrupt:
    robo.pare()
    print('Processo interrompido.')

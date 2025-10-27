from settings import DEPOSITAR_DE_FRENTE, VELOCIDADE_BAIXA, VELOCIDADE_MAXIMA, VELOCIDADE_PADRAO
from src.atuadores.robo.seguidor_linha import RoboSeguidorDeLinha
from src.definicao_cores import Cores, ValorAlinhamentoSeguidor
from src.estrategias.estrategia_area_verde import EstrategiaAreaVerde
from src.mapa import Mapa

robo = RoboSeguidorDeLinha()
estrategia = EstrategiaAreaVerde(robo, Mapa())

cor_bloco_pego, aresta_saida = Cores.VERMELHO, 4
estrategia.posicoes_lixeiras_depositadas[cor_bloco_pego] = 0
estrategia.posicoes_lixeiras = [Cores.VERMELHO, Cores.VERDE, Cores.AMARELO, Cores.AZUL, Cores.PRETO]
try:
    while True:
        robo.garra.fechar()
        estrategia.ir_ao_amarelo(velocidade=VELOCIDADE_BAIXA)
        robo.alinhe_entre_linhas(ValorAlinhamentoSeguidor.VERDE_AMARELO, velocidade=VELOCIDADE_BAIXA)

        if DEPOSITAR_DE_FRENTE and estrategia.deposita_de_frente(
            cor=cor_bloco_pego,
            aresta_saida=aresta_saida,
            velocidade=VELOCIDADE_PADRAO,
        ):
            estrategia.andar_ate_mapa(cor_bloco_pego=cor_bloco_pego, velocidade=VELOCIDADE_MAXIMA)

        else:
            estrategia.posicionar_e_depositar_lixo(
                cor=cor_bloco_pego,
                aresta_saida=aresta_saida,
                velocidade=VELOCIDADE_PADRAO,
            )

            estrategia.retornar_para_mapa(cor_bloco_pego=cor_bloco_pego, velocidade=VELOCIDADE_PADRAO)

        input('Aperte Enter para reiniciar o teste...')

    # estrategia.retornar_para_mapa(VELOCIDADE_PADRAO, cor_bloco_pego)


except KeyboardInterrupt:
    robo.pare()
    print('Processo interrompido.')

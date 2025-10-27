"""
Módulo que implementa um robô seguidor de linha com controle PID.
Estende a classe base Robo com funcionalidades específicas para seguir linhas,
detectar cores e manipular blocos.
"""

from __future__ import annotations

import time
from time import sleep
from typing import Callable

from settings import (
    KD_PADRAO,
    KP_PADRAO,
    VALOR_ENCRUZILHADA,
    VELOCIDADE_BAIXA,
    VELOCIDADE_BASE_SEGUIDOR,
    VELOCIDADE_PADRAO,
)
from src.atuadores.robo import Robo
from src.definicao_cores import Cores, DefinicaoCoresLinha, ValorAlinhamentoSeguidor


class DirecaoSeguirLinhaSimples:
    NORTE = 1
    SUL = -1


class RoboSeguidorDeLinha(Robo):
    """
    Implementa um robô seguidor de linha com controle PID.
    Estende a classe base Robo com funcionalidades para seguir linhas
    de forma precisa e realizar tarefas específicas como pegar blocos.
    """

    # Constantes para controle PID
    KP_SIMPLES = 0.7
    KD_SIMPLES = 0.7
    VALOR_MAXIMO = 100

    def __init__(self):
        super().__init__()
        # Variáveis de estado para controle PID
        self.erro_anterior = 0
        self.erro_anterior_simples = 0

    # ====================================================================
    # MÉTODOS BÁSICOS
    # ====================================================================

    def erro_pid(self) -> float:
        """Calcula o erro do PID com base nos valores lidos pelos sensores de cor."""
        extrema_direita, direita, esquerda, extrema_esquerda = self.sensor_de_linha.le_reflexao()
        return (extrema_esquerda + esquerda) - (extrema_direita + direita)

    def compensacao_potencia(self, potencia1: int, potencia2: int) -> tuple[int, int]:
        """Compensa as potências dos motores para que não ultrapassem o valor máximo."""
        diferenca_potencia1 = potencia1 - self.VALOR_MAXIMO
        if diferenca_potencia1 > 0:
            potencia2 -= diferenca_potencia1
            potencia1 = self.VALOR_MAXIMO

        diferemca_potencia2 = potencia2 - self.VALOR_MAXIMO
        if diferemca_potencia2 > 0:
            potencia1 -= diferemca_potencia2
            potencia2 = self.VALOR_MAXIMO

        return potencia1, potencia2

    def obter_velocidades_PID(
        self, velocidade: int = VELOCIDADE_BASE_SEGUIDOR, KP=KP_PADRAO, KD=KD_PADRAO
    ) -> tuple[int, int]:
        """
        Calcula as potências dos motores com base no controle PID.

        Esta função implementa um controlador PID (Proporcional-Derivativo) que ajusta
        as velocidades dos motores para manter o robô seguindo a linha. O termo proporcional
        responde ao erro atual, enquanto o termo derivativo suaviza o movimento,
        reduzindo oscilações.
        """
        erro_pid = self.erro_pid()

        # Calcula o termo proporcional (responde ao erro atual)
        ganho_proporcional = erro_pid * KP

        # Calcula o termo derivativo (responde à taxa de mudança do erro)
        d = (erro_pid - self.erro_anterior) * KD

        # Soma os termos para obter o valor de correção
        valor = int(ganho_proporcional + d)

        # Atualiza o erro anterior para o próximo cálculo
        self.erro_anterior = erro_pid

        # Aplica a correção e compensa os valores para não ultrapassar limites
        return self.compensacao_potencia(velocidade + valor, velocidade - valor)

    # ====================================================================
    # SEGUIDOR DE LINHA COMPLETO
    # ====================================================================

    def seguir_linha(
        self,
        *,
        velocidade: int = VELOCIDADE_BASE_SEGUIDOR,
        modo: int = Robo.ModoMotor.POTENCIA,
        KP=KP_PADRAO,
        KD=KD_PADRAO,
    ):
        potencia1, potencia2 = self.obter_velocidades_PID(velocidade=velocidade, KP=KP, KD=KD)
        if modo == Robo.ModoMotor.POTENCIA:
            self.motores.potencia_motores(potencia1, potencia2)
        elif modo == Robo.ModoMotor.VELOCIDADE:
            self.motores.velocidade_motores(potencia1, potencia2)

        sleep(0.02)

    def seguir_linha_distancia(
        self,
        distancia: int,
        velocidade: int = VELOCIDADE_PADRAO,
        modo: int = Robo.ModoMotor.POTENCIA,
        kp=KP_PADRAO,
        kd=KD_PADRAO,
    ):
        graus = distancia * self.DISTANCIA_PARA_GRAUS

        angulo_motor_direito_inicial = self.motores.angulo_motor(self.MOTOR_DIREITO)
        angulo_motor_esquerdo_inicial = self.motores.angulo_motor(self.MOTOR_ESQUERDO)

        # Calcula a média inicial para referência
        media_motor_inicial = (angulo_motor_direito_inicial + angulo_motor_esquerdo_inicial) // 2
        media_motor = media_motor_inicial

        # Segue a linha até atingir a distância desejada
        while media_motor_inicial - graus < media_motor < media_motor_inicial + graus:
            angulo_motor_direito = self.motores.angulo_motor(self.MOTOR_DIREITO)
            angulo_motor_esquerdo = self.motores.angulo_motor(self.MOTOR_ESQUERDO)

            media_motor = (angulo_motor_direito + angulo_motor_esquerdo) // 2

            self.seguir_linha(
                velocidade=velocidade,
                modo=modo,
                KP=kp,
                KD=kd,
            )
        self.pare()

    def seguir_ate_encruzilhada(
        self,
        velocidade: int = VELOCIDADE_BASE_SEGUIDOR,
        modo: int = Robo.ModoMotor.POTENCIA,
        tempo_minimo: float = 0,
        valor_encruzilhada: int = VALOR_ENCRUZILHADA,
        com_cubo: bool = False,
    ) -> bool:
        """
        Faz o robô seguir a linha até encontrar uma encruzilhada.

        Uma encruzilhada é detectada quando a média dos valores dos sensores de reflexão
        está abaixo do valor definido como VALOR_ENCRUZILHADA. O parâmetro tempo_minimo
        evita a detecção de falsos positivos, exigindo que o robô siga por um tempo mínimo.
        """
        # Se tempo_minimo for maior que 0, espera esse tempo antes de começar a detectar encruzilhadas
        tempo_inicio_execucao = time.time()

        while True:
            extrema_direita, direita, esquerda, extrema_esquerda = self.sensor_de_linha.le_reflexao()
            # media = (extrema_esquerda + esquerda + direita + extrema_direita) // 4

            # Só detecta a encruzilhada se já passou o tempo mínimo definido
            tempo_atual = time.time() - tempo_inicio_execucao
            # if media < valor_encruzilhada and tempo_atual >= tempo_minimo:
            #     break
            if (
                all((
                    direita < valor_encruzilhada,
                    esquerda < valor_encruzilhada,
                    (extrema_direita < valor_encruzilhada or extrema_esquerda < valor_encruzilhada),
                ))
                and tempo_atual >= tempo_minimo
            ):
                break

            self.seguir_linha(velocidade=velocidade, modo=modo)

            if com_cubo:
                valor1 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_ESQUERDO)
                valor2 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_CENTRO)
                valor3 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_DIREITO)

                # se ao menos dois sensores verem verde
                if (
                    DefinicaoCoresLinha.e_verde(valor1)
                    + DefinicaoCoresLinha.e_verde(valor2)
                    + DefinicaoCoresLinha.e_verde(valor3)
                ) >= 2:
                    self.pare_suave()
                    sleep(1)
                    self.pare()
                    valor1 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_ESQUERDO)
                    valor2 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_CENTRO)
                    valor3 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_DIREITO)

                    if (
                        DefinicaoCoresLinha.e_verde(valor1)
                        + DefinicaoCoresLinha.e_verde(valor2)
                        + DefinicaoCoresLinha.e_verde(valor3)
                    ) >= 2:
                        print(f'Encruzilhada encontrada por verde! {valor1} {valor2} {valor3}')
                        return False

        self.pare_suave()
        print('Encruzilhada encontrada!')
        return True

    def seguir_linha_ate_cor(
        self,
        funcao_cor: Callable[[tuple[int, int, int, int]], bool],
        *,
        velocidade: int = VELOCIDADE_PADRAO,
        modo: int = Robo.ModoMotor.POTENCIA,
    ):
        """Faz o robô seguir uma linha até encontrar uma cor específica."""
        while True:
            valor1 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_ESQUERDO)
            valor2 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_DIREITO)
            valor3 = self.sensor_de_linha.le_hsv(self.SENSOR_COR_CENTRO)

            if funcao_cor(valor1) or funcao_cor(valor2) or funcao_cor(valor3):
                print(f'Seguir linha até cor: cor encontrada! {valor1} {valor2} {valor3}')
                break

            self.seguir_linha(velocidade=velocidade, modo=modo)

        self.pare()

    def alinhe_parado(
        self,
        tempo=0.5,
    ):
        tempo_inicial = time.time()
        while time.time() - tempo_inicial < tempo:
            self.seguir_linha(
                velocidade=0,
                modo=Robo.ModoMotor.VELOCIDADE,
            )
            sleep(0.02)

    # ====================================================================
    # SEGUIDOR DE LINHA SIMPLES
    # ====================================================================

    def seguir_linha_simples(
        self,
        indice_sensor: int = Robo.SENSOR_COR_CENTRO,
        dados_alinhamento: tuple[int, int] = ValorAlinhamentoSeguidor.VERDE_AMARELO,
        *,
        velocidade: int = VELOCIDADE_PADRAO,
        direcao: int = DirecaoSeguirLinhaSimples.NORTE,
        modo: int = Robo.ModoMotor.POTENCIA,
    ):
        """
        Implementação simplificada de seguimento de linha usando um único sensor de cor.

        Este método utiliza um controle proporcional-derivativo mais simples baseado
        em um único sensor de cor, ideal para linhas bem definidas ou seguimento
        de bordas coloridas.
        """
        indice_cor, valor_alinhamento = dados_alinhamento
        valor_sensor = self.sensor_de_linha.le_rgbc(indice_sensor)[indice_cor]

        erro = (valor_sensor - valor_alinhamento) * direcao
        ganho_proporcional = erro * self.KP_SIMPLES
        d = (erro - self.erro_anterior_simples) * self.KD_SIMPLES
        valor = int(ganho_proporcional + d)
        self.erro_anterior_simples = erro

        potencia1, potencia2 = self.compensacao_potencia(velocidade + valor, velocidade - valor)

        if modo == Robo.ModoMotor.POTENCIA:
            self.motores.potencia_motores(potencia2, potencia1)
        elif modo == Robo.ModoMotor.VELOCIDADE:
            self.motores.velocidade_motores(potencia2, potencia1)

        sleep(0.025)

    def seguir_linha_simples_distancia(
        self,
        distancia: int,
        velocidade: int = VELOCIDADE_PADRAO,
        direcao: int = DirecaoSeguirLinhaSimples.NORTE,
        sensor: int = Robo.SENSOR_COR_CENTRO,
        modo: int = Robo.ModoMotor.POTENCIA,
        parar_ao_final: bool = True,
    ):
        if distancia <= 0:
            return
        graus = distancia * self.DISTANCIA_PARA_GRAUS

        angulo_motor_inicial = self.motores.angulo_motor(self.MOTOR_DIREITO)
        angulo_motor = angulo_motor_inicial
        while angulo_motor_inicial - graus < angulo_motor < angulo_motor_inicial + graus:
            angulo_motor = self.motores.angulo_motor(self.MOTOR_DIREITO)

            self.seguir_linha_simples(
                sensor,
                velocidade=velocidade,
                direcao=direcao,
                modo=modo,
            )
        if parar_ao_final:
            self.pare()

    def seguir_linha_simples_e_analisar_cor(  # noqa
        self,
        funcao_cor: Callable[[tuple[int, int, int, int]], bool],
        indice_sensor: int = Robo.SENSOR_COR_CENTRO,
        dados_alinhamento: tuple[int, int] = ValorAlinhamentoSeguidor.VERDE_AMARELO,
        *,
        velocidade: int = VELOCIDADE_PADRAO,
        direcao: int = DirecaoSeguirLinhaSimples.NORTE,
        modo=Robo.ModoMotor.POTENCIA,
    ) -> bool:
        valor_cor_esquerdo = self.sensor_de_linha.le_hsv(self.SENSOR_COR_ESQUERDO)
        valor_cor_centro = self.sensor_de_linha.le_hsv(self.SENSOR_COR_CENTRO)
        valor_cor_direito = self.sensor_de_linha.le_hsv(self.SENSOR_COR_DIREITO)

        if funcao_cor(valor_cor_esquerdo) or funcao_cor(valor_cor_centro) or funcao_cor(valor_cor_direito):
            print(
                f'Seguir linha simples e analisar cor: cor encontrada! {valor_cor_esquerdo} {valor_cor_centro} {valor_cor_direito}'
            )
            self.pare()
            return True

        self.seguir_linha_simples(
            indice_sensor, dados_alinhamento, velocidade=velocidade, direcao=direcao, modo=modo
        )

        return False

    def alinhe_parado_simples(
        self,
        indice_sensor: int = Robo.SENSOR_COR_CENTRO,
        dados_alinhamento: tuple[int, int] = ValorAlinhamentoSeguidor.VERDE_AMARELO,
        direcao=DirecaoSeguirLinhaSimples.NORTE,
        tempo=0.8,
    ):
        tempo_inicial = time.time()
        while time.time() - tempo_inicial < tempo:
            self.seguir_linha_simples(
                velocidade=0,
                indice_sensor=indice_sensor,
                dados_alinhamento=dados_alinhamento,
                modo=Robo.ModoMotor.VELOCIDADE,
                direcao=direcao,
            )
            sleep(0.02)

        self.pare()

    def alinhe_se_mexendo_simples(
        self,
        indice_sensor: int = Robo.SENSOR_COR_CENTRO,
        dados_alinhamento: tuple[int, int] = ValorAlinhamentoSeguidor.VERDE_AMARELO,
        tempo: float = 0.8,
        distancia_entre_alinhamentos: float = 50,
        direcao: int = DirecaoSeguirLinhaSimples.NORTE,
    ):
        self.alinhe_parado_simples(
            indice_sensor=indice_sensor, dados_alinhamento=dados_alinhamento, tempo=tempo, direcao=direcao
        )
        self.ande_certa_distancia(distancia_entre_alinhamentos, velocidade=VELOCIDADE_BAIXA)
        self.alinhe_parado_simples(
            indice_sensor=indice_sensor, dados_alinhamento=dados_alinhamento, tempo=tempo, direcao=direcao
        )
        self.ande_certa_distancia(distancia_entre_alinhamentos * 1.8, velocidade=-VELOCIDADE_BAIXA)

    # ==========================================================
    # AÇÕES COMPLEXAS / INTERAÇÃO COM GARRA
    # ==========================================================

    def pegar_bloco(self, posicoes_lixeiras: list[tuple[int, int]], distancia: int = 40) -> Cores | None:
        """
        Executa a sequência completa para pegar um bloco, identificar sua cor
        e validar se deve ser mantido.

        O processo inclui:
        1. Posicionamento do robô na encruzilhada
        2. Ajuste de posição para alcançar o bloco
        3. Operação da garra para pegar o bloco
        4. Identificação da cor do bloco
        5. Decisão de manter ou soltar o bloco com base na cor
        """
        self.garra.fechar_porta()
        self.garra.abrir()

        self.voltar_encruzilhada(velocidade=VELOCIDADE_BAIXA)
        self.ande_certa_distancia(20, velocidade=VELOCIDADE_BAIXA)
        self.seguir_linha_distancia(
            70,
            velocidade=VELOCIDADE_BAIXA // 2,
            modo=Robo.ModoMotor.VELOCIDADE,
            kp=0.2,
            kd=0.2,
        )

        self.voltar_encruzilhada(velocidade=VELOCIDADE_BAIXA)
        self.garra.abaixar_parcial_pegar()
        self.gire_graus(5, velocidade=5)  # Pequeno ajuste para alinhar com o bloco
        self.ande_certa_distancia(distancia, velocidade=VELOCIDADE_BAIXA)

        self.garra.pegar_bloco()
        sleep(1)

        # Primeira verificação da cor do bloco
        cor = self.garra.ler_cor_bloco()
        self.tela_teclado.escreve_cor(cor)

        if cor is None or cor not in posicoes_lixeiras:
            sleep(1)
            cor = self.garra.ler_cor_bloco()
            self.tela_teclado.escreve_cor(cor)

        if cor == Cores.BRANCO or cor is None or cor not in posicoes_lixeiras:
            # Se a cor não for válida, solta o bloco e recua
            self.garra.abrir(tempo=0.2)
            self.ande_certa_distancia(10, velocidade=-VELOCIDADE_BAIXA)
            self.garra.subir(tempo=0.2)
            return cor

        # Levanta a garra e faz uma segunda verificação da cor
        self.garra.subir()
        sleep(0.5)
        cor = self.garra.ler_cor_bloco()
        self.tela_teclado.escreve_cor(cor)
        if cor == Cores.BRANCO or cor is None or cor not in posicoes_lixeiras:
            # Se a cor não for válida após a segunda verificação, solta o bloco e recua
            self.ande_certa_distancia(20, velocidade=-VELOCIDADE_BAIXA)
            self.garra.abaixar_total(tempo=0.5)
            self.garra.abrir(tempo=0.5)
            self.ande_certa_distancia(20, velocidade=-VELOCIDADE_BAIXA)
            self.garra.subir()

        return cor

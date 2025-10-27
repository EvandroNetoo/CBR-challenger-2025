"""Implementa a estratégia para navegação e operação do robô na área verde do mapa.

Este módulo contém a implementação da estratégia para a área verde, que inclui:
- Localização e mapeamento de lixeiras
- Navegação entre o mapa principal e a área de lixeiras
- Depósito de blocos nas lixeiras corretas

A estratégia coordena o comportamento do robô para cumprir a tarefa de coleta
e descarte seletivo de blocos nas lixeiras correspondentes.
"""

from time import sleep, time

from libs.vl53 import VL53L0X
from settings import DEPOSITAR_DE_FRENTE, VELOCIDADE_BAIXA, VELOCIDADE_MAXIMA, VELOCIDADE_PADRAO
from src.atuadores.robo.seguidor_linha import DirecaoSeguirLinhaSimples, RoboSeguidorDeLinha
from src.definicao_cores import Cores, DefinicaoCoresLinha, DefinicaoCoresLixeira, ValorAlinhamentoSeguidor
from src.estrategias.estrategia_mapa import EstrategiaMapa


class EstrategiaAreaVerde(EstrategiaMapa):
    """Implementa a estratégia para navegação e operação do robô na área verde do mapa.

    Esta classe estende a estratégia base de mapa para adicionar funcionalidades específicas
    da área verde, como a localização das lixeiras, identificação das cores de cada lixeira,
    e depósito dos blocos nas lixeiras correspondentes de acordo com sua cor.

    A estratégia coordena toda a navegação entre o mapa principal e a área verde,
    mantendo controle sobre os blocos coletados e as posições das lixeiras.
    """

    def __init__(self, robo, mapa):
        super().__init__(robo, mapa)

    def iniciar(self):
        """Inicia a execução da estratégia para a área verde.

        O processo completo inclui:
        1. Localização do amarelo no início do percurso
        2. Posicionamento na área de lixeiras
        3. Análise e mapeamento das lixeiras disponíveis
        4. Retorno à posição inicial no mapa (0,0)
        5. Ciclo contínuo de:
           - Coleta de blocos (executado pela estratégia base)
           - Navegação até a área verde
           - Depósito do bloco na lixeira correta
           - Retorno ao mapa principal

        Este método executa continuamente até a finalização do programa.
        """
        # Fase inicial - mapeamento da área verde
        self.encontre_amarelo_inicio(velocidade=VELOCIDADE_MAXIMA)

        # Se ainda não temos as posições das lixeiras, fazemos o mapeamento
        if not self.posicoes_lixeiras:
            self.posicionar_posicao_lixeira(velocidade=VELOCIDADE_BAIXA, velocidade_max=VELOCIDADE_MAXIMA)
            self.analisar_lixeiras(velocidade=VELOCIDADE_PADRAO)
        else:
            self.ir_amarelo_ao_vermelho(
                velocidade=VELOCIDADE_BAIXA,
                velocidade_max=VELOCIDADE_MAXIMA,
                distancia=10,
            )

        self.retornar_para_0_0(velocidade=VELOCIDADE_PADRAO, giro_especial=True)

        # Ciclo principal - coletar e depositar blocos
        while True:
            cor_bloco_pego, aresta_saida = super().iniciar()

            self.ir_ao_amarelo(velocidade=VELOCIDADE_BAIXA)
            self.robo.alinhe_entre_linhas(ValorAlinhamentoSeguidor.VERDE_AMARELO, velocidade=VELOCIDADE_BAIXA)

            if DEPOSITAR_DE_FRENTE and self.deposita_de_frente(
                cor=cor_bloco_pego,
                aresta_saida=aresta_saida,
                velocidade=VELOCIDADE_PADRAO,
            ):
                self.andar_ate_mapa(cor_bloco_pego=cor_bloco_pego, velocidade=VELOCIDADE_MAXIMA)

            else:
                self.posicionar_e_depositar_lixo(
                    cor=cor_bloco_pego,
                    aresta_saida=aresta_saida,
                    velocidade=VELOCIDADE_PADRAO,
                )

                self.retornar_para_mapa(cor_bloco_pego=cor_bloco_pego, velocidade=VELOCIDADE_PADRAO)

    # ==========================================================================
    # MÉTODOS DE NAVEGAÇÃO PRIMÁRIA
    # ==========================================================================

    def encontre_amarelo_inicio(self, *, velocidade: int = VELOCIDADE_PADRAO):
        """Procura a cor amarela no inicio do mapa."""
        while True:
            self.robo.ande_reto(velocidade, modo=self.robo.ModoMotor.VELOCIDADE)
            vermelho, azul, amarelo = DefinicaoCoresLinha.e_vermelho_ou_azul_ou_amarelo(
                self.robo.sensor_de_linha.le_hsv(self.robo.SENSOR_COR_ESQUERDO)
            )
            vermelho2, azul2, amarelo2 = DefinicaoCoresLinha.e_vermelho_ou_azul_ou_amarelo(
                self.robo.sensor_de_linha.le_hsv(self.robo.SENSOR_COR_CENTRO)
            )
            vermelho3, azul3, amarelo3 = DefinicaoCoresLinha.e_vermelho_ou_azul_ou_amarelo(
                self.robo.sensor_de_linha.le_hsv(self.robo.SENSOR_COR_DIREITO)
            )

            if amarelo or amarelo2 or amarelo3:
                self.robo.alinhe_entre_linhas(
                    ValorAlinhamentoSeguidor.VERDE_AMARELO, velocidade=VELOCIDADE_BAIXA
                )
                break

            if any((vermelho, vermelho2, vermelho3, azul, azul2, azul3)):
                self.robo.pare()
                self.robo.ande_certa_distancia(80, velocidade=-velocidade)
                self.robo.gire_graus(90, velocidade=velocidade)

    def ir_ao_amarelo(self, *, velocidade: int = VELOCIDADE_PADRAO):
        """Vai do azul ao amarelo na área verde."""
        self.robo.seguir_linha_ate_cor(
            DefinicaoCoresLinha.e_verde,
            velocidade=velocidade,
            modo=self.robo.ModoMotor.VELOCIDADE,
        )
        self.robo.ande_ate_cor(DefinicaoCoresLinha.e_amarelo, velocidade=VELOCIDADE_MAXIMA)

    def ir_amarelo_ao_vermelho(
        self,
        *,
        velocidade: int = VELOCIDADE_PADRAO,
        velocidade_max: int | None = None,
        distancia: int = 55,
        step: float = 0.5,
        direcao: int = DirecaoSeguirLinhaSimples.NORTE,
        indice_sensor: int = RoboSeguidorDeLinha.SENSOR_COR_ESQUERDO,
    ):
        self.robo.ande_certa_distancia(distancia, velocidade=velocidade)
        self.robo.gire_graus(90 * direcao, velocidade=VELOCIDADE_MAXIMA)
        if direcao == DirecaoSeguirLinhaSimples.NORTE:
            self.robo.alinhe_se_mexendo_simples(indice_sensor=indice_sensor, direcao=direcao)

        while not (
            self.robo.seguir_linha_simples_e_analisar_cor(
                DefinicaoCoresLinha.e_vermelho,
                indice_sensor=indice_sensor,
                direcao=direcao,
                velocidade=velocidade,
                modo=RoboSeguidorDeLinha.ModoMotor.VELOCIDADE,  # aaa
            )
        ):
            if velocidade_max:
                velocidade = min(velocidade + step, velocidade_max)
                step += 0.05

    def posicionar_posicao_lixeira(
        self,
        *,
        velocidade: int = VELOCIDADE_PADRAO,
        velocidade_max: int | None = None,
        step: float = 0.5,
    ):
        self.ir_amarelo_ao_vermelho(
            velocidade=velocidade,
            velocidade_max=velocidade_max,
            step=step,
            direcao=DirecaoSeguirLinhaSimples.SUL,
            distancia=35,
        )

        self.robo.gire_graus_giroscopio(180, velocidade=VELOCIDADE_MAXIMA)
        self.robo.alinhe_se_mexendo_simples(indice_sensor=self.robo.SENSOR_COR_DIREITO)

    def procurar_lixeira(
        self,
        index_lixeira: int,
        direcao: int = DirecaoSeguirLinhaSimples.NORTE,
        *,
        distancia: float = float('inf'),
        velocidade: int = VELOCIDADE_PADRAO,
        velocidade_max: int | None = None,
        step: float = 0.5,
        modo=RoboSeguidorDeLinha.ModoMotor.POTENCIA,
        indice_sensor_cor: int,
        tempo_ultima_lixeira_lido: float = 0,
        seguir_ate_deixar_de_ver: bool = False,
        parar_suave: bool = True,
        procurar_vermelho: bool = True,
    ) -> tuple[bool, bool]:
        """
        Move o robô até a lixeira de índice especificado, usando o sensor de distância esquerdo.
        O robô avança pela linha e conta as lixeiras detectadas pela proximidade.
        retorna uma tupla (bool, bool) onde o primeiro valor indica se a lixeira foi encontrada
        e o segundo valor indica se houve detecção de vermelho.
        """
        DISTANCIA_MAXIMA_LIXEIRA = 100
        QTD_LEITURAS_PARA_CONFIRMAR = 3
        TEMPO_MIN_ENTRE_LIXEIRAS = 0.1
        graus_maximo_entre_lixeira = distancia * self.robo.DISTANCIA_PARA_GRAUS

        index_atual = 0
        lixeira_detectada = False

        sensor_distancia = (
            self.robo.sensor_distancia_esquerdo
            if direcao == DirecaoSeguirLinhaSimples.NORTE
            else self.robo.sensor_distancia_direito
        )

        # usado para tentar resolver o problema de lixeira errada ao depostirar
        entrou = False if tempo_ultima_lixeira_lido == 0 else True

        # usado para seguir linha até deixar de ver a lixeira
        compara = (lambda x, y: x > y) if seguir_ate_deixar_de_ver else (lambda x, y: x < y)

        angulo_motor_inicial = self.robo.motores.angulo_motor(self.robo.MOTOR_DIREITO)
        while index_atual < index_lixeira:
            angulo_motor_atual = self.robo.motores.angulo_motor(self.robo.MOTOR_DIREITO)
            sensor_distancia.iniciar_thread()

            # if not parar_suave and index_atual + 1 == index_lixeira and direcao == DirecaoSeguirLinhaSimples.NORTE:
            #     velocidade = VELOCIDADE_BAIXA

            dentro_do_limite_de_graus = (
                angulo_motor_inicial - graus_maximo_entre_lixeira
                < angulo_motor_atual
                < angulo_motor_inicial + graus_maximo_entre_lixeira
            )

            if not dentro_do_limite_de_graus:
                self.robo.pare_suave()
                sensor_distancia.parar_thread()
                return False, False

            if compara(sensor_distancia.valor_distancia_thread, DISTANCIA_MAXIMA_LIXEIRA):
                tempo_desde_ultimo_cubo_lido = time() - tempo_ultima_lixeira_lido
                if (
                    not lixeira_detectada and tempo_desde_ultimo_cubo_lido > TEMPO_MIN_ENTRE_LIXEIRAS
                ) or not entrou:
                    entrou = True

                    if (
                        not parar_suave
                        and index_atual + 1 == index_lixeira
                        and direcao == DirecaoSeguirLinhaSimples.NORTE
                    ):
                        self.robo.pare()
                    else:
                        self.robo.pare_suave()

                    sensor_distancia.parar_thread()
                    confirmou = True
                    for _ in range(QTD_LEITURAS_PARA_CONFIRMAR):
                        if not compara(
                            sensor_distancia.read_range_single_millimeters(),
                            DISTANCIA_MAXIMA_LIXEIRA,
                        ):
                            confirmou = False
                            angulo_motor_inicial = self.robo.motores.angulo_motor(self.robo.MOTOR_DIREITO)
                            break
                    if confirmou:
                        index_atual += 1
                        lixeira_detectada = True

                    sensor_distancia.iniciar_thread()

                tempo_ultima_lixeira_lido = time()
            else:
                lixeira_detectada = False

            if self.robo.seguir_linha_simples_e_analisar_cor(
                DefinicaoCoresLinha.e_vermelho,
                indice_sensor=indice_sensor_cor,
                velocidade=velocidade,
                direcao=direcao,
                modo=modo,
            ):
                if procurar_vermelho:
                    self.robo.pare()
                    sensor_distancia.parar_thread()
                    return False, True
                else:
                    self.robo.ande_certa_distancia(20, velocidade=VELOCIDADE_BAIXA)

            if velocidade_max:
                velocidade = min(velocidade + step, velocidade_max)
                step += 0.05

        if not parar_suave and direcao == DirecaoSeguirLinhaSimples.NORTE:
            self.robo.pare()
        else:
            self.robo.pare_suave()

        sensor_distancia.parar_thread()
        return True, False

    # ==========================================================================
    # MÉTODOS DE ANÁLISE DE LIXEIRAS
    # ==========================================================================

    def _erro_durante_analise_lixeiras(self, velocidade=VELOCIDADE_PADRAO):
        """Executa uma rotina de correção quando ocorre um erro durante a análise das lixeiras."""
        self.posicoes_lixeiras = []

        self.robo.gire_graus_giroscopio(180, velocidade=VELOCIDADE_MAXIMA)

        velocidade_linha = VELOCIDADE_BAIXA
        while not (
            self.robo.seguir_linha_simples_e_analisar_cor(
                DefinicaoCoresLinha.e_vermelho,
                indice_sensor=self.robo.SENSOR_COR_ESQUERDO,
                velocidade=velocidade_linha,
                direcao=DirecaoSeguirLinhaSimples.SUL,
                modo=RoboSeguidorDeLinha.ModoMotor.VELOCIDADE,
            )
        ):
            velocidade_linha = min(velocidade_linha + 0.5, velocidade)

        self.robo.gire_graus_giroscopio(-180, velocidade=VELOCIDADE_MAXIMA)

        self.robo.alinhe_se_mexendo_simples(indice_sensor=self.robo.SENSOR_COR_DIREITO)

    def analisar_lista_lixeiras(self) -> bool:
        """Verifica se a lista de lixeiras está completa e correta."""
        if None in self.posicoes_lixeiras:
            return False

        if len(self.posicoes_lixeiras) > 5 or len(self.posicoes_lixeiras) == 0:
            return False

        # Filtra as cores vazias e verifica se existem cores repetidas
        filtrado = list(filter(lambda x: x != Cores.VAZIO, self.posicoes_lixeiras))
        if len(set(filtrado)) < len(filtrado):
            return False

        return True

    def analisar_lixeiras(self, *, velocidade: int = VELOCIDADE_PADRAO):
        """Analisa as lixeiras presentes na área verde e armazena suas cores."""
        tempo_ultimo_cubo_lido = 0
        qtd_erros = 0
        QTD_MAX_ERROS = 5
        velocidade_inicial = VELOCIDADE_BAIXA
        while qtd_erros < QTD_MAX_ERROS:
            print(f'Posições Lixeiras: {self.posicoes_lixeiras}')

            encontrou_lixeira, encontrou_vermelho = self.procurar_lixeira(
                1,
                velocidade=velocidade_inicial,
                velocidade_max=velocidade,
                tempo_ultima_lixeira_lido=tempo_ultimo_cubo_lido,
                indice_sensor_cor=self.robo.SENSOR_COR_DIREITO,
                distancia=270,
                step=0,
            )

            print(f'Encontrei lixeira: {encontrou_lixeira}, encontrei vermelho: {encontrou_vermelho}')

            velocidade_inicial = velocidade

            if encontrou_vermelho:
                if self.analisar_lista_lixeiras():
                    break

                qtd_erros += 1
                if qtd_erros >= QTD_MAX_ERROS:
                    break
                self._erro_durante_analise_lixeiras(velocidade=VELOCIDADE_MAXIMA)
                velocidade_inicial = VELOCIDADE_BAIXA
                continue

            if not encontrou_lixeira:
                self.posicoes_lixeiras.append(Cores.VAZIO)
                continue

            # seguir um pouco para o posicionamento do sensor de cor em relação a lixeira
            self.robo.seguir_linha_simples_distancia(
                70,
                velocidade=velocidade,
                sensor=self.robo.SENSOR_COR_DIREITO,
                modo=self.robo.ModoMotor.VELOCIDADE,  # aaa
            )

            hsv = self.robo.sensor_cor_esquerdo.le_hsv()
            cor = DefinicaoCoresLixeira.cor(hsv)

            print(f'Cor da lixeira: {cor}, HSV: {hsv}')

            # Se não conseguiu identificar a cor, tenta novamente
            if cor is None or cor in self.posicoes_lixeiras:
                self.robo.seguir_linha_simples_distancia(
                    10,
                    velocidade=VELOCIDADE_BAIXA,
                    sensor=self.robo.SENSOR_COR_DIREITO,
                    modo=self.robo.ModoMotor.VELOCIDADE,
                )

                hsv = self.robo.sensor_cor_esquerdo.le_hsv()
                cor = DefinicaoCoresLixeira.cor(hsv)
                print(f'Cor da lixeira (segunda tentativa): {cor}, HSV: {hsv}')

            self.posicoes_lixeiras.append(cor)
            self.robo.tela_teclado.escreve_cor(cor)

            tempo_ultimo_cubo_lido = time()

        print('Posição Lixeiras final:', self.posicoes_lixeiras)

    # ==========================================================================
    # MÉTODOS DE MANIPULAÇÃO DE LIXEIRAS E BLOCOS
    # ==========================================================================

    def _calcular_indice_lixeira(self, cor: Cores, aresta_saida: int) -> tuple[int, int]:
        """
        Calcula o índice da lixeira e a direção para alcançá-la.
        """
        index_lixeira_reverso = self.posicoes_lixeiras[::-1].index(cor)
        index_lixeira = abs(index_lixeira_reverso - aresta_saida) + 1

        if DEPOSITAR_DE_FRENTE:
            comparacao = index_lixeira_reverso <= aresta_saida
        else:
            comparacao = index_lixeira_reverso < aresta_saida

        direcao = DirecaoSeguirLinhaSimples.NORTE if comparacao else DirecaoSeguirLinhaSimples.SUL

        # Ajusta o índice da lixeira considerando as lixeiras vazias
        if direcao == DirecaoSeguirLinhaSimples.NORTE:
            index_lixeira -= self.posicoes_lixeiras[
                abs(aresta_saida - 4) : self.posicoes_lixeiras.index(cor)
            ].count(Cores.VAZIO)
        else:
            index_lixeira -= self.posicoes_lixeiras[::-1][
                aresta_saida : self.posicoes_lixeiras[::-1].index(cor)
            ].count(Cores.VAZIO)

        print(f'Índice da lixeira calculado: {index_lixeira}, direção: {direcao}')
        return index_lixeira, direcao

    def _posicionar_para_busca(self, velocidade: int, direcao: int):
        """Posiciona o robô para iniciar a busca pela lixeira."""
        self.robo.ande_certa_distancia(20, velocidade=velocidade)
        self.robo.gire_graus_giroscopio(90 * direcao, velocidade=velocidade)
        self.robo.ande_certa_distancia(75, velocidade=-velocidade)

    def _buscar_lixeira_correta(
        self,
        cor: Cores,
        index_lixeira: int,
        direcao: int,
        velocidade: int,
        velocidade_max: int | None = None,
    ) -> int:
        lista_sem_vazio = list(filter(lambda x: x != Cores.VAZIO, self.posicoes_lixeiras))

        while True:
            _, encontrou_vermelho = self.procurar_lixeira(
                index_lixeira,
                direcao=direcao,
                velocidade=VELOCIDADE_BAIXA,
                velocidade_max=velocidade_max,
                step=0.3,
                indice_sensor_cor=self.robo.SENSOR_COR_CENTRO,
                modo=self.robo.ModoMotor.VELOCIDADE,  # aaa
                parar_suave=False,
            )

            if encontrou_vermelho:
                self.robo.gire_graus(180 * direcao, velocidade=VELOCIDADE_MAXIMA)
                self.robo.ande_certa_distancia(30, velocidade=-velocidade)
                direcao *= -1
                index_lixeira = lista_sem_vazio[::direcao].index(cor) + 1
                print(f'Índice da lixeira corrigido: {index_lixeira}')
                continue
            break

        return direcao

    def _ajustar_posicao_sul(self, direcao: int, velocidade: int) -> int:
        """
        Ajusta a posição quando a direção é sul.
        """
        if direcao != DirecaoSeguirLinhaSimples.SUL:
            return direcao

        encontrou_lixeira, encontrou_vermelho = self.procurar_lixeira(
            2,
            direcao=direcao,
            velocidade=velocidade,
            velocidade_max=VELOCIDADE_MAXIMA,
            indice_sensor_cor=self.robo.SENSOR_COR_CENTRO,
            modo=self.robo.ModoMotor.VELOCIDADE,  # aaa
            distancia=300,
        )
        if not encontrou_vermelho:
            sleep(0.1)
            self.robo.seguir_linha_simples_distancia(
                90,
                velocidade=VELOCIDADE_PADRAO,
                direcao=direcao,
                sensor=self.robo.SENSOR_COR_CENTRO,
                modo=self.robo.ModoMotor.VELOCIDADE,  # aaa
            )

        sleep(0.1)

        self.robo.gire_graus_giroscopio(180, velocidade=VELOCIDADE_MAXIMA)

        if encontrou_vermelho:
            self.robo.alinhe_se_mexendo_simples(indice_sensor=self.robo.SENSOR_COR_CENTRO)
        else:
            self.robo.ande_certa_distancia(20, velocidade=-VELOCIDADE_BAIXA)

        direcao = DirecaoSeguirLinhaSimples.NORTE

        index_lixeira = 2 if encontrou_lixeira else 1

        print(f'Índice da lixeira após ajuste sul: {index_lixeira}')

        self.procurar_lixeira(
            index_lixeira,
            direcao=direcao,
            velocidade=VELOCIDADE_BAIXA,
            # velocidade_max=velocidade if not encontrou_vermelho else None,
            velocidade_max=VELOCIDADE_PADRAO,
            indice_sensor_cor=self.robo.SENSOR_COR_CENTRO,
            modo=self.robo.ModoMotor.VELOCIDADE,  # aaa
            parar_suave=False,
            procurar_vermelho=False,
        )

        return direcao

    def _posicionar_e_depositar(
        self,
        cor: Cores,
        velocidade: int = VELOCIDADE_PADRAO,
    ):
        """Posiciona o robô e deposita o bloco na lixeira correspondente."""

        self.robo.pare()

        qtd_depositos = self.posicoes_lixeiras_depositadas[cor]

        # # --- Depósito normal ( 2ª vez) ---
        if qtd_depositos >= 1 or self.posicoes_lixeiras.index(cor) == 0:
            self.procurar_lixeira(
                1,
                velocidade=velocidade,
                indice_sensor_cor=self.robo.SENSOR_COR_CENTRO,
                modo=self.robo.ModoMotor.VELOCIDADE,  # aaa
                seguir_ate_deixar_de_ver=True,
                parar_suave=False,
            )

            distancias = [130, 90, 80]
            distancia = distancias[min(qtd_depositos, 2)]  # Limita a 80 na terceira vez

            self.robo.garra.abrir_e_abaixar_parcial_depositar()

            self.robo.ande_certa_distancia(distancia, velocidade=-velocidade)
        else:
            self.robo.ande_certa_distancia(10, velocidade=velocidade)

        self.robo.garra.depositar_bloco()

    def deposita_de_frente(
        self,
        cor: Cores,
        aresta_saida: int,
        velocidade: int = VELOCIDADE_PADRAO,
    ):
        qtd_depositos = self.posicoes_lixeiras_depositadas[cor]
        index_lixeira_lista = self.posicoes_lixeiras.index(cor)
        if qtd_depositos == 0 and abs(index_lixeira_lista - 4) == aresta_saida:
            giros = [12, 0, 0, 0, -12]
            self.robo.ande_certa_distancia(30, velocidade=VELOCIDADE_BAIXA)
            self.robo.gire_graus_giroscopio(giros[index_lixeira_lista], velocidade=VELOCIDADE_BAIXA)
            if index_lixeira_lista in (0, 4):
                self.robo.ande_certa_distancia(5, velocidade=VELOCIDADE_BAIXA)
            self.robo.garra.depositar_bloco(abrir_porta=False)

            self.posicoes_lixeiras_depositadas[cor] += 1

            self.robo.ande_certa_distancia(20, velocidade=-VELOCIDADE_BAIXA)
            self.robo.alinhe_entre_linhas(ValorAlinhamentoSeguidor.VERDE_AMARELO, velocidade=VELOCIDADE_BAIXA)
            self.robo.gire_graus_giroscopio(175, velocidade=velocidade)
            return True

        return False

    def posicionar_e_depositar_lixo(
        self,
        cor: Cores,
        aresta_saida: int,
        velocidade: int = VELOCIDADE_PADRAO,
    ):
        index_lixeira, direcao = self._calcular_indice_lixeira(cor, aresta_saida)

        self._posicionar_para_busca(velocidade=velocidade, direcao=direcao)
        direcao = self._buscar_lixeira_correta(
            cor,
            index_lixeira,
            direcao=direcao,
            velocidade=VELOCIDADE_BAIXA,
            velocidade_max=VELOCIDADE_MAXIMA,
        )

        velocidade = VELOCIDADE_BAIXA if index_lixeira == 1 else VELOCIDADE_MAXIMA
        direcao = self._ajustar_posicao_sul(direcao=direcao, velocidade=velocidade)
        self._posicionar_e_depositar(cor, velocidade=VELOCIDADE_BAIXA)

        self.posicoes_lixeiras_depositadas[cor] += 1

    # ==========================================================================
    # MÉTODOS DE NAVEGAÇÃO DE RETORNO
    # ==========================================================================

    def retornar_para_0_0(
        self,
        direcao: int = DirecaoSeguirLinhaSimples.NORTE,
        *,
        velocidade: int = VELOCIDADE_PADRAO,
        giro_especial: bool = False,
    ):
        """Retorna para a posicao 0,0 do mapa.
        Ele segue linha ate encontrar a cor vermelha,
        depois vira 90 graus a direita e segue linha ate encontrar a cor azul.
        """

        graus = 90
        if giro_especial:
            self.robo.gire_graus_giroscopio(-15 * direcao, velocidade=VELOCIDADE_BAIXA)
            self.robo.ande_certa_distancia(125, velocidade=-velocidade)
            graus = 107
        else:
            self.robo.ande_certa_distancia(105, velocidade=-velocidade)
        sleep(0.2)
        self.robo.gire_graus_giroscopio(graus * direcao, velocidade=velocidade)

        # AS VEZES NAO ACHAVA O AZUL, ENTAO TIREI ESSA PARTE
        # self.robo.ande_ate_cor(DefinicaoCoresLinha.e_azul, velocidade=velocidade)
        self.robo.ande_ate_deixar_de_ver_cor(DefinicaoCoresLinha.e_verde, velocidade=VELOCIDADE_MAXIMA)
        self.robo.ande_certa_distancia(30, velocidade=velocidade)
        self.robo.encontrar_linha_preta(velocidade=velocidade)
        self.robo.pare()
        sleep(0.1)

        self.robo.seguir_ate_encruzilhada(velocidade=velocidade, modo=self.robo.ModoMotor.VELOCIDADE)

        if direcao == DirecaoSeguirLinhaSimples.NORTE:
            self.pos_anterior = (0, -1)
            self.pos_atual = (0, 0)
        else:
            self.pos_anterior = (4, -1)
            self.pos_atual = (4, 0)

    def andar_ate_mapa(
        self,
        cor_bloco_pego: Cores = Cores.VAZIO,
        velocidade: int = VELOCIDADE_PADRAO,
    ):
        """Andar até a posição do mapa correspondente à cor do bloco pego."""
        posicao_atual = self.posicoes_lixeiras.index(cor_bloco_pego) + 1

        # Mapeia as posições possíveis para seus dados
        mapa_posicoes = {
            1: {'anterior': (4, -1), 'atual': (4, 0)},
            2: {'anterior': (3, -1), 'atual': (3, 0)},
            3: {'anterior': (2, -1), 'atual': (2, 0)},
            4: {'anterior': (1, -1), 'atual': (1, 0)},
        }

        # Busca o valor no dicionário ou usa padrão se >=5
        dados = mapa_posicoes.get(posicao_atual, {'anterior': (0, -1), 'atual': (0, 0)})

        self.robo.ande_ate_deixar_de_ver_cor(DefinicaoCoresLinha.e_verde, velocidade=VELOCIDADE_MAXIMA)
        sleep(0.1)
        self.robo.ande_certa_distancia(20, velocidade=VELOCIDADE_BAIXA)
        self.robo.encontrar_linha_preta(velocidade=VELOCIDADE_PADRAO)

        self.robo.seguir_ate_encruzilhada(
            velocidade=VELOCIDADE_BAIXA, modo=self.robo.ModoMotor.VELOCIDADE, tempo_minimo=0.2
        )

        self.pos_anterior = dados['anterior']
        self.pos_atual = dados['atual']

    def retornar_para_mapa(
        self,
        velocidade: int = VELOCIDADE_PADRAO,
        cor_bloco_pego: Cores = Cores.VAZIO,
    ):
        """Retorna para a posicao 0,0 do mapa.
        Ele segue linha ate encontrar a cor vermelha,
        depois vira 90 graus a direita e segue linha ate encontrar a cor azul.
        """
        posicao_atual = self.posicoes_lixeiras.index(cor_bloco_pego) + 1

        # Mapeia as posições possíveis para seus dados
        distancia_de_recuo = {
            1: {'dist': 160},
            2: {'dist': 130},
            3: {'dist': 70},
            4: {'dist': 30},
        }

        # Busca o valor no dicionário ou usa padrão se >=5
        dados = distancia_de_recuo.get(posicao_atual, {'dist': 0})

        distancia_adicional = dados['dist']

        fim_lixeira, viu_vermelho = self.procurar_lixeira(
            1,
            velocidade=VELOCIDADE_BAIXA,
            indice_sensor_cor=self.robo.SENSOR_COR_CENTRO,
            modo=self.robo.ModoMotor.VELOCIDADE,
            distancia=250,
            seguir_ate_deixar_de_ver=True,
            parar_suave=False,
        )

        sleep(0.1)

        if not fim_lixeira:
            if not viu_vermelho:
                while not self.robo.seguir_linha_simples_e_analisar_cor(
                    funcao_cor=DefinicaoCoresLinha.e_vermelho,
                    indice_sensor=self.robo.SENSOR_COR_CENTRO,
                    velocidade=velocidade,
                ):
                    pass

            self.retornar_para_0_0(velocidade=velocidade)
            return

        self.robo.ande_certa_distancia(distancia_adicional, velocidade=-velocidade)
        sleep(0.1)
        self.robo.gire_graus_giroscopio(90, velocidade=VELOCIDADE_PADRAO)

        self.andar_ate_mapa(cor_bloco_pego=cor_bloco_pego, velocidade=VELOCIDADE_MAXIMA)

    def recuar_ate_fim_lixeira(
        self, velocidade=-VELOCIDADE_PADRAO, sensor=VL53L0X, modo=RoboSeguidorDeLinha.ModoMotor.VELOCIDADE
    ):
        """Recua até que o sensor de distância esquerdo não detecte mais a lixeira ao lado."""
        DISTANCIA_SEM_LIXEIRA = 170  # mm
        QUANTIDADE_CONFIRMACOES = 3

        print('[recuar_ate_fim_lixeira] Iniciando recuo até o fim da lixeira...')
        while True:
            self.robo.ande_reto(-abs(velocidade), modo=modo)
            distancia = sensor.read_range_single_millimeters()
            print(f'[recuar_ate_fim_lixeira] Distância lida: {distancia} mm')
            if distancia > DISTANCIA_SEM_LIXEIRA:
                print('[recuar_ate_fim_lixeira] Possível fim da lixeira detectado, confirmando...')
                self.robo.pare()
                confirmado = True
                for i in range(QUANTIDADE_CONFIRMACOES):
                    sleep(0.05)
                    distancia_conf = sensor.read_range_single_millimeters()
                    print(f'[recuar_ate_fim_lixeira] Confirmação {i + 1}: {distancia_conf} mm')
                    if distancia_conf < DISTANCIA_SEM_LIXEIRA:
                        confirmado = False
                        print('[recuar_ate_fim_lixeira] Lixeira ainda detectada, continuando recuo.')
                        break
                if confirmado:
                    print('[recuar_ate_fim_lixeira] Fim da lixeira confirmado.')
                    break
            # Pequeno delay para evitar leituras muito rápidas
            sleep(0.02)
        self.robo.pare()
        print('[recuar_ate_fim_lixeira] Recuo finalizado.')

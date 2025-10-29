# CBR Challenge 2025 - Equipe Titans da Robótica

![CBR 2025](https://img.shields.io/badge/CBR-2025-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-green)

## 🏆 Campeão CBR 2025 - Categoria Challenge

Este repositório contém o código-fonte desenvolvido pela **Equipe Titãs da Robótica (IFES Colatina)**, campeã da **Competição Brasileira de Robótica (CBR) 2025** na categoria Challenge.

A equipe decidiu disponibilizar o código para compartilhar conhecimento e ajudar outras equipes a desenvolverem suas soluções.

## 👥 Equipe

- **[@evandronetoo](https://github.com/evandronetoo)** - Desenvolvedor
- **[@JoelHanerth](https://github.com/JoelHanerth)** - Desenvolvedor
- **Elis Moraes** - Montadora
- **[@juliovendramini](https://github.com/juliovendramini)** - Professor Orientador

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Requisitos](#requisitos)
- [Estrutura do Código](#estrutura-do-código)
- [Arquitetura](#arquitetura)
- [Classes Principais](#classes-principais)
- [Estratégias](#estratégias)
- [Sensores e Atuadores](#sensores-e-atuadores)
- [Como Usar](#como-usar)
- [Configurações](#configurações)
- [Bibliotecas](#bibliotecas)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O desafio da categoria Challenge consiste em um robô autônomo que deve:

1. **Navegar pelo mapa principal** explorando um ambiente de 5x6 nós conectados por linhas pretas
2. **Detectar e coletar blocos coloridos** dispersos pelo mapa
3. **Identificar a cor dos blocos** usando sensores de cor
4. **Navegar até a área verde** (zona das lixeiras)
5. **Depositar os blocos nas lixeiras correspondentes** baseado na cor do bloco

### Principais Desafios Técnicos

- **Mapeamento dinâmico**: O robô cria um mapa do ambiente usando sensores de distância
- **Seguimento de linha com PID**: Controle proporcional-derivativo para seguimento preciso
- **Detecção de cores**: Identificação confiável de cores em diferentes condições de iluminação
- **Planejamento de rotas**: Algoritmo de Dijkstra para caminhos mais curtos
- **Localização**: Sistema de posicionamento baseado em odometria e giroscópio

## ⚙️ Sobre nosso robô

- **Hardware**: Brick [MariolaZero](https://github.com/juliovendramini/MariolaZero/) 
- **Python**: 3.11 ou superior
- **Sistema Operacional**: Linux (recomendado para o EV3)

### Sensores Utilizados

- 1x Sensor de seguir linha (4x sensores de reflexão e 3x TCS34725 para identificação de cor)
- 2x Sensores de cor TCS34725 (garra e lateral)
- 3x Sensores de distância VL53L0X (esquerdo, direito e frontal)
- 1x Giroscópio

### Atuadores

- 2x Motores médios EV3 (movimentação)
- 3x Servo motores (garra, alavanca e porta)

## 📁 Estrutura do Código

```
cbr/
├── main.py                          # Ponto de entrada do programa
├── settings.py                      # Configurações globais (velocidades, portas, etc)
├── mapa.py                          # Representação do mapa usando grafo
├── src/
│   ├── definicao_cores.py          # Definições e detecção de cores
│   ├── mapa.py                     # Classe do mapa com algoritmo de Dijkstra
│   ├── servico_web.py              # Visualização web do mapa (debug)
│   ├── atuadores/
│   │   ├── robo/
│   │   │   ├── __init__.py         # Classe base Robo
│   │   │   ├── seguidor_linha.py  # Implementação do seguidor de linha
│   │   │   ├── garra.py            # Controle da garra
│   │   │   └── tela_teclado.py    # Interface com display e botões
│   │   └── interface_atuador.py   # Interface abstrata para atuadores
│   └── estrategias/
│       ├── estrategia_base.py      # Classe base para estratégias
│       ├── estrategia_mapa.py      # Estratégia para navegação no mapa
│       └── estrategia_area_verde.py # Estratégia para área das lixeiras
├── libs/                            # Bibliotecas de baixo nível (MariolaZero)
│   ├── motores.py                  # Controle dos motores EV3
│   ├── giroscopio.py               # Interface com giroscópio
│   ├── sensorCorReflexao.py       # Sensor de cor/reflexão EV3
│   ├── tcs34725.py                 # Sensor de cor RGB
│   ├── vl53.py                     # Sensor de distância
│   └── ...
└── testes/                          # Arquivos de teste e calibração
```

## 🏗️ Arquitetura

O projeto utiliza uma arquitetura baseada em **estratégias** e **camadas de abstração**:

```
┌─────────────────────────────────────┐
│     Estratégias (Alto Nível)        │
│  - EstrategiaAreaVerde              │
│  - EstrategiaMapa                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Atuadores (Camada Média)         │
│  - RoboSeguidorDeLinha              │
│  - Garra                            │
│  - Mapa                             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Bibliotecas (Baixo Nível)         │
│  - Motores, Sensores, I/O           │
│  (MariolaZero)                      │
└─────────────────────────────────────┘
```

## 🔧 Classes Principais

### `Robo` (cbr/src/atuadores/robo/**init**.py)

Classe base que encapsula o controle do robô físico.

**Responsabilidades:**

- Movimentação básica (andar reto, girar)
- Controle de motores e servos
- Leitura de sensores
- Funções auxiliares de navegação

**Métodos principais:**

- `ande_reto(velocidade, modo)`: Move o robô para frente/trás
- `gire_graus(graus, velocidade)`: Gira o robô usando encoders
- `gire_graus_giroscopio(graus, velocidade)`: Gira usando giroscópio (mais preciso)
- `ande_certa_distancia(distancia, velocidade)`: Move uma distância específica
- `encontrar_linha_preta(velocidade)`: Busca linha em padrão zigue-zague
- `ande_ate_cor(funcao_cor, velocidade)`: Move até detectar cor específica
- `alinhe_entre_linhas(dados_alinhamento)`: Alinha entre duas cores

**Constantes importantes:**

```python
DISTANCIA_PARA_GRAUS = 800 / 300 * 1.6  # Conversão mm -> graus do encoder
MOTOR_DIREITO = 1
MOTOR_ESQUERDO = 2
SENSOR_COR_ESQUERDO = 1
SENSOR_COR_CENTRO = 2
SENSOR_COR_DIREITO = 3
```

### `RoboSeguidorDeLinha` (cbr/src/atuadores/robo/seguidor_linha.py)

Estende `Robo` com capacidades de seguimento de linha usando controle PID.

**Controle PID:**

```python
erro = valor_sensor - valor_desejado
proporcional = erro * KP
derivativo = (erro - erro_anterior) * KD
correção = proporcional + derivativo
```

**Métodos principais:**

- `seguir_linha(velocidade, KP, KD)`: Segue linha usando 4 sensores
- `seguir_linha_distancia(distancia)`: Segue por distância específica
- `seguir_ate_encruzilhada(velocidade)`: Segue até encontrar cruzamento
- `seguir_linha_ate_cor(funcao_cor)`: Segue até detectar cor
- `seguir_linha_simples(indice_sensor)`: Segue usando um único sensor
- `pegar_bloco(posicoes_lixeiras, distancia)`: Sequência completa de coleta

**Parâmetros de tuning:**

```python
KP_PADRAO = 0.5      # Ganho proporcional (resposta ao erro)
KD_PADRAO = 0.5      # Ganho derivativo (suavização)
KP_SIMPLES = 0.7     # KP para seguidor simples
KD_SIMPLES = 0.7     # KD para seguidor simples
```

### `Garra` (cbr/src/atuadores/robo/garra.py)

Controla a garra para manipulação de blocos.

**Componentes:**

- Servo da garra (abertura/fechamento)
- Servo da alavanca (altura)
- Servo da porta (depósito)
- Sensor de cor (identificação)

**Métodos principais:**

- `pegar_bloco()`: Fecha a garra
- `depositar_bloco()`: Sequência de depósito
- `ler_cor_bloco()`: Identifica cor do bloco capturado
- `subir() / abaixar_total() / abaixar_parcial_pegar()`: Controle de altura

**Posições dos servos:**

```python
POSICAO_ALAVANCA_SUBIDA = 40°
POSICAO_ALAVANCA_DESCIDA_TOTAL = 170°
POSICAO_GARRA_FECHADA = 70°
POSICAO_GARRA_ABERTA = 180°
POSICAO_PORTA_ABERTA = 83°
```

### `Mapa` (cbr/src/mapa.py)

Representa o ambiente como um grafo usando NetworkX.

**Estrutura:**

- Grafo 2D de 5x6 nós (altura x largura)
- Arestas com conhecimento (VAZIO, BLOCO, DESCONHECIDA, BLOCO_BRANCO)
- Nó especial AREA_VERDE = (-1, -1)

**Tipos de conhecimento:**

```python
INICIO = {'peso': 50, 'cor': 'blue'}          # Conexão inicial
VAZIO = {'peso': 1, 'cor': 'green'}           # Caminho livre
DESCONHECIDA = {'peso': 2, 'cor': 'gray'}     # Não explorado
BLOCO = {'peso': None, 'cor': 'yellow'}       # Bloco presente
BLOCO_BRANCO = {'peso': None, 'cor': 'red'}   # Bloco inválido
```

**Métodos principais:**

- `dijkstra_multiplos_destinos(origem, destinos)`: Caminho mais curto
- `nos_com_bloco()`: Retorna nós com blocos detectados
- `nos_com_arestas_desconhecidas()`: Nós para exploração
- `caminho_saida(origem)`: Caminho para área verde
- `zerar()`: Reseta conhecimento do mapa

## 🎮 Estratégias

### `EstrategiaBase` (cbr/src/estrategias/estrategia_base.py)

Classe abstrata que define estrutura comum.

**Responsabilidades:**

- Classificação de distâncias dos sensores
- Cálculo de direções baseado em posições
- Atualização dinâmica do mapa
- Determinação do próximo movimento

**Classificação de distâncias:**

```python
NAO_ENCONTRADO = 0  # > 700mm
PERTO = 1           # ≤ 250mm (bloco adjacente)
MEDIO = 2           # 250-700mm (bloco a 1 nó de distância)
```

**Direções:**

```python
CIMA = 0      # Linha -1
DIREITA = 1   # Coluna +1
BAIXO = 2     # Linha +1
ESQUERDA = 3  # Coluna -1
```

**Métodos de navegação:**

- `atualizacao_dinamica_mapa()`: Atualiza grafo com leituras dos sensores
- `proximo_no()`: Decide próximo destino (bloco > desconhecido > área verde)
- `no_para_bloco_mais_proximo()`: Dijkstra para blocos
- `no_para_no_desconhecido_mais_proximo()`: Dijkstra para exploração

### `EstrategiaMapa` (cbr/src/estrategias/estrategia_mapa.py)

Estratégia para navegação e exploração do mapa principal.

**Fluxo de execução:**

```
1. Andar um pouco para centralizar na encruzilhada
2. Loop principal:
   a. Atualizar mapa com sensores
   b. Verificar blocos adjacentes
   c. Se houver bloco:
      - Girar para o bloco
      - Pegar bloco
      - Se cor válida: retornar à área verde
      - Se cor inválida: continuar explorando
   d. Se não houver bloco:
      - Calcular próximo nó (Dijkstra)
      - Rotacionar para o nó
      - Seguir até próxima encruzilhada
```

**Métodos principais:**

- `iniciar()`: Loop principal da estratégia
- `pegar_bloco()`: Tenta pegar bloco com ajuste de distância
- `rotacionar_para_no(proximo_no)`: Alinha robô com destino
- `seguir_ate_encruzilhada()`: Move e atualiza posição
- `girar_para_bloco_vizinho_se_houver()`: Detecta blocos próximos
- `retornar_para_area_verde()`: Navega até saída do mapa

### `EstrategiaAreaVerde` (cbr/src/estrategias/estrategia_area_verde.py)

Estratégia para área das lixeiras. Herda de `EstrategiaMapa`.

**Fases:**

**Fase 1 - Mapeamento (primeira execução):**

```
1. Encontrar linha amarela
2. Posicionar na área de lixeiras
3. Varrer linha vermelha detectando lixeiras
4. Para cada lixeira:
   - Detectar com sensor de distância
   - Posicionar sensor de cor
   - Identificar cor da lixeira
   - Armazenar em lista
5. Retornar para posição (0,0)
```

**Fase 2 - Ciclo de depósito:**

```
Loop:
   1. Executar EstrategiaMapa (coletar bloco)
   2. Ir até área verde (linha amarela)
   3. Calcular índice da lixeira correta
   4. Navegar até lixeira:
      - Seguir linha vermelha
      - Contar lixeiras com sensor de distância
   5. Posicionar e depositar bloco
   6. Retornar ao mapa principal
```

**Métodos de navegação:**

- `encontre_amarelo_inicio()`: Localiza entrada da área verde
- `ir_ao_amarelo()`: Navega do azul ao amarelo
- `ir_amarelo_ao_vermelho()`: Vai para linha das lixeiras
- `posicionar_posicao_lixeira()`: Alinha na linha vermelha

**Métodos de lixeiras:**

- `analisar_lixeiras()`: Mapeia cores de todas as lixeiras
- `procurar_lixeira(index, direcao)`: Navega contando lixeiras
- `posicionar_e_depositar_lixo(cor, aresta_saida)`: Sequência completa
- `_calcular_indice_lixeira(cor, aresta_saida)`: Determina posição e direção
- `deposita_de_frente(cor, aresta_saida)`: Deposita sem virar (otimização)

**Métodos de retorno:**

- `retornar_para_0_0()`: Volta para origem do mapa
- `retornar_para_mapa(cor_bloco_pego)`: Retorna otimizado baseado em posição
- `andar_ate_mapa(cor_bloco_pego)`: Atalho para coluna correta

**Lista de lixeiras:**

```python
posicoes_lixeiras = [Cores.VERDE, Cores.AZUL, Cores.VAZIO, Cores.AMARELO, Cores.VERMELHO]
# Índices:          [    0    ,      1   ,      2    ,       3     ,        4      ]
# Aresta saída:      4           3           2            1             0
```

## 🌈 Detecção de Cores

### `DefinicaoCoresLinha` (cbr/src/definicao_cores.py)

Detecta cores nas linhas do mapa usando valores HSV.

**Calibrações:**

```python
VERDE:    H: 35-55,  S: 25-60,  V: 30-55
AZUL:     H: 65-90,  S: 30-60,  V: 35-55
AMARELO:  H: 12-25,  S: 45-80,  V: 60-127
VERMELHO: H: 0-10 ou 110-127, S: 40-90, V: 55-95
PRETO:    V < 20
```

### `DefinicaoCoresLixeira`

Detecta cores das lixeiras (ranges mais amplos por iluminação variável).

### `DefinicaoCoresBloco`

Identifica cores dos blocos usando RGBC e HSV:

- BRANCO e PRETO: Baseado no canal Clear (C)
- Demais cores: Baseado em HSV

## ⚡ Sensores e Atuadores

### Sensores de Distância (VL53L0X)

Medem distância em milímetros (0-2000mm).

**Uso:**

```python
distancia_esq, distancia_frontal, distancia_dir = robo.sensores_laterais
```

**Classificação:**

- ≤ 250mm: Bloco adjacente
- 250-700mm: Bloco a 1 nó de distância
- \> 700mm: Caminho livre

### Sensores de Cor (TCS34725)

Retornam valores RGBC e HSV.

**Leitura:**

```python
rgbc = sensor.le_rgbc()  # (R, G, B, Clear)
rgb = sensor.rgbc_to_rgb255(rgbc)
hsv = sensor.rgb_to_hsv(rgb)
```

### Sensor de Reflexão (EV3)

4 sensores para seguimento de linha.

**Posições:**

```
[Extrema Esquerda] [Esquerda] [Direita] [Extrema Direita]
```

**Valores:** 0 (preto) - 100 (branco)

### Giroscópio

Fornece ângulo absoluto para giros precisos.

```python
angulo = giroscopio.le_angulo_z()  # 0-360°
```

## 🚀 Como Usar

### Executar o Programa Principal

```bash
cd cbr
python main.py
```

### Calibrar Sensores

Execute os scripts de calibração antes da competição:

```bash
# Calibrar sensor de cor da linha
python cbr/calibra_sensor_cor_esq.py

# Calibrar sensor de cor da garra
python cbr/calibra_sensor_cor_garra.py

# Calibrar branco e preto
python cbr/calibra_branco.py
python cbr/calibra_preto.py
```

### Testes Individuais

```bash
# Testar motores
python cbr/teste_motores.py

# Testar seguidor de linha
python cbr/teste_seguidor.py

# Testar garra
python cbr/teste_garra.py

# Testar sensores de distância
python cbr/teste_sensores_laterais.py

# Testar giroscópio
python cbr/teste_giroscopio.py
```

### Visualizar Mapa (Debug)

O código inclui um servidor web para visualizar o mapa em tempo real:

```bash
# Acesse no navegador: http://<IP_DO_EV3>:5000
```

O mapa mostra:

- Nós explorados (azul claro)
- Arestas conhecidas (verde = vazio, amarelo = bloco, vermelho = bloco branco)
- Posição atual do robô
- Arestas desconhecidas (cinza)

## ⚙️ Configurações

### `settings.py`

Arquivo central de configurações:

```python
# Debug
DEBUG = True  # Ativa servidor web de visualização

# Velocidades (0-100)
VELOCIDADE_PADRAO = 45
VELOCIDADE_BAIXA = 25
VELOCIDADE_BASE_SEGUIDOR = 60
VELOCIDADE_MAXIMA = 80

# Controle PID
KP_PADRAO = 0.5
KD_PADRAO = 0.5
KP_BAIXA_VELOCIDADE = 0.5
KD_BAIXA_VELOCIDADE = 0.2

# Detecção de encruzilhada
VALOR_ENCRUZILHADA = 50  # Média de reflexão para detectar cruzamento

# Portas dos sensores
PORTA_SENSOR_COR_LINHA = Portas.SERIAL5
PORTA_SENSOR_COR_ESQUERDO = Portas.I2C3

# Estratégia
DEPOSITAR_DE_FRENTE = False  # Otimização de depósito
```

### Ajustando Parâmetros

**Para ajustar o seguidor de linha:**

1. Teste em `teste_seguidor.py`
2. Ajuste `KP` para resposta ao erro (↑ mais agressivo)
3. Ajuste `KD` para suavização (↑ menos oscilações)

**Para ajustar velocidades:**

1. Comece com velocidades baixas
2. Aumente gradualmente até perder precisão
3. Use velocidades mais altas em trechos retos

**Para ajustar detecção de cores:**

1. Execute calibrações
2. Ajuste ranges em `definicao_cores.py`
3. Teste em diferentes iluminações

## 📚 Bibliotecas

### MariolaZero (libs/)

As bibliotecas na pasta `libs/` são um clone do repositório [MariolaZero](https://github.com/juliovendramini/MariolaZero/) desenvolvido por [@juliovendramini](https://github.com/juliovendramini).

Estas bibliotecas fornecem interfaces de baixo nível para:

- Controle de motores EV3
- Leitura de sensores I2C
- Comunicação serial
- Controle de servos
- Interface com giroscópio HiTechnic
- Multiplexadores de sensores

**Não é necessário documentar em detalhes estas bibliotecas**, pois são código de terceiros. Consulte o repositório original para mais informações.

### Dependências Externas

- **NetworkX**: Manipulação de grafos para o mapa
- **Matplotlib**: Visualização do mapa (debug)
- **Flask**: Servidor web para visualização (se DEBUG=True)

## 🎓 Conceitos e Algoritmos

### Algoritmo de Dijkstra

Usado para encontrar o caminho mais curto no mapa:

```python
caminho = mapa.dijkstra_multiplos_destinos(origem, [destino1, destino2, ...])
```

**Pesos das arestas:**

- VAZIO: 1 (preferido)
- DESCONHECIDA: 2 (explorar se necessário)
- BLOCO/BLOCO_BRANCO: None (bloqueado)
- INICIO: 50 (evitar retornar)

### Controle PID

Controlador Proporcional-Derivativo para seguimento:

```
correção = KP * erro + KD * (erro - erro_anterior)
velocidade_motor_direito = velocidade_base + correção
velocidade_motor_esquerdo = velocidade_base - correção
```

### Odometria

Rastreamento de posição baseado em encoders e giroscópio:

```python
distancia = graus_encoder / DISTANCIA_PARA_GRAUS
angulo = giroscopio.le_angulo_z()
```

### Máquina de Estados

A estratégia funciona como uma máquina de estados:

```
ESTADO_EXPLORAR → (bloco encontrado) → ESTADO_PEGAR_BLOCO
ESTADO_PEGAR_BLOCO → (cor válida) → ESTADO_RETORNAR_AREA_VERDE
ESTADO_RETORNAR_AREA_VERDE → ESTADO_DEPOSITAR
ESTADO_DEPOSITAR → ESTADO_EXPLORAR
```

## 🐛 Debugging

### Prints de Debug

O código inclui vários prints para debugging:

```python
print(f'Posição atual: {self.pos_atual}')
print(f'Cor pega: {cor_pega}')
print(f'Distâncias - Esq: {dist_esq}, Frontal: {dist_frontal}, Dir: {dist_dir}')
```

### Servidor Web

Com `DEBUG = True`, acesse `http://<IP_DO_EV3>:5000` para:

- Visualizar mapa em tempo real
- Ver posição atual do robô
- Acompanhar conhecimento do mapa

### Logs de Sensores

Use os testes individuais para verificar leituras:

```bash
python cbr/teste_sensor_cor_esq.py  # Monitora HSV em tempo real
python cbr/teste_sensores_laterais.py  # Monitora distâncias
```

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT. Sinta-se livre para usar, modificar e distribuir.

---

## 🎯 Dicas para Outras Equipes

### Começando do Zero

1. **Comece simples**: Teste primeiro o seguidor de linha básico
2. **Calibre bem**: Dedique tempo à calibração dos sensores
3. **Teste incremental**: Adicione funcionalidades uma de cada vez

### Otimizações Possíveis

- **Ajuste de PID**: Tune fino para sua pista específica
- **Velocidades adaptativas**: Reduzir em curvas, aumentar em retas
- **Cache de caminhos**: Memorizar rotas bem-sucedidas
- **Detecção de blocos brancos**: Evitar tentar pegar blocos inválidos repetidamente

### Armadilhas Comuns

1. **Iluminação**: Cores mudam drasticamente com iluminação diferente
2. **Bateria**: Velocidades e comportamento mudam com bateria baixa
3. **Encruzilhadas**: Detecção confiável é crítica
4. **Alinhamento**: Pequenos desalinhamentos acumulam ao longo do tempo

---

## 📞 Contato

Para dúvidas sobre o código, abra uma issue ou entre em contato com a equipe:

- **Evandro Neto** @evandronetoo evandro.rsneto@gmail.com
- **Joel Hanerth** @JoelHanerth hanerthjoel1@gmail.com
- **Equipe Titans da Robótica**
- **Professor Orientador**: Julio Vendramini

---

**Boa sorte na sua jornada na CBR! 🤖🏆**

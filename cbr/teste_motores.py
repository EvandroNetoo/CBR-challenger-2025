from libs.motores import Motores

motores = Motores(True)
motores.direcao_motor(1, motores.INVERTIDO)
motores.direcao_motor(2, motores.NORMAL)
motores.set_modo_freio(motores.HOLD)

velocidade = 50


while True:
    # motores.velocidade_motores(round(velocidade * 0.92), velocidade)
    # motores.velocidade_motores(velocidade, velocidade)
    motores.move_motores(velocidade, 1320, -velocidade, 1320)
    input('Pressione Enter para inverter')
    # print(motores.angulo_motor(1), motores.angulo_motor(2))

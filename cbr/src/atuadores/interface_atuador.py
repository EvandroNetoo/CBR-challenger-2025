from abc import ABC, abstractmethod
from typing import Tuple

from settings import VALOR_ENCRUZILHADA, VELOCIDADE_PADRAO


class InterfaceAtuador(ABC):
    @abstractmethod
    def ande_certa_distancia(self, distancia: int, *, velocidade: int = VELOCIDADE_PADRAO) -> None:
        pass

    @abstractmethod
    def gire_graus(self, graus: int, *, velocidade: int = VELOCIDADE_PADRAO) -> None:
        pass

    @abstractmethod
    def seguir_ate_encruzilhada(
        self,
        modo: int,
        velocidade: int = VELOCIDADE_PADRAO,
        tempo_minimo: int = 0,
        valor_encruzilhada: int = VALOR_ENCRUZILHADA,
        com_cubo: bool = False,
    ) -> bool:
        pass

    @abstractmethod
    def voltar_encruzilhada(self, *, velocidade: int = VELOCIDADE_PADRAO) -> None:
        pass

    @abstractmethod
    def gire_graus_giroscopio(self, graus: int, *, velocidade: int = VELOCIDADE_PADRAO) -> None:
        pass

    @property
    @abstractmethod
    def sensores_laterais(self) -> Tuple[int, int, int]:
        pass

    @abstractmethod
    def pegar_bloco(self, distancia: int, posicoes_lixeiras: list[tuple[int, int]]) -> bool:
        """Pega o bloco que está na frente do robô"""
        pass

    @abstractmethod
    def seguir_linha(self, *, velocidade: int, modo: int):
        pass

    @abstractmethod
    def pare(self) -> None:
        """Para todos os motores do robô"""
        pass

from abc import ABC, abstractmethod


class CalcInterfaceInconsistent(ABC):
    @abstractmethod
    def add(self, a, b) -> int:
        pass

    @abstractmethod
    def sub(self, a: int, b: int) -> int:
        pass

    @abstractmethod
    def mult(self, a: int, b: int) -> int:
        pass

    @abstractmethod
    def div(self, a: int, b: int) -> float:
        pass

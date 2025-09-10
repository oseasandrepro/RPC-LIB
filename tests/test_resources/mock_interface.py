from abc import ABC, abstractmethod


class MockInterface(ABC):
    @abstractmethod
    def add(self, a: int, b: int) -> int:
        pass

    @abstractmethod
    def sub(self, a: int, b: int) -> int:
        pass

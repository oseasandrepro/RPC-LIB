from abc import ABC, abstractmethod


class CalcinconsistentgenInterface(ABC):
    @abstractmethod
    def count_ones_in_int_list(self, list: list) -> int:
        pass

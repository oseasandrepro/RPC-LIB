from abc import ABC, abstractmethod


class CalcconsistentgenInterface(ABC):
    @abstractmethod
    def count_ones_in_int_list(self, list: list[int]) -> int:
        pass

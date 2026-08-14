from .calc_interface import CalcInterface


class Calc(CalcInterface):
    def add(self, a: int, b: int) -> int:
        return a + b

    def sub(self, a: int, b: int) -> int:
        return a - b

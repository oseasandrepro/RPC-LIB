from Calculadora_Interface import CalculadoraInterface

class Calculadora(CalculadoraInterface):
    def add(self, a, b):
        return a + b

    def mult(self, a, b):
        return a * b
    
    def div(self, a, b):
        return a/b
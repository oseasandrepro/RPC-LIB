from Rpc_Client_Stub import Calc_Stub


calc = Calc_Stub()
a = 5
b = 6
print(f"{a} + {b} = {calc.add(a,'5')}")
print(f"{a} * {b} = {calc.mult(a,b)}")
print(f"{a} / {b} = {calc.div(a,b)}")
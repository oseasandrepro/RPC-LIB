from calc_rpc_client_stub import calc_stub

calc = calc_stub()
a = 1
b = 3
print(f"{a} + {b} = {calc.add(a,b)}")
print(f"{a} * {b} = {calc.mult(a,b)}")
print(f"{a} / {b} = {calc.div(a,b)}")
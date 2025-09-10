from calc_rpc_client_stub import calc_stub

calc = calc_stub()
a = 4
b = 2
print(f"{calc.add(a,b)}")
print(f"{calc.mult(a,b)}")
print(f"{calc.sub(a,b)}")
print(f"{calc.div(a,b)}")

from srpc_calc_client_stub import SrpcCalcClientStub
calc = SrpcCalcClientStub()
a = 4
b = 2
print(f"{calc.add(a, b)}")
print(f"{calc.mult(a, b)}")
print(f"{calc.sub(a, b)}")
print(f"{calc.div(a, b)}")

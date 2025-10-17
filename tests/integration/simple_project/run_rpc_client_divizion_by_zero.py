from srpc_calc_client_stub import SrpcCalcClientStub

calc = SrpcCalcClientStub()
a = 4
try:
    print(calc.div(a, 0))
except ZeroDivisionError as e:
    print(f"ZeroDivisionError: {e}")

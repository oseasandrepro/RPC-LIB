from srpc_calc_client_stub import SrpcCalcClientStub

SERVER_HOST = "127.0.0.1"
calcStub = SrpcCalcClientStub(SERVER_HOST, 5000)
a = 4
try:
    print(calcStub.div(a, 0))
except ZeroDivisionError as e:
    print(f"ZeroDivisionError: {e}")

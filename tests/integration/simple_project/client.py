from srpc_calc_client_stub import SrpcCalcClientStub

from srpcLib.utils.srpc_network import get_lan_ip_or_localhost

SERVER_HOST = get_lan_ip_or_localhost()
calcStub = SrpcCalcClientStub(SERVER_HOST, 5000)
a = 4
b = 2
print(f"{calcStub.add(a, b)}")
print(f"{calcStub.mult(a, b)}")
print(f"{calcStub.sub(a, b)}")
print(f"{calcStub.div(a, b)}")
print(calcStub.hello_world())
print(calcStub.square(2.5))

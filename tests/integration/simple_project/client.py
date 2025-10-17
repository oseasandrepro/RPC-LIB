from srpc_calc_client_stub import SrpcCalcClientStub

from srpcLib.utils.srpc_network_util import get_lan_ip_or_localhost

SERVER_HOST = get_lan_ip_or_localhost()
calcStub = SrpcCalcClientStub(SERVER_HOST)
a = 4
b = 2
print(f"{calcStub.add(a, b)}")
print(f"{calcStub.mult(a, b)}")
print(f"{calcStub.sub(a, b)}")
print(f"{calcStub.div(a, b)}")

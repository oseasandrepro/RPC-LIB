from srpc_calc_client_stub import SrpcCalcClientStub

from srpcLib.utils.srpc_network_util import get_lan_ip_or_localhost

SERVER_HOST = get_lan_ip_or_localhost()
calcStub = SrpcCalcClientStub(SERVER_HOST, 5000)
a = 4
try:
    print(calcStub.div(a, 0))
except ZeroDivisionError as e:
    print(f"ZeroDivisionError: {e}")

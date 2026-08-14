from srpc_calc_client_stub import SrpcCalcClientStub
from srpc_calc_server_stub import SrpcTLSConfig

SERVER_HOST = "127.0.0.1"

tls_config = SrpcTLSConfig(cafile="./rootCA.pem")
calcStub = SrpcCalcClientStub(SERVER_HOST, 5000, tls_config)

a = 4
b = 2
print(f"{calcStub.add(a, b)}")
print(f"{calcStub.sub(a, b)}")

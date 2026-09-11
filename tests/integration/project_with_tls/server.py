import time

from srpc_calc_server_stub import SrpcCalcServerStub, SrpcTLSConfig

tls_config = SrpcTLSConfig(certfile="./server.crt", keyfile="./server.key")
srpc_server = SrpcCalcServerStub(tls_config=tls_config, host="127.0.0.1")
srpc_server.start()

try:
    # Mantém a thread principal viva apenas esperando o Ctrl+C
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    srpc_server.stop()

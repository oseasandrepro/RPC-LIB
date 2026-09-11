import time

from srpc_calc_server_stub import SrpcCalcServerStub

srpc_server = SrpcCalcServerStub()
srpc_server.start()

try:
    # Mantém a thread principal viva apenas esperando o Ctrl+C
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    srpc_server.stop()

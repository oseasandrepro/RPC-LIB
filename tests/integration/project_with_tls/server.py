from srpc_calc_server_stub import SrpcCalcServerStub, SrpcTLSConfig

tls_config = SrpcTLSConfig(certfile="./server.crt", keyfile="./server.key")
srpc_server = SrpcCalcServerStub(tls_config=tls_config, host="127.0.0.1")
srpc_server.start()

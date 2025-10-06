import socket
import threading

from srpc_calc_server_stub import SrpcCalcServerStub

from binder.srpc_server_binder import SrpcServerBinder

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

server_stub = SrpcCalcServerStub(ip_address)
binder = SrpcServerBinder(ip_address)

# This logic is to gracefully shutdown the server and binder on receiving termination signals
# TODO: put this logic inside the RpcServerStub and SrpcServerBinder classes
stop_event = threading.Event()
try:
    binder_thread = threading.Thread(target=binder.start_binder, name="binder_thread", daemon=True)
    binder_thread.start()

    server_stub.start()
    print("server started, press Ctrl+C to stop\n")
    stop_event.wait()
except KeyboardInterrupt:
    binder.stop()
    server_stub.stop()

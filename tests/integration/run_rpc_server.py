from binder.srpc_server_binder import SrpcServerBinder
from calc_rpc_server_stub import RpcServerStub
import threading
import socket


hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

server_stub = RpcServerStub(ip_address)
binder = SrpcServerBinder(ip_address)

# This logic is to gracefully shutdown the server and binder on receiving termination signals
# TODO: put this logic inside the RpcServerStub and SrpcServerBinder classes
stop_event = threading.Event()
try:
    binder_thread = threading.Thread(
        target=binder.start_binder, name="binder_thread", daemon=True
    )
    binder_thread.start()

    server_stub.start()
    print("server started, press Ctrl+C to stop\n")
    stop_event.wait()
except KeyboardInterrupt:
    binder.stop()
    server_stub.stop()

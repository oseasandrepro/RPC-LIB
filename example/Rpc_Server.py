from binder.srpc_server_binder import SrpcServerBinder
from calc_rpc_server_stub import RpcServerStub
import threading

HOST = "192.168.0.75"
server_stub = RpcServerStub(HOST)
binder = SrpcServerBinder(HOST)

binder_thread = threading.Thread(target=binder.start_binder,name="binder_thread", daemon=True)
binder_thread.start()


server_stub.start()
input("server started, press any key to stop\n")
binder.stop()
server_stub.stop()
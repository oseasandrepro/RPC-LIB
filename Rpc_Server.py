from Rpc_Server_Stub import RpcServerStub
from Rpc_Server_Binder import RpcServerBinder
import threading


HOST = "localhost"

binder = RpcServerBinder(HOST)
binder_thread = threading.Thread(target=binder.start_binder,name="binder_thread", daemon=True)
binder_thread.start()


stub = RpcServerStub(HOST)
stub.start()
input("server started, press any key to stop\n")
binder.stop()
stub.stop()
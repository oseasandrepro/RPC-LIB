import socket
import os
from Rpc_Serializer import RpcSerializer
from Rpc_Client_Binder import RpcClientBinder
from Rpc_Exceptions import RpcCallException, RpcTransportException
from interface.Rpc_Client_Stub_Interface import RpcClientStubInterface

from Calculadora_Interface import CalculadoraInterface

class Calc_Stub(CalculadoraInterface):
    def __init__(self):
        self.__client_stub = _RpcClientStub()

    def add(self, a, b):
        try:
            return self.__client_stub.remote_call('add', (a, b) )

        except RpcCallException as e:
            exc_name = e.code #exception type
            exc_class = eval(exc_name)
            raise exc_class(e.message)
        except RpcTransportException as e:
            print(f"Network issue: {e}")
            print("Mission aborted. Exiting.")
            os._exit(1)
    
    def mult(self, a, b):
        try:
            return self.__client_stub.remote_call('mult', (a, b) )

        except RpcCallException as e:
            exc_name = e.code #exception type
            exc_class = eval(exc_name)
            raise exc_class(e.message)
        except RpcTransportException as e:
            print(f"Network issue: {e}")
            print("Mission aborted. Exiting.")
            os._exit(1)
    
    def div(self, a, b):
        try:
            return self.__client_stub.remote_call('div', (a, b) )
        except RpcCallException as e:
            exc_name = e.code #exception type
            exc_class = eval(exc_name)
            raise exc_class(e.message)
        except RpcTransportException as e:
            print(f"Network issue: {e}")
            print("Mission aborted. Exiting.")
            os._exit(1)

        
    

class _RpcClientStub(RpcClientStubInterface):

    def __init__(self):
        self.__serializer = RpcSerializer()
        self.__HOST = "localhost"
        self.__functions = {}
        self.__bind()
    
    def __bind(self):
        binder = RpcClientBinder(self.__HOST)
        self.__functions = binder.binding_lookup()
        
    
    def remote_call(self, func_name, parameters: tuple):
        try:
            socket_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_cli.connect((self.__HOST, self.__functions[func_name]))
                    
            request = (func_name, *parameters)
            serialized_request = self.__serializer.serialize(request)
            socket_cli.sendall(serialized_request)

            serialized_response = socket_cli.recv(1024)
            deserialized_response = self.__serializer.deserialize(serialized_response)

            if deserialized_response[0] != "200":
                raise RpcCallException(deserialized_response[1], deserialized_response[2]) #(code, message, excepiton type)
                    
            return deserialized_response[2]
        
        except RpcCallException as e:
            raise RpcCallException(e.message, e.code)
        except socket.timeout:
           raise RpcTransportException("Timeout occurred during RPC call.")
        except OSError as e:
            print(f"General OS error: {e}")
            print("Mission aborted. Exiting.")
            os._exit(1)
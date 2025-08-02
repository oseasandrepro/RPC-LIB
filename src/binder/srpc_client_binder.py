from util.srpc_serializer import SrpcSerializer
from interface.srpc_client_binder_interface import SrpcClientBinderInterface
import socket
from srpc_exceptions import RpcBinderRequestException
import os

class RpcClientBinder(SrpcClientBinderInterface):
    def __init__(self, host="0.0.0.0"):
        self.__serializer = SrpcSerializer()
        self.__host = host
        self.__BINDER_PORT = 5000

    def binding_lookup(self):
        try:
            socket_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_cli.connect((self.__host, self.__BINDER_PORT))
                 
            request = ("LOOKUP", None, None)
            serialized_request = self.__serializer.serialize(request)
            socket_cli.sendall(serialized_request)
        
            serialized_response = socket_cli.recv(1024)
            deserialized_response = self.__serializer.deserialize(serialized_response)
            
            if deserialized_response[0] != "200":
                raise RpcBinderRequestException(deserialized_response[1], code=deserialized_response[0])
                    
            return deserialized_response[2]
        except socket.timeout:
            raise ("Timeout occurred during binding lookup.")
        except RpcBinderRequestException as e:
            print(f"RPC Binder returns an error response during binding lookup: {e}")
            print("Mission aborted. Exiting.")
            os._exit(1)
        except Exception as e:
            print(f"An error occurred during binding lookup. error: {e}")
            print("Mission aborted. Exiting.")
            os._exit(1)
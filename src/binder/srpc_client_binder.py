from util.srpc_serializer import SrpcSerializer
from interface.srpc_client_binder_interface import SrpcClientBinderInterface
import socket
from srpc_exceptions import RpcBinderRequestException
import logging

class RpcClientBinder(SrpcClientBinderInterface):
    def __init__(self, host="0.0.0.0"):
        self.__serializer = SrpcSerializer()
        self.__host = host
        self.__BINDER_PORT = 5000

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    def binding_lookup(self) -> dict[str, int]:
        response = None
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
                    
            response = deserialized_response[2]
        except ConnectionRefusedError as e:
            self.logger.error(str(e))
            self.logger.error("Ensure the RPC Binder Server is running. Mission aborted.")
            exit(1)
        except socket.timeout as e:
            self.logger.error(f"Connection timed out while trying to connect to the RPC Binder Server: {str(e)}")
            self.logger.error("Ensure the RPC Binder Server is running and reachable. Mission aborted.")
            exit(1)
        except RpcBinderRequestException as e:
            self.logger.error(f"RPC Binder Server returns an error response during lookup")
            self.logger.error(f"RPC Binder Server Error: {str(e)}")
            self.logger.error("Mission aborted.")
            exit(1)
        except socket.error as e:
            self.logger.error(f"Socket error: {str(e)}")
            self.logger.error("Mission aborted.")
            exit(1)
        except OSError as e:
            self.logger.error(f"OSError: {str(e)}")
            self.logger.error("Mission aborted.")
            exit(1)
        else:
            self.logger.info("Binding lookup successful.")
            return response
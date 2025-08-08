
import logging
import stub_generator.srpc_stub_utils as stub_utils

logger = logging.getLogger(__name__)

def gen_client_stub(interface_file_name, interface_name, 
                    dictionary_of_methods: dict, server_hostname):
    module_name = interface_file_name.split('_')[0]
    code = f"""
import socket
import logging
from util.srpc_serializer import SrpcSerializer
from binder.srpc_client_binder import RpcClientBinder
from srpc_exceptions import RpcCallException, RpcProcUnvailException
from interface.srpc_client_stub_interface import SrpcClientStubInterface

from {interface_file_name.split('.')[0]} import {interface_name}

class _RpcClientStub(SrpcClientStubInterface):

    def __init__(self):
        self.__serializer = SrpcSerializer()
        self.__HOST = "{server_hostname}"
        self.__functions = {{}}
        self.__bind()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    
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

            #(code, message, excepiton type)
            if deserialized_response[0] == "500":
                raise RpcCallException(deserialized_response[1], deserialized_response[2]) 
            elif deserialized_response[0] == "404":
                raise RpcProcUnvailException(deserialized_response[1])
                    
            return deserialized_response[2]
        
        except RpcCallException as e:
            raise RpcCallException(e.message, e.code)
        except RpcProcUnvailException as e:
            self.logger.error(f"Procedure {{func_name}} is unavailable on the server: {{e.message}}")
        except socket.timeout:
            self.logger.error("Timeout occurred during RPC call.")
        except socket.gaierror:
            self.logger.error(f"Network error: Unable to connect to the server. Check the hostname and port.")
        except ConnectionRefusedError:
            self.logger.error(f"Connection refused. Is the server running and reachable?")
        except socket.error as e:
            self.logger.error(f"Socket error: {{e}}")
        except OSError as e:
            self.logger.error(f"OS error during RPC call: {{e}}")
"""+f"""
class {module_name}_stub({interface_name}):
    def __init__(self):
        self.__client_stub = _RpcClientStub()
"""
    methods = f""""""
    for key, value in dictionary_of_methods.items():
        parameters = stub_utils.extract_params_from_method_sig(value)
        parameter_tuple = stub_utils.build_param_tuple(parameters)
        peace_of_code = f"""
    def {key}(self{ ',' if parameter_tuple else ''} {parameter_tuple[1:-1] if parameter_tuple else ''}):
        try:
            return self.__client_stub.remote_call('{key}', ({parameter_tuple[1:-1] if parameter_tuple else ''}) )
        except RpcCallException as e:
            exc_name = e.code #exception type
            exc_class = eval(exc_name)
            raise exc_class(e.message)
        """+"""
            """
        methods += peace_of_code
    code += methods
    stub_file_name = f"{module_name}_rpc_client_stub.py"

    try:
        with open(f"{stub_file_name}", "w") as f:
            f.write(code)
    except IOError as e:
        logger.error(f"Error writing to file {stub_file_name}: {e}")
        exit(1)
    else:
        logger.info(f"Client stub successfully generated: {stub_file_name}")
        logger.info(f"you should import {module_name}_stub from {stub_file_name} to call the procedures")
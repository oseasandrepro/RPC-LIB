import logging
from stub_generator.srpc_stub_utils import DEFAULT_BINDER_PORT

logger = logging.getLogger(__name__)

def gen_server_stub(interface_file_name, interface_name):
    server_module_name = interface_file_name.split('_')[0]
    server_class_name = server_module_name[0].upper() + server_module_name[1:]
    code = f'''
from concurrent.futures import ThreadPoolExecutor
import socket
import threading
import inspect
import time
import os

from util.srpc_serializer import SrpcSerializer
from srpc_exceptions import RpcBinderRequestException, RpcProcUnvailException
from interface.srpc_server_stub_interface import SrpcServerStubInterface
import logging

from {interface_file_name.split('.')[0]} import {interface_name}
from {server_module_name} import {server_class_name}

class RpcServerStub(SrpcServerStubInterface):

    def __init__(self, host='0.0.0.0'):
        self.__BINDER_PORT = {DEFAULT_BINDER_PORT}
        self.__lib_procedures_name = self.__get_lib_procedures_name()
        self.__host = host
        self.__executor = ThreadPoolExecutor(max_workers=10)
        self.__threads = []
        self.__stop_event = threading.Event()
        self.__serializer = SrpcSerializer()
        self.__lib_procedures = {server_class_name}()
        self.__check_implements_interface(self.__lib_procedures, {interface_name})
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")


    def __get_lib_procedures_name(self):
        return [name for name, member in inspect.getmembers({interface_name}, predicate=inspect.isfunction)]
    
    def __check_implements_interface(self, obj, interface):
        if not isinstance(obj, interface):
            logging.error(f"Object of type {{type(obj).__name__}} must implement interface {{interface.__name__}}")
            self.logger.error("Mission aborted.")
            os._exit(1)
        
    def __call_func(self, t: tuple):
        try:
            method = getattr(self.__lib_procedures, t[0])
            return method(*t[1:])
        except AttributeError:
            return None
        
    def __register_func_in_binder(self, func_name, port):
        try:
            socket_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_cli.connect((self.__host, self.__BINDER_PORT))
            request = ("REGISTER", func_name, port)
            serialized_request = self.__serializer.serialize(request)
            socket_cli.sendall(serialized_request)
        
            serialized_response = socket_cli.recv(1024)
            deserialized_response = self.__serializer.deserialize(serialized_response)
            
            if deserialized_response[0] != "200":
                raise RpcBinderRequestException(deserialized_response[1], code=deserialized_response[0])

            socket_cli.close()      
        except socket.timeout:
            self.logger.error(f"Timeout occurred during RPC bind for function [{{func_name}}].")
        except OSError as e:
            self.logger.error(f"An error occurred during function [{{func_name}}] registration: {{e}}")
            self.logger.error("Mission aborted.")
            os._exit(1)
        except RpcBinderRequestException as e:
            self.logger.error(f"RPC Binder returns an error response during function [{{func_name}}] registration: {{e}}")
            self.logger.error("Mission aborted.")
            os._exit(1)
        

    def __handle_request(self, func_name, conn, addr):
        with conn:
            try:
                msg = conn.recv(1024)
                request_tuple = self.__serializer.deserialize(msg)
                
                if isinstance(request_tuple, tuple) and request_tuple[0] == func_name:
                    self.logger.info(f"Request: {{request_tuple}} from: {{addr[0]}}")
                    result = self.__call_func(request_tuple)
                    response = ("200", "", result)
                else:
                    raise RpcProcUnvailException("The program cannot support the requested procedure.")
            except RpcProcUnvailException as e:
                self.logger.info(f"Procedure [{{func_name}}] is unavailable: {{e.message}}")
                response = ("404", e.message, type(e).__name__)
            except Exception as e:
                self.logger.error(f"Function [{{func_name}}] call error: {{e}}")
                response = ("500", str(e), type(e).__name__)
            finally:
                conn.sendall( self.__serializer.serialize(response))
                
    def __listen_for_func(self, func_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.__host, 0))
            port = s.getsockname()[1]
            self.__register_func_in_binder(func_name, port)
            s.listen()
            s.settimeout(1.0)
            
            while not self.__stop_event.is_set():
                try:
                    conn, addr = s.accept()
                    self.__executor.submit(self.__handle_request, func_name, conn, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.error(f"An error occurred while listening for function [{{func_name}}] in port [{{port}}]: {{e}}")
                    os._exit(1)

    def start(self):
        time.sleep(2)
        try:
            for func_name in self.__lib_procedures_name:
                t = threading.Thread(None,
                    target=self.__listen_for_func,
                    name=f"Thread-Listener-for-func-{{func_name}}", 
                    args=[func_name]
                    )
                self.__threads.append(t)
                t.start()
        except Exception as e:
            self.logger.error(f"An error occurred while starting the server stub: {{e}}")
            self.logger.error("Mission aborted.")
            os._exit(1)

    def stop(self):
        self.logger.info("Stopping stub...")
        self.__stop_event.set()
        for t in self.__threads:
            t.join()
        self.__executor.shutdown(wait=True)
        self.logger.info("Stub successfully stopped.")
'''
    with open(f"{server_module_name}_rpc_server_stub.py", "w") as f:
        f.write(code)
    
    server_stub_file_name = f"{server_module_name}_rpc_server_stub.py"
    logger.info(f"Server stub successfully generated: {server_stub_file_name}")
    logger.info(f"You must implement the Class '{server_class_name}' that implements '{interface_name}', " + 
                      f"inside '{server_module_name}.py' file.")
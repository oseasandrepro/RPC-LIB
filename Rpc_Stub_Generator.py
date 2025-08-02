import importlib.util
import sys
import os
import inspect
from abc import ABC

def load_module_from_path(path: str, module_name: str = "dynamic_interface"):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def get_interfaces(module):
    interfaces = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, ABC) and obj.__module__ == module.__name__:
            interfaces.append(obj)
    return interfaces

def list_methods(cls):
    for name, func in inspect.getmembers(cls, inspect.isfunction):
        print(f"Method: {name} - Signature: {inspect.signature(func)}")

def dictionary_of_methods_and_signatures(cls):
    dictionary = {}
    for name, func in inspect.getmembers(cls, inspect.isfunction):
        dictionary[name] = inspect.signature(func).__str__()
    return dictionary

def extract_param_names(sig: str) -> list[str]:
    start = sig.find('(')
    end = sig.find(')', start)
    if start == -1 or end == -1:
        raise ValueError("Invalid signature format")

    param_block = sig[start+1:end]
    raw_params = []
    buffer = ''
    depth = 0
    for char in param_block:
        if char in '([{':
            depth += 1
        elif char in ')]}':
            depth -= 1
        if char == ',' and depth == 0:
            raw_params.append(buffer.strip())
            buffer = ''
        else:
            buffer += char
    if buffer:
        raw_params.append(buffer.strip())
    names = []
    for param in raw_params:
        if not param or param == "self":
            continue
        name = param.split(':')[0].split('=')[0].strip()
        names.append(name)

    return names

def build_param_tuple(params: list[str]) -> str:
    return f"({', '.join(params)})"


def gen_server_stub(interface_file_name, interface_name):
    server_module_name = interface_file_name.split('_')[0]
    code = f'''
from Rpc_Serializer import RpcSerializer
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

import socket
import threading
import inspect
import time
import os


from Rpc_Exceptions import RpcBinderRequestException, RpcProcUnvailException
from interface.Rpc_Server_Sub_Interface import RpcServerStubInterface

from {interface_file_name.split('.')[0]} import {interface_name}
from {server_module_name} import {server_module_name}

class RpcServerStub(RpcServerStubInterface):

    def __init__(self, host='0.0.0.0'):
        self.__BINDER_PORT = 5000
        self.__lib_procedures_name = self.__get_lib_procedures_name()
        self.__host = host
        self.__executor = ThreadPoolExecutor(max_workers=10)
        self.__threads = []
        self.__stop_event = threading.Event()
        self.__serializer = RpcSerializer()
        self.__lib_procedures = {server_module_name}()
        self.__check_implements_interface(self.__lib_procedures, {interface_name})


    def __get_lib_procedures_name(self):
        return [name for name, member in inspect.getmembers({interface_name}, predicate=inspect.isfunction)]
    
    def __check_implements_interface(self, obj, interface):
        if not isinstance(obj, interface):
            raise TypeError(f"Object of type {{type(obj).__name__}} must implement interface {{interface.__name__}}")
        
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
            else:
                print(f"func [{{func_name}}] in port [{{port}}] Listening...")

            socket_cli.close()      
        except socket.timeout:
            raise ("Timeout occurred during RPC bind.")
        except OSError as e:
            print(f"an error occurred during function [{{func_name}}] registration: {{e}}")
            print("Mission aborted. Exiting.")
            os._exit(1)
        except RpcBinderRequestException as e:
            print(f"RPC Binder returns an error response during function [{{func_name}}] registration: {{e}}")
            print("Mission aborted. Exiting.")
            os._exit(1)
        

    def __handle_request(self, func_name, conn, addr):
        with conn:
            try:
                msg = conn.recv(1024)
                request_tuple = self.__serializer.deserialize(msg)
                
                if isinstance(request_tuple, tuple) and request_tuple[0] == func_name:
                    print(f"Request: {{request_tuple}} from: {{addr[0]}}")
                    result = self.__call_func(request_tuple)
                    response = ("200", "", result)
                else:
                    raise RpcProcUnvailException("The program cannot support the requested procedure.")
            except Exception as e:
                print(f"func [{{func_name}}] call error: {{e}}")
                response = ("500", str(e), type(e).__name__)
            finally:
                conn.sendall( self.__serializer.serialize(response))
                
    def __listen_for_func(self, func_name, ponte):
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
                    #print(f"Port [{{port}}] Connected: {{addr}}")
                    self.__executor.submit(self.__handle_request, func_name, conn, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[{{port}}] Listener error: {{e}}")

    def start(self):
        time.sleep(2)
        for func_name in self.__lib_procedures_name:
            t = threading.Thread(
                target=self.__listen_for_func, 
                args=(func_name, 5), 
                daemon=True
                )
            self.__threads.append(t)
            t.start()

    def stop(self):
        print("Stopping stub...")
        self.__stop_event.set()
        for t in self.__threads:
            t.join()
        self.__executor.shutdown(wait=True)
        print("stub successfully stoped.")
'''
    with open(f"{server_module_name}_rpc_server_stub.py", "w") as f:
        f.write(code)
    
    stub_file_name = f"{server_module_name}_rpc_server_stub.py"
    print(f"server stub generated: {stub_file_name}")
    print(f"you should implent the interface {interface_name} and put the file in the same directory of server script")
    print(f"in a class caled {server_module_name}")


def gen_client_stub(interface_file_name, interface_name, dictionary_of_methods: dict, host, binder_port):
    module_name = interface_file_name.split('_')[0]
    code = f"""
import socket
import os
from Rpc_Serializer import RpcSerializer
from Rpc_Client_Binder import RpcClientBinder
from Rpc_Exceptions import RpcCallException, RpcTransportException
from interface.Rpc_Client_Stub_Interface import RpcClientStubInterface

from {interface_file_name.split('.')[0]} import {interface_name}

class _RpcClientStub(RpcClientStubInterface):

    def __init__(self):
        self.__serializer = RpcSerializer()
        self.__HOST = "{host}"
        self.__functions = {{}}
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
            print(f"General OS error: {{e}}")
            print("Mission aborted. Exiting.")
            os._exit(1)
"""+f"""
class {module_name}_Stub({interface_name}):
    def __init__(self):
        self.__client_stub = _RpcClientStub()
"""
    methods = f""""""
    for key, value in dictionary_of_methods.items():
        parameters = extract_param_names(value)
        parameter_tuple = build_param_tuple(parameters)
        peace_of_code = f"""
    def {key}(self{ ',' if parameter_tuple else ''} {parameter_tuple[1:-1] if parameter_tuple else ''}):
        try:
            return self.__client_stub.remote_call('{key}', ({parameter_tuple[1:-1] if parameter_tuple else ''}) )

        except RpcCallException as e:
            exc_name = e.code #exception type
            exc_class = eval(exc_name)
            raise exc_class(e.message)
        except RpcTransportException as e:
            print(f"Network issue: {{e}}")
            print("Mission aborted. Exiting.")
            os._exit(1)
        """+"""
            """
        methods += peace_of_code
    code += methods
    stub_file_name = f"{module_name}_rpc_client_stub.py"
    with open(f"{stub_file_name}", "w") as f:
        f.write(code)
    print(f"client stub generated: {stub_file_name}")
    print(f"you should import {module_name}_Stub from {stub_file_name} to call the procedures")

     

BINDER_PORT = 5000
path = input("get the interface path: ")
host = input("server IP-address: ")

mod = load_module_from_path(path)
interfaces = get_interfaces(mod)

file_name = os.path.basename(path)
interface_name = interfaces[0].__name__


gen_client_stub(file_name, interface_name, 
                dictionary_of_methods_and_signatures(interfaces[0]), 
                host, BINDER_PORT)
print("---------------------------------------")
gen_server_stub(file_name, interface_name)
from Rpc_Serializer import RpcSerializer
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

import socket
import threading
import inspect
import random
import time
import os


from Rpc_Exceptions import RpcBinderRequestException
from interface.Rpc_Server_Sub_Interface import RpcServerStubInterface

from Calculadora_Interface import CalculadoraInterface
from Calculadora import Calculadora

class RpcServerStub(RpcServerStubInterface):

    def __init__(self, host='0.0.0.0'):
        self.__BINDER_PORT = 5000
        self.__lib_procedures_name = self.__get_lib_procedures_name()
        self.__host = host
        self.__executor = ThreadPoolExecutor(max_workers=10)
        self.__threads = []
        self.__stop_event = threading.Event()
        self.__serializer = RpcSerializer()
        self.__lib_procedures = Calculadora()
        self.__check_implements_interface(self.__lib_procedures, CalculadoraInterface)


    def __get_lib_procedures_name(self):
        return [name for name, member in inspect.getmembers(CalculadoraInterface, predicate=inspect.isfunction)]
    
    def __check_implements_interface(self, obj, interface):
        if not isinstance(obj, interface):
            raise TypeError(f"Object of type {type(obj).__name__} must implement interface {interface.__name__}")
        
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
                print(f"func [{func_name}] in port [{port}] Listening...")

            socket_cli.close()      
        except socket.timeout:
            raise ("Timeout occurred during RPC bind.")
        except OSError as e:
            print(f"an error occurred during function [{func_name}] registration: {e}")
            print("Mission aborted. Exiting.")
            os._exit(1)
        except RpcBinderRequestException as e:
            print(f"RPC Binder returns an error response during function [{func_name}] registration: {e}")
            print("Mission aborted. Exiting.")
            os._exit(1)
        
    def __gen_random_port_number(self):
        port = random.randint(1029, 48657)
        while port in [5000] :
            port = random.randint(1029, 48657)

        return port

    def __handle_request(self, func_name, conn, addr):
        with conn:
            try:
                msg = conn.recv(1024)
                request_tuple = self.__serializer.deserialize(msg)
                
                if isinstance(request_tuple, tuple) and request_tuple[0] == func_name:
                    print(f"Request: {request_tuple} from: {addr[0]}")
                    result = self.__call_func(request_tuple)
                    response = ("200", "", result)
                else:
                    response = ("400", "Invalid function name or format", None)
            except Exception as e:
                print(f"func [{func_name}] call error: {e}")
                response = ("500", str(e), type(e).__name__)
            finally:
                conn.sendall( self.__serializer.serialize(response))
                
    def __listen_for_func(self, func_name, ponte):
        port = self.__gen_random_port_number()
        self.__register_func_in_binder(func_name, port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.__host, port))
            s.listen()
            s.settimeout(1.0)
            
            while not self.__stop_event.is_set():
                try:
                    conn, addr = s.accept()
                    #print(f"Port [{port}] Connected: {addr}")
                    self.__executor.submit(self.__handle_request, func_name, conn, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[{port}] Listener error: {e}")


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
import logging
import textwrap

from ...interface.srpc_stub_generator_interface import SrpcStubGeneratorInterface
from ...utils.srpc_stub import (
    DEFAULT_CONNECTION_PORT,
    LIB_NAME,
    get_service_interface_class_name,
    get_service_name,
)
from ..language import Language
from ..stub_type import StubType

logger = logging.getLogger(__name__)

str_imports = textwrap.dedent(
    f"""
from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod
from dataclasses import dataclass
import socket
import ssl
import threading
import inspect
import os

from {LIB_NAME}.utils.srpc_serializer import SrpcSerializer
import {LIB_NAME}.utils.srpc_network as srpcnetwork
import logging

"""
).lstrip()

str_server_TLSConfig = textwrap.dedent(
    """
# ############# TLS config class ###############
# certfile -> Path of certfile, usend in server side
# keyfile -> Path of keyfile, used in server side
# cafile -> Path of Certificate Authority (used in client side)
@dataclass
class  SrpcTLSConfig:
    certfile: str | None = None
    keyfile: str | None = None
    cafile: str | None = None

    minimum_tls_version: ssl.TLSVersion = ssl.TLSVersion.TLSv1_2

"""
).lstrip()

str_server_stub_interface = textwrap.dedent(
    """
class SrpcServerStubInterface(ABC):
    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def start(self):
        pass

    """
).lstrip()


class ServerPythonStubGenerator(SrpcStubGeneratorInterface):
    type = StubType.SERVER
    language = Language.PYTHON

    def __init__(self, interface_path: str):
        self.interface_path = interface_path

    def get_type(self):
        return self.type

    def get_language(self):
        return self.language

    def generate_stub(self, dest_path: str = None):
        service_interface_class_name = get_service_interface_class_name(
            self.interface_path
        )
        service_name = get_service_name(self.interface_path)
        service_class_name = service_name.capitalize()

        str_service_class = textwrap.dedent(
            f"""
from {service_name}.{service_name} import {service_class_name}
from {service_name}.{service_name}_interface import {service_interface_class_name}

class Srpc{service_name.capitalize()}ServerStub(SrpcServerStubInterface):
    def __init__(self, tls_config: SrpcTLSConfig = None, host:str=None, num_threads = 8):

        if host == None:
            self.__host = srpcnetwork.get_lan_ip_or_localhost()
        else:
            self.__host = host

        self.__CONNECTION_PORT = {DEFAULT_CONNECTION_PORT}

        self.__handler_threads_pool = ThreadPoolExecutor(num_threads)

        self.__listner_thread = None
        self.__handler_threads_pool = ThreadPoolExecutor(max_workers=10)
        self.__stop_event = threading.Event()
        self.__serializer = SrpcSerializer()
        self.__lib_procs = {service_class_name}()
        self.__check_implements_interface(self.__lib_procs, {service_interface_class_name})

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)
        self.__console_handler = logging.StreamHandler()
        self.__formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        self.__console_handler.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__console_handler)

        self.__proc_id_dic : dict[int, str] = self.__get_proc_id_dic()
        self.__tls_config = tls_config
        self.__ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)


    def __get_proc_id_dic(self):
        index:int = 0
        procs : dict[int,str] = {{}}
        procedures = {{ name: obj for name, obj in {service_interface_class_name}.__dict__.items()
            if inspect.isfunction(obj) and not name.startswith("__") }}
        for proc_name in procedures:
            procs[index] = proc_name
            index = index+1

        return procs

    def __check_implements_interface(self, obj, interface):
        if not isinstance(obj, interface):
            logging.error(f"Object of type {{type(obj).__name__}} must implement interface {{interface.__name__}}")
            self.__logger.error("Mission aborted.")
            os._exit(1)

    def __call_procedure(self, proc_id: int, args: list):
        try:
            procedure = getattr(self.__lib_procs, self.__proc_id_dic[proc_id])
            return procedure(*args)
        except AttributeError:
            return None

    def __handle_request(self, client_socket, client_addr):
        try:
            if not (self.__tls_config == None):
                self.__ssl_context.minimum_version = self.__tls_config.minimum_tls_version
                self.__ssl_context.load_cert_chain(certfile=self.__tls_config.certfile, keyfile=self.__tls_config.keyfile)
                client_socket = self.__ssl_context.wrap_socket(client_socket, server_side=True)

        except (ssl.SSLError, ssl.CertificateError) as e:
            self.__logger.warning(f"Captured Requests SSL Error: {{e}}")
            self.__logger.warning(f"From: {{client_addr}}")
            client_socket.close()

        except Exception as e:
            self.__logger.error(f"An error occurred while TLS handshake for {{client_addr}}.: {{e}}")
            client_socket.close()

        with client_socket:
            try:
                #recive header
                header_bytes = srpcnetwork.recv_n(client_socket, srpcnetwork.HEADER_SIZE)
                request = srpcnetwork.Request.deserialize_header(header_bytes)

                #check protocol version

                procedure_name = self.__proc_id_dic[request.proc_id]

                self.__logger.info(f"Requested procedure {{procedure_name}} from: {{client_addr[0]}}")

                request.payload = srpcnetwork.recv_n(client_socket, request.payload_size)
                if not request.payload:
                    raise ValueError("Srpc: empty payload request")

                # deserialize the list of parameters
                proc_parameters_list = self.__serializer.deserialize(request.payload)

                #Call procedure
                result = self.__call_procedure(request.proc_id, proc_parameters_list)

                # build response, payload=(msg, returned-value)
                # 0 in response code mean sucess
                response_payload = result
                response_payload_bytes = self.__serializer.serialize(response_payload)
                response = srpcnetwork.Response(0, 0, len(response_payload_bytes), response_payload_bytes)

            except KeyError as e:
                response_payload = "The service do not support the requested procedure"
                response_payload_bytes = self.__serializer.serialize(response_payload)
                response = srpcnetwork.Response(0, 1, len(response_payload_bytes), response_payload_bytes)
                self.__logger.info(f"Procedure not suported: {{e.message}}")
            except Exception as e:
                self.__logger.error(f"Procedure [{{procedure_name}}] call error: {{e}}")
                response_payload = str(e)
                response_payload_bytes = self.__serializer.serialize(response_payload)
                response = srpcnetwork.Response(0, 2, len(response_payload_bytes), response_payload_bytes)
            finally:
                client_socket.sendall( response.serialize())
                client_socket.close()

    def __listner(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listner_socket:
            listner_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listner_socket.bind((self.__host, self.__CONNECTION_PORT))
            port = listner_socket.getsockname()[1]
            listner_socket.listen()
            listner_socket.settimeout(1.0)

            while not self.__stop_event.is_set():
                try:
                    client_socket, client_addr = listner_socket.accept()
                    self.__handler_threads_pool.submit(self.__handle_request, client_socket, client_addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    self.__logger.error(f"An error occurred while listening for users requests in port [{{port}}]: {{e}}")
                    os._exit(1)

    def start(self):
        try:
            self.__listner_thread = threading.Thread(target=self.__listner,name="SRPC Thread-Listener")
            self.__listner_thread.start()
            self.__logger.info(f"Procedure calls on [tcp-{{self.__host}}:{{self.__CONNECTION_PORT}}].")
            self.__logger.info("Press Ctrl+C to stop.")
            self.__stop_event.wait()

        except KeyboardInterrupt:
            self.stop()

        except Exception as e:
            self.__logger.error(f"An error occurred while starting the server stub: {{e}}")
            raise

    def stop(self):
        self.__logger.info("Stopping SRPC server...")
        self.__stop_event.set()

        if self.__listner_thread is not None:
            self.__listner_thread.join()

        self.__handler_threads_pool.shutdown(wait=True)

        self.__logger.info("Server successfully stopped.")

        """
        ).lstrip()

        stub_code = (
            str_imports
            + str_server_TLSConfig
            + str_server_stub_interface
            + str_service_class
        )

        # server_stub_file_name = f"{dest_path + "/" if dest_path else ""}srpc_{service_name}_server_stub.py"
        server_stub_file_name = (
            f"{dest_path}/srpc_{service_name}_server_stub.py"
            if dest_path
            else f"srpc_{service_name}_server_stub.py"
        )

        with open(server_stub_file_name, "w") as f:
            f.write(stub_code)

        logger.info(f"Server stub successfully generated: {server_stub_file_name}")


# python -m srpcLib.stub_generator.client_python_stub_generator
if __name__ == "__main__":
    stub_gen = ServerPythonStubGenerator(
        "/home/saesolab/software-experiments/rpc-experiment/calc/calc_interface.py"
    )
    print(f"{stub_gen.get_type()}, {stub_gen.get_language()}")
    stub_gen.generate_stub()

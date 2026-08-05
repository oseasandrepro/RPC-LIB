import logging
import textwrap

from ...interface.srpc_stub_generator_interface import SrpcStubGeneratorInterface
from ...utils.srpc_stub_util import (
    DEFAULT_CONNECTION_PORT,
    LIB_NAME,
    LOG_PATH,
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
import socket
import threading
import inspect
import time
import os

from {LIB_NAME}.metrics.srpc_metrics_types import SrpcmetricsTypes
from {LIB_NAME}.metrics.srpc_metric import SrpcMetric
from {LIB_NAME}.utils.srpc_serializer import SrpcSerializer
from {LIB_NAME}.srpc_exceptions import SrpcProcUnvailException
from {LIB_NAME}.utils.srpc_network_util import get_lan_ip_or_localhost
import logging

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
    def __init__(self):
        self.__mestrics = SrpcMetric("{LOG_PATH}")

        self.__host = get_lan_ip_or_localhost()
        self.__CONNECTION_PORT = {DEFAULT_CONNECTION_PORT}

        self.__lib_procedures_name = self.__get_lib_procedures_name()
        self.__executor = ThreadPoolExecutor(max_workers=10)
        self.__threads = []
        self.__stop_event = threading.Event()
        self.__serializer = SrpcSerializer()
        self.__lib_procedures = {service_class_name}()
        self.__check_implements_interface(self.__lib_procedures, {service_interface_class_name})
        self.__set_metrics()

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)
        self.__console_handler = logging.StreamHandler()
        self.__formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        self.__console_handler.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__console_handler)


    def __set_metrics(self):
        for procedure_name in self.__lib_procedures_name:
            self.__mestrics.add_metric(procedure_name, SrpcmetricsTypes.COUNTER_SUCCESS)
            self.__mestrics.add_metric(procedure_name, SrpcmetricsTypes.COUNTER_FAIL)
            self.__mestrics.add_metric(procedure_name, SrpcmetricsTypes.TIME)

    def __get_lib_procedures_name(self):
        return [name for name, member in inspect.getmembers({service_interface_class_name}, predicate=inspect.isfunction)]

    def __check_implements_interface(self, obj, interface):
        if not isinstance(obj, interface):
            logging.error(f"Object of type {{type(obj).__name__}} must implement interface {{interface.__name__}}")
            self.__logger.error("Mission aborted.")
            os._exit(1)

    def __call_procedure(self, t: tuple):
        try:
            method = getattr(self.__lib_procedures, t[0])
            return method(*t[1:])
        except AttributeError:
            return None

    def __handle_request(self, client_socket, client_addr):
        with client_socket:
            try:
                msg = client_socket.recv(1024)
                request_tuple = self.__serializer.deserialize(msg)
                procedure_name = request_tuple[0]

                if isinstance(request_tuple, list):
                    self.__logger.info(f"Request: {{request_tuple}} from: {{client_addr[0]}}")
                    start_time = time.time()  # Start time measurement
                    result = self.__call_procedure(request_tuple)
                    end_time = time.time()  # End time measurement
                    response = ("200", "", result)
                    self.__mestrics.inc_counter_success(f"{{procedure_name}}")
                    self.__mestrics.record_time(f"{{procedure_name}}", end_time - start_time)
                else:
                    raise SrpcProcUnvailException("The program cannot support the requested procedure.")
            except SrpcProcUnvailException as e:
                self.__logger.info(f"Procedure [{{procedure_name}}] is unavailable: {{e.message}}")
                response = ("404", e.message, type(e).__name__)
            except Exception as e:
                self.__logger.error(f"Procedure [{{procedure_name}}] call error: {{e}}")
                response = ("500", str(e), type(e).__name__)
                self.__mestrics.inc_counter_fail(f"{{procedure_name}}")
            finally:
                client_socket.sendall( self.__serializer.serialize(response))

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
                    self.__executor.submit(self.__handle_request, client_socket, client_addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    self.__logger.error(f"An error occurred while listening for users requests in port [{{port}}]: {{e}}")
                    os._exit(1)

    def start(self):
        stop_event = threading.Event()
        try:
            t = threading.Thread(None,target=self.__listner,name=f"SRPC Thread-Listener")
            self.__threads.append(t)
            t.start()
            self.__logger.info(f"Procedurs call on [tcp-{{self.__host}}:{{self.__CONNECTION_PORT}}].")
            self.__logger.info(f"press Ctrl+C to stop.")
            stop_event.wait()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            self.__logger.error(f"An error occurred while starting the server stub: {{e}}")
            self.__logger.error("Mission aborted.")
            os._exit(1)

    def stop(self):
        self.__logger.info("Stopping stub...")
        self.__stop_event.set()
        for t in self.__threads:
            t.join()
        self.__executor.shutdown(wait=True)
        self.__logger.info("Stub successfully stopped.")

        """
        ).lstrip()

        stub_code = str_imports + str_server_stub_interface + str_service_class

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

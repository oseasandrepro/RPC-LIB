import logging
import textwrap

from ...interface.srpc_stub_generator_interface import SrpcStubGeneratorInterface
from ...utils.srpc_stub_util import (
    DEFAULT_CONNECTION_PORT,
    LIB_NAME,
    get_procedures,
    get_service_interface_class_name,
    get_service_name,
    remove_type_hint_from_param_list,
)
from ..language import Language
from ..stub_type import StubType

logger = logging.getLogger(__name__)

str_imports = textwrap.dedent(
    f"""
    from abc import ABC, abstractmethod
    import socket
    import logging
    from {LIB_NAME}.utils.srpc_serializer import SrpcSerializer

    """
).lstrip()

str_client_stub_interface = textwrap.dedent(
    """
class SrpcClientStubInterface(ABC):
    @abstractmethod
    def remote_call(self, func_name, parameters: tuple):
        pass

"""
).lstrip()

str_client_stub_class = textwrap.dedent(
    """
class _SrpcClientStub(SrpcClientStubInterface):

    def __init__(self, server_host, port):
        self.__serializer = SrpcSerializer()
        self.__server_host = server_host
        self.__connection_port = port

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)
        self.__console_handler = logging.StreamHandler()
        self.__formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        self.__console_handler.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__console_handler)

    def remote_call(self, procedure_name, parameters: tuple):
        try:
            socket_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_cli.connect((self.__server_host, self.__connection_port))

            request = (procedure_name, *parameters)
            serialized_request = self.__serializer.serialize(request)
            socket_cli.sendall(serialized_request)

            serialized_response = socket_cli.recv(1024)
            deserialized_response = self.__serializer.deserialize(serialized_response)

            if deserialized_response[0] == "200":
                return deserialized_response[2]
            elif deserialized_response[0] == "500" or deserialized_response[0] == "404":
                raise RuntimeError(deserialized_response[1])

        except socket.timeout:
            self.__logger.error("Timeout occurred during RPC call.")
        except socket.gaierror:
            self.__logger.error(f"Network error: Unable to connect to the server.")
        except ConnectionRefusedError:
            self.__logger.error(f"Connection refused. Is the server running and reachable?")
        except socket.error as e:
            self.__logger.error(f"Socket error: {{e}}")
        except OSError as e:
            self.__logger.error(f"OS error during RPC call: {{e}}")

"""
).lstrip()


class ClientPythonStubGenerator(SrpcStubGeneratorInterface):
    type = StubType.CLIENT
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

        str_service_class = textwrap.dedent(
            f"""
        from {service_name}.{service_name}_interface import {service_interface_class_name}

        class Srpc{service_name.capitalize()}ClientStub({service_interface_class_name}):
            def __init__(self, server_host='127.0.0.1', port = {DEFAULT_CONNECTION_PORT}):
                self.__client_stub = _SrpcClientStub(server_host, port)

        """
        ).lstrip()

        str_procs = ""

        procs_list = get_procedures(self.interface_path)

        for proc in procs_list:
            proc_name = proc[0]
            proc_return_value = proc[1]
            proc_param_list = proc[2]
            proc_param_list_without_type_hint = remove_type_hint_from_param_list(
                proc_param_list
            )

            str_proc = textwrap.indent(
                textwrap.dedent(
                    f"""
            def {proc_name}(self{", " + ', '.join(proc_param_list) if proc_param_list else ''} ) -> {proc_return_value}:
                return self.__client_stub.remote_call( '{proc_name}', ({proc_param_list_without_type_hint[0] + ',' if len(proc_param_list_without_type_hint) == 1 else ', '.join(proc_param_list_without_type_hint) if proc_param_list_without_type_hint else ''}) )

            """
                ).lstrip(),
                "    ",
            )
            str_procs += str_proc

        str_service_class += str_procs

        stub_code = (
            str_imports
            + str_client_stub_interface
            + str_client_stub_class
            + str_service_class
        )

        # stub_file_name = f"{dest_path + "/" if dest_path else ""}srpc_{service_name}_client_stub.py"
        stub_file_name = (
            f"{dest_path}/srpc_{service_name}_client_stub.py"
            if dest_path
            else f"srpc_{service_name}_client_stub.py"
        )

        try:
            with open(f"{stub_file_name}", "w") as f:
                f.write(stub_code)
        except IOError as e:
            logger.error(f"Error writing to file {stub_file_name}: {e}")
            exit(1)
        else:
            logger.info(f"Client stub successfully generated: {stub_file_name}")
            logger.info(
                f"you should import {service_name}_stub from {stub_file_name} to call the procedures"
            )


# python -m srpcLib.stub_generator.client_python_stub_generator
if __name__ == "__main__":
    stub_gen = ClientPythonStubGenerator(
        "/home/saesolab/software-experiments/rpc-experiment/calc/calc_interface.py"
    )
    print(f"{stub_gen.get_type()}, {stub_gen.get_language()}")
    stub_gen.generate_stub()

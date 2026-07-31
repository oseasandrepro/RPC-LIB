from .lenguage import Lenguage
from .python.client_python_stub_generator import ClientPythonStubGenerator
from .python.server_python_stub_generator import ServerPythonStubGenerator
from .stub_type import StubType


class StubGeneratorFactory:
    stub_classes = {
        StubType.SERVER.name + Lenguage.PYTHON.name: ServerPythonStubGenerator,
        StubType.CLIENT.name + Lenguage.PYTHON.name: ClientPythonStubGenerator,
    }

    @staticmethod
    def create_stub_generator(stub_type: str, lenguage: str, interface_path: str):
        stub_class = StubGeneratorFactory.stub_classes.get(stub_type + lenguage)

        if stub_class:
            return stub_class(interface_path)
        else:
            raise ValueError(f"Unknown lenguage: {lenguage}")

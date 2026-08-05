from .language import Language
from .python.client_python_stub_generator import ClientPythonStubGenerator
from .python.server_python_stub_generator import ServerPythonStubGenerator
from .stub_type import StubType


class StubGeneratorFactory:
    stub_classes = {
        StubType.SERVER.name + Language.PYTHON.name: ServerPythonStubGenerator,
        StubType.CLIENT.name + Language.PYTHON.name: ClientPythonStubGenerator,
    }

    @staticmethod
    def create_stub_generator(stub_type: str, language: str, interface_path: str):
        stub_class = StubGeneratorFactory.stub_classes.get(stub_type + language)

        if stub_class:
            return stub_class(interface_path)
        else:
            raise ValueError(f"Unknown language: {language}")

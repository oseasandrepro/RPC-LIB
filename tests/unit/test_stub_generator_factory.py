from srpcLib.stub_generator.lenguage import Lenguage
from srpcLib.stub_generator.python.client_python_stub_generator import (
    ClientPythonStubGenerator,
)
from srpcLib.stub_generator.python.server_python_stub_generator import (
    ServerPythonStubGenerator,
)
from srpcLib.stub_generator.stub_generator_factory import StubGeneratorFactory
from srpcLib.stub_generator.stub_type import StubType


class TestStubGeneratorFactory:
    def test_python_client_stub_gen(self):
        path = "tests/test_resources/calc/calc_interface.py"
        stub_gen = StubGeneratorFactory.create_stub_generator("CLIENT", "PYTHON", path)

        assert StubType.CLIENT == stub_gen.get_type()
        assert Lenguage.PYTHON == stub_gen.get_lenguage()
        assert isinstance(stub_gen, ClientPythonStubGenerator)

    def test_python_server_stub_gen(self):
        path = "tests/test_resources/calc/calc_interface.py"
        stub_gen = StubGeneratorFactory.create_stub_generator("SERVER", "PYTHON", path)

        assert StubType.SERVER == stub_gen.get_type()
        assert Lenguage.PYTHON == stub_gen.get_lenguage()
        assert isinstance(stub_gen, ServerPythonStubGenerator)

import argparse
import logging

from ..stub_generator.language import Language
from ..stub_generator.stub_generator_factory import StubGeneratorFactory
from ..stub_generator.stub_type import StubType
from ..utils.srpc_stub import check_service_definition


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


parser = argparse.ArgumentParser(
    prog="srpc_stub_gen",
    description="Generate server and client stubs, from a Python interface.",
)

parser.add_argument("path", type=str, help="Path of the python interface")
parser.add_argument(
    "type",
    type=str,
    help="The stub type SERVER/CLIENT",
    choices=[StubType.CLIENT.name, StubType.SERVER.name],
)

parser.add_argument(
    "language", type=str, help="The target language", choices=[Language.PYTHON.name]
)


# python -m srpcLib.tools.srpc_stub_gen /home/saesolab/software-projects/RPC-LIB/tests/test_resources/calc/calc_interface.py CLIENT PYTHON
if __name__ == "__main__":
    args = parser.parse_args()

    check_service_definition(args.path)

    stub_gen = StubGeneratorFactory.create_stub_generator(
        args.type, args.language, args.path
    )
    stub_gen.generate_stub()

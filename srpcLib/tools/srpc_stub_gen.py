import argparse
import logging
from os import path

from ..stub_generator.srpc_client_stub_gen import gen_client_stub
from ..stub_generator.srpc_server_stub_gen import gen_server_stub
from ..utils.srpc_stub_util import (
    get_interface_from_module,
    get_methodname_signature_map_from_interface,
    load_module_from_path,
)


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


parser = argparse.ArgumentParser(
    prog="srpc_stub_gen",
    description="Generate server and client stubs, from a python interface.",
)

parser.add_argument("path", type=str, help="Path of the python interface")
parser.add_argument(
    "ip", type=str, help="Ip-adress of the server that will provide de service"
)


if __name__ == "__main__":
    args = parser.parse_args()
    configure_logging()
    module = load_module_from_path(args.path)
    interface = get_interface_from_module(module)
    file_name = path.basename(args.path)
    interface_name = interface.__name__

    gen_client_stub(
        file_name,
        interface_name,
        get_methodname_signature_map_from_interface(interface),
        args.ip,
    )
    gen_server_stub(file_name, interface_name)

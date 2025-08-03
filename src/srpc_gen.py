from os import path
import logging
import stub_generator.srpc_client_stub_gen as client_stub_gen
import stub_generator.srpc_server_stub_gen as server_stub_gen
import stub_generator.srpc_stub_utils as stub_util

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

if __name__ == "__main__":
    configure_logging()
    file_path = input("get the interface path: ")
    server_host = input("server IP-address: ")

    module = stub_util.load_module_from_path(file_path)
    interface = stub_util.get_interface_from_module(module)
    file_name = path.basename(file_path)
    interface_name = interface.__name__

    client_stub_gen.gen_client_stub(file_name, interface_name, 
                                    stub_util.get_methodname_signature_map_from_interface(interface), 
                                    server_host)
    server_stub_gen.gen_server_stub(file_name, interface_name)
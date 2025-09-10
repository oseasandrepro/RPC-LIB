import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from utils.srpc_serializer import SrpcSerializer
from interface.srpc_server_binder_interface import SrpcServerBinderInterface
import logging


class SrpcServerBinder(SrpcServerBinderInterface):
    def __init__(self, host="0.0.0.0"):
        self.__host = host
        self.__BINDER_PORT = 5000
        self.__total_lookup_request = 0
        self.__serializer = SrpcSerializer()
        self.__functions = {}
        self.__shutdown_event = threading.Event()
        self.__binder_socket = None
        self.__set_binder_socket(self.__host, self.__BINDER_PORT)

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s : %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def __set_binder_socket(self, host, port):
        self.__binder_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__binder_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__binder_socket.bind((host, port))
        self.__binder_socket.listen(5)
        self.__binder_socket.settimeout(1.0)

    def __handle_lookup_request(self, conn):
        try:
            msg = conn.recv(1024)
            request_tuple = self.__serializer.deserialize(msg)
            if request_tuple[0] == "LOOKUP":
                response_tuple = ("200", "", self.__functions)
                self.__total_lookup_request += 1
                self.logger.info(
                    f"Total lookup requests: {self.__total_lookup_request}"
                )
            elif request_tuple[0] == "REGISTER":
                req_function = request_tuple[1]
                port = request_tuple[2]
                self.__functions[req_function] = port
                response_tuple = ("200", "", None)
                self.logger.info(
                    f"Function [{req_function}] registered on port [{port}]"
                )
            else:
                self.logger.error(f"Unknown request type: {request_tuple[0]}")
                response_tuple = ("500", "erro simulado", None)

        except IOError as e:
            response_tuple = ("500", str(e), None)
            self.logger.error(f"IO error: {str(e)}")
        except OSError as e:
            response_tuple = ("500", str(e), None)
            self.logger.error(f"OS error: {str(e)}")
        except Exception as e:
            response_tuple = ("500", str(e), None)
            self.logger.error(f"Error handling lookup request: {str(e)}")
        finally:
            serialized_response = self.__serializer.serialize(response_tuple)
            conn.sendall(serialized_response)
            conn.close()

    def start_binder(self):
        self.logger.info(f"Binder listening on port {self.__BINDER_PORT}")
        with ThreadPoolExecutor(max_workers=5) as pool:
            while not self.__shutdown_event.is_set():
                try:
                    client_socket, client_address = self.__binder_socket.accept()
                    pool.submit(self.__handle_lookup_request, client_socket)

                except socket.timeout:
                    continue
                except OSError as e:
                    if self.__shutdown_event.is_set():
                        self.logger.info("Binder shutdown event set, stopping server.")
                        break
                    else:
                        self.logger.error(
                            f"Binder server encountered an error while accepting connections: {str(e)}"
                        )
                        self.logger.error("Mission aborted.")
                        break
            exit(1)

    def stop(self):
        self.logger.info("Stopping binder...")
        self.__shutdown_event.set()
        if self.__binder_socket:
            try:
                self.__binder_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.__binder_socket.close()
        self.logger.info("Binder stopped.")

import socket
import struct
from dataclasses import dataclass

# ############# REQUEST ###############
# header
#   protocol_version: 2 byte
#   id_proc: 2 bytes (máx 65000 procs)
#   payload_size: 4 bytes
# payload
#   payload: n bytes
HEADER = struct.Struct("!HHI")

PROTOCOL_VERSION = 0
HEADER_SIZE = HEADER.size


@dataclass
class Request:
    protocol_version: int
    proc_id: int
    payload_size: int
    payload: bytes

    def serialize(self) -> bytes:
        header = HEADER.pack(
            self.protocol_version,
            self.proc_id,
            len(self.payload),
        )

        return header + self.payload

    @classmethod
    def deserialize_header(cls, data: bytes) -> "Request":
        if HEADER.size != len(data):
            raise ValueError("Srpc: Incomplete header")

        protocol_version, proc_id, payload_size = HEADER.unpack_from(data)

        return cls(protocol_version, proc_id, payload_size, None)


# ############# RESPONSE ###############
# header
#   protocol_version: 2 bytes
#   type: 2 bytes
#   payload_size: 4 bytes
# payload
#   payload: n bytes
HEADER = struct.Struct("!HHI")


@dataclass
class Response:
    protocol_version: int
    type: int
    payload_size: int
    payload: bytes

    def serialize(self) -> bytes:
        header = HEADER.pack(
            self.protocol_version,
            self.type,
            len(self.payload),
        )

        return header + self.payload

    @classmethod
    def deserialize_header(cls, data: bytes) -> "Response":
        if HEADER.size != len(data):
            raise ValueError("Srpc: Incomplete header")
        protocol_version, proc_id, payload_size = HEADER.unpack_from(data)

        return cls(protocol_version, proc_id, payload_size, None)


# recive only n bytes , assumes n >= 1
def recv_n(socket: socket, n: int) -> bytes:
    bytes = b""
    len_bytes = 0

    while len_bytes < n:
        new_bytes = socket.recv(n - len_bytes)
        if not new_bytes:
            raise ValueError("Remote host has disconnected, during recv_n execution.")

        bytes += new_bytes
        len_bytes += len(new_bytes)

    assert len_bytes == n

    return bytes


def get_lan_ip_or_localhost():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Try to get LAN IP using the routing table
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        # If there’s no network route, fallback to localhost
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


# Example usage
if __name__ == "__main__":
    print("Detected IP:", get_lan_ip_or_localhost())

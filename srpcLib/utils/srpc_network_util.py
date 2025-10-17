import socket


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

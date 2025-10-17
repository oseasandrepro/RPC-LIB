# This test checks the basic flow of the RPC library by calling the four arithmetic operations
import logging
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from srpcLib.utils.srpc_network_util import get_lan_ip_or_localhost

logger = logging.getLogger(__name__)
SERVER_HOST = get_lan_ip_or_localhost()

LIB_DIR = "srpcLib"
LOG_FILE = "srpc_server_metrics.log"
SERVER_STUB = "srpc_calc_server_stub.py"
CLIENT_STUB = "srpc_calc_client_stub.py"


STUB_GEN_SCRIPT = "srpcLib.tools.srpc_stub_gen"
SERVER_SCRIPT = "run_rpc_server.py"
CLIENT_SCRIPT = "run_rpc_client_divizion_by_zero.py"
INTERFACE_FILE_PATH = "calc/calc_interface.py"
MODULE_DIR = "tests/test_resources/calc/"


def clean():
    files_to_delete = [LOG_FILE, SERVER_STUB, CLIENT_STUB, SERVER_SCRIPT, CLIENT_SCRIPT]

    if os.path.exists(Path("calc/")):
        shutil.rmtree("calc/")

    for file in files_to_delete:
        if os.path.exists(Path(file)):
            os.remove(file)


def wait_for_server(host, port, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
    raise RuntimeError("Server did not start in time")


def test_division_by_zero_exception():
    try:
        time.sleep(5)
        clean()

        shutil.copytree(MODULE_DIR, "calc/")
        shutil.copy("tests/integration/run_rpc_server.py", SERVER_SCRIPT)
        shutil.copy(
            "tests/integration/run_rpc_client_divizion_by_zero.py", CLIENT_SCRIPT
        )

        # Gen Stubs
        subprocess.run(
            [
                sys.executable,
                "-m",
                f"{STUB_GEN_SCRIPT}",
                f"{INTERFACE_FILE_PATH}",
                f"{SERVER_HOST}",
            ],
            check=True,
        )

        # lunch server
        server_proc = subprocess.Popen([sys.executable, f"{SERVER_SCRIPT}"])

        assert os.path.exists(CLIENT_STUB)
        assert os.path.exists(SERVER_STUB)

        wait_for_server(SERVER_HOST, 5000)
        # run client
        client_proc = subprocess.run(
            [sys.executable, CLIENT_SCRIPT], text=True, capture_output=True, check=True
        )

        expected_output = "ZeroDivisionError: division by zero"
        assert client_proc.stdout.splitlines()[-1] == expected_output

        server_proc.kill()
        server_proc.wait(timeout=5)
    except Exception as e:
        pytest.fail(f"Error during integration test: {e}")
    finally:
        clean()

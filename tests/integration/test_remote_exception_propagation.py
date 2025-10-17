# This test checks the basic flow of the RPC library by calling the four arithmetic operations
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)
SERVER_HOST = "127.0.1.1"
SERVER_PORT = 5000

LIB_DIR = "srpcLib"
LOG_FILE = "srpc_server_metrics.log"
SERVER_STUB = "srpc_calc_server_stub.py"
CLIENT_STUB = "srpc_calc_client_stub.py"


STUB_GEN_SCRIPT = "srpc_stub_gen.py"
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


def test_division_by_zero_exception():
    try:
        clean()

        shutil.copytree(MODULE_DIR, "calc/")
        shutil.copy("tests/integration/run_rpc_server.py", SERVER_SCRIPT)
        shutil.copy("tests/integration/run_rpc_client_divizion_by_zero.py", CLIENT_SCRIPT)

        stub_gen_input = f"{INTERFACE_FILE_PATH}\n{SERVER_HOST}"
        subprocess.run(
            [sys.executable, f"{LIB_DIR}/{STUB_GEN_SCRIPT}"],
            input=stub_gen_input,
            text=True,
            check=True,
        )

        assert os.path.exists(SERVER_STUB)
        assert os.path.exists(CLIENT_STUB)

        # launch server
        server_proc = subprocess.Popen(
            [sys.executable, SERVER_SCRIPT], stdout=None, stderr=None, text=True
        )

        time.sleep(0.5)

        # run client
        client_proc = subprocess.run(
            [sys.executable, CLIENT_SCRIPT], text=True, capture_output=True, check=True
        )

        expected_output = "ZeroDivisionError: division by zero"
        assert client_proc.stdout.splitlines()[-1] == expected_output

    except Exception as e:
        pytest.fail(f"Error during integration test: {e}")
    finally:
        try:
            server_proc.terminate()
        except Exception:
            pass
        clean()

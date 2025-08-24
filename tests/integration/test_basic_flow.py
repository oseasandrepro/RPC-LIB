#This test checks the basic flow of the RPC library by calling the four arithmetic operations
import subprocess
import sys
import os
import time
import pytest
import shutil
import socket
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
INTEGRATION_TEST_WORK_DIR = "./integrationTestWorkDir"
STUB_GEN_SCRIPT = "src/srpc_gen.py"
SERVER_SCRIPT = f"{INTEGRATION_TEST_WORK_DIR}/run_rpc_server.py"
CLIENT_SCRIPT = f"{INTEGRATION_TEST_WORK_DIR}/run_rpc_client.py"
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 500

def seting_up():
    shutil.copytree("./src/binder", f"{INTEGRATION_TEST_WORK_DIR}/binder")
    shutil.copytree("./src/interface", f"{INTEGRATION_TEST_WORK_DIR}/interface")
    shutil.copytree("./src/utils", f"{INTEGRATION_TEST_WORK_DIR}/utils")
    shutil.copy("./src/srpc_exceptions.py", f"{INTEGRATION_TEST_WORK_DIR}/srpc_exceptions.py")
    shutil.copy("./tests/integration/run_rpc_server.py", f"{INTEGRATION_TEST_WORK_DIR}/run_rpc_server.py")
    shutil.copy("./tests/integration/run_rpc_client.py", f"{INTEGRATION_TEST_WORK_DIR}/run_rpc_client.py")
    shutil.copy("./tests/test_resources/calc_interface.py", f"{INTEGRATION_TEST_WORK_DIR}/calc_interface.py")
    shutil.copy("./tests/test_resources/calc.py", f"{INTEGRATION_TEST_WORK_DIR}/calc.py")

def clean():
    if os.path.exists(INTEGRATION_TEST_WORK_DIR):
        shutil.rmtree(INTEGRATION_TEST_WORK_DIR)


def wait_for_server(host, port, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.1)
    return False

def test_basic_rpc_flow():
    clean()
    try:
        seting_up()

        stub_gen_input = f"{ROOT}/tests/test_resources/calc_interface.py\n127.0.0.1"
        subprocess.run(
            [sys.executable, STUB_GEN_SCRIPT],
            input=stub_gen_input,
            text=True,
            check=True
        )

        stub_client = ROOT / "calc_rpc_client_stub.py"
        stub_server = ROOT / "calc_rpc_server_stub.py"
        assert stub_client.exists()
        assert stub_server.exists()

        shutil.copy(stub_client, INTEGRATION_TEST_WORK_DIR / "calc_rpc_client_stub.py")
        shutil.copy(stub_server, INTEGRATION_TEST_WORK_DIR / "calc_rpc_server_stub.py")

        # launch server
        server_proc = subprocess.Popen(
            [sys.executable, SERVER_SCRIPT],
            stdout=None, stderr=None, text=True
        )

        assert wait_for_server(SERVER_HOST, SERVER_PORT), "Server did not start in time"

        # run client
        client_proc = subprocess.run(
            [sys.executable, CLIENT_SCRIPT],
            text=True,
            capture_output=True,
            check=True
        )

        expected_output = ["6", "8", "2", "2.0"]
        assert client_proc.stdout.splitlines() == expected_output

    except Exception as e:
        pytest.fail(f"Error during integration test: {e}")
    finally:
        try:
            server_proc.terminate()
            server_proc.wait(timeout=3)
        except Exception:
            pass
        clean()

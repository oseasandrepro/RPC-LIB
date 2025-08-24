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
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000


def test_basic_rpc_flow():
    try:
        clean()
        time.sleep(1)
        seting_up()
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        stub_gen_input = f"./tests/test_resources/calc_interface.py\n{ip_address}"
        stup_gen_proc = subprocess.run(
            [sys.executable, STUB_GEN_SCRIPT],
            input=stub_gen_input,
            text=True,
            capture_output=True,
            check=True
        )

        time.sleep(1)
        assert True == os.path.exists("calc_rpc_client_stub.py")
        assert True == os.path.exists("calc_rpc_server_stub.py")
        shutil.copy("./calc_rpc_client_stub.py", f"{INTEGRATION_TEST_WORK_DIR}/calc_rpc_client_stub.py")
        shutil.copy("./calc_rpc_server_stub.py", f"{INTEGRATION_TEST_WORK_DIR}/calc_rpc_server_stub.py")
        os.remove("./calc_rpc_client_stub.py")
        os.remove("./calc_rpc_server_stub.py")

        logger.info("Integration test environment ready...")

        
        server_proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True 
        )
        logger.info("Server process lunched")

        time.sleep(1)  # wait for the server to start
        client_proc = subprocess.run(
            [sys.executable, CLIENT_SCRIPT],
            text=True,
            capture_output=True,
            check=True
        )
        logger.info("Client process lunched")

        lines = client_proc.stdout.splitlines()
        expected_output = ["6", "8", "2", "2.0"]
        index = 0
        for line in lines:
            assert line == expected_output[index]
            index += 1
        

        print("integration test sucefully finished.")
    except Exception as e:
        pytest.fail(f"Error during intergration test: {str(e)}")
    finally:
        clean()
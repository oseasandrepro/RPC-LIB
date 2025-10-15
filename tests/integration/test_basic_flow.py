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

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
INTEGRATION_TEST_WORK_DIR = ROOT / "integrationTestWorkDir"
STUB_GEN_SCRIPT = ROOT / "src/srpc_stub_gen.py"
SERVER_SCRIPT = f"{INTEGRATION_TEST_WORK_DIR}/run_rpc_server.py"
CLIENT_SCRIPT = f"{INTEGRATION_TEST_WORK_DIR}/run_rpc_client.py"

SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 500


def seting_up():
    shutil.copytree("./src/binder", f"{INTEGRATION_TEST_WORK_DIR}/binder")
    shutil.copytree("./src/interface", f"{INTEGRATION_TEST_WORK_DIR}/interface")
    shutil.copytree("./src/utils", f"{INTEGRATION_TEST_WORK_DIR}/utils")
    shutil.copytree("./src/metrics", f"{INTEGRATION_TEST_WORK_DIR}/metrics")
    shutil.copy("./src/srpc_exceptions.py", f"{INTEGRATION_TEST_WORK_DIR}/srpc_exceptions.py")
    shutil.copy(
        "./tests/integration/run_rpc_server.py",
        f"{INTEGRATION_TEST_WORK_DIR}/run_rpc_server.py",
    )
    shutil.copy(
        "./tests/integration/run_rpc_client.py",
        f"{INTEGRATION_TEST_WORK_DIR}/run_rpc_client.py",
    )
    shutil.copy(
        "./tests/test_resources/calc_interface.py",
        f"{INTEGRATION_TEST_WORK_DIR}/calc_interface.py",
    )
    shutil.copy("./tests/test_resources/calc.py", f"{INTEGRATION_TEST_WORK_DIR}/calc.py")


def clean():
    if os.path.exists(INTEGRATION_TEST_WORK_DIR):
        shutil.rmtree(INTEGRATION_TEST_WORK_DIR)


def test_basic_rpc_flow():
    clean()
    try:
        seting_up()

        stub_gen_input = f"{ROOT}/tests/test_resources/calc_interface.py\n{SERVER_HOST}"
        subprocess.run(
            [sys.executable, str(STUB_GEN_SCRIPT)],
            cwd=str(INTEGRATION_TEST_WORK_DIR),
            input=stub_gen_input,
            text=True,
            check=True,
        )

        stub_client = INTEGRATION_TEST_WORK_DIR / "srpc_calc_client_stub.py"
        stub_server = INTEGRATION_TEST_WORK_DIR / "srpc_calc_server_stub.py"
        assert stub_client.exists()
        assert stub_server.exists()

        # launch server
        server_proc = subprocess.Popen(
            [sys.executable, SERVER_SCRIPT], stdout=None, stderr=None, text=True
        )

        time.sleep(3)

        # run client
        client_proc = subprocess.run(
            [sys.executable, CLIENT_SCRIPT], text=True, capture_output=True, check=True
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

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from srpcLib.utils.srpc_network_util import get_lan_ip_or_localhost

# Paths
ROOT_DIR = Path(__file__).resolve().parents[2]  # rpc-lib/
TEST_PROJECT = ROOT_DIR / "tests/integration/simple_project"
STUB_GEN_SCRIPT = "srpcLib.tools.srpc_stub_gen"
SERVER_STUB_SCRIPT = "srpc_calc_server_stub.py"
CLIENT_STUB_SCRIPT = "srpc_calc_client_stub.py"
INTERFACE_DEF = TEST_PROJECT / "calc/calc_interface.py"

SERVER_SCRIPT = "server.py"
CLIENT_SCRIPT = "client.py"
CLIENT_SCRIPT_DIVISION_BY_ZERO = "run_rpc_client_divizion_by_zero.py"

LOG_FILE = "srpc_server_metrics.log"

# Network
SERVER_HOST = get_lan_ip_or_localhost()
SERVER_PORT = 5000


def wait_for_server(host, port, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
    raise RuntimeError("Server did not start in time")


@pytest.fixture(scope="session", autouse=True)
def install_lib():
    """
    Install the library into the test_project virtual environment context.
    """
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", str(ROOT_DIR)],
        cwd=TEST_PROJECT,
        check=True,
    )


@pytest.fixture(scope="session", autouse=True)
def generate_stubs():
    """
    Run the stub generator as a CLI tool inside test_project.
    """
    result = subprocess.run(
        [sys.executable, "-m", f"{STUB_GEN_SCRIPT}", f"{INTERFACE_DEF}"],
        cwd=TEST_PROJECT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Stub generation failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    # Assert generated scripts exist
    server_file = TEST_PROJECT / SERVER_STUB_SCRIPT
    client_file = TEST_PROJECT / CLIENT_STUB_SCRIPT
    assert server_file.exists(), f"Missing server stub: {server_file}"
    assert client_file.exists(), f"Missing client stub: {client_file}"
    return TEST_PROJECT


@pytest.fixture(scope="session")
def server_process(generate_stubs, request):
    """
    Launch the server once for the entire test session.
    """
    proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        cwd=generate_stubs,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    wait_for_server(SERVER_HOST, SERVER_PORT)  # give server time to boot

    if proc.poll() is not None:
        out, err = proc.communicate()
        raise RuntimeError(f"Server failed to start.\nSTDOUT:\n{out}\nSTDERR:\n{err}")

    def finalizer():
        """Terminate server and clean generated files."""
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

        # Remove stubs and log file
        for f in [SERVER_STUB_SCRIPT, CLIENT_STUB_SCRIPT, LOG_FILE]:
            file_path = generate_stubs / f
            if file_path.exists():
                file_path.unlink()

    request.addfinalizer(finalizer)
    yield proc


def test_rpc_the_for_operations_of_calc(server_process, generate_stubs):
    result = subprocess.run(
        [sys.executable, CLIENT_SCRIPT],
        cwd=generate_stubs,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    expected_output = "6\n8\n2\n2.0"
    assert (
        result.stdout.strip() == expected_output
    ), f"Expected:\n{expected_output}\nGot:\n{result.stdout.strip()}"


def test_rpc_remote_exception_propagation(server_process, generate_stubs):
    result = subprocess.run(
        [sys.executable, CLIENT_SCRIPT_DIVISION_BY_ZERO],
        cwd=generate_stubs,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    expected_output = "ZeroDivisionError: division by zero"
    assert result.stdout.splitlines()[-1] == expected_output

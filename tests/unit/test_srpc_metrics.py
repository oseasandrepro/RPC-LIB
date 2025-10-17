import subprocess
import sys
from pathlib import Path
from time import sleep

ROOT_DIR = Path(__file__).resolve().parents[2]  # rpc-lib/
TEST_DIR = ROOT_DIR / "tests/unit/"
LOG_FILE = TEST_DIR / "test_metrics.log"
METRIC_LOGGER_SCRIPT = "run_metric_logger.py"


def test_srpc_metrics():
    subprocess.Popen(
        [sys.executable, METRIC_LOGGER_SCRIPT],
        cwd=TEST_DIR,
        stdout=None,
        stderr=None,
        text=True,
    )

    sleep(1)

    with open(LOG_FILE, "r") as f:
        metric = f.readline().split(" ")[4]
        assert metric == "test_function.counter_success=1\n"

        metric = f.readline().split(" ")[4]
        assert metric == "test_function.counter_fail=1\n"

        metric = f.readline().split(" ")[4]
        assert metric == "test_function.time=123.0\n"

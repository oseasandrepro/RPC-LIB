import os
import shutil
import subprocess
import sys
from pathlib import Path
from time import sleep

ROOT = Path(__file__).resolve().parent.parent.parent
INTEGRATION_TEST_WORK_DIR = ROOT / "testmetricsDir"
LOG_PATH = "test_metrics.log"
METRIC_LOGGER_SCRIPT = f"{INTEGRATION_TEST_WORK_DIR}/run_metric_logger.py"


def seting_up():
    shutil.copytree("./src/binder", f"{INTEGRATION_TEST_WORK_DIR}/binder")
    shutil.copytree("./src/interface", f"{INTEGRATION_TEST_WORK_DIR}/interface")
    shutil.copytree("./src/utils", f"{INTEGRATION_TEST_WORK_DIR}/utils")
    shutil.copytree("./src/metrics", f"{INTEGRATION_TEST_WORK_DIR}/metrics")
    shutil.copy("./src/srpc_exceptions.py", f"{INTEGRATION_TEST_WORK_DIR}/srpc_exceptions.py")
    shutil.copy(
        "./tests/integration/run_metric_logger.py",
        f"{INTEGRATION_TEST_WORK_DIR}/run_metric_logger.py",
    )


def clean():
    if os.path.exists(INTEGRATION_TEST_WORK_DIR):
        shutil.rmtree(INTEGRATION_TEST_WORK_DIR)

    if os.path.exists("test_metrics.log"):
        os.remove("test_metrics.log")


def test_srpc_metrics():
    clean()
    seting_up()

    subprocess.Popen([sys.executable, METRIC_LOGGER_SCRIPT], stdout=None, stderr=None, text=True)

    sleep(0.1)

    with open(LOG_PATH, "r") as f:
        metric = f.readline().split(" ")[4]
        assert metric == "test_function.counter_success=1\n"

        metric = f.readline().split(" ")[4]
        assert metric == "test_function.counter_fail=1\n"

        metric = f.readline().split(" ")[4]
        assert metric == "test_function.time=123.0\n"

    clean()

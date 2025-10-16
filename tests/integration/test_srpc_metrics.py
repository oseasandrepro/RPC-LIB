import os
import shutil
import subprocess
import sys
from time import sleep

LOG_FILE = "test_metrics.log"
METRIC_LOGGER_SCRIPT = "run_metric_logger.py"


def clean():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    if os.path.exists(METRIC_LOGGER_SCRIPT):
        os.remove(METRIC_LOGGER_SCRIPT)


def test_srpc_metrics():
    clean()

    shutil.copy("./tests/integration/run_metric_logger.py", "run_metric_logger.py")

    subprocess.Popen([sys.executable, METRIC_LOGGER_SCRIPT], stdout=None, stderr=None, text=True)

    sleep(0.1)

    with open(LOG_FILE, "r") as f:
        metric = f.readline().split(" ")[4]
        assert metric == "test_function.counter_success=1\n"

        metric = f.readline().split(" ")[4]
        assert metric == "test_function.counter_fail=1\n"

        metric = f.readline().split(" ")[4]
        assert metric == "test_function.time=123.0\n"

    clean()

import logging

from interface.srpc_metrics_interface import SrpcMetricsInterface
from metrics.srpc_metrics_types import SrpcmetricsTypes


class SrpcMetric(SrpcMetricsInterface):
    def __init__(self, log_path: str):
        self.__mestrics = []

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)
        self.__file_handler = logging.FileHandler(log_path)
        self.__formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        self.__file_handler.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__file_handler)

    def add_metric(self, metric_name, metric_type):
        self.__mestrics.append((f"{metric_name}.{metric_type}"))

    def inc_counter_sucess(self, metric_name):
        if f"{metric_name}.{SrpcmetricsTypes.COUNTER_SUCCESS}" in self.__mestrics:
            self.__logger.info(f"{metric_name}.{SrpcmetricsTypes.COUNTER_SUCCESS}=1")

    def inc_counter_fail(self, metric_name):
        if f"{metric_name}.{SrpcmetricsTypes.COUNTER_FAIL}" in self.__mestrics:
            self.__logger.info(f"{metric_name}.{SrpcmetricsTypes.COUNTER_FAIL}=1")

    def record_time(self, metric_name, time_taken):
        if f"{metric_name}.time" in self.__mestrics:
            self.__logger.info(
                f"{metric_name}.{SrpcmetricsTypes.TIME}={round(time_taken * 1000, 3)}"
            )

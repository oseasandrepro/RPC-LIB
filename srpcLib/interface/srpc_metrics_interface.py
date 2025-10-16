from abc import ABC, abstractmethod


class SrpcMetricsInterface(ABC):
    @abstractmethod
    def __init__(self, log_path: str, mestrics: dict):
        pass

    @abstractmethod
    def add_metric(self, metric_name: str, metric_type: str):
        pass

    @abstractmethod
    def inc_counter_success(self, metric_name: str):
        pass

    @abstractmethod
    def inc_counter_fail(self, metric_name: str):
        pass

    @abstractmethod
    def record_time(self, metric_name: str, time_taken: float):
        pass

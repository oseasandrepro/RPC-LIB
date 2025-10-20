from srpcLib.metrics.srpc_metric import SrpcMetric
from srpcLib.metrics.srpc_metrics_types import SrpcmetricsTypes

LOG_PATH = "test_metrics.log"

test_metric = SrpcMetric(LOG_PATH)
test_metric.add_metric("test_function", SrpcmetricsTypes.COUNTER_SUCCESS)
test_metric.add_metric("test_function", SrpcmetricsTypes.COUNTER_FAIL)
test_metric.add_metric("test_function", SrpcmetricsTypes.TIME)

test_metric.inc_counter_success("test_function")
test_metric.inc_counter_fail("test_function")
test_metric.record_time("test_function", 0.123)

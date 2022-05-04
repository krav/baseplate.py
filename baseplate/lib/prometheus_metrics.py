from typing import Any
from typing import Dict

from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram


# default_buckets creates the default bucket values for histogram metrics.
# we want this to match the baseplate.go default_buckets, ref: https://github.com/reddit/baseplate.go/blob/master/prometheusbp/metrics.go.
# start is the value of the lowest bucket.
# factor is amount to multiply the previous bucket by to get the value for the next bucket.
# count is the number of buckets created.
start = 0.0001
factor = 2.5
count = 14
# creates 14 buckets from 100us ~ 14.9s.
default_buckets = [start * factor ** i for i in range(count)]


# thrift server labels
thrift_server_latency_labels = [
    "thrift_method",
    "thrift_success",
]
thrift_server_requests_total_labels = [
    "thrift_method",
    "thrift_success",
    "thrift_exception_type",
    "thrift_baseplate_status",
    "thrift_baseplate_status_code",
]
thrift_server_active_requests_labels = ["thrift_method"]

# thrift server metrics
thrift_server_latency_seconds = Histogram(
    "thrift_server_latency_seconds",
    "RPC latencies",
    thrift_server_latency_labels,
    buckets=default_buckets,
)
thrift_server_requests_total = Counter(
    "thrift_server_requests_total",
    "Total RPC request count",
    thrift_server_requests_total_labels,
)
thrift_server_active_requests = Gauge(
    "thrift_server_active_requests",
    "The number of in-flight requests being handled by the service",
    thrift_server_active_requests_labels,
)


class PrometheusThriftServerMetrics:
    def __init__(self) -> None:
        pass

    def latency_seconds_metric(self, tags: Dict[str, str]) -> Any:
        """Return the latency_seconds metrics with labels set"""
        return thrift_server_latency_seconds.labels(
            thrift_method=tags.get("thrift.method", ""),
            thrift_success=tags.get("success", ""),
        )

    def requests_total_metric(self, tags: Dict[str, str]) -> Any:
        """Return the requests_total metrics with labels set"""
        return thrift_server_requests_total.labels(
            thrift_method=tags.get("thrift.method", ""),
            thrift_success=tags.get("success", ""),
            thrift_exception_type=tags.get("exception_type", ""),
            thrift_baseplate_status=tags.get("thrift.status", ""),
            thrift_baseplate_status_code=tags.get("thrift.status_code", ""),
        )

    def active_requests_metric(self, tags: Dict[str, str]) -> Any:
        """Return the active_requests metrics with labels set"""
        return thrift_server_active_requests.labels(
            thrift_method=tags.get("thrift.method", ""),
        )

    def get_latency_seconds_metric(self) -> Histogram:
        """Return the latency_seconds metrics"""
        return thrift_server_latency_seconds

    def get_requests_total_metric(self) -> Counter:
        """Return the requests_total metrics"""
        return thrift_server_requests_total

    def get_active_requests_metric(self) -> Gauge:
        """Return the active_requests metrics"""
        return thrift_server_active_requests


# http server labels and metrics
http_server_histogram_labels = [
    "http_method",
    "http_endpoint",
    "http_success",
]
http_server_requests_total_labels = [
    "http_method",
    "http_endpoint",
    "http_success",
    "http_response_code",
]
http_server_active_requests_labels = [
    "http_method",
    "http_endpoint",
]

http_server_latency_seconds = Histogram(
    "http_server_latency_seconds",
    "Time spent processing requests",
    http_server_histogram_labels,
    buckets=default_buckets,
)

http_server_requests_total = Counter(
    "http_server_requests_total",
    "Total number of request handled",
    http_server_requests_total_labels,
)
http_server_active_requests = Gauge(
    "http_server_active_requests",
    "Current requests in flight",
    http_server_active_requests_labels,
)


class PrometheusHTTPServerMetrics:
    def __init__(self) -> None:
        pass

    def latency_seconds_metric(self, tags: Dict[str, str]) -> Any:
        return http_server_latency_seconds.labels(
            http_method=tags.get("http.method", ""),
            http_endpoint=tags.get("http.route", ""),
            http_success=getHTTPSuccessLabel(int(tags.get("http.status_code", "0"))),
        )

    def requests_total_metric(self, tags: Dict[str, str]) -> Any:
        return http_server_requests_total.labels(
            http_method=tags.get("http.method", ""),
            http_endpoint=tags.get("http.route", ""),
            http_success=getHTTPSuccessLabel(int(tags.get("http.status_code", "0"))),
            http_response_code=tags.get("http.status_code", ""),
        )

    def active_requests_metric(self, tags: Dict[str, str]) -> Any:
        return http_server_active_requests.labels(
            http_method=tags.get("http.method", ""),
            http_endpoint=tags.get("http.route", ""),
        )

    def get_latency_seconds_metric(self) -> Any:
        return http_server_latency_seconds

    def get_requests_total_metric(self) -> Any:
        return http_server_requests_total

    def get_active_requests_metric(self) -> Any:
        return http_server_active_requests


def getHTTPSuccessLabel(httpStatusCode: int) -> str:
    """
    The HTTP success label is "true" if the status code is 2xx or 3xx, "false" otherwise.
    """
    return str(httpStatusCode >= 200 < 400).lower()

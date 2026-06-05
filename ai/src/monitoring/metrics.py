"""Prometheus metrics for the API.

Exposes counters/histograms that can be scraped via `/api/v1/metrics`.
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram

API_REQUESTS_TOTAL = Counter(
    "api_requests_total",
    "Total API requests",
    labelnames=("endpoint", "status"),
)

API_REQUEST_DURATION_SECONDS = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    labelnames=("endpoint",),
)

CLASSIFICATION_CONFIDENCE = Histogram(
    "classification_confidence",
    "Classification confidence score",
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)

CACHE_HITS_TOTAL = Counter(
    "cache_hits_total",
    "Total cache hits",
    labelnames=("endpoint",),
)

CACHE_MISSES_TOTAL = Counter(
    "cache_misses_total",
    "Total cache misses",
    labelnames=("endpoint",),
)

MODEL_RELOADS_TOTAL = Counter(
    "model_reloads_total",
    "Total model reload attempts",
    labelnames=("status",),
)

RATE_LIMITED_TOTAL = Counter(
    "rate_limited_total",
    "Total rate-limited requests",
    labelnames=("endpoint",),
)

import time
import structlog

logger = structlog.get_logger(__name__)

class PerformanceTracker:
    def __init__(self, request):
        self.request = request
        self.segments = {}

    def start(self, name: str):
        self.segments[name] = time.time()

    def end(self, name: str):
        start = self.segments.get(name)
        if not start:
            return
        duration_ms = int((time.time() - start) * 1000)
        logger.debug(
            "performance_segment",
            segment=name,
            duration_ms=duration_ms
        )

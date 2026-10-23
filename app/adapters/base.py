import abc
import time
from typing import Any, Dict, Optional
from app.config import settings, logger

class BaseAdapter(abc.ABC):
    """Abstract base class for all external service adapters."""

    def __init__(self, name: str):
        self.name = name
        self.is_demo_mode = settings.demo_mode

    @abc.abstractmethod
    def is_configured(self) -> bool:
        """Return True if real credentials for the adapter are configured."""
        pass

    @abc.abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Perform a non-destructive connection and health verification."""
        pass

    def execute_with_retry(self, operation, max_retries: int = 3, backoff_factor: float = 0.5, *args, **kwargs):
        """Execute an external operation with exponential backoff and error tracking."""
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                start_time = time.time()
                result = operation(*args, **kwargs)
                duration = time.time() - start_time
                return {
                    "success": True,
                    "attempt": attempt,
                    "duration_seconds": round(duration, 3),
                    "data": result
                }
            except Exception as e:
                last_error = e
                logger.warning(f"[{self.name}] Attempt {attempt}/{max_retries} failed: {str(e)}")
                if attempt < max_retries:
                    sleep_time = backoff_factor * (2 ** (attempt - 1))
                    time.sleep(sleep_time)

        logger.error(f"[{self.name}] All {max_retries} attempts failed: {str(last_error)}")
        return {
            "success": False,
            "attempt": max_retries,
            "error": str(last_error)
        }

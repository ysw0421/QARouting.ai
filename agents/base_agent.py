import logging
from typing import Any, Dict

class BaseAgent:
    logger = logging.getLogger("Agent")

    def success(self, data: Any) -> Dict:
        return {"success": True, "data": data, "error": None}

    def fail(self, error: str) -> Dict:
        self.logger.error(error)
        return {"success": False, "data": None, "error": error} 
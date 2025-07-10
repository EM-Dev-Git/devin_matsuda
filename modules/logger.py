import logging
import json
from datetime import datetime
from typing import Any, Dict
import os
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

class APILogger:
    def __init__(self):
        self.logger = logging.getLogger("api_logger")
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def log_request(self, endpoint: str, method: str, user_id: str = None, request_body: Dict[str, Any] = None):
        log_data = {
            "type": "REQUEST",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "request_body": request_body
        }
        self.logger.info(f"REQUEST: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_response(self, endpoint: str, method: str, status_code: int, user_id: str = None, 
                    response_body: Dict[str, Any] = None, processing_time: float = None):
        log_data = {
            "type": "RESPONSE",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "user_id": user_id,
            "response_body": response_body,
            "processing_time_ms": processing_time * 1000 if processing_time else None
        }
        self.logger.info(f"RESPONSE: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_error(self, endpoint: str, method: str, error: str, user_id: str = None):
        log_data = {
            "type": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "error": error
        }
        self.logger.error(f"ERROR: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_auth_attempt(self, user_id: str, success: bool, ip_address: str = None):
        log_data = {
            "type": "AUTH_ATTEMPT",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address
        }
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, f"AUTH: {json.dumps(log_data, ensure_ascii=False)}")

api_logger = APILogger()

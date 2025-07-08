from typing import Dict, List
from datetime import datetime
import uuid
from schema.lim import LogEntry


class LogManager:
    def __init__(self):
        self.logs: Dict[str, LogEntry] = {}
    
    def create_log_entry(self, request_body: dict, response_body: dict, 
                        processing_time_ms: float, status: str) -> LogEntry:
        log_id = str(uuid.uuid4())
        log_entry = LogEntry(
            id=log_id,
            timestamp=datetime.now(),
            request_body=request_body,
            response_body=response_body,
            processing_time_ms=processing_time_ms,
            status=status
        )
        self.logs[log_id] = log_entry
        return log_entry
    
    def get_all_logs(self) -> List[LogEntry]:
        return sorted(list(self.logs.values()), key=lambda x: x.timestamp, reverse=True)
    
    def get_log(self, log_id: str) -> LogEntry:
        return self.logs.get(log_id)
    
    def clear_logs(self) -> int:
        count = len(self.logs)
        self.logs.clear()
        return count


log_manager = LogManager()

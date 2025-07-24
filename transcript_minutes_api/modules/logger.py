<<<<<<< HEAD
import logging
import os
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")

def setup_logger():
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()
||||||| ab1cd5e
=======
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("transcript_minutes_api")

def log_request(user_id: str, endpoint: str, method: str):
    logger.info(f"Request - User: {user_id}, Endpoint: {endpoint}, Method: {method}")

def log_error(user_id: str, error: str, details: str = None):
    error_msg = f"Error - User: {user_id}, Error: {error}"
    if details:
        error_msg += f", Details: {details}"
    logger.error(error_msg)

def log_auth_attempt(username: str, success: bool):
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Authentication attempt - Username: {username}, Status: {status}")

def log_openai_request(user_id: str, transcript_length: int):
    logger.info(f"OpenAI request - User: {user_id}, Transcript length: {transcript_length} characters")
>>>>>>> af772fe42f0bc45e327e1468df85f437de342f3b

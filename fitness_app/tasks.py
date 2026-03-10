

from celery import shared_task
from celery.utils.log import get_task_logger 
from .user_tasks import * 

logger = get_task_logger(__name__)

@shared_task
def test_task():
    logger.info("Task chal raha hai!")
    return "Success!"

@shared_task
def add_numbers(x, y):
    result = x + y
    logger.info(f"Result: {result}")
    return result
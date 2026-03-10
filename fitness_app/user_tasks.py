

from celery import shared_task
from celery.utils.log import get_task_logger 
from.models import Signup 

logger = get_task_logger(__name__)




@shared_task 
def new():

    obj=Signup.objects.all() 

    for i in obj: 
        print(f"User name: {i.username}") 

        











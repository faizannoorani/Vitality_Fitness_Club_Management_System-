from django.test import TestCase
from .models import Centre  
from .serializers import CentreGetSerializer
from .user_tasks import user_task 

class TestCentreModel(TestCase):

    def test_create_model(self):
        c = Centre.objects.create(
            Centre_name="Vitality_centre",
            Centre_address="xyz",
            phone_no="098775"
        )

        ser=CentreGetSerializer(c) 
        self.assertEqual(set(ser.data.keys()), {"Centre_name", "Centre_address", "phone_no"})

        








        
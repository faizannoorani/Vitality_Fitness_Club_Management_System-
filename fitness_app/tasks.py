


from celery import shared_task
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from .models import Signup

@shared_task
def send_welcome_email(email):

    user = Signup.objects.filter(email=email).first()
    
    if not user:
        print("User not found")
        return

    name = user.username
    message = Mail(
        from_email=settings.EMAIL_FROM,
        to_emails=email,
        subject=f"Welcome {name} to Vitality Fitness Club",
        plain_text_content=f"Welcome {name}! to our Fitness Club"
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        print("Status Code:", response.status_code)
        print("Response Body:", response.body)
        print(f"Email sent successfully to {name} 🔥")

    except Exception as e:
        print("Email sending failed ❌:", str(e))





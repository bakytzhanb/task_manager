from celery import shared_task
from django.core.mail import send_mail

from task_manager import settings


@shared_task
def celery_send_email(subject, message, target_mail):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[target_mail],
    )

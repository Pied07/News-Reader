from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Subscription_Model
from django.template.loader import render_to_string

@shared_task
def sending_mails(subject,message,from_mail,recipient_lists):
    try:
        send_mail(subject,message,from_mail,recipient_lists,fail_silently=False)
        return True
    except:
        return False
    
@shared_task
def expire_subscriptions():
    now = timezone.now()
    expire_subscription = Subscription_Model.objects.filter(subscription_end__lt = now , subscription=True)
    for subscription in expire_subscription:
        user = subscription.user
        plan = subscription.subscription_type
        email = subscription.user.email
        subscription.delete()
        subject = f"Dear {user} your subscription validity has been expired"
        message = render_to_string('expired.html',{'user':user,'type':plan})
        sending_mails(subject,message,'',[email])
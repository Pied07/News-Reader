from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta



# Create your models here.
class Subscription_Model(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.BooleanField(default=False)
    subscription_start = models.DateTimeField(auto_now=True)
    subscription_end = models.DateTimeField(null=True)
    subscription_type = models.CharField(max_length=10,default="monthly")

    def save(self,*args, **kwargs):
        if self.subscription and self.subscription_type:
            if self.subscription_type == "monthly":
                self.subscription_end = self.subscription_start + timedelta(days=30)
            elif self.subscription_type == "yearly":
                self.subscription_end = self.subscription_start + timedelta(days=365)
            super().save(*args,**kwargs)

    def __str__(self):
        return self.user.username
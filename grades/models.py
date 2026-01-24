from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Grades(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    weight = models.FloatField(default=1)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} | {self.subject} | {self.grade}"
    
class SkolaOnlineProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sol_username = models.CharField(max_length=100)
    sol_password = models.CharField(max_length=100)



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        from .models import SkolaOnlineProfile
        SkolaOnlineProfile.objects.create(user=instance)
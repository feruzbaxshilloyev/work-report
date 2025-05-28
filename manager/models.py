from django.db import models
from django.contrib.auth.models import User


class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    kompaniya = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile_images/', default='default.png', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Message(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    sarlavha = models.CharField(max_length=255)
    matn = models.TextField()
    is_view = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha

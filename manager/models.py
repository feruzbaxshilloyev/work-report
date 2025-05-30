from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from worker.models import Worker


class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    kompaniya = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile_images/', default='default.png', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Message(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    sarlavha = models.CharField(max_length=255)
    matn = models.TextField()
    is_view = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.ManyToManyField(Worker, blank=True)

    def __str__(self):
        return self.sarlavha

    def add_view(self, worker):
        self.views.add(worker)


class MonthlyPayment(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE,)
    summa= models.DecimalField(max_digits=20, decimal_places=2)  # To‘lov summasi
    sana = models.DateField(default=timezone.now)  # To‘lov sanasi
    created = models.DateTimeField(auto_now_add=True)  # Yaratilgan vaqt
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # To‘lovni amalga oshirgan manager

    def save(self, *args, **kwargs):
        # To‘lov summasini Worker.total_earned dan ayirish
        self.worker.tolangan += self.summa
        if self.worker.tolangan < 0:
            self.worker.tolangan = Decimal('0')
        self.worker.qoldiq = self.worker.ishlangan - self.worker.tolangan
        self.worker.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.worker} - {self.summa} so‘m ({self.sana})"

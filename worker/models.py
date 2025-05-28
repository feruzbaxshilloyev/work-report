from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Worker(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='as_worker')
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    ism = models.CharField(max_length=100)
    familiya = models.CharField(max_length=100)
    worker_id = models.IntegerField(unique=True)
    password = models.CharField(max_length=128)
    image = models.ImageField(upload_to='worker_images/', blank=True, null=True)
    is_login = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.worker_id:
            last_worker = Worker.objects.all().order_by('worker_id').last()
            if last_worker:
                self.worker_id = last_worker.worker_id + 1
            else:
                self.worker_id = 10001
        if not self.password:
            self.password = str(self.worker_id) + str(self.worker_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ism} {self.familiya}"


class DailyWork(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='daily_works')
    sana = models.DateField(default=timezone.now, blank=True, null=True)
    umumiy_mahsulot = models.CharField(max_length=255)
    sifatsiz_mahsulot = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    alohida = []
    narx_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    hisoblangan_haqi = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        foydali_mahsulot = self.umumiy_mahsulot - self.sifatsiz_mahsulot
        self.hisoblangan_haqi = foydali_mahsulot * self.narx_per_kg
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.worker} - {self.sana} - {self.hisoblangan_haqi} so'm"


class ChatMessage(models.Model):
    sender = models.CharField()
    receiver = models.CharField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.message[:30]}"

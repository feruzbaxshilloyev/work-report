# from django.db import models
#
#
# class UserProfile(models.Model):
#     username = models.CharField(max_length=150)
#     profile_image = models.ImageField(upload_to='profile_images/')
#     company_name = models.CharField(max_length=255)
#     workers = []
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.username
#
#
# class Worker(models.Model):
#     worker_id = models.CharField(max_length=5, unique=True)
#     username = models.CharField(max_length=100, unique=True)
#     password = models.CharField(max_length=100)
#     ism = models.CharField(max_length=100)
#     familiya = models.CharField(max_length=100)
#     work = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
#     created = models.DateTimeField(auto_now_add=True)
#     image = models.ImageField(upload_to='worker_images/')
#
#
# class DailyWork(models.Model):
#     worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
#     date = models.DateField(auto_now_add=True)
#     total_kg = models.FloatField()
#     defect_kg = models.FloatField()
#     price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
#
#     @property
#     def net_kg(self):
#         return max(0, self.total_kg - self.defect_kg)
#
#     @property
#     def total_payment(self):
#         return self.net_kg * self.price_per_kg
#
#     def __str__(self):
#         return f"{self.worker.ism} - {self.date}"




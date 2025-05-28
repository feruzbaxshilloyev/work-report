from django.contrib import admin
from .models import Worker, DailyWork


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'ism', 'familiya', 'worker_id')


@admin.register(DailyWork)
class DailyWorkAdmin(admin.ModelAdmin):
    list_display = ('worker', 'sana', 'umumiy_mahsulot', 'sifatsiz_mahsulot', 'narx_per_kg', 'hisoblangan_haqi')

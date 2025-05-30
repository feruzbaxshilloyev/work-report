from django.contrib import admin

from manager.models import MonthlyPayment, ManagerProfile


# Register your models here.
@admin.register(MonthlyPayment)
class MonthlyPaymentAdmin(admin.ModelAdmin):
    list_display = ['worker', 'summa', 'sana', 'manager']
    list_filter = ['sana', 'manager']
    search_fields = (['worker__ism', 'worker__familiya', 'worker__worker_id'])


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ['phone', 'image']

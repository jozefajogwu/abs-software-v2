from django.db import models

from django.utils import timezone

class Operation(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    income = models.DecimalField(max_digits=15, decimal_places=2)
    expenditure = models.DecimalField(max_digits=15, decimal_places=2)
    rate = models.IntegerField()
    balance = models.DecimalField(max_digits=15, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.balance = self.income - self.expenditure
        super().save(*args, **kwargs)


class Maintenance(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    quantity = models.CharField(max_length=50)
    income = models.DecimalField(max_digits=15, decimal_places=2)
    expenditure = models.DecimalField(max_digits=15, decimal_places=2)
    rate = models.IntegerField()
    balance = models.DecimalField(max_digits=15, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.balance = self.income - self.expenditure
        super().save(*args, **kwargs)


class Production(models.Model):
    date = models.DateField(default=timezone.now)
    trucks = models.IntegerField()
    federal_royalty = models.DecimalField(max_digits=15, decimal_places=2)
    state_haulage = models.DecimalField(max_digits=15, decimal_places=2)
    mou_fee = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    remarks = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.total = self.federal_royalty + self.state_haulage + self.mou_fee
        super().save(*args, **kwargs)

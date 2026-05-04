from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

# Get the user model so we can track who logged the daily records
User = get_user_model()

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
    # This tracks the haulage, trucks, and fees
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


# --- NEW: Daily Production Tracking ---
class DailyProductionRecord(models.Model):
    # This tracks the actual physical work, targets, and efficiency
    date = models.DateField(default=timezone.now)
    item_name = models.CharField(max_length=200)
    shift = models.CharField(max_length=50, blank=True, null=True)
    
    target_quantity = models.IntegerField(default=0)
    actual_quantity = models.IntegerField(default=0)
    defective_quantity = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True, null=True)
    logged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='daily_production_logs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} - {self.date}"

    @property
    def efficiency_percentage(self):
        # Automatically calculates efficiency based on target vs actual
        if self.target_quantity > 0:
            return round((self.actual_quantity / self.target_quantity) * 100, 2)
        return 0
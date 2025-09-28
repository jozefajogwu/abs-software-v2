from django.db import models

# Create your models here.
# finance/models.py

class FinanceRecord(models.Model):
    TRANSACTION_TYPES = (
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    )

    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    activity = models.CharField(max_length=100, default='General')

    def __str__(self):
        return f"{self.type.title()} - ₦{self.amount} on {self.date}"

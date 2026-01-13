from django.db import models
from django.utils import timezone



class FinanceRecord(models.Model):
    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    CATEGORY_CHOICES = (
        ('operations', 'Operations'),
        ('maintenance', 'Maintenance'),
    )

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='income'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='operations'
    )
    date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)  # 👈 use default instead of auto_now_add

    def __str__(self):
        return f"{self.description} - ₦{self.amount}"

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class TransactionType(models.TextChoices):
    INCOME = 'income', 'Income'
    EXPENSE = 'expense', 'Expense'

class UserRole(models.TextChoices):
    VIEWER = 'viewer', 'Viewer'
    ANALYST = 'analyst', 'Analyst'
    ADMIN = 'admin', 'Admin'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.VIEWER)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    category = models.CharField(max_length=50)
    date = models.DateField()
    description = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.type} - {self.amount} - {self.date}"
    
    class Meta:
        ordering = ['-date', '-created_at']
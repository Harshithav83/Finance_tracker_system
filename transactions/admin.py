from django.contrib import admin
from .models import Transaction, UserProfile

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'type', 'category', 'amount')
    list_filter = ('type', 'category', 'date')
    search_fields = ('category', 'description', 'user__username')
    date_hierarchy = 'date'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)
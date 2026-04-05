from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transactions/', login_required(views.transaction_list), name='transaction_list'),
    path('transactions/create/', login_required(views.transaction_create), name='transaction_create'),
    path('transactions/<int:pk>/edit/', login_required(views.transaction_edit), name='transaction_edit'),
    path('transactions/<int:pk>/delete/', login_required(views.transaction_delete), name='transaction_delete'),
    path('analytics/', login_required(views.transaction_analytics), name='analytics'),
    path('export/', login_required(views.export_transactions_csv), name='export_csv'),
    path('users/', login_required(views.user_management), name='user_management'),
]
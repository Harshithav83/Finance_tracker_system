from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),
    path('dashboard/', include('transactions.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='transactions/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
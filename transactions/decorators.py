# transactions/decorators.py
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps
from .models import UserRole

def role_required(allowed_roles):
    """
    Decorator to check if user has required role.
    Usage: @role_required(['admin', 'analyst'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Check if user has profile, if not create one
            if not hasattr(request.user, 'profile'):
                from .models import UserProfile
                UserProfile.objects.get_or_create(
                    user=request.user, 
                    defaults={'role': UserRole.VIEWER}
                )
            
            user_role = request.user.profile.role
            
            if user_role not in allowed_roles:
                raise PermissionDenied("You don't have permission to access this page.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def admin_required(view_func):
    """Decorator for admin-only views"""
    return role_required([UserRole.ADMIN])(view_func)

def analyst_or_admin_required(view_func):
    """Decorator for analyst or admin views"""
    return role_required([UserRole.ANALYST, UserRole.ADMIN])(view_func)

def viewer_or_higher(view_func):
    """Decorator for all authenticated users (Viewer, Analyst, Admin)"""
    return role_required([UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN])(view_func)
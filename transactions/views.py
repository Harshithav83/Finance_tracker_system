from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.core.paginator import Paginator
from .models import Transaction, TransactionType
from .forms import TransactionForm, TransactionFilterForm
from .decorators import admin_required, analyst_or_admin_required, viewer_or_higher
from datetime import datetime

@login_required
@viewer_or_higher
def dashboard(request):
    """Main dashboard view - Accessible by all authenticated users (Viewer, Analyst, Admin)"""
    # Get all transactions for the logged-in user
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate totals
    total_income = transactions.filter(type=TransactionType.INCOME).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(type=TransactionType.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expenses
    
    # Recent transactions (last 10)
    recent_transactions = transactions.order_by('-date')[:10]
    
    # Category breakdown
    categories = transactions.values('category', 'type').annotate(total=Sum('amount'))
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'transaction_count': transactions.count(),
        'recent_transactions': recent_transactions,
        'categories': categories,
        'user_role': request.user.profile.role if hasattr(request.user, 'profile') else 'viewer',
    }
    return render(request, 'transactions/dashboard.html', context)

@login_required
@viewer_or_higher
def transaction_list(request):
    """List all transactions with filters - Accessible by all authenticated users"""
    transactions = Transaction.objects.filter(user=request.user)
    user_role = request.user.profile.role if hasattr(request.user, 'profile') else 'viewer'
    
    # Filter form - only show filters for Analyst and Admin
    filter_form = TransactionFilterForm(request.GET)
    if filter_form.is_valid() and user_role in ['analyst', 'admin']:
        data = filter_form.cleaned_data
        if data.get('type'):
            transactions = transactions.filter(type=data['type'])
        if data.get('category'):
            transactions = transactions.filter(category__icontains=data['category'])
        if data.get('start_date'):
            transactions = transactions.filter(date__gte=data['start_date'])
        if data.get('end_date'):
            transactions = transactions.filter(date__lte=data['end_date'])
        if data.get('min_amount'):
            transactions = transactions.filter(amount__gte=data['min_amount'])
        if data.get('max_amount'):
            transactions = transactions.filter(amount__lte=data['max_amount'])
    
    # Pagination
    paginator = Paginator(transactions.order_by('-date'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'filter_form': filter_form,
        'user_role': user_role,
        'is_admin': user_role == 'admin',
        'is_analyst': user_role == 'analyst',
    }
    return render(request, 'transactions/transaction_list.html', context)

@login_required
@admin_required
def transaction_create(request):
    """Create new transaction - Admin only"""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction created successfully!')
            return redirect('transactions:transaction_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TransactionForm()
    
    return render(request, 'transactions/transaction_form.html', {'form': form, 'title': 'Add Transaction'})

@login_required
@admin_required
def transaction_edit(request, pk):
    """Edit transaction - Admin only"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transactions:transaction_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'transactions/transaction_form.html', {'form': form, 'title': 'Edit Transaction'})

@login_required
@admin_required
def transaction_delete(request, pk):
    """Delete transaction - Admin only"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transactions:transaction_list')
    
    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': transaction})

@login_required
@analyst_or_admin_required
def transaction_analytics(request):
    """Advanced analytics view - Analyst and Admin only"""
    transactions = Transaction.objects.filter(user=request.user)
    user_role = request.user.profile.role if hasattr(request.user, 'profile') else 'viewer'
    
    # Calculate various metrics
    total_income = transactions.filter(type=TransactionType.INCOME).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(type=TransactionType.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expenses
    
    # Category breakdown with percentages
    category_data = []
    for category in transactions.values('category').distinct():
        cat_total = transactions.filter(category=category['category']).aggregate(Sum('amount'))['amount__sum'] or 0
        percentage = (cat_total / total_expenses * 100) if total_expenses > 0 else 0
        category_data.append({
            'name': category['category'],
            'total': cat_total,
            'percentage': percentage
        })
    
    # Monthly trends (last 6 months)
    from django.db.models.functions import TruncMonth
    from collections import defaultdict
    
    monthly_data = transactions.annotate(
        month=TruncMonth('date')
    ).values('month', 'type').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    monthly_totals = defaultdict(lambda: {'income': 0, 'expense': 0, 'month': ''})
    for entry in monthly_data:
        if entry['month']:
            month_key = entry['month'].strftime('%Y-%m')
            monthly_totals[month_key]['month'] = entry['month'].strftime('%B %Y')
            monthly_totals[month_key][entry['type']] = float(entry['total'])
    
    context = {
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'balance': float(balance),
        'transaction_count': transactions.count(),
        'category_data': category_data,
        'monthly_totals': dict(monthly_totals),
        'average_transaction': float(transactions.aggregate(Sum('amount'))['amount__sum'] or 0) / max(transactions.count(), 1),
        'user_role': user_role,
    }
    return render(request, 'transactions/analytics.html', context)

@login_required
@admin_required
def user_management(request):
    """User management view - Admin only"""
    from django.contrib.auth.models import User
    from .models import UserRole
    
    users = User.objects.all().prefetch_related('profile')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        user = get_object_or_404(User, pk=user_id)
        if hasattr(user, 'profile'):
            user.profile.role = new_role
            user.profile.save()
            messages.success(request, f"Role updated for {user.username}")
        else:
            messages.error(request, f"Profile not found for {user.username}")
        return redirect('transactions:user_management')
    
    context = {
        'users': users,
        'role_choices': UserRole.choices,
    }
    return render(request, 'transactions/user_management.html', context)

@login_required
@analyst_or_admin_required
def export_transactions_csv(request):
    """Export transactions to CSV - Analyst and Admin only"""
    import csv
    from django.http import HttpResponse
    
    transactions = Transaction.objects.filter(user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description', 'Created At'])
    
    for t in transactions:
        writer.writerow([
            t.date.strftime('%Y-%m-%d'),
            t.type,
            t.category,
            f"{t.amount:.2f}",
            t.description,
            t.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response
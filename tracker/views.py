from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.paginator import Paginator
from datetime import date
from .models import Expense
from .forms import ExpenseForm

#------ Dashboard ------#

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    today = date.today()

    expenses_queryset = Expense.objects.filter(user=request.user).order_by('-date')

    total = expenses_queryset.aggregate(total=Sum('amount'))['total'] or 0

    category_data = expenses_queryset.values('category').annotate(total=Sum('amount'))

    paginator = Paginator(expenses_queryset, 20)
    page_number = request.GET.get('page')
    expenses = paginator.get_page(page_number)

    return render(request, 'tracker/dashboard.html', {
        'total': total,
        'category_data': category_data,
        'expenses': expenses
    })

#------ CRUD ------#

def add_expense(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect('home')
    else:
        form = ExpenseForm()

    return render(request, 'tracker/add_expense.html', {'form': form})

def edit_expense(request, expense_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully!")
            return redirect('home')
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'tracker/edit_expense.html', {'form': form})

def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully!")
        return redirect('home')

    return render(request, 'tracker/delete_expense.html', {'expense': expense})

#------ Authentication ------#
def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return render(request, 'tracker/register.html', {'error': "Passwords do not match"})

        user = User.objects.create_user(username=username, password=password1)
        login(request, user)
        return redirect('home')

    return render(request, 'tracker/register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'tracker/login.html', {'error': "Invalid credentials"})

    return render(request, 'tracker/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')
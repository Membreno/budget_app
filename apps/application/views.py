from django.shortcuts import render, HttpResponse,redirect
from django.contrib import messages
import re
import bcrypt
from .models import User, Bill, Expense, Income
from time import gmtime, strftime, localtime

# Create your views here.
def index(request):
    return render(request,'application/index.html')

def dashboard(request):
    if "id" not in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id = request.session['id'])
        user_first_name = user.first_name
        bills = Bill.objects.filter(uploaded_by=user).order_by('due_date')
        user_bills = user.bills_uploaded.all()
        sum = 0
        for bill in user_bills:
            sum += bill.amount
        context = {
            'user': user,
            'bills': bills,
            'sum': sum,
            'date': strftime("%B %d, %Y", localtime()),
        }
        return render(request, 'application/dashboard.html', context)

def add_user(request):
    errors = User.objects.basic_validator(request.POST,isCreate=True)
    if len(errors) > 0:
        for key,value in errors.items():
            messages.error(request, value,extra_tags=key )
        return redirect('/')
    else: # If non errors were found go through process of creating an account for user
        pwhash = bcrypt.hashpw(request.POST['password'].encode(),bcrypt.gensalt()) # Hash user password
        new_user = User.objects.create(first_name=request.POST['first_name'].title(), last_name=request.POST['last_name'].title(), email=request.POST['email'], password=pwhash)
        request.session['id'] = new_user.id # This returns an object
        request.session['first_name'] = new_user.first_name
        return redirect('/dashboard')

def login_user(request):
    errors = User.objects.basic_validator(request.POST, isCreate=False)
    if len(errors) > 0:
        for key,value in errors.items():
            messages.error(request, value,extra_tags=key )
        return redirect('/')
    else:
        user= User.objects.filter(email = request.POST['login_email'])
        request.session['id'] = user[0].id
        request.session['first_name'] = user[0].first_name
        return redirect('/dashboard')

def logout(request):
    del request.session['id']
    return redirect('/')

def new_bill(request):
    if "id" not in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id = request.session['id'])
        user_first_name = user.first_name
        return render(request, 'application/new_bill.html')

def add_bill(request):
    if "id" not in request.session:
        return redirect('/')
    errors = Bill.objects.bill_validator(request.POST)
    if len(errors) > 0:
        for key,value in errors.items():
            messages.error(request, value,extra_tags=key )
        return redirect('bills/new')
    else:
        current_user = User.objects.get(id=request.session['id'])
        Bill.objects.create(title=request.POST['title'].title(), amount=request.POST['amount'], due_date=request.POST['due_date'],uploaded_by=current_user)

        return redirect('/dashboard')

def edit(request, id):
    if "id" not in request.session:
        return redirect('/')
    bill = Bill.objects.get(id=id)
    context = {
        "bill": bill,
    }
    if bill.uploaded_by.id != request.session['id']:
        return redirect('/dashboard')
    else:
        return render(request, 'application/edit_bill.html', context)

def process_edit(request, id):
    if "id" not in request.session:
        return redirect('/')
    errors = Bill.objects.bill_validator(request.POST)
    if len(errors) > 0:
        for key,value in errors.items():
            messages.error(request, value,extra_tags=key )
        return redirect('/bills/'+str(id)+'/edit')
    else:
        bill_to_update = Bill.objects.get(id=id)
        bill_to_update.title=request.POST['title'].title()
        bill_to_update.amount=request.POST['amount']
        bill_to_update.due_date=request.POST['due_date']
        bill_to_update.save()

        return redirect('/dashboard')

def delete(request,id):
    if "id" not in request.session:
        return redirect('/')
    bill_to_delete = Bill.objects.get(id=id)
    if bill_to_delete.uploaded_by.id != request.session['id']:
        return redirect('/dashboard')
    bill_to_delete.delete()
    return redirect("/dashboard")

def add_funds(request):
    if "id" not in request.session:
        return redirect('/')
    return render(request, "application/income.html")

def increase(request):
    if "id" not in request.session:
        return redirect('/')
    errors = Income.objects.income_validator(request.POST)
    if len(errors) > 0:
        for key,value in errors.items():
            messages.error(request, value,extra_tags=key )
        return redirect('/add_funds')
    else:
        user = User.objects.get(id = request.session['id'])
        bank = float(user.bank)
        print('*'*50)
        bank = bank + float(request.POST['income_amount'])
        print(bank)
        user.bank = bank
        user.save()
        return redirect('/dashboard')

def subtract_funds(request):
    if "id" not in request.session:
        return redirect('/')
    return render(request, "application/expense.html")

def decrease(request):
    if "id" not in request.session:
        return redirect('/')
    errors = Expense.objects.expense_validator(request.POST)
    if len(errors) > 0:
        for key,value in errors.items():
            messages.error(request, value,extra_tags=key )
        return redirect('/subtract_funds')
    user = User.objects.get(id = request.session['id'])
    bank = float(user.bank)
    bank = bank - float(request.POST['expense_amount'])
    user.bank = bank
    user.save()
    return redirect('/dashboard')

def pay(request,id):
    if "id" not in request.session:
        return redirect('/')
    user = User.objects.get(id = request.session['id'])
    bank = user.bank
    bill = Bill.objects.get(id=id)
    if bill.uploaded_by.id != request.session['id']:
        return redirect('/dashboard')
    amount = bill.amount
    bank -= amount
    user.bank = bank
    user.save()

    bill.paid = True
    bill.save()
    return redirect('/dashboard')

def reset_bills(request):
    if "id" not in request.session:
        return redirect('/')
    user = User.objects.get(id = request.session['id'])
    all_bills = user.bills_uploaded.all()
    all_bills.update(paid=False)
    return redirect('/dashboard')

def reset_bank(request):
    if "id" not in request.session:
        return redirect('/')
    user = User.objects.get(id = request.session['id'])
    bank = user.bank
    bank = 0
    user.bank = bank
    user.save()
    return redirect('/dashboard')

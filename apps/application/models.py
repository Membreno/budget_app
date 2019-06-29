from django.db import models
import re
import bcrypt
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def basic_validator(self, postData, isCreate): #Added isCreate so we can use one validation method
        errors = {} # All of our error messages will go in this dictionary
        if isCreate==True: # Will only run if user is creating an account
            if len(postData['first_name']) < 2:
                errors["first_name"] = "Name should be at least 2 characters"
            if len(postData['last_name']) < 2:
                errors["last_name"] = "Name should be at least 2 characters"

            if not EMAIL_REGEX.match(postData['email']): # Checks for correct format for email input
                errors["email"] = "Email format is not valid"

            existing_user = User.objects.filter(email=postData['email']) # Returns a list of objects
            if len(existing_user) > 0:
                errors["email"] = "Email already exist"

            if len(postData['password']) < 8:
                errors["password"] = "Password should be at least 8 characters"
            if len(postData['confirm_password']) < 8:
                errors["confirm_password"] = "Password should be at least 8 characters"
            if postData['confirm_password'] != postData['password']:
                errors["confirm_password"] = "Passwords do not match"
            return errors

        if isCreate==False: # Will only run if user is trying to log in
            if len(postData['login_email']) < 1:
                errors["login_email"] = "Email field cannot be left blank"
            if len(postData['login_password']) < 1:
                errors["login_password"] = "Password field cannot be left blank"
                return errors
            if not EMAIL_REGEX.match(postData['login_email']):
                errors["login_email"] = "Email format is not valid"
            existing_user = User.objects.filter(email=postData['login_email']) # Searches database for existing user and returns a list of objects

            if len(existing_user) < 1: # if no matching user exists
                errors["login_email"] = "Account does not exist"

            else: # if user does exist, check if password matches
                if len(postData['login_password']) < 1:
                    errors["login_password"] = "Password cannot be left blank"
                elif bcrypt.checkpw(postData['login_password'].encode(), existing_user[0].password.encode()): # We have to use the index of "[0]" because we are going through a list of objects
                    return errors # If everything is good return 0 errors
                else:
                    errors["login_email"] = "You could not be logged in"
            return errors

class User(models.Model):
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=70)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    bank = models.DecimalField(default=0, max_digits=1000, decimal_places=2)

    def __repr__(self):
        return f'ID: {self.id} Name: {self.first_name} {self.last_name} Email: {self.email}'

class BillManager(models.Manager):
    def bill_validator(self, postData):
        errors = {} # All of our error messages will go in this dictionary
        if len(postData['title']) < 3:
            errors["title"] = "Title should be at least 3 characters"
        if len(postData['amount']) < 1:
            errors["amount"] = "Amount is required"
        elif float(postData['amount']) < 0.01:
            errors["amount"] = "Amount has to be greater than $0.01"
        if len(postData['due_date']) < 1:
            errors["due_date"] = "Due date is required"
        elif (int(postData['due_date']) < 1) or (int(postData['due_date']) > 31):
            errors["due_date"] = "Due date should be within a monthly range (1st - 31st)"
        return errors

class Bill(models.Model):
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=1000, decimal_places=2)
    due_date = models.IntegerField()
    paid = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, related_name="bills_uploaded")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BillManager()

    def __repr__(self):
        return f'ID: {self.id} Title: {self.title} Amount: {self.amount} Due: {self.due_date} Status: {self.paid}'

class ExpenseManager(models.Manager):
    def expense_validator(self, postData):
        errors = {} # All of our error messages will go in this dictionary
        if len(postData['expense_title']) < 3:
            errors["expense_title"] = "Title should be at least 3 characters"
        if len(postData['expense_amount']) < 1:
            errors["expense_amount"] = "Amount is required"
        elif float(postData['expense_amount']) < 0.01:
            errors["expense_amount"] = "Amount has to be greater than $0.01"
        return errors

class Expense(models.Model):
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=1000, decimal_places=2)
    desc = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, related_name="expenses_uploaded")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ExpenseManager()

class IncomeManager(models.Manager):
    def income_validator(self, postData):
        errors = {} # All of our error messages will go in this dictionary
        if len(postData['income_title']) < 1:
            errors["income_title"] = "Title should be at least 3 characters"
        if len(postData['income_amount']) < 1:
            errors["income_amount"] = "Amount is required"
        elif float(postData['income_amount']) < 0.01:
            errors["income_amount"] = "Amount has to be greater than $0.01"
        return errors

class Income(models.Model):
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=1000, decimal_places=2)
    desc = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, related_name="income_uploaded")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = IncomeManager()

from django.db import models

# Create your models here.

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    monthly_salary = models.BigIntegerField()
    approved_limit = models.BigIntegerField()
    phone_number = models.CharField(max_length=20)
    current_debt = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_id = models.AutoField(primary_key=True)
    loan_amount = models.FloatField()
    tenure = models.IntegerField() # in months
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    date_approved = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    emis_paid_on_time = models.IntegerField(default=0)
    num_of_repayments = models.IntegerField(default=0)
    loan_status = models.CharField(max_length=20, default='Pending') # Options: Pending, Approved, Rejected, Paid

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer.first_name}"
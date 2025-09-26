from .models import Loan, Customer
from datetime import date
from django.db import models
from django.db.models import F

def calculate_credit_score(customer_id):
    customer = Customer.objects.get(customer_id=customer_id)
    loans = Loan.objects.filter(customer=customer)

    credit_score = 0

    # Factor 1: Past loans paid on time
    # Assuming 'emis_paid_on_time' refers to all EMIs for a loan, and 'tenure' is total EMIs
    on_time_payments = loans.filter(emis_paid_on_time__gte=F('tenure')).count()
    total_paid_loans = loans.filter(loan_status='Paid').count()
    
    if total_paid_loans > 0:
        # Simple ratio for now, can be made more complex
        credit_score += (on_time_payments / total_paid_loans) * 10 # Max 10 points

    # Factor 2: Number of loans taken in the past (active loans)
    active_loans_count = loans.filter(loan_status__in=['Approved', 'Running']).count()
    credit_score += min(active_loans_count * 5, 20) # Max 20 points for up to 4 loans

    # Factor 3: Loan activity in the current year
    current_year = date.today().year
    current_year_loans = loans.filter(date_approved__year=current_year).count()
    credit_score += min(current_year_loans * 7, 25) # Max 25 points for up to ~3-4 loans

    # Factor 4: Total volume of loans approved
    total_approved_volume = loans.filter(loan_status__in=['Approved', 'Running']).aggregate(sum_amount=models.Sum('loan_amount'))['sum_amount'] or 0
    if total_approved_volume > 0:
        credit_score += min(total_approved_volume / 100000, 20) # Max 20 points for every 1 lakh of loan volume

    # Additional Check: If sum of current loans > approved_limit, credit score is 0
    total_current_loan_amount = loans.filter(loan_status__in=['Approved', 'Running']).aggregate(sum_amount=models.Sum('loan_amount'))['sum_amount'] or 0
    if total_current_loan_amount > customer.approved_limit:
        credit_score = 0

    # Ensure score is within 0-100
    return max(0, min(100, int(credit_score)))

def calculate_emi(loan_amount, interest_rate, tenure):
    # Monthly interest rate
    monthly_interest_rate = (interest_rate / 12) / 100
    
    if monthly_interest_rate == 0: # Avoid division by zero for 0% interest
        return loan_amount / tenure
    
    # EMI calculation formula
    emi = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate)**tenure) / (((1 + monthly_interest_rate)**tenure) - 1)
    return round(emi, 2)

def round_to_nearest_lakh(amount):
    return round(amount / 100000) * 100000

from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('customer_id', 'first_name', 'last_name', 'age', 'monthly_salary', 'approved_limit', 'phone_number', 'current_debt')
        read_only_fields = ('customer_id', 'approved_limit', 'current_debt')

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ('loan_id', 'customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_installment', 'date_approved', 'start_date', 'end_date', 'emis_paid_on_time', 'num_of_repayments', 'loan_status')
        read_only_fields = ('loan_id', 'monthly_installment', 'date_approved', 'start_date', 'end_date', 'emis_paid_on_time', 'num_of_repayments', 'loan_status')

class CustomerRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    monthly_income = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=20)


class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer, CustomerRegistrationSerializer, CheckEligibilitySerializer, CreateLoanSerializer
from .utils import calculate_credit_score, calculate_emi, round_to_nearest_lakh
from datetime import date


class CustomerRegistrationViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            age = serializer.validated_data['age']
            monthly_income = serializer.validated_data['monthly_income']
            phone_number = serializer.validated_data['phone_number']

            # Calculate approved_limit
            approved_limit = round_to_nearest_lakh(36 * monthly_income)

            try:
                customer = Customer.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    age=age,
                    monthly_salary=monthly_income,
                    approved_limit=approved_limit,
                    phone_number=phone_number
                )
                response_data = CustomerSerializer(customer).data
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"DEBUG: IntegrityError during customer creation: {e}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckEligibilityViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']

            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Calculate credit score
            credit_score = calculate_credit_score(customer_id)
            
            # Check loan approval criteria based on credit score
            approval = False
            corrected_interest_rate = None
            min_interest_rate = 0.0

            if credit_score > 50:
                approval = True
            elif 30 <= credit_score <= 50:
                min_interest_rate = 12.0
                if interest_rate > 12:
                    approval = True
                else:
                    corrected_interest_rate = 12.0
            elif 10 <= credit_score <= 30:
                min_interest_rate = 16.0
                if interest_rate > 16:
                    approval = True
                else:
                    corrected_interest_rate = 16.0
            else: # credit_score < 10
                approval = False

            # Additional Check: Sum of current monthly EMIs exceeds 50% of monthly salary
            # Sum of all current EMIs for the customer
            total_current_emi = Loan.objects.filter(customer=customer, loan_status__in=['Approved', 'Running']).aggregate(Sum('monthly_installment'))['monthly_installment__sum'] or 0
            if (total_current_emi + calculate_emi(loan_amount, interest_rate, tenure)) > (0.50 * customer.monthly_salary):
                approval = False
                corrected_interest_rate = None # Reset corrected rate if not approved due to EMI
            
            monthly_installment = calculate_emi(loan_amount, interest_rate, tenure) if approval else 0

            response_data = {
                'customer_id': customer_id,
                'approval': approval,
                'interest_rate': interest_rate,
                'corrected_interest_rate': corrected_interest_rate,
                'tenure': tenure,
                'monthly_installment': monthly_installment
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateLoanViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = CreateLoanSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']

            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({'message': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Re-run eligibility check (as per /check-eligibility logic)
            credit_score = calculate_credit_score(customer_id)

            approval = False
            corrected_interest_rate = None
            
            if credit_score > 50:
                approval = True
            elif 30 <= credit_score <= 50:
                if interest_rate > 12:
                    approval = True
                else:
                    corrected_interest_rate = 12.0
            elif 10 <= credit_score <= 30:
                if interest_rate > 16:
                    approval = True
                else:
                    corrected_interest_rate = 16.0
            else: # credit_score < 10
                approval = False
            
            # Apply corrected interest rate if needed for approval logic
            actual_interest_rate = corrected_interest_rate if corrected_interest_rate else interest_rate

            # Additional Check: Sum of current monthly EMIs exceeds 50% of monthly salary
            total_current_emi = Loan.objects.filter(customer=customer, loan_status__in=['Approved', 'Running']).aggregate(Sum('monthly_installment'))['monthly_installment__sum'] or 0
            proposed_emi = calculate_emi(loan_amount, actual_interest_rate, tenure)

            if (total_current_emi + proposed_emi) > (0.50 * customer.monthly_salary):
                approval = False

            loan_id = None
            monthly_installment = 0
            message = 'Loan not approved based on eligibility criteria.'

            if approval:
                monthly_installment = proposed_emi
                # Create the loan
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    tenure=tenure,
                    interest_rate=actual_interest_rate,
                    monthly_installment=monthly_installment,
                    date_approved=date.today(),
                    start_date=date.today(),
                    end_date=date(date.today().year + (tenure // 12), (date.today().month + tenure) % 12 or 12, date.today().day),
                    emis_paid_on_time=0,
                    num_of_repayments=tenure, # Total repayments expected
                    loan_status='Approved'
                )
                loan_id = loan.loan_id
                message = 'Loan approved successfully.'
                # Update customer current debt (optional, but good practice)
                customer.current_debt += monthly_installment
                customer.save()

            response_data = {
                'loan_id': loan_id,
                'customer_id': customer_id,
                'loan_approved': approval,
                'message': message,
                'monthly_installment': monthly_installment
            }
            return Response(response_data, status=status.HTTP_201_CREATED if approval else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewLoanView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response({'error': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)

        customer_data = CustomerSerializer(loan.customer).data
        loan_data = LoanSerializer(loan).data

        response_data = {
            'loan_id': loan.loan_id,
            'customer': {
                'id': customer_data['customer_id'],
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name'],
                'phone_number': customer_data['phone_number'],
                'age': customer_data['age'],
            },
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_installment,
            'tenure': loan.tenure,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ViewCustomerLoansView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)
        
        response_data = []
        for loan in loans:
            repayments_left = loan.tenure - loan.emis_paid_on_time
            response_data.append({
                'loan_id': loan.loan_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_installment,
                'repayments_left': repayments_left,
            })
        return Response(response_data, status=status.HTTP_200_OK)

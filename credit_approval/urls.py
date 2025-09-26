from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'register', views.CustomerRegistrationViewSet, basename='register')
router.register(r'check-eligibility', views.CheckEligibilityViewSet, basename='check-eligibility')
router.register(r'create-loan', views.CreateLoanViewSet, basename='create-loan')

urlpatterns = [
    path('', include(router.urls)),
    path('view-loan/<int:loan_id>', views.ViewLoanView.as_view(), name='view-loan'),
    path('view-loans/<int:customer_id>', views.ViewCustomerLoansView.as_view(), name='view-customer-loans'),
]

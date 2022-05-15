from django.urls import path

from .views import (DoctorDetailView, DoctorView, PatientView, PatientDetailView)
                    # VerifyPhoneView, ConfirmPhone)

urlpatterns = [
    path('doctor/', DoctorView.as_view()),
    path('doctor/<str:pk>/', DoctorDetailView.as_view()),
    path('patient/', PatientView.as_view()),
    path('patient/<int:pk>/', PatientDetailView.as_view()),
    # path('verifyphone/', VerifyPhoneView.as_view()),
    # path('confirmphone/', ConfirmPhone.as_view())
]

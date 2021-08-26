from django.urls import path

from .views import ClinicView, PatientView, ListClinic, ReservationView, RegisterPatientAPIView, RegisterDoctorAPIView, \
    LoginUserAPIView

urlpatterns = [
    path('clinic', ClinicView.as_view(), name='clinic-controller'),
    path('patient', PatientView.as_view(), name='patient'),
    path('get-clinics', ListClinic.as_view(), name='get-clinics'),
    path('reserve', ReservationView.as_view(), name='reservation'),
    path('register/doctor/', RegisterDoctorAPIView.as_view(), name='register-doctor'),
    path('register/patient/', RegisterPatientAPIView.as_view(), name='register-patient'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
]

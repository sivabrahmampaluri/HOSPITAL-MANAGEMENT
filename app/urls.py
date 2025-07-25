from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('doctor/', views.doctor, name='doctor'),
    path('reception/', views.reception, name='reception'),
    path('view-files/', views.view_files, name='view_files'),
    path('patient/', views.patient, name='patient'),
    path('patient/new_patient/', views.new_patient, name='new_patient'),
    path('patient/existing_patient/', views.existing_patient, name='existing_patient'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_patient/', views.verify_patient, name='verify_patient'),
]

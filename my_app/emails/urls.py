# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('applicants/', views.applicant_list, name='applicant_list'),
]

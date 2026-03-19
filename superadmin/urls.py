from django.urls import path
from . import views

urlpatterns = [
    path('patient/', views.PatientView.as_view(), name="parient"),
]
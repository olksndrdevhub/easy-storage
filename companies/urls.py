from django.urls import path

from . import views

app_name = "companies"

urlpatterns = [
    path("companies/create/", views.CreateCompanyView.as_view(), name="create_company"),
    path("companies/", views.CompaniesView.as_view(), name="companies"),
    path("companies/<slug:slug>/", views.CompanyView.as_view(), name="company"),
]

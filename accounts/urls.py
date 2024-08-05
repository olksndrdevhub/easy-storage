from django.urls import path

from . import views


urlpatterns = [
    path("registration/", views.registration_view, name="registration_view"),
    path("signin/", views.signin_view, name="signin_view"),
    path("signout/", views.signout_view, name="signout_view"),
]

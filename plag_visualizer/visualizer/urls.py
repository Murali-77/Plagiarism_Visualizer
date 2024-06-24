from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('signup', views.signup, name='signup'),
    path('verify-otp', views.verify_otp_view, name= 'verify_otp'),

]
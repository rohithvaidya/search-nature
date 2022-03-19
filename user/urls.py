from django.urls import path
from . import views


urlpatterns = [
    path('user/signup/', views.register, name='register'),
    path('alert/', views.alert, name='alert'),
    path('send-activation-mail/', views.send_activation_mail, name='send_activation_mail'),
    path('confirm/', views.confirm, name='confirm'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),  
    path('login_view/', views.login_view, name='login_view'),
]
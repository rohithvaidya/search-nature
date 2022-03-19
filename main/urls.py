from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('view-article/<slug:slug>/', views.article_view, name='article_view'),
    path('contact-us/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('instructions/', views.instructions, name='instructions'),
]
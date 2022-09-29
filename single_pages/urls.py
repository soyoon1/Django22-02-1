from django.urls import path
from . import views

urlpatterns = [ # IP주소/
    path('', views.landing),            # IP 주소/
    path('about_me/', views.about_me)   # IP 주소/about_me/
]
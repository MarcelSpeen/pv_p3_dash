from django.urls import path
from . import views

urlpatterns = [
    path('p3_dash/', views.p3_view, name='p3_dash'),
]
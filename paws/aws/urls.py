from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('options/', views.options, name='options'),
    path('list_resources/', views.list_resources, name='list_resources'),  # Remove user_id
    path('delete_resources/', views.delete_resources, name='delete_resources'),  # Remove user_id
]

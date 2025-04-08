from django.urls import path
from .views import (
    UserCreateView,
    UserListView,
    UserDetailView,
)

urlpatterns = [
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('users/list/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/edit/', UserDetailView.as_view(), name='user-edit'),

]
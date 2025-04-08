from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDeleteView,
    TaskCompletionView,
    TaskReportView,
    TaskListView,
    TaskCreateView,
    TaskUpdateView,
    TaskCompleteView,
    TaskReportDetailView

)

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('tasks/<int:pk>/complete/', TaskCompletionView.as_view(), name='task-complete'),
    path('tasks/<int:pk>/report/', TaskReportView.as_view(), name='task-report'),
    path('dashboard/tasks/', TaskListView.as_view(), name='task-list-web'),
    path('dashboard/tasks/add/', TaskCreateView.as_view(), name='task-add'),
    path('dashboard/tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='task-edit'),
    path('dashboard/tasks/<int:pk>/complete/', TaskCompleteView.as_view(), name='task-complete-web'),
    path('dashboard/tasks/<int:pk>/report/', TaskReportDetailView.as_view(), name='task-report-web'),
]
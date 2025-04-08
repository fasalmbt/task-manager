from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from users.models import CustomUser
from .models import Task
from .serializers import TaskSerializer, TaskCompletionSerializer
from .forms import TaskForm
from users.permissions import IsSuperAdmin, IsAdmin, IsUser, IsTaskOwner
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from tasks import serializers
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

# API Views
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsSuperAdmin | IsAdmin]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_superadmin():
            return Task.objects.select_related('assigned_to').all()
        elif user.is_admin():
            return Task.objects.select_related('assigned_to').all()
        return Task.objects.select_related('assigned_to').filter(assigned_to=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Task

@method_decorator(csrf_exempt, name='dispatch')
class TaskDeleteView(View):
    def delete(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(pk=pk)
            task.delete()
            return JsonResponse({'message': 'Deleted', 'task_id': pk})
        except Task.DoesNotExist:
            return JsonResponse({'message': 'Task not found'}, status=404)


       
class TaskCompletionView(generics.UpdateAPIView):
    serializer_class = TaskCompletionSerializer
    permission_classes = [IsUser & IsTaskOwner]
    
    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data.get('status') == Task.Status.COMPLETED:
            if not all([serializer.validated_data.get('completion_report'), 
                       serializer.validated_data.get('worked_hours')]):
                raise serializers.ValidationError(
                    "Completion report and worked hours are required when marking task as completed."
                )
        serializer.save()

class TaskReportView(generics.RetrieveAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsSuperAdmin | IsAdmin | (IsUser & IsTaskOwner)]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(status=Task.Status.COMPLETED)
        if user.is_user():
            return queryset.filter(assigned_to=user)
        return queryset

# Template Views
class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        if self.request.user.is_superadmin:
            # SuperAdmin sees all tasks
            return Task.objects.select_related('assigned_to').all()
        elif self.request.user.is_admin:
            # Admin sees all tasks except those assigned to superadmins
            return Task.objects.select_related('assigned_to').exclude(
                assigned_to__role=CustomUser.Role.SUPERADMIN
            )
        else:
            # Regular users only see their own tasks
            return Task.objects.select_related('assigned_to').filter(
                assigned_to=self.request.user
            )

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list-web')
    permission_classes = [IsAdmin]

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superadmin or request.user.is_admin):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Task created successfully!")
        return super().form_valid(form)

class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list-web')

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if not (request.user.is_superadmin or 
                request.user.is_admin or 
                task.assigned_to == request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Task updated successfully!")
        return super().form_valid(form)

    def get_queryset(self):
        user = self.request.user
        if user.is_superadmin or user.is_admin:
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

class TaskCompleteView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['status', 'completion_report', 'worked_hours']
    template_name = 'tasks/task_complete.html'
    success_url = reverse_lazy('task-list-web')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.assigned_to != self.request.user:
            raise Http404("You do not have permission to complete this task.")
        return obj

    def form_valid(self, form):
        task = form.instance
        if task.status != Task.Status.COMPLETED:
            form.add_error('status', 'You must set status to Completed.')
            return self.form_invalid(form)
        
        if not task.completion_report or not task.worked_hours:
            form.add_error(None, 'Completion report and worked hours are required.')
            return self.form_invalid(form)

        messages.success(self.request, 'Task marked as completed.')
        return super().form_valid(form)


class TaskReportDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_report.html'
    context_object_name = 'task'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not (
            self.request.user.is_superadmin or
            self.request.user.is_admin
        ):
            raise PermissionDenied
        if obj.status != Task.Status.COMPLETED:
            raise Http404("Task is not completed yet.")
        return obj

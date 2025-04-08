from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.views import LoginView

from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationForm

# ------------------- Role-Based Mixin -------------------

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superadmin

# ------------------- User Views -------------------

class UserCreateView(SuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user-list')
    success_message = "User was created successfully"

class UserListView(SuperAdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

class UserDetailView(SuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/user_detail.html'
    success_url = reverse_lazy('user-list')
    success_message = "User was updated successfully"

    def post(self, request, *args, **kwargs):
        if "delete" in request.POST:
            return self.delete(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, "User was deleted successfully")
        return redirect(self.success_url)

# ------------------- Auth Views -------------------

class CustomLoginView(LoginView):
    template_name = 'login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('task-list-web')  # Redirect to your dashboard or landing page
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('task-list-web')

def custom_logout(request):
    logout(request)
    return redirect(reverse('login'))

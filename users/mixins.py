from django.core.exceptions import PermissionDenied

class SuperAdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superadmin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
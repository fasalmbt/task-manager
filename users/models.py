from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = 'SUPERADMIN', _('SuperAdmin')
        ADMIN = 'ADMIN', _('Admin')
        USER = 'USER', _('User')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )
    
    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN or self.is_superuser

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superadmin

    @property
    def is_user(self):
        return self.role == self.Role.USER

    def get_role_display(self):
        role_map = {
            self.Role.SUPERADMIN: 'Super Admin',
            self.Role.ADMIN: 'Admin',
            self.Role.USER: 'User'
        }
        return role_map.get(self.role, self.role)

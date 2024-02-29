import uuid

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser

from .manager import UserManager
from .validators import validate_username


class User(AbstractBaseUser):
    """
    Custom user model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name='ID')
    username = models.CharField(
        max_length=20,
        verbose_name='username',
        unique=True,
        validators=[validate_username],
        help_text='Enter a username containing 4-20 characters. It can only contain letters,'
                  ' hyphens, and underscores.'
    )
    email = models.EmailField(max_length=255, verbose_name='email', unique=True)

    is_active = models.BooleanField(default=True, verbose_name='is active')
    is_staff = models.BooleanField(default=False, verbose_name='is staff')
    is_admin = models.BooleanField(default=False, verbose_name='is admin')
    created = models.DateTimeField(default=timezone.now, verbose_name='created')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin or (self.is_active and self.is_staff)

    def has_module_perms(self, app_label):
        return self.is_admin or (self.is_active and self.is_staff)

    class Meta:
        ordering = ('username',)

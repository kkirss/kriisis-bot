from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from hashid_field import HashidAutoField


class UserManager(BaseUserManager):
    """Simple user manager to implement required functions

    Mostly copied from django.contrib.auth.models.UserManager
    """

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """Create and save a User with the given username, email and password."""
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        """Create a new regular user."""
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create a new superuser."""
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class User(AbstractBaseUser,
           PermissionsMixin):
    """User model for each registered user"""
    id = HashidAutoField(primary_key=True)
    email = models.EmailField('email address', max_length=255, unique=True, help_text='Email of user')

    is_staff = models.BooleanField('staff status', default=False, help_text='Whether user is staff')
    is_active = models.BooleanField('active', default=True, help_text='Whether user is active')
    date_joined = models.DateTimeField('date joined', default=timezone.now, help_text='The datetime the user joined')

    USERNAME_FIELD = 'email'

    objects = UserManager()


class Profile(models.Model):
    """Profile of user, containing any additional info/settings of the user"""
    id = HashidAutoField(primary_key=True)
    user = models.OneToOneField(User, related_name='profile', help_text='User of the profile', on_delete=models.DO_NOTHING, null=True, blank=True)
    telegram_user_id = models.IntegerField(null=True, blank=True)
    telegram_chat_id = models.IntegerField(null=True, blank=True)

    language = models.CharField(choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, max_length=10, help_text='Preferred language of user')
    telegram_picture_notifications = models.BooleanField(default=False)
    kriisis_last_discount_id = models.IntegerField(default=0)

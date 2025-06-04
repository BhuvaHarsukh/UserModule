from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Role(models.TextChoices):
    ADMIN = 'admin', 'Admin Role'
    NORMAL = 'normal', 'Normal User Role'

class UserManager(BaseUserManager):
    def create_user(self, cell_number, email, name, role_id=Role.NORMAL, password=None):
        if not cell_number:
            raise ValueError("Users must have a cell number")
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(cell_number=cell_number, email=email, name=name, role_id=role_id)
        user.set_password(password)  # This hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, cell_number, email, name, password):
        user = self.create_user(cell_number, email, name, role_id=Role.ADMIN, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    name = models.CharField(max_length=255)
    cell_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role_id = models.CharField(max_length=10, choices=Role.choices, default=Role.NORMAL)

    is_staff = models.BooleanField(default=False)  
    is_active = models.BooleanField(default=True)  

    USERNAME_FIELD = 'cell_number'  
    REQUIRED_FIELDS = ['email', 'name'] 

    objects = UserManager()

    def __str__(self):
        return self.name


class AccessToken(models.Model):
    token = models.CharField(max_length=512, unique=True)
    ttl = models.BigIntegerField()  # expiration in ms
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.name}'
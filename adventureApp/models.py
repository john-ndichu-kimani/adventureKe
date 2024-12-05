from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, fullname, phone_number, password=None, role='USER'):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            fullname=fullname,
            phone_number=phone_number,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, phone_number, password=None):
        user = self.create_user(
            email=email,
            fullname=fullname,
            phone_number=phone_number,
            password=password,
            role='ADMIN',
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('USER', 'User'),
        ('ADMIN', 'Admin'),
    )

    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')

    # Add related_name to prevent conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='adventure_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='adventure_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'phone_number']

    def __str__(self):
        return f"{self.email} ({self.role})"

    def has_perm(self, perm, obj=None):
        """
        Custom permission check that allows admins all permissions
        """
        if self.is_staff or self.role == 'ADMIN':
            return True
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        """
        Custom module permission check
        """
        if self.is_staff or self.role == 'ADMIN':
            return True
        return super().has_module_perms(app_label)


class Tour(models.Model):
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MODERATE', 'Moderate'),
        ('HARD', 'Hard')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    max_group_size = models.IntegerField()

    def __str__(self):
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    number_of_participants = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.fullname} - {self.tour.title}"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.fullname} for {self.tour.title}"
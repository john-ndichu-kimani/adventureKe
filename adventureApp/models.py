from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
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
    profile_picture = models.ImageField(upload_to='profile_pictures',default='https://img.freepik.com/free-vector/businessman-character-avatar-isolated_24877-60111.jpg')

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

class Destination(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)  # Optional additional details
    image = models.ImageField(upload_to='destination_images/', blank=True, null=True)  # Optional image

    def __str__(self):
            return self.name

class Tour(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    # Computed duration field
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    available_slots = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='tours')
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True, blank=True)
    featured_image = models.ImageField(upload_to='images/', blank=True, null=True)
    average_rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    reviews_count = models.PositiveIntegerField(default=0)
    max_group_size = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of participants for this tour"
    )
    min_group_size = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = "Tour"
        verbose_name_plural = "Tours"

    def __str__(self):
        return self.title

    def get_booked_slots(self):
        """
        Calculate total booked slots for the tour
        with confirmed bookings.
        """
        return self.bookings.filter(
            status='CONFIRMED'
        ).aggregate(
            total_slots=models.Sum('slots_booked')
        )['total_slots'] or 0

    def is_available(self):
        """Check if the tour has available slots."""
        return self.available_slots > 0


    def clean(self):
        """
        Validate that end_date is after start_date
        """
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date must be after start date")


class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('PAID','Paid')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name="bookings")
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=BOOKING_STATUS_CHOICES, default='PENDING')
    slots_booked = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-booking_date']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

        unique_together = ('user','tour')

    def __str__(self):
        return f"Booking by {self.user.get_full_name() or self.user.email} for {self.tour.title}"

    def save(self, *args, **kwargs):
        """Calculate the total price based on the slots booked."""
        self.total_price = self.slots_booked * self.tour.price
        super().save(*args, **kwargs)


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ]

    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal')
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    transaction_code = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    mpesa_receipt_number = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='mpesa'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.booking} - {self.status}"

    class Meta:
        verbose_name_plural = "Payments"
        ordering = ['-created_at']


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tour')  # Ensures a user can review a tour only once.
        ordering = ['-created_at']
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"Review by {self.user.get_full_name() or self.user.username} for {self.tour.title}"

class TourGuide(models.Model):
    DESIGNATION_CHOICES = [
        ('LEAD', 'Lead Guide'),
        ('ASSISTANT', 'Assistant Guide'),
        ('FREELANCE', 'Freelance Guide'),
        ('LOCAL', 'Local Guide'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES, default='LOCAL')
    experience_years = models.IntegerField(
        validators=[MinValueValidator(0)],  # Correct way to use validator
        help_text='Years of experience (must be 0 or more)'
    )
    education = models.CharField(max_length=300, blank=True, null=True)
    languages_spoken = models.TextField(help_text="Comma-separated list of languages", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='tour_guides/profile_pictures/', blank=True, null=True)
    tours = models.ManyToManyField('Tour', related_name='guides', blank=True)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Tour Guide"
        verbose_name_plural = "Tour Guides"

    def __str__(self):
        return f"{self.name} ({self.designation})"
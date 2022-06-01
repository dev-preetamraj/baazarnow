from django.db import models
from django.contrib.auth.models import User
from main_app.models import Product

class Profile(models.Model):
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others')
    )
    id = models.AutoField(primary_key = True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, choices=GENDER, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pic/', default='profile_pic/default.png')
    adrs_line_1 = models.CharField(max_length=50, blank=True, null=True)
    adrs_line_2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    district = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    postal_code = models.CharField(max_length=6, blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    is_phone_number_verified = models.BooleanField(default=False)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    is_aadhar_number_verified = models.BooleanField(default=False)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    is_pan_number_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    reset_password_token = models.CharField(max_length=100)
    rating = models.CharField(max_length=4, default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"@{self.user.username}'s Profile"

    def get_rating_count(self):
        rating_count = 0
        try:
            rating_count = SupplierRating.objects.filter(rated_to=self.user).count()
        except Exception as e:
            print(e)
        return rating_count
    
    def get_product_count(self):
        product_count = 0
        try:
            product_count = Product.objects.filter(product_owner=self.user).count()
        except Exception as e:
            print(e)
        return product_count

class SupplierRating(models.Model):
    RATING_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    )
    rated_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rated_to_supplier')
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rated_by_user')
    rating = models.CharField(max_length=1, choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.rated_to.username}\'s rating'

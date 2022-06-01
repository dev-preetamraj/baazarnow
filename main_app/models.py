from operator import mod
from django.db import models
from django.contrib.auth.models import User
import uuid

class SupplierCompanyDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    gstin_number = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Grocery', 'Grocery'),
        ('Garments', 'Garments'),
        ('Cosmetics', 'Cosmetics'),
        ('Electronics', 'Electronics'),
        ('Stationery', 'Stationery'),
        ('Musical', 'Musical'),
        ('Pharmacy', 'Pharmacy'),
        ('Furniture', 'Furniture'),
        ('Sports', 'Sports'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.CharField(max_length=200, blank=True, null=True)
    product_brand = models.CharField(max_length=100, blank=True, null=True)
    product_image = models.ImageField(upload_to="product_pic/", blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    discounted_price = models.FloatField(blank=True, null=True)
    quantity_over_bulk_discount = models.IntegerField(default=0, blank=True, null=True)
    percent_discount_over_bulk = models.FloatField(blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    each_weight_in_grams = models.FloatField(blank=True, null=True)
    product_category = models.CharField(max_length=11, choices=CATEGORY_CHOICES)
    product_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if(len(self.product_name)>10):
            return f"{self.product_name[:10]}... | by - @{self.product_owner.username}"
        else:
            return f"{self.product_name} | by - @{self.product_owner.username}"

    def get_percentage_discount(self):
        price = float(self.price)
        discounted_price = float(self.discounted_price)
        percentage = ((price-discounted_price)/price)*100
        result = round(percentage,2)
        return result

    def get_short_name(self):
        name = self.product_name
        result = ""
        if(len(name)>63):
            result = f"{name[:60]}..."
        else:
            result = name
        return result

class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    adrs_line_1 = models.CharField(max_length=50)
    adrs_line_2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=20)
    district = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    postal_code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"@{self.user.username}'s address"

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    order_complete_status = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"Order Id: {self.id}"

    @property
    def get_cart_total(self):
        order_items = self.orderitem_set.all()
        total = sum([item.get_total for item in order_items])
        return total

    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])
        return total

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    order_complete_status = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        quantity = self.quantity
        price = float(self.product.discounted_price)
        total = quantity*price
        return total
    
    @property
    def get_short_name(self):
        name = ""
        if(len(self.product.product_name)>33):
            name = f"{self.product.product_name[:30]}..."
        else:
            name = self.product.product_name[:30]
        return name
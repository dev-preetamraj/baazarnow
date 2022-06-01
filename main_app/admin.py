from django.contrib import admin
from .models import (
    Product,
    SupplierCompanyDetail,
    DeliveryAddress,
    Order,
    OrderItem
)

admin.site.register(Product)
admin.site.register(SupplierCompanyDetail)
admin.site.register(DeliveryAddress)
admin.site.register(Order)
admin.site.register(OrderItem)
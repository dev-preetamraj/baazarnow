from django.forms import SelectMultiple, TextInput
from django_filters import FilterSet, CharFilter
from .models import Product
from django.contrib.auth.models import User
from accounts.models import Profile

class ProductFilter(FilterSet):
    product_name = CharFilter(field_name='product_name', lookup_expr='icontains')
    product_brand = CharFilter(field_name='product_brand', lookup_expr='icontains')
    class Meta:
        model = Product
        fields = ['product_name', 'product_brand', 'product_category']

class SupplierFilter(FilterSet):
    adrs_line_1 = CharFilter(
        field_name='adrs_line_1',
        lookup_expr='icontains',
        widget = TextInput(attrs={'class': 'form-control filter-input'})
    )
    city = CharFilter(
        field_name='city',
        lookup_expr='icontains',
        widget = TextInput(attrs={'class': 'form-control filter-input'})
    )
    district = CharFilter(
        field_name='district',
        lookup_expr='icontains',
        widget = TextInput(attrs={'class': 'form-control filter-input'})
    )
    state = CharFilter(
        field_name='state',
        lookup_expr='icontains',
        widget = TextInput(attrs={'class': 'form-control filter-input'})
    )
    country = CharFilter(
        field_name='country',
        lookup_expr='icontains',
        widget = TextInput(attrs={'class': 'form-control filter-input'})
    )
    postal_code = CharFilter(
        field_name='postal_code',
        lookup_expr='icontains',
        widget = TextInput(attrs={'class': 'form-control filter-input'})
    )
    class Meta:
        model = Profile
        fields = ['adrs_line_1', 'city', 'district', 'state', 'country', 'postal_code']
        
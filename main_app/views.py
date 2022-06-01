import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from accounts.decorators import allowed_users, email_verified_user
from accounts.models import Profile, SupplierRating
from .filters import ProductFilter, SupplierFilter
import datetime
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import (
    Product,
    Order,
    OrderItem,
    DeliveryAddress
)

OBJECTS_PER_PAGE = 12

def index(request):
    suppliers = Profile.objects.filter(user__groups__name="supplier").order_by('-rating')
    my_filter = SupplierFilter(request.GET, queryset=suppliers)
    suppliers = my_filter.qs
    supplier_count = suppliers.count()
    page = request.GET.get('page', 1)
    suppliers_paginator = Paginator(suppliers, OBJECTS_PER_PAGE)
    
    try:
        suppliers = suppliers_paginator.page(page)
    except PageNotAnInteger:
        suppliers = suppliers_paginator.page(OBJECTS_PER_PAGE)
    except EmptyPage:
        suppliers = suppliers_paginator.page(suppliers_paginator.num_pages)

    products = Product.objects.all().order_by('-created_at')[:12]
    context = {
        'suppliers': suppliers,
        'my_filter': my_filter,
        'page': page,
        'supplier_count': supplier_count,
        'products': products
    }
    try:
        order = Order.objects.get(customer=request.user, complete=False)
        context['order'] = order
    except Exception as e:
        print(e)
    return render(request, 'accounts/index.html', context)

@login_required
@email_verified_user
def dashboard(request):
    user = request.user
    context = {}
    try:
        order = Order.objects.get(customer=request.user, complete=False)
        context['order'] = order
    except Exception as e:
        print(e)
        
    try:
        total_clients = 0
        clients = []
        order_items = OrderItem.objects.filter(product__product_owner=user, order_complete_status=False)
        order_items_count = order_items.count()
        for item in order_items:
            if(item.order.customer not in clients):
                total_clients += 1
        context['total_clients'] = total_clients
        context['order_items'] = order_items
        context['order_items_count'] = order_items_count
    except Exception as e:
        print(e)
    
    try:
        order_for_retailer = OrderItem.objects.filter(order__customer=user, order_complete_status=False)
        order_for_retailer_count = order_for_retailer.count()
        context['order_for_retailer'] = order_for_retailer
        context['order_for_retailer_count'] = order_for_retailer_count
    except Exception as e:
        print(e)

    try:
        open_order_for_supplier = OrderItem.objects.filter(product__product_owner=user, order_complete_status=False)
        open_order_for_supplier_count = open_order_for_supplier.count()
        context['open_order_for_supplier'] = open_order_for_supplier
        context['open_order_for_supplier_count'] = open_order_for_supplier_count
    except Exception as e:
        print(e)
    
    try:
        total_suppliers = User.objects.filter(groups__name="supplier").count()
        context['total_suppliers'] = total_suppliers
    except Exception as e:
        print(e)
    return render(request, 'supplier/dashboard.html', context)

@login_required
@email_verified_user
@allowed_users(allowed_roles=['supplier'])
def manage_products(request):
    context = {}
    try:
        order = Order.objects.get(customer=request.user, complete=False)
        context['order'] = order
    except Exception as e:
        print(e)
    return render(request, 'supplier/manage_products.html', context)

@login_required
@email_verified_user
@allowed_users(allowed_roles=['supplier'])
def add_product_view(request):
    if(request.method=='POST'):
        product_name = request.POST.get('product_name')
        product_brand = request.POST.get('product_brand')
        product_image = request.FILES.get('product_image')
        price = request.POST.get('price')
        discounted_price = request.POST.get('discounted_price')
        quantity_over_bulk_discount = request.POST.get('quantity_over_bulk_discount')
        percent_discount_over_bulk = request.POST.get('percent_discount_over_bulk')
        quantity = request.POST.get('quantity')
        each_weight_in_grams = request.POST.get('each_weight_in_grams')
        product_category = request.POST.get('product_category')
        try:
            product = Product(
                product_name=product_name,
                product_brand=product_brand,
                product_image=product_image,
                price=price,
                discounted_price=discounted_price,
                product_category=product_category,
                product_owner=request.user
            )
            if(quantity != ''):
                product.quantity = quantity
            else:
                product.quantity = 0
            if(each_weight_in_grams != ''):
                product.each_weight_in_grams = each_weight_in_grams
            if(quantity_over_bulk_discount != ''):
                product.quantity_over_bulk_discount = quantity_over_bulk_discount
            else:
                product.quantity_over_bulk_discount = 0
            if(percent_discount_over_bulk != ''):
                product.quantity_over_bulk_discount = quantity_over_bulk_discount
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect('view_products')
        except Exception as e:
            messages.error(request, "Something went wrong.")
            print(e)
    context = {}
    return render(request, 'supplier/add_product.html', context)

@login_required
@email_verified_user
@allowed_users(allowed_roles=['supplier'])
def update_product_view(request, pk):
    context = {}
    try:
        product = Product.objects.get(id=pk)
        context['product'] = product
        if(request.method=='POST'):
            product_name = request.POST.get('product_name')
            product_brand = request.POST.get('product_brand')
            product_image = request.FILES.get('product_image')
            price = request.POST.get('price')
            discounted_price = request.POST.get('discounted_price')
            quantity_over_bulk_discount = request.POST.get('quantity_over_bulk_discount')
            percent_discount_over_bulk = request.POST.get('percent_discount_over_bulk')
            print(percent_discount_over_bulk!='')
            quantity = request.POST.get('quantity')
            each_weight_in_grams = request.POST.get('each_weight_in_grams')
            product_category = request.POST.get('product_category')

            product.product_name = product_name
            product.product_brand = product_brand
            if(product_image is not None):
                product.product_image = product_image
            product.price = price
            product.discounted_price = discounted_price
            if(quantity != ''):
                product.quantity = quantity
            else:
                product.quantity = 0
            if(each_weight_in_grams != ''):
                product.each_weight_in_grams = each_weight_in_grams
            if(quantity_over_bulk_discount != ''):
                product.quantity_over_bulk_discount = quantity_over_bulk_discount
            else:
                product.quantity_over_bulk_discount = 0
            if(percent_discount_over_bulk != ''):
                product.percent_discount_over_bulk = percent_discount_over_bulk
            prev_product_cat = product.product_category
            if(product_category!=''):
                product.product_category = product_category
            else:
                product.product_category = prev_product_cat
            product.save()
            messages.success(request, "Product Updated successfully.")
            return redirect('view_products')
    except Exception as e:
        messages.error(request, "Something went wrong.")
        print(e)
    return render(request, 'supplier/update_product.html', context)

@login_required
@email_verified_user
@allowed_users(allowed_roles=['supplier'])
def view_product_view(request):
    products = Product.objects.filter(product_owner=request.user).order_by('-created_at')
    product_count = products.count()
    my_filter = ProductFilter(request.GET, queryset=products)
    products = my_filter.qs
    product_count = products.count()
    page = request.GET.get('page', 1)
    products_paginator = Paginator(products, OBJECTS_PER_PAGE)
    
    try:
        products = products_paginator.page(page)
    except PageNotAnInteger:
        products = products_paginator.page(OBJECTS_PER_PAGE)
    except EmptyPage:
        products = products_paginator.page(products_paginator.num_pages)
    context = {
        'products': products,
        'my_filter': my_filter,
        'product_count': product_count,
        'page': page
    }
    return render(request, 'supplier/view_product.html', context)

@login_required
@email_verified_user
@allowed_users(allowed_roles=['supplier'])
def delete_product(request, pk):
    context = {}
    try:
        product = Product.objects.get(id=pk)
        context['product'] = product
        if(request.method=='POST'):
            product.delete()
            messages.success(request, f"{product.product_name} deleted successfully.")
            return redirect('view_products')
    except Exception as e:
        messages.error(request, "Something went wrong")
        print(e)
    return render(request, "supplier/delete_product.html", context)

@login_required
@email_verified_user
def give_rating_view(request, pk):
    context = {}
    try:
        rated_to = User.objects.get(id=pk)
        context['rated_to'] = rated_to
        rated_by = request.user
        previous_rating = float(rated_to.profile.rating) if (rated_to.profile.rating != None) else 0
        supplier_ratings = SupplierRating.objects.filter(rated_to=rated_to)
        previous_rating_count = int(supplier_ratings.count()) if (supplier_ratings.exists()) else 0
        if(rated_to==rated_by):
            messages.error(request, 'You cannot rate yourself.')
            return redirect('supplier_index')
        elif(SupplierRating.objects.filter(rated_to=rated_to,rated_by=rated_by).exists()):
            messages.error(request, 'You have already rated this supplier.')
            return redirect('supplier_index')
        else:
            if(request.method == 'POST'):
                rating = request.POST.get('rating')
                supplier_rating = SupplierRating(
                    rated_to = rated_to,
                    rated_by = rated_by,
                    rating = rating
                )
                supplier_rating.save()
                rated_to_profile = rated_to.profile
                new_rating = round(((previous_rating+float(rating))/(previous_rating_count+1)),2)
                rated_to_profile.rating = str(new_rating)
                rated_to_profile.save()
                messages.success(request, 'Rated successfully.')
                return redirect('supplier_index')
    except Exception as e:
        messages.error(request, 'Something went wrong, we are working on it.')
        print(e)
        return redirect('supplier_index')
    return render(request, 'supplier/rating.html', context)

def product_detail_page(request, product_id):
    context = {}
    try:
        product = Product.objects.get(id=product_id)
        context['product'] = product
    except Exception as e:
        print(e)
    return render(request, 'supplier/product_detail_page.html', context)

def supplier_profile(request, supplier_id):
    try:
        supplier = Profile.objects.get(id=supplier_id)
        user = supplier.user
        products = Product.objects.filter(product_owner=user).order_by('-created_at')
        
        my_filter = ProductFilter(request.GET, queryset=products)
        products = my_filter.qs
        product_count = products.count()

        page = request.GET.get('page', 1)
        products_paginator = Paginator(products, OBJECTS_PER_PAGE)
        
        try:
            products = products_paginator.page(page)
        except PageNotAnInteger:
            products = products_paginator.page(OBJECTS_PER_PAGE)
        except EmptyPage:
            products = products_paginator.page(products_paginator.num_pages)

    except Exception as e:
        print(e)
    context = {
        'supplier': supplier,
        'product_count': product_count,
        'my_filter': my_filter,
        'products': products
    }
    try:
        order = Order.objects.get(customer=request.user, complete=False)
        context['order'] = order
    except Exception as e:
        print(e)
    return render(request, 'supplier/supplier_profile.html', context)

@login_required
def cart_view(request):
    user = request.user
    context = {}
    if(user.is_authenticated):
        customer = user
        try:
            order = Order.objects.get(
                customer=customer,
                complete=False
            )
            context['order'] = order
            if(order):
                context['active'] = True
            items = OrderItem.objects.filter(order=order)
            context['items'] = items
            item_count = items.count()
            context['item_count'] = item_count
        except Exception as e:
            print(e)
            items = []
    else:
        items = []
    return render(request, 'consumer/cart.html', context)

@csrf_exempt
def update_cart_view(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    if request.user.is_authenticated:
        try:
            product = Product.objects.get(id=productId)
            if(product.product_owner == request.user):
                return JsonResponse('You cannot purchase your own product.', safe=False)
            else:
                order, created = Order.objects.get_or_create(customer=request.user, complete=False)
                
                if(created):
                    order_item = OrderItem(
                        product=product,
                        order=order,
                        quantity=1
                    )
                    order_item.save()
                    return JsonResponse('Product added to Cart.', safe=False)
                else:
                    if(OrderItem.objects.filter(product=product, order=order).exists()):
                        return JsonResponse('Product already added to Cart. Check Cart to increase quantity.', safe=False)
                    else:
                        order_item = OrderItem(
                            product=product,
                            order=order,
                            quantity=1
                        )
                        order_item.save()
                        return JsonResponse('Product added to Cart.', safe=False)
        except Exception as e:
            print(e)
            return JsonResponse('Something went wrong. We are working on it.', safe=False)
    else:
        return JsonResponse('Please Login to add Items to Cart.', safe=False)

@login_required
def checkout_view(request):
    context = {}
    try:
        user = request.user
        order = Order.objects.get(customer=user, complete=False)
        context['order'] = order
        items = OrderItem.objects.filter(order=order)
        context['items'] = items
        address = DeliveryAddress.objects.filter(user=user)
        context['address'] = address
    except Exception as e:
        print(e)
        items = []
        context['items'] = items
    return render(request, 'consumer/checkout.html', context)

@csrf_exempt
def add_order_address(request):
    data = json.loads(request.body)
    adrs_line_1 = data['adrs_line_1']
    adrs_line_2 = data['adrs_line_2']
    city = data['city']
    district = data['district']
    state = data['state']
    country = data['country']
    postal_code = data['postal_code']
    phone_number = data['phone_number']
    user = request.user
    if(adrs_line_1==""):
        return JsonResponse('Address Line 1 cannot be empty.', safe=False)
    if(city==""):
        return JsonResponse('City cannot be empty.', safe=False)
    if(district==""):
        return JsonResponse('District cannot be empty.', safe=False)
    if(state==""):
        return JsonResponse('State cannot be empty.', safe=False)
    if(country==""):
        return JsonResponse('Country cannot be empty.', safe=False)
    if(postal_code==""):
        return JsonResponse('Postal Code cannot be empty.', safe=False)
    if(phone_number==""):
        return JsonResponse('Phone Number cannot be empty.', safe=False)
    if(len(phone_number)>10):
        return JsonResponse('Please add phone number without country code or other prefix.', safe=False)
    if(len(phone_number)<10):
        return JsonResponse('Please add correct 10 digit phone number.', safe=False)
    else:

        try:
            address = DeliveryAddress(
                user=user,
                adrs_line_1=adrs_line_1,
                adrs_line_2=adrs_line_2,
                city=city,
                district=district,
                state=state,
                country=country,
                postal_code=postal_code,
                phone_number=phone_number
            )
            address.save()
            order = Order.objects.get(customer=request.user, complete=False)
            order.address = address
            order.save()
            return JsonResponse('Address added successfully.', safe=False)
        except Exception as e:
            print(e)
            return JsonResponse('Something went wrong. We are working on it...', safe=False)

@csrf_exempt
def change_order_address(request):
    data = json.loads(request.body)
    addressId = data['addressId']
    success = data['success']
    if(success):
        try:
            address = DeliveryAddress.objects.get(id=addressId)
            order = Order.objects.get(customer=request.user, complete=False)
            order.address = address
            order.save()
            return JsonResponse('Address selected...', safe=False)
        except Exception as e:
            print(e)
            return JsonResponse('Something went wrong. We are working on it.', safe=False)
    else:
        return JsonResponse('Please select an address.', safe=False)

@csrf_exempt
def update_cart_item_quantity(request):
    data = json.loads(request.body)
    if(data['quantity'].isdecimal()):
        quantity = int(data['quantity'])
        productId = data['productId']
        try:
            order = Order.objects.get(customer=request.user, complete=False)
            product = Product.objects.get(id=productId)
            if(quantity>product.quantity):
                return JsonResponse(f'Only {product.quantity} items are left. Add under this value', safe=False)
            else:
                order_item = OrderItem.objects.get(product=product, order=order)
                order_item.quantity = quantity
                order_item.save()
                return JsonResponse('Quantity added.', safe=False)
        except Exception as e:
            print(e)
            return JsonResponse('Something went wrong. We are working on it.', safe=False)
    else:
        return JsonResponse('Please enter valid number.', safe=False)

@csrf_exempt
def delete_item_from_cart(request):
    data = json.loads(request.body)
    item_id = data['item_id']
    try:
        item = OrderItem.objects.get(id=item_id)
        item.delete()
        return JsonResponse('Item Deleted', safe=False)
    except Exception as e:
        print(e)
        return JsonResponse('Something went wrong. We are working on it', safe=False)

def all_products_view(request):
    try:
        products = Product.objects.all().order_by('-created_at')
        my_filter = ProductFilter(request.GET, queryset=products)
        products = my_filter.qs
        product_count = products.count()

        page = request.GET.get('page', 1)
        products_paginator = Paginator(products, OBJECTS_PER_PAGE)
        
        try:
            products = products_paginator.page(page)
        except PageNotAnInteger:
            products = products_paginator.page(OBJECTS_PER_PAGE)
        except EmptyPage:
            products = products_paginator.page(products_paginator.num_pages)

    except Exception as e:
        print(e)
    context = {
        'product_count': product_count,
        'page': page,
        'products': products,
        'my_filter': my_filter
    }
    try:
        order = Order.objects.get(customer=request.user, complete=False)
        context['order'] = order
    except Exception as e:
        print(e)
    return render(request, 'supplier/all_products.html', context)

@csrf_exempt
def process_order(request):
    data = json.loads(request.body)
    transaction_id = datetime.datetime.now().timestamp()
    order_id = data['order_id']
    total_amount = float(data['total_amount'])
    try:
        order = Order.objects.get(id=order_id)
        if(total_amount == order.get_cart_total):
            order.complete = True
            order.transaction_id = datetime.datetime.now().timestamp()
            order.save()
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                item_product = item.product
                prev_quantity = item_product.quantity
                ordered_quantity = item.quantity
                left_quantity = prev_quantity-ordered_quantity
                item_product.quantity = left_quantity
                item_product.save()
            return JsonResponse('Payment received...', safe=False)
        else:
            return JsonResponse('Error while processing payment. Try again.', safe=False)
    except Exception as e:
        print(e)
        return JsonResponse('Something went wrong, we are working on it.', safe=False)

@login_required
@allowed_users(allowed_roles=['supplier'])
def order_received(request):
    user = request.user
    try:
        order_items = OrderItem.objects.filter(order_complete_status=False).order_by('-created_at')
        final_order_items = []
        for item in order_items:
            if(item.product.product_owner==user):
                final_order_items.append(item)
    except Exception as e:
        print(e)
    context ={
        'final_order_items': final_order_items
    }
    return render(request, 'supplier/order_received.html', context)

@login_required
def your_orders(request):
    customer = request.user
    try:
        orders = Order.objects.filter(customer=customer, order_complete_status=False).order_by('-date_ordered')
        order_items_2d = []
        for order in orders:
            items = OrderItem.objects.filter(order=order, order_complete_status=False)
            order_items_2d.append(items)
        order_items = []
        for items_2d in order_items_2d:
            for item_1d in items_2d:
                order_items.append(item_1d)
    except Exception as e:
        print(e)

    context = {
        'order_items': order_items
    }
    return render(request, 'consumer/your_orders.html', context)

@login_required
@allowed_users(allowed_roles=['supplier'])
def manage_order(request, item_id):
    context = {}
    try:
        order_item = OrderItem.objects.get(id=item_id)
        context['order_item'] = order_item
    except Exception as e:
        print(e)
        context['order_item'] = []
    return render(request, 'supplier/manage_order.html', context)

@csrf_exempt
@login_required
@allowed_users(allowed_roles=['supplier'])
def mark_order_item_complete(request):
    data = json.loads(request.body)
    order_id = data['order_id']
    try:
        order_item = OrderItem.objects.get(id=order_id)
        order_item.order_complete_status = True
        order_item.save()
        order = Order.objects.get(id=order_item.order.id)
        order_item_set = OrderItem.objects.filter(order=order)
        uncomplete_count = 0
        for item in order_item_set:
            if not item.order_complete_status:
                uncomplete_count +=1
        if uncomplete_count == 0:
            order.order_complete_status = True
            order.save()
        return JsonResponse('Order marked as complete.', safe=False)
    except Exception as e:
        print(e)
        return JsonResponse('Something went wrong, we are working on it.', safe=False)
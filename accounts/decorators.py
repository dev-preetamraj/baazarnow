from django.shortcuts import redirect, render
from django.contrib import messages


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, "You cannot access this page!")
            return redirect('supplier_index')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func

def email_verified_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.profile.is_email_verified:
            messages.warning(request, "First verify your email")
            return redirect('supplier_index')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return render(request, 'accounts/not_allowed.html', {})
        return wrapper_func
    return decorator
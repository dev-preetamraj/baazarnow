from django.urls import path
from .views import (
    forgot_password_view,
    register_user_view,
    login_view,
    logout_view,
    profile_view,
    update_profile_pic,
    update_profile,
    email_verification_view,
    initiate_email_verification,
    edit_email_view,
    forgot_password_view,
    reset_password_view
)

urlpatterns = [
    path('register/', register_user_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile_view'),
    path('update_profile_pic/', update_profile_pic, name="update_profile_pic"),
    path('update_profile/', update_profile, name="update_profile"),
    path('email_verification/', email_verification_view, name='email_verification_view'),
    path('initiate_email_verification', initiate_email_verification, name="initiate_email_verification"),
    path('edit_email/', edit_email_view, name='edit_email_view'),
    path('forgot_password/', forgot_password_view, name='forgot_password'),
    path('reset_password/<email_token>/', reset_password_view, name='reset_password')
]
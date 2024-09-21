from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('',views.index,name="home"),
    path('news/', views.news, name="news"),
    path('login/',views.Login,name="login"),
    path('register/',views.register,name="register"),
    path('logout/',views.logout,name="logout"),
    path('premium/',views.premium, name="premium"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('payment/success/<str:subscription_type>/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('cancel-premium/', views.cancel_subscription,name="cancel_subscription" ),
    
    path('password_reset/', views.password_reset_request,name="password_reset"),
    path('password_reset_done/', auth_view.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>', auth_view.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),name="password_reset_confirm"),
    path('password_reset_complete/', auth_view.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),name="password_reset_complete"),
]
from django.urls import path, include
from . import views

app_name = 'store'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('profile/edit/<int:pk>', views.EditProfile.as_view(), name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('my_orders/', views.OrdersView.as_view(), name='my_orders'),
    path('my_orders/products/<int:pk>', views.OrderProductsList.as_view(), name='my_order_products'),
    path('<slug:product_slug>/', views.DetailView.as_view(), name='detail'),
    path('categories/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('streamers/<slug:slug>/', views.StreamerView.as_view(), name='streamer'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('user/cart/', views.CartView.as_view(), name='cart'),
    path('user/cart/delete/<int:pk>', views.DeleteFromCart.as_view(), name='delete_cart'),
    path('user/cart/increase/<int:pk>', views.IncreaseCartQuantity.as_view(), name='increase_cart_quantity'),
    path('user/cart/decrease/<int:pk>', views.DecreaseCartQuantity.as_view(), name='decrease_cart_quantity'),
    path('user/cart/user_data/<int:pk>', views.InsertUserData.as_view(), name='teste'),
    path('user/cart/order/', views.InsertOrder.as_view(), name='order'),
    path('user/cart/order/payment/', views.Payment.as_view(), name='payment'),
    path('user/cart/order/payment/charge/', views.charge, name='charge'),
    path('new_product', views.InsertProducts.as_view(), name='new_product'),

]

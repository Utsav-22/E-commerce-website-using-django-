from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('view/', views.view_cart, name='view_cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_cart, name='update_cart'),
    path("checkout/",views.checkout, name="checkout"),
    path("place_order/", views.place_order, name="place_order"),
    path("order_history/", views.order_history, name="order_history"),
    path("cancel_order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    
    ]

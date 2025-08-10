from django.urls import path
from . import views

app_name = 'store'


urlpatterns = [
    path('', views.index, name='index'),
    path("profile/", views.profile, name="profile"),
    path("address/", views.address, name="address"),
    path("update-contact/<int:contact_id>/", views.update_contact, name="update_contact"),
    path("change-password/", views.change_password, name="change_password"),
    path('category/<int:id>/', views.category_detail, name='category_detail'),  
    path('category/<int:id>/subcategory/<int:subcategory_id>/', views.category_detail, name='subcategory_detail'),  
    path('ajax/search/', views.ajax_search_all, name='ajax_search'),
    path('search/',views.search_results, name='search_results'),  
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('get-cart-item-count/', views.get_cart_item_count, name='get_cart_item_count'),
    path('about/', views.about_us, name='about_us'),
    path('Privacy_policy/', views.Privacy_policy, name='Privacy-policy'),
]

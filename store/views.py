from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.decorators import login_required
from userlogin.models import ContactInfo
from django.contrib.auth import update_session_auth_hash
from .models import SliderImage ,Category, SubCategory, Product
from django.http import JsonResponse
from django.db.models import Q
import random
from cart.models import Cart , CartItem

@login_required(login_url='userlogin:login')
def profile(request):
    categories = Category.objects.all()
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        address = request.POST.get("address")
        city = request.POST.get("city")
        district = request.POST.get("district")
        state = request.POST.get("state")
        zipcode = request.POST.get("zipcode")

        
        ContactInfo.objects.create(
            user=request.user,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            address=address,
            city=city,
            district=district,
            state=state,
            zipcode=zipcode,
        )
        return redirect("store:address")  

    return render(request, "profile.html" , {'categories': categories}) 

@login_required(login_url='userlogin:login')
def update_contact(request, contact_id):
    contact = get_object_or_404(ContactInfo, id=contact_id, user=request.user)
    categories = Category.objects.all()
    if request.method == "POST":
        contact.phone_number = request.POST.get("phone_number")
        contact.first_name = request.POST.get("first_name")
        contact.last_name = request.POST.get("last_name")
        contact.address = request.POST.get("address")
        contact.city = request.POST.get("city")
        contact.district = request.POST.get("district")
        contact.state = request.POST.get("state")
        contact.zipcode = request.POST.get("zipcode")
        contact.save()
        return redirect("store:address")  

    return render(request, "update_contact.html", {"contact": contact ,'categories': categories})

@login_required(login_url='userlogin:login')
def address(request):
    categories = Category.objects.all()
    return render(request, "address.html" , {'categories': categories})


@login_required(login_url='userlogin:login')
def change_password(request):
    error_message = None
    success_message = None
    categories = Category.objects.all()
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(old_password):
            error_message = "Your old password is incorrect."
        elif new_password != confirm_password:
            error_message = "New password and confirm password do not match."
        elif len(new_password) < 8:  
            error_message = "Your new password must be at least 8 characters long."
        else:
            request.user.set_password(new_password)
            request.user.save()
            
            update_session_auth_hash(request, request.user)

            success_message = "Your password has been changed successfully."
            error_message = None  

    return render(request, "change_password.html", {"error_message": error_message, "success_message": success_message , 'categories': categories})

def index(request):
    slider_images = SliderImage.objects.all()
    categories = Category.objects.all()
    best_selling_products = Product.objects.filter(best_selling=True)
    
    for product in best_selling_products:
        main_image = product.images.filter(is_main=True).first()
        product.main_image = main_image

    # Check if the main product is in the cart
    product_in_cart = False
    cart_product_ids = []  # Store all product IDs in the cart
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)
        cart_product_ids = list(cart_items.values_list('product_id', flat=True))
        product_in_cart = product.id in cart_product_ids

    return render(request, 'index.html', {'slider_images': slider_images , 'categories': categories , 'products': best_selling_products,'product_in_cart': product_in_cart,'cart_product_ids': cart_product_ids,})


def category_detail(request, id, subcategory_id=None):
    
    category = get_object_or_404(Category, id=id)
    categories = Category.objects.all()
    
    subcategories = SubCategory.objects.filter(category=category)
    
    if subcategory_id:
        selected_subcategory = get_object_or_404(SubCategory, id=subcategory_id, category=category)
        products = Product.objects.filter(subcategory=selected_subcategory)
    else:
        selected_subcategory = None
        products = Product.objects.filter(category=category)

    for product in products:
        main_image = product.images.filter(is_main=True).first()
        product.main_image = main_image



    # Check if the main product is in the cart
    product_in_cart = False
    cart_product_ids = []  # Store all product IDs in the cart
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)
        cart_product_ids = list(cart_items.values_list('product_id', flat=True))
        product_in_cart = product.id in cart_product_ids

    return render(request, 'category_details.html', {
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'selected_subcategory': subcategory_id,
        'categories': categories,
        'product_in_cart':product_in_cart,
        'cart_product_ids':cart_product_ids,
    })


def subcategory_detail(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    products = Product.objects.filter(subcategory=subcategory)

    return render(request, 'category_details.html', {
        'category': subcategory.category,
        'subcategories': SubCategory.objects.filter(category=subcategory.category),
        'products': products,
        'selected_subcategory': subcategory.id,
    })


def ajax_search_all(request):
    query = request.GET.get('q', '').strip()
    results = {'products': [], 'categories': [], 'subcategories': []}

    if query:
        
        products = Product.objects.filter(name__icontains=query).values('id', 'name')
        categories = Category.objects.filter(name__icontains=query).values('id', 'name')
        subcategories = SubCategory.objects.filter(name__icontains=query).values('id', 'name', 'category_id', 'category__name')

        results['products'] = list(products)
        results['categories'] = list(categories)
        results['subcategories'] = list(subcategories)

    return JsonResponse({'results': results})


def search_results(request):
    query = request.GET.get('q', '').strip()  
    results = []
    categories = Category.objects.all()
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(subcategory__name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
        for product in results:
             main_image = product.images.filter(is_main=True).first()
             product.main_image = main_image
    
    # Check if the main product is in the cart
    product_in_cart = False
    cart_product_ids = []  # Store all product IDs in the cart
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)
        cart_product_ids = list(cart_items.values_list('product_id', flat=True))
        product_in_cart = any(p.id in cart_product_ids for p in results)
           
    return render(request, 'search_results.html', {'query': query, 'results': results , 'categories': categories,'product_in_cart':product_in_cart,'cart_product_ids':cart_product_ids,})



def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()
    images = product.images.all()  # Get all product images

    # Fetch related products from the same category (excluding the current product)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)

    # Ensure we don't get an IndexError with random.sample
    related_products = list(related_products)
    if len(related_products) > 4:
        related_products = random.sample(related_products, 4)

    # Add main image to each related product
    for related_product in related_products:
        main_image = related_product.images.filter(is_main=True).first()
        related_product.main_image = main_image

    # Check if the main product is in the cart
    product_in_cart = False
    cart_product_ids = []  # Store all product IDs in the cart
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)
        cart_product_ids = list(cart_items.values_list('product_id', flat=True))
        product_in_cart = product.id in cart_product_ids

    context = {
        'product': product,
        'categories': categories,
        'images': images,
        'related_products': related_products,
        'product_in_cart': product_in_cart,  # Pass for the main product button logic
        'cart_product_ids': cart_product_ids,  # Pass for related products button logic
    }
    
    return render(request, 'product_detail.html', context)



@login_required(login_url='userlogin:login')
def get_cart_item_count(request):
    if request.user.is_authenticated:
        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Count the items in the cart (which are instances of CartItem)
        cart_item_count = cart.items.count()  # Count CartItems related to the Cart
    else:
        cart_item_count = 0  # If the user is not authenticated, return 0

    return JsonResponse({'cart_item_count': cart_item_count})

def about_us(request):
    categories = Category.objects.all()
    return render(request, 'about_us.html', {'categories': categories})

def Privacy_policy(request):
    categories = Category.objects.all()
    return render(request, 'Privacy-policy.html', {'categories': categories})
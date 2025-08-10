from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem,  Shipping
from store.models import Product, Category
from userlogin.models import ContactInfo  # Import the user address model

@login_required(login_url='userlogin:login')
def add_to_cart(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	if product.quantity_available <= 0:
		messages.error(request, "This product is out of stock.")
		return redirect('store:product_list')
	
	cart, created = Cart.objects.get_or_create(user=request.user)
	quantity = int(request.POST.get('quantity', 1))
	cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
	
	if not created:
		if cart_item.quantity + quantity <= product.quantity_available:
			cart_item.quantity += quantity
		else:
			messages.error(request, "Not enough stock available.")
			return redirect('cart:view_cart')
	else:
		cart_item.quantity = min(quantity, product.quantity_available)
	
	cart_item.save()
	return redirect('cart:view_cart')

@login_required(login_url='userlogin:login')
def view_cart(request):
	cart, _ = Cart.objects.get_or_create(user=request.user)
	cart_items = cart.items.all()
	categories = Category.objects.all()
	subtotal = sum(item.get_total_price() for item in cart_items)
	shipping = Shipping.objects.first()
	shipping_charge = shipping.charge if shipping else 0
	total = subtotal + shipping_charge
	
	for item in cart_items:
		item.main_image = item.product.images.filter(is_main=True).first()

	return render(request, 'cart.html', {
		'cart_items': cart_items,
		'subtotal': subtotal,
		'shipping_charge': shipping_charge,
		'total': total,
		'categories': categories,
		'is_cart_empty': cart_items.count() == 0
	})

@login_required(login_url='userlogin:login')
def remove_from_cart(request, item_id):
	cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
	cart_item.delete()
	return redirect('cart:view_cart')

@login_required(login_url='userlogin:login')
def update_cart(request, item_id):
	cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
	quantity = int(request.POST.get('quantity', cart_item.quantity))
	quantity_change = request.POST.get('quantity_change')
	
	if quantity_change == 'increase':
		if cart_item.quantity < cart_item.product.quantity_available:
			cart_item.quantity += 1
	elif quantity_change == 'decrease' and cart_item.quantity > 1:
		cart_item.quantity -= 1
	else:
		cart_item.quantity = min(quantity, cart_item.product.quantity_available)
	
	cart_item.save()
	subtotal = sum(item.get_total_price() for item in cart_item.cart.items.all())
	shipping = Shipping.objects.first()
	shipping_charge = shipping.charge if shipping else 0
	total = subtotal + shipping_charge
	
	return JsonResponse({
		'success': True,
		'item_total_price': f'{cart_item.get_total_price():.2f}',
		'cart_summary': {
			'subtotal': f'${subtotal:.2f}',
			'shipping_charge': f'${shipping_charge:.2f}',
			'total': f'${total:.2f}'
		}
	})

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    
    # If cart is empty, prevent access to checkout
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty! Add items before proceeding to checkout.")
        return redirect("cart:view_cart")

    cart_items = cart.items.all()
    subtotal = sum(item.get_total_price() for item in cart_items)
    shipping = Shipping.objects.first()
    shipping_charge = shipping.charge if shipping else 0
    total = subtotal + shipping_charge
    addresses = ContactInfo.objects.filter(user=request.user)
    categories = Category.objects.all()

    for item in cart_items:
        item.main_image = item.product.images.filter(is_main=True).first()
        
    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping_charge": shipping_charge,
        "total": total,
        "addresses": addresses,
        'categories': categories,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import now
from django.db import transaction
from datetime import timedelta
from .models import Cart, CartItem, Order, Shipped, Delivered, Canceled, Shipping
from store.models import Product
from userlogin.models import ContactInfo

@login_required
def place_order(request):
    if request.method == "POST":
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
        address_id = request.POST.get("address_id")

        if not address_id:
            messages.error(request, "Please select an address!")
            return redirect("cart:checkout")

        address = get_object_or_404(ContactInfo, id=address_id)
        subtotal = sum(item.get_total_price() for item in cart_items)
        shipping = Shipping.objects.first()
        shipping_charge = shipping.charge if shipping else 0
        total = subtotal + shipping_charge
        
        # ✅ Use `products` instead of `product_details`
        products = {item.product.name: item.quantity for item in cart_items}

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                products=products,  # ✅ Fixed Field Name
                total_price=total,
                shipping=shipping,
                address=address,
                status='pending'
            )
            
            # Deduct stock
            for item in cart_items:
                item.product.quantity_available -= item.quantity
                item.product.save()
            
        cart_items.delete()
        return redirect("cart:order_history")

    return redirect("cart:checkout")


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Order, Shipped, Delivered, Canceled
from store.models import Product  # ✅ Import Product

@login_required
def order_history(request):
    all_orders = []
    categories = Category.objects.all()
    def get_main_image(product_name):
        product = Product.objects.filter(name=product_name).first()
        return product.images.filter(is_main=True).first() if product else None

    for order in Order.objects.filter(user=request.user):
        products_with_images = [
            {'name': product, 'quantity': qty, 'main_image': get_main_image(product)}
            for product, qty in order.products.items()
        ]

        all_orders.append({
            'products': products_with_images,
            'date': timezone.make_aware(datetime.combine(order.order_date, datetime.min.time())),  
            'status': 'Pending',
            'total_price': order.total_price,
            'id': order.id,
            'order_time': order.order_time,
        })

    for order in Shipped.objects.filter(user=request.user):
        products_with_images = [
            {'name': product, 'quantity': qty, 'main_image': get_main_image(product)}
            for product, qty in order.products.items()
        ]

        all_orders.append({
            'products': products_with_images,
            'date': order.shipped_date,
            'status': 'Shipped',
            'total_price': order.total_price,
        })

    for order in Delivered.objects.filter(user=request.user):
        products_with_images = [
            {'name': product, 'quantity': qty, 'main_image': get_main_image(product)}
            for product, qty in order.products.items()
        ]

        all_orders.append({
            'products': products_with_images,
            'date': order.delivered_date,
            'status': 'Delivered',
            'total_price': order.total_price,
        })

    for order in Canceled.objects.filter(user=request.user):
        products_with_images = [
            {'name': product, 'quantity': qty, 'main_image': get_main_image(product)}
            for product, qty in order.products.items()
        ]

        all_orders.append({
            'products': products_with_images,
            'date': order.canceled_date,
            'status': 'Canceled',
            'total_price': order.total_price,
        })

    # ✅ Sort by date
    all_orders.sort(key=lambda order: order['date'], reverse=True)

    return render(request, 'order_history.html', {'orders': all_orders , 'categories': categories,})

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Order, Canceled, Product

@login_required
def cancel_order(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id, user=request.user)

        with transaction.atomic():
            # ✅ Restock the product
            if isinstance(order.products, str):  
                product_list = eval(order.products)  # Convert string to dictionary
            else:
                product_list = order.products

            for product_name, quantity in product_list.items():
                product = Product.objects.filter(name=product_name).first()
                if product:
                    product.quantity_available += quantity  # ✅ Increase quantity
                    product.save()

            # ✅ Move order to Canceled table
            Canceled.objects.create(
                user=order.user,
                products=order.products,
                total_price=order.total_price,
                shipping=order.shipping,
                address=order.address,
                canceled_date=timezone.now(),
            )

            # ✅ Delete order from Order table
            order.delete()

        return redirect("cart:order_history")

    return JsonResponse({'error': "Invalid request method"}, status=400)


from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.utils import timezone
from cart.models import Order, Shipped, Delivered, Canceled, Product

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)  # Ensure we fetch the correct order
    new_status = request.POST.get('status')

    with transaction.atomic():
        if new_status == "shipped":
            # Move to Shipped table
            Shipped.objects.create(
                user=order.user,
                products=order.products,
                total_price=order.total_price,
                shipping=order.shipping,
                address=order.address,
                shipped_date=timezone.now(),
                status="shipped"
            )
            order.delete()  # ✅ Remove from Order table

        elif new_status == "delivered":
            shipped_order = get_object_or_404(Shipped, user=order.user, product=order.product)  # ✅ Fetch from Shipped
            Delivered.objects.create(
                user=shipped_order.user,
                products=shipped_order.products,
                total_price=shipped_order.total_price,
                shipping=shipped_order.shipping,
                address=shipped_order.address,
                
            )
            shipped_order.delete()  # ✅ Remove from Shipped table

        elif new_status == "canceled":
            Canceled.objects.create(
                user=order.user,
                products=order.products,
                total_price=order.total_price,
                shipping=order.shipping,
                address=order.address,
            )

            # ✅ Restock inventory
            for product_name, quantity in order.products.items():
                product = Product.objects.get(name=product_name)
                product.quantity_available += quantity
                product.save()

            order.delete()  # ✅ Remove from Order table

    return redirect("cart:order_history")

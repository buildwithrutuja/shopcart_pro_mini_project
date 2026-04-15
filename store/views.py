from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import random, string, json

from .models import (Category, Product, Cart, CartItem, Coupon,
                     Order, OrderItem, Transaction, Review, UserProfile)
from .forms import (RegisterForm, LoginForm, CheckoutForm, ReviewForm,
                    ProductForm, CouponForm)


def is_admin(user):
    return user.is_staff or user.is_superuser


# ─── HOME ────────────────────────────────────────────────────────────────────

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    top_rated = Product.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(review_count__gt=0).order_by('-avg_rating')[:4]
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'top_rated': top_rated,
    })


# ─── AUTH ────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.save()
        UserProfile.objects.create(user=user)
        Cart.objects.create(user=user)
        login(request, user)
        messages.success(request, f'Welcome to ShopCart Pro, {user.username}!')
        return redirect('home')
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ─── PRODUCTS ────────────────────────────────────────────────────────────────

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', '')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    return render(request, 'store/products.html', {
        'products': products,
        'categories': categories,
        'category_slug': category_slug,
        'query': query,
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.all()
    review_form = ReviewForm()
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]

    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = reviews.filter(user=request.user).exists()

    if request.method == 'POST' and request.user.is_authenticated and not user_reviewed:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been submitted!')
            return redirect('product_detail', slug=slug)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'related': related,
        'user_reviewed': user_reviewed,
    })


# ─── CART ────────────────────────────────────────────────────────────────────

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    coupon_code = request.session.get('coupon_code', '')
    discount = request.session.get('discount', 0)
    subtotal = float(cart.subtotal)
    shipping = 50 if subtotal > 0 else 0
    total = subtotal - float(discount) + shipping
    return render(request, 'store/cart.html', {
        'cart': cart,
        'items': items,
        'coupon_code': coupon_code,
        'discount': discount,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    })


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock:
        messages.error(request, f'Only {product.stock} items available in stock.')
        return redirect(request.META.get('HTTP_REFERER', 'cart'))

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        new_qty = item.quantity + quantity
        if new_qty > product.stock:
            messages.error(request, f'Cannot add more. Only {product.stock} in stock.')
        else:
            item.quantity = new_qty
            item.save()
            messages.success(request, f'Cart updated: {product.name}')
    else:
        item.quantity = quantity
        item.save()
        messages.success(request, f'{product.name} added to cart!')

    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        item.delete()
        messages.info(request, 'Item removed.')
    elif quantity > item.product.stock:
        messages.error(request, f'Only {item.product.stock} available.')
    else:
        item.quantity = quantity
        item.save()
        messages.success(request, 'Cart updated.')
    return redirect('cart')


@login_required
@require_POST
def apply_coupon(request):
    code = request.POST.get('coupon_code', '').strip().upper()
    cart, _ = Cart.objects.get_or_create(user=request.user)
    subtotal = float(cart.subtotal)
    try:
        coupon = Coupon.objects.get(code=code)
        if not coupon.is_valid():
            messages.error(request, 'This coupon is expired or invalid.')
        elif subtotal < float(coupon.minimum_order_amount):
            messages.error(request, f'Minimum order amount ₹{coupon.minimum_order_amount} required.')
        else:
            discount = float(coupon.calculate_discount(cart.subtotal))
            request.session['coupon_code'] = code
            request.session['coupon_id'] = coupon.id
            request.session['discount'] = discount
            messages.success(request, f'Coupon applied! You saved ₹{discount:.2f}')
    except Coupon.DoesNotExist:
        messages.error(request, 'Invalid coupon code.')
    return redirect('cart')


@login_required
def remove_coupon(request):
    for key in ['coupon_code', 'coupon_id', 'discount']:
        request.session.pop(key, None)
    messages.info(request, 'Coupon removed.')
    return redirect('cart')


# ─── CHECKOUT ────────────────────────────────────────────────────────────────

@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    if not items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    discount = float(request.session.get('discount', 0))
    coupon_id = request.session.get('coupon_id')
    subtotal = float(cart.subtotal)
    shipping = 50.0
    total = subtotal - discount + shipping

    profile = getattr(request.user, 'profile', None)
    initial = {}
    if profile:
        initial = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'state': profile.state,
            'pincode': profile.pincode,
        }

    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        # ── TRANSACTION: BEGIN ──────────────────────────────────────────────
        # SQL equivalent: BEGIN TRANSACTION;
        try:
            with transaction.atomic():
                # Verify stock for all items
                for item in items:
                    if item.quantity > item.product.stock:
                        raise ValueError(f'{item.product.name} is out of stock.')

                # Generate unique order number
                order_number = 'SCP' + ''.join(random.choices(string.digits, k=8))

                coupon = None
                if coupon_id:
                    try:
                        coupon = Coupon.objects.select_for_update().get(pk=coupon_id)
                        if not coupon.is_valid():
                            coupon = None
                            discount = 0
                        else:
                            coupon.used_count += 1
                            coupon.save()
                    except Coupon.DoesNotExist:
                        coupon = None

                # Create Order
                # SQL: INSERT INTO store_order (...) VALUES (...);
                order = Order.objects.create(
                    user=request.user,
                    order_number=order_number,
                    status='confirmed',
                    payment_status='paid',
                    coupon=coupon,
                    subtotal=subtotal,
                    discount_amount=discount,
                    shipping_cost=shipping,
                    total_amount=total,
                    full_name=form.cleaned_data['full_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    pincode=form.cleaned_data['pincode'],
                )

                # Create OrderItems and reduce stock
                for item in items:
                    # SQL: INSERT INTO store_orderitem (...) VALUES (...);
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        product_price=item.product.effective_price,
                        quantity=item.quantity,
                        line_total=item.line_total,
                    )
                    # SQL: UPDATE store_product SET stock = stock - quantity WHERE id = ...;
                    item.product.stock -= item.quantity
                    item.product.save()

                # Simulated Payment — Generate Transaction
                txn_id = 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                Transaction.objects.create(
                    order=order,
                    transaction_id=txn_id,
                    transaction_type='payment',
                    amount=total,
                    status='success',
                    payment_method=form.cleaned_data.get('payment_method', 'Simulated Payment'),
                )

                # Clear cart items
                # SQL: DELETE FROM store_cartitem WHERE cart_id = ...;
                items.delete()

                # Clear session coupon
                for key in ['coupon_code', 'coupon_id', 'discount']:
                    request.session.pop(key, None)

                # ── TRANSACTION: COMMIT ─────────────────────────────────────
                # SQL equivalent: COMMIT;
                messages.success(request, f'Order #{order_number} placed successfully! Payment confirmed.')
                return redirect('order_success', order_id=order.id)

        except ValueError as e:
            # ── TRANSACTION: ROLLBACK ───────────────────────────────────────
            # SQL equivalent: ROLLBACK;
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')

    return render(request, 'store/checkout.html', {
        'form': form,
        'items': items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total': total,
        'coupon_code': request.session.get('coupon_code', ''),
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


# ─── ORDERS ──────────────────────────────────────────────────────────────────

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'store/orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


# ─── ADMIN DASHBOARD ─────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_orders = Order.objects.count()
    total_revenue = sum(o.total_amount for o in Order.objects.filter(payment_status='paid'))
    total_products = Product.objects.count()
    total_users = User.objects.count()
    recent_orders = Order.objects.all()[:10]
    recent_transactions = Transaction.objects.all()[:10]
    low_stock = Product.objects.filter(stock__lte=5, is_active=True)
    return render(request, 'store/admin_dashboard.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'recent_transactions': recent_transactions,
        'low_stock': low_stock,
    })


@login_required
@user_passes_test(is_admin)
def admin_products(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'store/admin_products.html', {'products': products})


@login_required
@user_passes_test(is_admin)
def admin_add_product(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product added successfully!')
        return redirect('admin_products')
    return render(request, 'store/admin_product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
@user_passes_test(is_admin)
def admin_edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated!')
        return redirect('admin_products')
    return render(request, 'store/admin_product_form.html', {'form': form, 'title': 'Edit Product'})


@login_required
@user_passes_test(is_admin)
def admin_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('admin_products')
    return render(request, 'store/admin_confirm_delete.html', {'object': product})


@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    orders = Order.objects.select_related('user').all()
    return render(request, 'store/admin_orders.html', {'orders': orders})


@login_required
@user_passes_test(is_admin)
def admin_update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.status = request.POST.get('status', order.status)
        order.save()
        messages.success(request, f'Order #{order.order_number} status updated.')
    return redirect('admin_orders')


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.select_related('profile').all()
    return render(request, 'store/admin_users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_coupons(request):
    coupons = Coupon.objects.all()
    form = CouponForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Coupon created!')
        return redirect('admin_coupons')
    return render(request, 'store/admin_coupons.html', {'coupons': coupons, 'form': form})


@login_required
@user_passes_test(is_admin)
def admin_transactions(request):
    transactions = Transaction.objects.select_related('order').all()
    return render(request, 'store/admin_transactions.html', {'transactions': transactions})

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import Category, Product, Coupon, UserProfile, Cart
from datetime import timedelta
import random

# Real product image URLs from open sources
PRODUCT_IMAGES = {
    'iphone-15-pro':        'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&q=80',
    'samsung-galaxy-s24':   'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&q=80',
    'dell-inspiron-laptop': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80',
    'sony-wh1000xm5':       'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80',
    'boat-rockerz-450':     'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&q=80',
    'oneplus-nord-ce3':     'https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=400&q=80',
    'levis-501-jeans':      'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&q=80',
    'nike-air-max-270':     'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',
    'adidas-tshirt':        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80',
    'cotton-kurta-set':     'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400&q=80',
    'rich-dad-poor-dad':    'https://images.unsplash.com/photo-1592496431122-2349e0fbc666?w=400&q=80',
    'atomic-habits':        'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&q=80',
    'python-crash-course':  'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&q=80',
    'the-alchemist':        'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&q=80',
    'instant-pot-duo':      'https://images.unsplash.com/photo-1585515320310-259814833e62?w=400&q=80',
    'philips-air-fryer':    'https://images.unsplash.com/photo-1617333387457-e0d2f1fe7e6c?w=400&q=80',
    'ikea-desk-lamp':       'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&q=80',
    'yoga-mat-premium':     'https://images.unsplash.com/photo-1601925228997-9f53c9e7a793?w=400&q=80',
    'dumbbell-set-20kg':    'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=80',
    'decathlon-badminton':  'https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=400&q=80',
    'lakme-sunscreen':      'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&q=80',
    'mamaearth-face-wash':  'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&q=80',
    'biotique-shampoo':     'https://images.unsplash.com/photo-1526947425960-945c6e72858f?w=400&q=80',
}

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Categories
        categories_data = [
            ('Electronics', 'electronics', 'Phones, Laptops, Gadgets'),
            ('Clothing', 'clothing', 'Men, Women, Kids fashion'),
            ('Books', 'books', 'Fiction, Non-Fiction, Academic'),
            ('Home & Kitchen', 'home-kitchen', 'Appliances, Decor, Cookware'),
            ('Sports', 'sports', 'Fitness, Outdoor, Games'),
            ('Beauty', 'beauty', 'Skincare, Makeup, Haircare'),
        ]
        categories = {}
        for name, slug, desc in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=slug, defaults={'name': name, 'description': desc}
            )
            categories[slug] = cat
            self.stdout.write(f'  Category: {name}')

        # Products
        products_data = [
            ('iPhone 15 Pro', 'iphone-15-pro', 'electronics', 89999, 84999, 25,
             'Apple iPhone 15 Pro with A17 Pro chip, 48MP camera system, titanium design.'),
            ('Samsung Galaxy S24', 'samsung-galaxy-s24', 'electronics', 74999, 69999, 30,
             'Samsung Galaxy S24 with Snapdragon 8 Gen 3, AI features, brilliant AMOLED display.'),
            ('Dell Inspiron Laptop', 'dell-inspiron-laptop', 'electronics', 55000, 49999, 15,
             'Dell Inspiron 15 with Intel Core i5, 8GB RAM, 512GB SSD. Perfect for work and study.'),
            ('Sony WH-1000XM5', 'sony-wh1000xm5', 'electronics', 29990, 24990, 40,
             'Industry-leading noise cancelling headphones with 30-hour battery life.'),
            ('boAt Rockerz 450', 'boat-rockerz-450', 'electronics', 2999, 1999, 100,
             'Wireless Bluetooth headphones with 15 hours of playback and powerful bass.'),
            ('OnePlus Nord CE 3', 'oneplus-nord-ce3', 'electronics', 24999, 21999, 50,
             'OnePlus Nord CE 3 with Snapdragon 782G, 50MP camera, 80W fast charging.'),
            ("Levi's 501 Jeans", 'levis-501-jeans', 'clothing', 3999, 2999, 60,
             "Classic straight fit Levi's 501 jeans. Timeless style, durable denim."),
            ('Nike Air Max 270', 'nike-air-max-270', 'clothing', 10995, 8995, 45,
             'Nike Air Max 270 running shoes with Max Air cushioning for all-day comfort.'),
            ('Adidas T-Shirt', 'adidas-tshirt', 'clothing', 1499, 999, 120,
             'Premium Adidas cotton t-shirt with moisture-wicking technology.'),
            ('Cotton Kurta Set', 'cotton-kurta-set', 'clothing', 2499, 1799, 80,
             'Elegant cotton kurta set for men. Perfect for festivals and casual occasions.'),
            ('Rich Dad Poor Dad', 'rich-dad-poor-dad', 'books', 350, 299, 200,
             "Robert Kiyosaki's bestselling personal finance book."),
            ('Atomic Habits', 'atomic-habits', 'books', 499, 399, 180,
             "James Clear's guide to building good habits. Tiny changes, remarkable results."),
            ('Python Crash Course', 'python-crash-course', 'books', 650, 549, 90,
             'A hands-on introduction to programming in Python 3 with projects.'),
            ('The Alchemist', 'the-alchemist', 'books', 299, 249, 250,
             "Paulo Coelho's magical story about following your dreams."),
            ('Instant Pot Duo', 'instant-pot-duo', 'home-kitchen', 8999, 7499, 35,
             '7-in-1 multi-cooker: pressure cooker, slow cooker, rice cooker and more.'),
            ('Philips Air Fryer', 'philips-air-fryer', 'home-kitchen', 12999, 10999, 28,
             'Philips Air Fryer with Rapid Air Technology. Cook crispy food with 90% less fat.'),
            ('IKEA Desk Lamp', 'ikea-desk-lamp', 'home-kitchen', 1499, None, 55,
             'Minimalist LED desk lamp with adjustable arm and brightness settings.'),
            ('Yoga Mat Premium', 'yoga-mat-premium', 'sports', 1299, 999, 75,
             'Non-slip premium yoga mat with alignment lines. 6mm thick for joint support.'),
            ('Dumbbell Set 20kg', 'dumbbell-set-20kg', 'sports', 3499, 2799, 20,
             'Adjustable dumbbell set with anti-slip grip. Includes carrying case.'),
            ('Decathlon Badminton Racket', 'decathlon-badminton', 'sports', 799, None, 90,
             'Lightweight aluminum badminton racket for beginners and intermediate players.'),
            ('Lakme Sunscreen SPF50', 'lakme-sunscreen', 'beauty', 499, 399, 150,
             'Lakme Sun Expert SPF50 sunscreen. Broad spectrum UVA/UVB protection.'),
            ('Mamaearth Face Wash', 'mamaearth-face-wash', 'beauty', 299, 249, 200,
             'Ubtan face wash with turmeric and saffron for natural glow. Paraben-free.'),
            ('Biotique Shampoo', 'biotique-shampoo', 'beauty', 199, None, 300,
             'Biotique bio kelp protein shampoo for falling hair. 100% botanical extracts.'),
        ]

        for name, slug, cat_slug, price, disc, stock, desc in products_data:
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'category': categories[cat_slug],
                    'name': name,
                    'description': desc,
                    'price': price,
                    'discount_price': disc,
                    'stock': stock,
                    'is_active': True,
                    'image_url': PRODUCT_IMAGES.get(slug, ''),
                }
            )
            if not created and not product.image_url:
                product.image_url = PRODUCT_IMAGES.get(slug, '')
                product.save()
            self.stdout.write(f'  Product: {name}')

        # Coupons
        now = timezone.now()
        coupons_data = [
            ('SAVE10', 'percentage', 10, 500, 100),
            ('FLAT50', 'fixed', 50, 300, 50),
            ('WELCOME20', 'percentage', 20, 1000, 200),
            ('BIGDEAL', 'fixed', 150, 2000, 30),
            ('FREESHIP', 'fixed', 50, 0, 500),
        ]
        for code, dtype, value, min_amt, max_uses in coupons_data:
            Coupon.objects.get_or_create(
                code=code,
                defaults={
                    'discount_type': dtype,
                    'discount_value': value,
                    'minimum_order_amount': min_amt,
                    'max_uses': max_uses,
                    'is_active': True,
                    'valid_from': now - timedelta(days=1),
                    'valid_until': now + timedelta(days=365),
                }
            )
            self.stdout.write(f'  Coupon: {code}')

        # Users
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@shopcart.com', 'admin123')
            UserProfile.objects.get_or_create(user=admin, defaults={'is_customer': False})
            Cart.objects.get_or_create(user=admin)
            self.stdout.write('  Admin: admin / admin123')

        customers = [
            ('customer1', 'customer1@email.com', 'pass@1234', 'Rahul', 'Sharma'),
            ('customer2', 'customer2@email.com', 'pass@1234', 'Priya', 'Singh'),
            ('customer3', 'customer3@email.com', 'pass@1234', 'Arjun', 'Patel'),
        ]
        for uname, email, pwd, fn, ln in customers:
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(uname, email, pwd, first_name=fn, last_name=ln)
                UserProfile.objects.get_or_create(user=u, defaults={
                    'phone': f'98{random.randint(10000000, 99999999)}',
                    'city': random.choice(['Mumbai', 'Pune', 'Delhi', 'Bangalore']),
                    'state': 'Maharashtra',
                })
                Cart.objects.get_or_create(user=u)
                self.stdout.write(f'  Customer: {uname} / pass@1234')

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
        self.stdout.write('Login: admin / admin123')
        self.stdout.write('Coupons: SAVE10, FLAT50, WELCOME20, BIGDEAL, FREESHIP')

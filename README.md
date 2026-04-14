# 🛒 ShopCart Pro — Online Shopping Cart Transaction Management

**DBMS Mini Project** | Django + SQLite | Bootstrap 5

---

## 📁 Project Structure

```
shopcart_pro/
├── manage.py
├── requirements.txt
│
├── shopcart_pro/              ← Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── store/                     ← Main application
│   ├── models.py              ← All 10 database models
│   ├── views.py               ← All view logic
│   ├── urls.py                ← URL routing
│   ├── forms.py               ← Django forms
│   ├── admin.py               ← Admin panel config
│   ├── context_processors.py  ← Cart count in navbar
│   ├── management/commands/
│   │   └── seed_data.py       ← Sample data seeder
│   └── templates/store/       ← 19 HTML templates
│
└── static/
    ├── css/style.css          ← Premium emerald/blue theme
    └── js/main.js             ← Dark/light mode + interactions
```

---

## ⚙️ Setup & Run (Step by Step)

### Step 1 — Open terminal in project folder
Make sure you are inside the `shopcart_pro` folder (where `manage.py` is).

### Step 2 — Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Requirements
```bash
pip install -r requirements.txt
```

### Step 4 — Database Setup
```bash
python manage.py makemigrations store
python manage.py migrate
```

### Step 5 — Load Sample Data
```bash
python manage.py seed_data
```

### Step 6 — Run Server
```bash
# Local only
python manage.py runserver

# Access from phone/other devices on same WiFi
python manage.py runserver 0.0.0.0:8000
```

Open browser: **http://127.0.0.1:8000**

---

## 🔑 Login Credentials

| Role      | Username   | Password    |
|-----------|------------|-------------|
| Admin     | admin      | admin123    |
| Customer  | customer1  | pass@1234   |
| Customer  | customer2  | pass@1234   |
| Customer  | customer3  | pass@1234   |

---

## 🌐 Application URLs

| Page            | URL                               |
|-----------------|-----------------------------------|
| Home            | http://127.0.0.1:8000/            |
| Products        | http://127.0.0.1:8000/products/   |
| Cart            | http://127.0.0.1:8000/cart/       |
| Checkout        | http://127.0.0.1:8000/checkout/   |
| My Orders       | http://127.0.0.1:8000/orders/     |
| Login           | http://127.0.0.1:8000/login/      |
| Register        | http://127.0.0.1:8000/register/   |
| Admin Dashboard | http://127.0.0.1:8000/dashboard/  |
| Django Admin    | http://127.0.0.1:8000/admin/      |

---

## 🎟️ Coupon Codes

| Code       | Type       | Value | Min Order |
|------------|------------|-------|-----------|
| SAVE10     | Percentage | 10%   | ₹500      |
| FLAT50     | Fixed      | ₹50   | ₹300      |
| WELCOME20  | Percentage | 20%   | ₹1000     |
| BIGDEAL    | Fixed      | ₹150  | ₹2000     |
| FREESHIP   | Fixed      | ₹50   | ₹0        |

---

## 🗄️ Database Tables

| Table        | Description                          |
|--------------|--------------------------------------|
| User         | Django built-in auth                 |
| UserProfile  | Extended user info                   |
| Category     | Product categories                   |
| Product      | Products with price, stock, images   |
| Cart         | One cart per user                    |
| CartItem     | Items in cart                        |
| Coupon       | Discount codes                       |
| Order        | Placed orders                        |
| OrderItem    | Snapshot of products in order        |
| Transaction  | Payment records                      |
| Review       | Product ratings and comments         |

---

## 🔄 Transaction Management

Checkout uses `django.db.transaction.atomic()`:

```python
with transaction.atomic():
    # BEGIN TRANSACTION
    order = Order.objects.create(...)       # INSERT INTO store_order
    for item in cart_items:
        OrderItem.objects.create(...)       # INSERT INTO store_orderitem
        product.stock -= item.quantity      # UPDATE store_product SET stock
        product.save()
    Transaction.objects.create(...)         # INSERT INTO store_transaction
    cart_items.delete()                     # DELETE FROM store_cartitem
    # COMMIT on success / ROLLBACK on error
```

---

## 🛠 Tech Stack

| Layer    | Technology            |
|----------|-----------------------|
| Backend  | Python 3 + Django 4.2 |
| Frontend | HTML5, Bootstrap 5    |
| Styling  | CSS3, Outfit font     |
| Database | SQLite (Django ORM)   |
| Icons    | Bootstrap Icons       |

---

*DBMS Mini Project — ShopCart Pro v2.0*

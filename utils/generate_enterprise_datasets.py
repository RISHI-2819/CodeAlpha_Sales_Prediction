import json
import os
import random
from datetime import datetime, timedelta

os.makedirs('dataset', exist_ok=True)
random.seed(42)

# Copy advertising.csv to dataset/
if os.path.exists('advertising.csv'):
    with open('advertising.csv', 'r') as f_in:
        content = f_read = f_in.read()
    with open(os.path.join('dataset', 'advertising.csv'), 'w') as f_out:
        f_out.write(content)

# 1. GENERATE 100 REALISTIC PRODUCTS
categories = ['Electronics', 'Audio & Sound', 'Wearables', 'Accessories', 'Smart Home']
brands = ['Sony', 'Apple', 'Samsung', 'Bose', 'Anker', 'Logitech', 'Dell', 'LG', 'JBL', 'Sennheiser']
suppliers = ['TechData Global', 'Ingram Micro', 'Synnex Logistics', 'Apex Electronics Ltd', 'Nexus Distribution']

product_names_base = [
    "Wireless Noise-Canceling Headphones", "Ultra HD Smart Projector 4K", "Smart Fitness Watch Ultra",
    "Dual Wireless Charging Pad", "Spatial Audio Earbuds Pro", "RGB Mechanical Keyboard",
    "Ergonomic Gaming Mouse", "Portable Bluetooth Speaker", "Curved Gaming Monitor 34-inch",
    "Smart Security Camera 1080p", "USB-C Multi-Port Hub", "Active Noise Canceling Earphones",
    "Smart Thermostat Pro", "High-Speed WiFi 6 Router", "Studio Condenser Microphone",
    "Wireless Graphics Drawing Tablet", "Smart LED Desk Lamp", "4K Webcam with Autofocus",
    "Portable SSD Storage 1TB", "Smart Robot Vacuum Cleaner", "Over-Ear Hi-Fi Headphones",
    "True Wireless Earbuds Max", "Smart Doorbell Video Camera", "Bluetooth Tracker Tags 4-Pack",
    "Foldable Drone 4K Camera", "Action Camera Waterproof 60FPS", "Smart Plug Surge Protector",
    "Universal Laptop Power Bank", "Compact Soundbar with Subwoofer", "Mechanical Wireless Numpad"
]

images_pool = [
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1586816879360-004f5b0c51e3?w=500&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=500&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&auto=format&fit=crop&q=60"
]

products = []
for i in range(1, 101):
    cat = random.choice(categories)
    brand = random.choice(brands)
    base_name = random.choice(product_names_base)
    name = f"{brand} {base_name} v{random.randint(1,5)}"
    
    cost = round(random.uniform(15.0, 450.0), 2)
    mrp = round(cost * random.uniform(1.6, 2.4), 2)
    discount_pct = random.choice([0, 5, 10, 15, 20, 25])
    selling_price = round(mrp * (1 - discount_pct / 100.0), 2)
    profit = round(selling_price - cost, 2)
    stock = random.randint(0, 150)
    units_sold = random.randint(25, 850)
    rating = round(random.uniform(4.0, 5.0), 1)
    reviews = random.randint(15, 450)
    
    status = "Out of Stock" if stock == 0 else ("Low Stock" if stock < 15 else "In Stock")
    bestseller = units_sold > 400
    
    prod = {
        "id": f"PRD-{1000 + i}",
        "name": name,
        "category": cat,
        "brand": brand,
        "description": f"Enterprise-grade {name} delivering premium performance, sleek aesthetics, and high reliability.",
        "mrp": mrp,
        "selling_price": selling_price,
        "cost_price": cost,
        "discount": f"{discount_pct}% OFF" if discount_pct > 0 else "Regular Price",
        "profit": profit,
        "stock": stock,
        "units_sold": units_sold,
        "rating": rating,
        "reviews": reviews,
        "supplier": random.choice(suppliers),
        "warranty": random.choice(["1 Year Limited", "2 Year Extended", "3 Year Enterprise"]),
        "status": status,
        "bestseller": bestseller,
        "img": random.choice(images_pool)
    }
    products.append(prod)

with open('dataset/products.json', 'w') as f:
    json.dump(products, f, indent=2)

print("Generated dataset/products.json (100 products)")

# 2. GENERATE 200 REALISTIC CUSTOMERS
first_names = ["James", "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "Lucas", "Isabella", 
               "Arjun", "Priya", "Rahul", "Ananya", "Karthik", "Deepika", "Vijay", "Meera", "Siddharth", "Kavya"]
last_names = ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
              "Sharma", "Patel", "Kumar", "Iyer", "Raman", "Nair", "Sundaram", "Reddy", "Verma", "Gupta"]
locations = ["New York, NY", "San Francisco, CA", "Austin, TX", "Chicago, IL", "Seattle, WA", 
             "Chennai, India", "Bengaluru, India", "Mumbai, India", "London, UK", "Toronto, Canada"]

customers = []
for i in range(1, 201):
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    gender = random.choice(["Male", "Female", "Other"])
    age = random.randint(21, 62)
    loc = random.choice(locations)
    purchases = random.randint(2, 45)
    spend = round(purchases * random.uniform(85.0, 320.0), 2)
    clv = round(spend * random.uniform(1.5, 3.0), 2)
    loyalty = "VIP Gold" if spend > 4000 else ("Silver Member" if spend > 1500 else "Standard")
    
    cust = {
        "id": f"CUST-{2000 + i}",
        "name": f"{fname} {lname}",
        "gender": gender,
        "age": age,
        "location": loc,
        "email": f"{fname.lower()}.{lname.lower()}{i}@example.com",
        "phone": f"+1 ({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
        "purchases_count": purchases,
        "total_spending": spend,
        "favourite_category": random.choice(categories),
        "clv": clv,
        "loyalty_tier": loyalty
    }
    customers.append(cust)

with open('dataset/customers.json', 'w') as f:
    json.dump(customers, f, indent=2)

print("Generated dataset/customers.json (200 customers)")

# 3. GENERATE ORDERS & INVENTORY DATASETS
orders = []
statuses = ["Delivered", "Delivered", "Delivered", "Processing", "Shipped", "Cancelled"]
methods = ["Credit Card", "PayPal", "Apple Pay", "Bank Transfer"]

start_date = datetime.now() - timedelta(days=90)

for i in range(1, 151):
    prod = random.choice(products)
    cust = random.choice(customers)
    qty = random.randint(1, 4)
    rev = round(prod["selling_price"] * qty, 2)
    prof = round(prod["profit"] * qty, 2)
    order_dt = start_date + timedelta(days=random.randint(1, 90), hours=random.randint(0, 23))
    deliv_dt = order_dt + timedelta(days=random.randint(2, 5))
    
    ord_item = {
        "id": f"ORD-{5000 + i}",
        "product_name": prod["name"],
        "product_id": prod["id"],
        "customer_name": cust["name"],
        "customer_email": cust["email"],
        "quantity": qty,
        "order_date": order_dt.strftime("%Y-%m-%d"),
        "delivery_date": deliv_dt.strftime("%Y-%m-%d"),
        "status": random.choice(statuses),
        "payment_method": random.choice(methods),
        "revenue": rev,
        "profit": prof
    }
    orders.append(ord_item)

with open('dataset/orders.json', 'w') as f:
    json.dump(orders, f, indent=2)

print("Generated dataset/orders.json (150 order transactions)")

# Inventory
inventory = []
for p in products:
    inv = {
        "product_id": p["id"],
        "product_name": p["name"],
        "category": p["category"],
        "stock_qty": p["stock"],
        "warehouse": random.choice(["Warehouse East", "Warehouse West", "Central Distribution"]),
        "inventory_value": round(p["stock"] * p["cost_price"], 2),
        "restock_suggested": p["stock"] < 15,
        "velocity": "Fast Moving" if p["units_sold"] > 350 else "Standard Moving"
    }
    inventory.append(inv)

with open('dataset/inventory.json', 'w') as f:
    json.dump(inventory, f, indent=2)

print("Generated dataset/inventory.json")

print("All enterprise datasets generated successfully!")

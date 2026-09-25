import random
from datetime import datetime, timedelta
from .database import engine, SessionLocal, Base
from .models import Customer, Order, Refund

CUSTOMERS = [
    ("Anil Kumar", "anil@example.com", "9876500001"),
    ("Priya Sharma", "priya@example.com", "9876500002"),
    ("Sai Kiran", "sai@example.com", "9876500003"),
    ("Divya Reddy", "divya@example.com", "9876500004"),
    ("Rahul Verma", "rahul@example.com", "9876500005"),
    ("Sneha Rao", "sneha@example.com", "9876500006"),
    ("Karthik N", "karthik@example.com", "9876500007"),
    ("Meena Iyer", "meena@example.com", "9876500008"),
]

PRODUCTS = [
    ("Wireless Earbuds", 1999), ("Smartwatch", 3499), ("Laptop Bag", 1299),
    ("Bluetooth Speaker", 2499), ("Phone Case", 499), ("Power Bank", 1599),
    ("USB-C Charger", 899), ("Mechanical Keyboard", 3999),
]

STATUSES = ["placed", "shipped", "delivered", "delivered", "cancelled"]


def seed():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    random.seed(42)

    with SessionLocal() as db:
        customers = [Customer(name=n, email=e, phone=p) for n, e, p in CUSTOMERS]
        db.add_all(customers)
        db.flush()

        orders = []
        for i in range(25):
            product, price = random.choice(PRODUCTS)
            orders.append(Order(
                id=1001 + i,
                customer_id=random.choice(customers).id,
                product=product,
                amount=price,
                status=random.choice(STATUSES),
                order_date=datetime.now() - timedelta(days=random.randint(1, 30)),
            ))
        db.add_all(orders)
        db.flush()

        refunds = [
            Refund(order_id=o.id, amount=o.amount,
                   status=random.choice(["requested", "approved", "processed"]))
            for o in orders if o.status == "cancelled"
        ]
        db.add_all(refunds)
        db.commit()

        print(f"Created {len(customers)} customers, {len(orders)} orders, {len(refunds)} refunds")


if __name__ == "__main__":
    seed()
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.auth.models import User
from app.catalog.models import Product


app = create_app()

with app.app_context():

    # Remove existing seed data
    db.session.query(Product).delete()
    db.session.query(User).delete()

    # -------------------------
    # Sample Users
    # -------------------------

    user1 = User(
        name="Esha Kamran",
        email="esha@example.com",
        password_hash="hashed_password_123",
        role="customer"
    )

    user2 = User(
        name="Admin User",
        email="admin@example.com",
        password_hash="hashed_admin_password",
        role="admin"
    )

    # -------------------------
    # Sample Products
    # -------------------------

    product1 = Product(
        name="Wireless Headphones",
        description="Bluetooth wireless headphones",
        price=Decimal("4999.00"),
        stock=20
    )

    product2 = Product(
        name="Laptop",
        description="15-inch laptop for students and professionals",
        price=Decimal("125000.00"),
        stock=10
    )

    product3 = Product(
        name="Wireless Mouse",
        description="Ergonomic wireless mouse",
        price=Decimal("2500.00"),
        stock=30
    )

    # -------------------------
    # Add Data to Database
    # -------------------------

    db.session.add_all([
        user1,
        user2,
        product1,
        product2,
        product3
    ])

    # Save changes
    db.session.commit()

    print("Seed data added successfully!")
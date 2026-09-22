from flask import Blueprint, jsonify, request
from app.extensions import db
from app.orders.models import Order
from app.auth.models import User
from app.tasks.pdf_tasks import generate_invoice_pdf
from app.tasks.email_tasks import send_email_task


orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/test", methods=["GET"])
def orders_test():
    return jsonify({
        "message": "Orders module is working"
    })


@orders_bp.route("/", methods=["POST"])
def create_order():
    data = request.get_json()

    user_id = data.get("user_id")
    total_amount = data.get("total_amount")

    if not user_id or total_amount is None:
        return jsonify({
            "error": "user_id and total_amount are required"
        }), 400

    # Find customer
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    # Create order
    order = Order(
        user_id=user_id,
        total_amount=total_amount
    )

    db.session.add(order)
    db.session.commit()

    # Generate invoice in background
    generate_invoice_pdf.delay(
        order.id,
        order.user_id,
        order.total_amount
    )

    # Send real confirmation email in background
    send_email_task.delay(
        user.email,
        f"Order #{order.id} Confirmation",
        f"""Hello {user.name},

Thank you for your order!

Your order #{order.id} has been successfully placed.

Order Total: Rs. {order.total_amount}

Your invoice is being generated and will be available shortly.

Thank you for shopping with us!

E-Commerce Team
"""
    )

    return jsonify({
        "message": "Order created successfully",
        "order_id": order.id,
        "customer_email": user.email,
        "invoice": f"invoice_{order.id}.pdf",
        "email": "Confirmation email queued"
    }), 201
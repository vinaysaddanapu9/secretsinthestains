from flask import Blueprint, request, jsonify
import os
import razorpay

payment_bp = Blueprint("payment", __name__, url_prefix="/api/payment")

client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET")
    )
)


@payment_bp.route("/create-order", methods=["POST"])
def create_order():

    data = request.get_json()

    registration_id = data.get("registration_id")

    if not registration_id:
        return jsonify({
            "success": False,
            "message": "registration_id is required"
        }), 400

    # Get this from your database in production
    amount = 100

    order = client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "receipt": f"registration_{registration_id}",
        "payment_capture": 1
    })

    return jsonify({
        "success": True,
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": "INR",
        "key_id": os.getenv("RAZORPAY_KEY_ID")
    })


@payment_bp.route("/verify", methods=["POST"])
def verify():

    data = request.get_json()

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })

        # TODO:
        # Update registration/payment in database
        # payment_status = "PAID"

        return jsonify({
            "success": True,
            "message": "Payment verified successfully"
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": "Invalid payment"
        }), 400
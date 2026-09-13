from flask import Blueprint, request, jsonify
import os
import hmac
import razorpay

payment_bp = Blueprint(
    "payment",
    __name__,
    url_prefix="/api/payment"
)

# ============================================================
# RAZORPAY CONFIGURATION
# ============================================================

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    raise RuntimeError(
        "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET "
        "are not configured."
    )


client = razorpay.Client(
    auth=(
        RAZORPAY_KEY_ID,
        RAZORPAY_KEY_SECRET
    )
)


# ============================================================
# PAYMENT AMOUNT
# IMPORTANT:
# Do NOT accept amount from frontend.
# ============================================================

WEBINAR_AMOUNT = 39
CURRENCY = "INR"


# ============================================================
# CREATE RAZORPAY ORDER
# ============================================================

@payment_bp.route("/create-order", methods=["POST"])
def create_order():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    registration_id = data.get("registration_id")

    if not registration_id:
        return jsonify({
            "success": False,
            "message": "Registration ID is required."
        }), 400

    # Validate registration ID
    try:
        registration_id = int(registration_id)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid registration ID."
        }), 400

    if registration_id <= 0:
        return jsonify({
            "success": False,
            "message": "Invalid registration ID."
        }), 400

    # --------------------------------------------------------
    # IMPORTANT:
    # Amount is controlled by server.
    # Never take amount from request.
    # --------------------------------------------------------

    amount_paise = WEBINAR_AMOUNT * 100

    try:

        order = client.order.create({
            "amount": amount_paise,
            "currency": CURRENCY,
            "receipt": f"webinar_{registration_id}",
            "payment_capture": 1,
            "notes": {
                "registration_id": str(registration_id)
            }
        })

    except Exception:

        return jsonify({
            "success": False,
            "message": "Unable to create payment order."
        }), 500

    return jsonify({
        "success": True,
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key_id": RAZORPAY_KEY_ID,
        "registration_id": registration_id
    })


# ============================================================
# VERIFY PAYMENT
# ============================================================

@payment_bp.route("/verify", methods=["POST"])
def verify_payment():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    registration_id = data.get("registration_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")

    # --------------------------------------------------------
    # Validate required fields
    # --------------------------------------------------------

    if not registration_id:
        return jsonify({
            "success": False,
            "message": "Registration ID is required."
        }), 400

    if not razorpay_order_id:
        return jsonify({
            "success": False,
            "message": "Razorpay order ID is required."
        }), 400

    if not razorpay_payment_id:
        return jsonify({
            "success": False,
            "message": "Razorpay payment ID is required."
        }), 400

    if not razorpay_signature:
        return jsonify({
            "success": False,
            "message": "Razorpay signature is required."
        }), 400

    # --------------------------------------------------------
    # Validate registration ID
    # --------------------------------------------------------

    try:
        registration_id = int(registration_id)
    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Invalid registration ID."
        }), 400

    # --------------------------------------------------------
    # Verify Razorpay signature
    # --------------------------------------------------------

    try:

        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

    except Exception:

        return jsonify({
            "success": False,
            "message": "Payment verification failed."
        }), 400

    # --------------------------------------------------------
    # Fetch payment from Razorpay
    # --------------------------------------------------------

    try:

        payment = client.payment.fetch(
            razorpay_payment_id
        )

    except Exception:

        return jsonify({
            "success": False,
            "message": "Unable to verify payment."
        }), 500

    # --------------------------------------------------------
    # Verify payment belongs to this order
    # --------------------------------------------------------

    payment_order_id = payment.get("order_id")

    if not payment_order_id:
        return jsonify({
            "success": False,
            "message": "Invalid payment."
        }), 400

    if not hmac.compare_digest(
        str(payment_order_id),
        str(razorpay_order_id)
    ):
        return jsonify({
            "success": False,
            "message": "Payment order mismatch."
        }), 400

    # --------------------------------------------------------
    # Verify amount
    # --------------------------------------------------------

    expected_amount = WEBINAR_AMOUNT * 100

    if payment.get("amount") != expected_amount:
        return jsonify({
            "success": False,
            "message": "Payment amount mismatch."
        }), 400

    # --------------------------------------------------------
    # Verify currency
    # --------------------------------------------------------

    if payment.get("currency") != CURRENCY:
        return jsonify({
            "success": False,
            "message": "Invalid payment currency."
        }), 400

    # --------------------------------------------------------
    # Verify payment status
    # --------------------------------------------------------

    if payment.get("status") != "captured":
        return jsonify({
            "success": False,
            "message": "Payment has not been captured."
        }), 400

    # ========================================================
    # PAYMENT SUCCESS
    # ========================================================

    # TODO:
    # Update your database here:
    #
    # payment_status = "PAID"
    # razorpay_order_id = razorpay_order_id
    # razorpay_payment_id = razorpay_payment_id
    #
    # We will add this once your database function is known.

    return jsonify({
        "success": True,
        "message": "Payment verified successfully.",
        "registration_id": registration_id,
        "payment_id": razorpay_payment_id
    })
import uuid
from flask import current_app


def create_razorpay_order(amount_inr):
    """Create a Razorpay order or return a demo order."""
    if current_app.config.get('PAYMENT_DEMO_MODE'):
        return {
            'id': f'demo_{uuid.uuid4().hex[:16]}',
            'amount': int(amount_inr * 100),
            'currency': 'INR',
            'demo': True
        }

    import razorpay
    client = razorpay.Client(
        auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET'])
    )
    order = client.order.create({
        'amount': int(amount_inr * 100),  # Razorpay uses paise
        'currency': 'INR',
        'payment_capture': 1
    })
    return order


def verify_razorpay_payment(payment_id, order_id, signature):
    """Verify Razorpay payment signature."""
    if current_app.config.get('PAYMENT_DEMO_MODE'):
        return True

    import razorpay
    client = razorpay.Client(
        auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET'])
    )
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        return True
    except razorpay.errors.SignatureVerificationError:
        return False

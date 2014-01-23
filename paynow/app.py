# PayNow API

print "starting PayNow"
from flask import Flask, jsonify, session, request
from models import User, PaymentMethod, Payment
from session import ItsDangerousSessionInterface
from mongoengine import connect

app = Flask(__name__)
app.session_interface = ItsDangerousSessionInterface()

# Secret Key
app.secret_key = 'AZBTelodE7XnEShJx8dh'

# Connect to Mongo
connect('paynow')

@app.route('/')
def index():
    return jsonify(api="PayNow v 1.0", user=session.user.json if session.user else None)

# Authenticate
@app.route('/auth')
def auth():
    try:
        user = User.objects.get(phone="919-426-2830")
    except User.DoesNotExist:
        user = User.create(phone="919-426-2830", name="Maliki Mamane")

    session['user_id'] = str(user.id)
    return jsonify(user=user.json)

# Add Payment Method
@app.route('/payment-method', methods=['POST'])
def add_payment_method():
    user = session.user
    payment_method = PaymentMethod.add(user=user, **request.json)
    user.update(default_payment_method=payment_method)
    return jsonify(payment_method=payment_method.json)

# Generate code
@app.route('/code')
def generate_payment():
    payment_method = session.user.default_payment_method
    payment = Payment.generate(user=session.user, payment_method=payment_method)
    return jsonify(payment=payment.json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5999, debug=True)

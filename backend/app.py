from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Customer, Transaction
from datetime import datetime, timedelta
from config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def hello():
    return "Hello from the Grocery Store Debt Manager API!"

def get_customer_or_404(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return None, jsonify({"error": "Customer not found"}), 404
    return customer, None, None

@app.route('/customers', methods=['GET', 'POST'])
def handle_customers():
    if request.method == 'POST':
        data = request.json
        existing_customer = Customer.query.filter_by(name=data['name']).first()
        if existing_customer:
            return jsonify({"error": "Customer already exists"}), 400

        new_customer = Customer(name=data['name'], phone=data['phone'], address=data['address'])
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "Customer added successfully", "id": new_customer.id}), 201
    else:
        customers = Customer.query.all()
        return jsonify([
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "address": c.address,
                "balance": c.balance
            } for c in customers
        ])

@app.route('/customers/<int:customer_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_customer(customer_id):
    customer, error_response, status_code = get_customer_or_404(customer_id)
    if error_response:
        return error_response, status_code

    if request.method == 'GET':
        return jsonify({
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "address": customer.address,
            "balance": customer.balance
        })
    elif request.method == 'PUT':
        data = request.json
        customer.name = data['name']
        customer.phone = data['phone']
        customer.address = data['address']
        db.session.commit()
        return jsonify({"message": "Customer updated successfully"})
    elif request.method == 'DELETE':
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": "Customer deleted successfully"})

@app.route('/purchases', methods=['POST'])
def record_purchase():
    data = request.json
    customer_id = data['customer_id']
    amount = data['amount']

    customer, error_response, status_code = get_customer_or_404(customer_id)
    if error_response:
        return error_response, status_code

    new_transaction = Transaction(customer_id=customer_id, type='Purchase', amount=amount)
    customer.balance += amount
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({"message": "Purchase recorded successfully"})

@app.route('/payments', methods=['POST'])
def process_payment():
    data = request.json
    customer_id = data['customer_id']
    amount = data['amount']

    customer, error_response, status_code = get_customer_or_404(customer_id)
    if error_response:
        return error_response, status_code

    new_transaction = Transaction(customer_id=customer_id, type='Payment', amount=-amount)
    customer.balance -= amount
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({"message": "Payment processed successfully"})

@app.route('/statements/<int:customer_id>', methods=['GET'])
def generate_statement(customer_id):
    customer, error_response, status_code = get_customer_or_404(customer_id)
    if error_response:
        return error_response, status_code

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('transaction_type', None)

    query = Transaction.query.filter(Transaction.customer_id == customer_id)

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    if transaction_type:
        query = query.filter(Transaction.type.ilike(f'%{transaction_type}%'))

    transactions = query.order_by(Transaction.date.desc()).all()
    balance = customer.balance

    statement = {
        "customer": customer.name,
        "balance": balance,
        "transactions": [
            {
                "date": t.date.strftime('%Y-%m-%d %H:%M:%S'),
                "type": t.type if t.type else "Unknown",
                "amount": t.amount
            } for t in transactions
        ],
        "message": None
    }

    if not statement["transactions"]:
        statement["message"] = "No transactions found for the selected date range and/or transaction type."

    return jsonify(statement), 200


    return jsonify(statement)

@app.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    total_customers = Customer.query.count()
    total_debt = db.session.query(db.func.sum(Customer.balance)).scalar() or 0.0
    recent_transactions = Transaction.query.order_by(Transaction.date.desc()).limit(10).all()

    recent_transactions_data = [
        {
            "customer": t.customer.name,
            "date": t.date.strftime('%Y-%m-%d %H:%M:%S'),
            "type": t.type,
            "amount": t.amount
        } for t in recent_transactions
    ]
    return jsonify({
        "totalCustomers": total_customers,
        "totalDebt": total_debt,
        "recentTransactions": recent_transactions_data
    })

@app.route('/flush_database', methods=['POST'])
def flush_database():
    confirmation = request.json.get('confirmation')
    if confirmation != "I confirm that I want to delete all data":
        return jsonify({"error": "Confirmation phrase does not match"}), 400

    try:
        db.drop_all()
        db.create_all()
        return jsonify({"message": "Database flushed successfully"}), 200
    except Exception as e:
        logger.error(f"Error flushing database: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
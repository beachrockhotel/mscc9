import requests
from flask import Flask, jsonify
from flask import request, render_template
from models import db
from prometheus_flask_exporter import PrometheusMetrics
from functools import wraps
from keycloak import KeycloakOpenID, keycloak_openid
import os
from menu_service import add_menu_item, get_menu, make_order, get_orders
from reservation_service import reserve_seat, get_reservations, check_availability, cancel_reservation

app = Flask(__name__)

metrics = PrometheusMetrics(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://dmitriy:321123@localhost/club')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

is_db_initialized = False

keycloakid = KeycloakOpenID(server_url='http://keycloak:8080/', client_id='mscc', realm_name='cc', client_secret_key='gU5PljHnBxV2v5CgBXli5EpV6KnDCHhV')

@app.route('/login')
def login():
    user_name = request.args.get('login')
    password = request.args.get('password')
    token = keycloakid.token(grant_type=['password'], username=user_name, password=password)
    return jsonify(token)

def check_user_roles(token:str):
    try:
        token_info = keycloakid.introspect(token)
        roles = token_info.get("realm_access", {}).get("roles", [])
        return "moder" in roles
    except Exception as e:
        print(e)
        return False

@app.before_request
def create_tables():
    global is_db_initialized
    if not is_db_initialized:
        db.create_all()
        is_db_initialized = True

def require_auth(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            if check_user_roles(token):
                return func(*args, **kwargs)
            else:
                return jsonify({"error": "Access denied"}), 403
        else:
            return jsonify({"error": "Authorization header is missing or invalid"}), 401
    return decorated_function

@app.route('/')
@require_auth
def home():
    return render_template('index.html')

@app.route('/menu', methods=['POST'])
def add_menu_endpoint():
    return add_menu_item()

@app.route('/menu', methods=['GET'])
@require_auth
def get_menu_endpoint():
    return get_menu()

@app.route('/order', methods=['POST'])
def order_endpoint():
    return make_order()

@app.route('/orders', methods=['GET'])
@require_auth
def orders_endpoint():
    return get_orders()

@app.route('/reserve', methods=['POST'])
def reserve_seat():
    return reserve_seat()

@app.route('/reservations', methods=['GET'])
@require_auth
def reservations():
    return get_reservations()

@app.route('/check_availability', methods=['POST'])
def availability():
    return check_availability()

@app.route('/cancel_reservation/<int:reservation_id>', methods=['DELETE'])
def cancel(reservation_id):
    return cancel_reservation(reservation_id)


if __name__ == '__main__':
    port = int(os.getenv('PORT', '5002'))
    app.run(debug=True, port=port)
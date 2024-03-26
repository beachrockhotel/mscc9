from flask import Flask
from flask import request, render_template
from models import db
from prometheus_flask_exporter import PrometheusMetrics
from keycloak import KeycloakOpenID
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

token = ''

def token_get(password, user_name):
    global token
    token = keycloakid.token(grant_type=['password'], username = user_name, password = password)

@app.route('/login')
def login():
    login = request.args.get('login')
    password = request.args.get('password')
    token_get(password, login)
    return '''<h1>Logged in</h1>'''.format(login)

def check_user_roles():
    global token
    try:
        userinfo = keycloakid.userinfo(token["access_token"])
        token_info = keycloakid.introspect(token["access_token"])
        if "moder" not in token_info["realm_access"]["roles"]:
            print('no role')
        return token_info
    except Exception as e:
        return ('error')

@app.before_request
def create_tables():
    global is_db_initialized
    if not is_db_initialized:
        db.create_all()
        is_db_initialized = True

@app.route('/')
def home():
    if check_user_roles() != 'error':
        return render_template('index.html')
    else:
        return('please,login')

@app.route('/menu', methods=['POST'])
def add_menu_endpoint():
    return add_menu_item()

@app.route('/menu', methods=['GET'])
def get_menu_endpoint():
    if check_user_roles() != 'error':
        return get_menu()
    else:
        return('please,login')

@app.route('/order', methods=['POST'])
def order_endpoint():
    return make_order()

@app.route('/orders', methods=['GET'])
def orders_endpoint():
    if check_user_roles() != 'error':
        return get_orders()
    else:
        return('please,login')

@app.route('/reserve', methods=['POST'])
def reserve_seat():
    return reserve_seat()

@app.route('/reservations', methods=['GET'])
def reservations():
    if check_user_roles() != 'error':
        return get_reservations()
    else:
        return('please,login')

@app.route('/check_availability', methods=['POST'])
def availability():
    return check_availability()

@app.route('/cancel_reservation/<int:reservation_id>', methods=['DELETE'])
def cancel(reservation_id):
    return cancel_reservation(reservation_id)


if __name__ == '__main__':
    port = int(os.getenv('PORT', '5002'))
    app.run(debug=True, port=port)
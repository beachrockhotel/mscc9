from flask import Flask, request, jsonify
from models import db, MenuItem, Order

app = Flask(__name__)

def add_menu_item():
    data = request.json
    name = data.get('name')
    price = data.get('price')
    if not name or price is None:
        return jsonify({"error": "Имя или цена пропущены"}), 400
    new_item = MenuItem(name=name, price=price)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Позиция была создана", "id": new_item.id}), 201

def get_menu():
    menu_items = MenuItem.query.all()
    return jsonify(menu=[{'id': item.id, 'name': item.name, 'price': item.price} for item in menu_items])

def make_order():
    data = request.json
    item_ids = data['item_ids']

    total_price = 0
    order_items = []

    for item_id in item_ids:
        item = MenuItem.query.get(item_id)
        if item:
            total_price += item.price
            order_items.append(item.name)
        else:
            return jsonify(message="Заказ не найден", item_id=item_id), 404

    new_order = Order(items=str(order_items), total_price=total_price)
    db.session.add(new_order)
    db.session.commit()

    return jsonify(order_id=new_order.id, total_price=total_price, items=order_items)

def get_orders():
    orders = Order.query.all()
    return jsonify(orders=[
        {'id': order.id, 'items': order.items, 'total_price': order.total_price, 'order_time': order.order_time} for
        order in orders])
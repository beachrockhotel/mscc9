from flask import Flask, request, jsonify
from models import db, Reservation
from datetime import datetime

app = Flask(__name__)

def reserve_seat():
    data = request.json
    new_reservation = Reservation(
        user_name=data.get('user_name', 'Unknown'),
        seat_number=data['seat_number'],
        time=datetime.strptime(data['time'], '%Y-%m-%d %H:%M:%S')
    )
    db.session.add(new_reservation)
    db.session.commit()
    return jsonify(message="Место успешно забронировано", reservation_id=new_reservation.id)

def get_reservations():
    reservations = Reservation.query.all()
    reservations_list = [
        {
            'id': reservation.id,
            'user_name': reservation.user_name,
            'seat_number': reservation.seat_number,
            'time': reservation.time.strftime('%Y-%m-%d %H:%M:%S')
        } for reservation in reservations
    ]
    return jsonify(reservations=reservations_list)

def check_availability():
    data = request.json
    seat_number = data['seat_number']
    time = datetime.strptime(data['time'], '%Y-%m-%d %H:%M:%S')
    reservation = Reservation.query.filter_by(seat_number=seat_number, time=time).first()
    if reservation:
        return jsonify(available=False)
    return jsonify(available=True)

def cancel_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
        return jsonify(message="Бронь успешно отменена")
    return jsonify(message="Бронь не найдена"), 404
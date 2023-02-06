import json
import data
import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hm_16.db'

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    email = db.Column(db.String, unique=True)
    role = db.Column(db.String)
    phone = db.Column(db.String, unique=True)

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)
    price = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.drop_all()
    db.create_all()

    for user_data in data.users:
        db.session.add(User(**user_data))

    for order_data in data.orders:
        order_data['start_date'] = datetime.datetime.strptime(order_data['start_date'], '%m/%d/%Y').date()
        order_data['end_date'] = datetime.datetime.strptime(order_data['end_date'], '%m/%d/%Y').date()
        db.session.add(Order(**order_data))

    for offer_data in data.offers:
        db.session.add(Offer(**offer_data))
        db.session.commit()


@app.route('/users', methods=["GET", "POST"])
def page_all_users():
    if request.method == "GET":
        return jsonify([user.to_dict() for user in User.query.all()])
    elif request.method == "POST":
        new_user = json.loads(request.data)
        db.session.add(User(**new_user))
        db.session.commit()
        return 'User dobavlen', 201




@app.route('/users/<int:pk>', methods=["GET", "PUT", "DELETE"])
def user_page(pk):
    user = User.query.get(pk)
    if request.method == "GET":
        return jsonify(user.to_dict())
    elif request.method == "PUT":
        usr_data = json.loads(request.data)
        user.first_name = usr_data['first_name']
        user.last_name = usr_data['last_name']
        user.age = usr_data['age']
        user.email = usr_data['email']
        user.role = usr_data['role']
        user.phone = usr_data['phone']
        db.session.commit()
        return 'User izmenen'
    elif request.method == "DELETE":
        db.session.delete(user)
        db.session.commit()
        return 'User udalyon'


@app.route('/orders', methods=["GET"])
def page_all_orders():
    if request.method == "GET":
        res = []
        for order in Order.query.all():
            order.start_date = str(order.start_date)
            order.end_date = str(order.end_date)
            res.append(order.to_dict())
        return jsonify(res)
    elif request.method == "POST":
        new_order = json.loads(request.data)
        db.session.add(Order(**new_order))
        db.session.commit()
        return 'Order dobavlen', 201


@app.route('/orders/<int:pk>', methods=["GET", "PUT", "DELETE"])
def order_page(pk):
    order = Order.query.get(pk)
    if request.method == "GET":
        order.start_date = str(order.start_date)
        order.end_date = str(order.end_date)
        return jsonify(order.to_dict())
    elif request.method == "PUT":
        ordr_data = json.loads(request.data)
        ordr_data['start_date'] = datetime.datetime.strptime(ordr_data['start_date'], '%Y-%m-%d').date()
        ordr_data['end_date'] = datetime.datetime.strptime(ordr_data['end_date'], '%Y-%m-%d').date()
        order.name = ordr_data['name']
        order.description = ordr_data['description']
        order.start_date = ordr_data['start_date']
        order.end_date = ordr_data['end_date']
        order.address = ordr_data['address']
        order.price = ordr_data['price']
        order.customer_id = ordr_data['customer_id']
        order.executor_id = ordr_data['executor_id']
        db.session.commit()
        return 'Order izmenen'
    elif request.method == "DELETE":
        db.session.delete(order)
        db.session.commit()
        return 'Order udalyon'


@app.route('/offers', methods=["GET", "POST"])
def page_all_offers():
    if request.method == "GET":
        return jsonify([offer.to_dict() for offer in Offer.query.all()])
    elif request.method == "POST":
        new_offer = json.loads(request.data)
        db.session.add(User(**new_offer))
        db.session.commit()
        return 'Offer dobavlen', 201


@app.route('/offers/<int:pk>', methods=["GET", "PUT", "DELETE"])
def offer_page(pk):
    offer = Offer.query.get(pk)
    if request.method == "GET":
        return jsonify(offer.to_dict())
    elif request.method == "PUT":
        offr_data = json.loads(request.data)
        offer.order_id = offr_data['order_id']
        offer.executor_id = offr_data['executor_id']
        db.session.commit()
        return 'Offer izmenen'
    elif request.method == "DELETE":
        db.session.delete(offer)
        db.session.commit()
        return 'Offer udalyon'


if __name__ == '__main__':
    app.run(debug=True)

import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Updated to match your Streamlit reference image
class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), default=datetime.now().strftime("%Y/%m/%d"))
    client = db.Column(db.String(100))
    lpo_number = db.Column(db.String(50))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Float, default=0.0)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    deliveries = Delivery.query.order_by(Delivery.id.desc()).all()
    return render_template('index.html', deliveries=deliveries)

@app.route('/add', methods=['POST'])
def add():
    new_delivery = Delivery(
        client=request.form.get('client'),
        lpo_number=request.form.get('lpo'),
        product_name=request.form.get('product'),
        quantity=request.form.get('quantity')
    )
    db.session.add(new_delivery)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

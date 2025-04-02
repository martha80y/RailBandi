import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

local_server = True
app = Flask(__name__)

app.secret_key = 'ph@123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://matarishwa:9448990039aditya@localhost/train'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_number = db.Column(db.String(20), unique=True, nullable=False)
    train_name = db.Column(db.String(80), nullable=False)
    origin = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(80), nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    arrival_time = db.Column(db.String(20), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    train = db.relationship('Train', backref=db.backref('bookings', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Username: {username}, Password: {password}")  # Debugging
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id  # Store user ID in session
            print("Login successful, redirecting to index...")  # Debugging
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            print("Login failed. User not found or password incorrect.")  # Debugging
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST', 'GET'])
def search():
    from_station = request.form.get('from')
    to_station = request.form.get('to')
    date = request.form.get('date')
    available_trains = Train.query.filter_by(origin=from_station, destination=to_station).all()
    return render_template('trains.html', trains=available_trains)

@app.route('/trains', methods=['GET', 'POST'])
def trains():
    if request.method == 'POST':
        from_station = request.form['from']
        to_station = request.form['to']
        date = request.form['date']
        available_trains = Train.query.filter_by(origin=from_station, destination=to_station).all()
        return render_template('booking.html', trains=available_trains)
    else:
        flash('No available trains')
    return render_template('trains.html')



@app.route('/book', methods=['POST', 'GET'])
def book():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        email = request.form.get('email')
        train_id = request.form.get('train_id')

        print(f"Received booking: {name}, {age}, {gender}, {contact}, {email}, {train_id}")

        if not all([name, age, gender, contact, email, train_id]):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('book')) 

        new_booking = Booking(name=name, age=age, gender=gender, contact=contact, email=email, train_id=train_id)
        try:
            db.session.add(new_booking)
            db.session.commit()
            flash('Booking successful!', 'success')
            return redirect(url_for('confirmation', booking_id=new_booking.id))  # Redirect to confirmation page
        except Exception as e:
            db.session.rollback()
            print(f"Error adding booking: {e}")
            flash('An error occurred while processing your booking. Please try again.', 'danger')

    trains = Train.query.all()
    return render_template("booking.html", trains=trains)



@app.route('/confirmation/<int:booking_id>')
def confirmation(booking_id):
    # Retrieve booking details from the database
    booking = Booking.query.get(booking_id)
    
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('index'))
    
    # Retrieve train details
    train = Train.query.get(booking.train_id)
    if not train:
        flash('Train not found.', 'danger')
        return redirect(url_for('index'))
    
    # Use default values if no user is associated with the booking
    user_name = booking.user.username if booking.user else "Guest"
    booking_name = booking.name
    train_name = train.train_name
    return render_template('confirmation.html', user_name=user_name, booking_name=booking_name, booking_id=booking_id, train_name=train_name)





@app.route('/cancel', methods=['GET', 'POST'])
def cancel_booking():
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        
        if not booking_id:
            flash('Booking ID is required.', 'danger')
            return redirect(url_for('cancel_booking'))

        try:
            booking = Booking.query.get(booking_id)
            
            if not booking:
                flash('Booking not found.', 'danger')
                return redirect(url_for('cancel_booking'))

            db.session.delete(booking)
            db.session.commit()
            flash('Booking cancelled successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while cancelling the booking. Please try again.', 'danger')
            print(f"Error: {e}")

        return redirect(url_for('cancel_confirmation'))  # Redirect to index after cancellation

    # Render the cancel page with the form
    return render_template("cancel.html")



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/find_ticket', methods=['GET', 'POST'])
def find_ticket():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Please enter a name.', 'danger')
            return redirect(url_for('find_ticket'))

        bookings = Booking.query.filter_by(name=name).all()
        if not bookings:
            flash('No bookings found for the provided name.', 'danger')
            return redirect(url_for('find_ticket'))

        return render_template('view_ticket.html', bookings=bookings)

    return render_template('find_ticket.html')

@app.route('/track', methods=['GET', 'POST'])
def track():
    # Retrieve all train names from the database
    
    
    if request.method == 'POST':
        train_number = request.form['trainNumber']
        train_name = request.form['trainName']
        train = Train.query.filter_by(train_number=train_number, train_name=train_name).first()
        if train:
            return render_template('track.html', train=train)
        else:
            flash('Train not found.', 'danger')
        
    trains = Train.query.all()
    return render_template('track.html', trains=trains)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cancel_confirmation')
def cancel_confirmation():
    return render_template('cancel_confirmation.html')





# Main block
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)

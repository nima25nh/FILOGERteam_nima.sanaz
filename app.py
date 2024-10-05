from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from model import predict_class
import pickle
import json


app = Flask(__name__)

#app configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = ';aksdjf;kjkj;kj'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    predictions = db.relationship('Prediction', backref='user', lazy=True)
    
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    input_data = db.Column(db.Text, nullable=False)  # Store input features as JSON or string
    result = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Ensure tables are created
with app.app_context():
    db.create_all()

def login_required(f):
    def wrap(*args, **kwargs):
        if 'username' not in session:
            flash('You need to login first!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap


@app.route('/')
def home():
    return render_template('home.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pasword = bcrypt.generate_password_hash(password).decode('utf_8')

        new_user = User(username = username, password = hashed_pasword)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful, Please log in.', 'success')

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = user.username

            flash(' Login successful!', 'success')
            return redirect(url_for('input_data'))
        else:
            flash('Login failed, Check your username or password', 'danger')
        
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username')
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route('/input' , methods=['GET', 'POST'])
@login_required
def input_data():
    if request.method == 'POST':
        featurs = [
            float(request.form['mean radius']), 
            float(request.form['mean texture']), 
            float(request.form['mean perimeter']), 
            float(request.form['mean area']), 
            float(request.form['mean smoothness']), 
            float(request.form['mean compactness']),
            float(request.form['mean concavity']), 
            float(request.form['mean concave points']), 
            float(request.form['mean symmetry']), 
            float(request.form['mean fractal dimension']), 
            float(request.form['radius error']), 
            float(request.form['texture error']),
            float(request.form['perimeter error'] ),
            float(request.form['area error'] ),
            float(request.form['smoothness error'] ),
            float(request.form['compactness error'] ),
            float(request.form['concavity error'] ),
            float(request.form['concave points error'] ),
            float(request.form['symmetry error'] ),
            float(request.form['fractal dimension error'] ),
            float(request.form['worst radius'] ),
            float(request.form['worst texture'] ),
            float(request.form['worst perimeter'] ),
            float(request.form['worst area'] ),
            float(request.form['worst smoothness'] ),
            float(request.form['worst compactness'] ),
            float(request.form['worst concavity'] ),
            float(request.form['worst concave points'] ),
            float(request.form['worst symmetry'] ),
            float(request.form['worst fractal dimension'] )
        ]

        predicted_class = predict_class(featurs)
        
        # Get current user
        user = User.query.filter_by(username=session['username']).first()

        # Store prediction in database
        input_data = json.dumps(request.form.to_dict())
        result_text = "Benign" if predicted_class == 0 else "Malignant"
        new_prediction = Prediction(user_id=user.id, input_data=input_data, result=result_text)
        db.session.add(new_prediction)
        db.session.commit()

        return render_template('result.html', Diagnosis=result_text)
    return render_template('input.html')

@app.route('/history')
@login_required
def history():
    # Fetch the current user
    user = User.query.filter_by(username=session['username']).first()
    if user:
        predictions = user.predictions
        return render_template('history.html', predictions=predictions)
    return redirect(url_for('login'))

@app.route('/result')
@login_required
def result():
    #dispaly outputed result.
    return render_template('result.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

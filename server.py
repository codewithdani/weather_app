from flask import Flask, render_template, request, flash, redirect,url_for,session,logging
from main import get_current_weather
from waitress import serve
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
from jinja2 import Environment, BaseLoader
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "thisismysecratkey"

db = SQLAlchemy(app)

        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)


class CityVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    city = db.Column(db.String(100), nullable=False)
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)

'''
@app.route('/visit_history')
def visit_history():
    if is_authenticated():
        user_id = session.get('user_id')
        user_visits = CityVisit.query.filter_by(user_id=user_id).all()
        return render_template('visit_history.html', user_visits=user_visits)
    else:
        return redirect(url_for('signin'))  # Redirect to the signin page

# Your is_authenticated function can be updated like this'''
def is_authenticated():
    return 'user_id' in session

# Define a function to read visit history from the JSON file
def read_visit_history():
    with open('visit_history.json', 'r') as json_file:
        visit_history = json.load(json_file)
    return visit_history


def obfuscate_password(password):
    return '*' * len(password)

# Add the custom filter to the Jinja2 environment
app.jinja_env.filters['obfuscate_password'] = obfuscate_password


visited_cities = []

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/')
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == "POST":
        uname = request.form["username"]
        passw = request.form["password"]
        
        if User.query.filter_by(username=uname, password=passw).first():
            return redirect(url_for('index'))
    
    return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        uname = request.form['username']
        mail = request.form['email']
        passw = request.form['password']

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=mail).first()
        if existing_user:
            flash('Email address already in use. Please choose a different one.')
            return redirect(url_for('signup'))

        register = User(username=uname, email=mail, password=passw)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("signin"))

    return render_template('signup.html')


@app.route('/logout')
def logout():
  # return render_template('logout.html')
  return redirect(url_for("signin"))

@app.route('/weather')
def get_weather():
    city = request.args.get('city')

    weather_data = get_current_weather(city)

    # City is not found by API
    if not weather_data['cod'] == 200:
        return render_template('404.html')

    return render_template(
        "weather.html",
        title=weather_data["name"],
        status=weather_data["weather"][0]["description"].capitalize(),
        temp=f"{weather_data['main']['temp']:.1f}",
        feels_like=f"{weather_data['main']['feels_like']:.1f}"
    )


@app.route('/register_city', methods=['POST'])
def register_city():
    city = request.form['city']  # Get the city from the form data

    visited_cities.append(city)  # Add the city to the list

    return redirect(url_for('index'))


@app.route('/visited_cities')
def get_visited_cities():
    # Combine the visited cities into a single string, separated by commas
    cities = ", ".join(visited_cities)

    # Render the 'visited_cities.html' template with the cities data
    return render_template('visited_cities.html', cities=cities)

@app.route('/user_report')
def user_report():
    users = User.query.all()
    return render_template('user_report.html', users=users)


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
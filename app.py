from flask import Flask, request
from flask import Flask, request, render_template
import requests
import random
import json
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
api_key = os.environ.get("WEATHER_API_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_text = db.Column(db.String(250), nullable=False)

class WeatherLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(250), nullable=False)
    current_temp = db.Column(db.Float, nullable=False)
    condition_text = db.Column(db.String(250), nullable=False)

with app.app_context():
    db.create_all()

def get_activity_recommendation(temp, condition_text):
    condition = condition_text.lower()
    
    if "rain" in condition or "snow" in condition or "ice" in condition or "drizzle" in condition or "shower" in condition or "blizzard" in condition or "sleet" in condition:
        broad_condition = "Precipitation"
    elif "cloud" in condition or "overcast" in condition or "fog" in condition or "mist" in condition:
        broad_condition = "Cloudy"
    else:
        broad_condition = "Sunny"

    if temp < 41:
        if broad_condition == "Sunny":
            options = ["Bundle up for a brisk walk.", "Read a book by a sunny window.","Good strect and some home exercises","Catch up on a good film.","What about doing some puzzle?","Bake some cookies."]
        elif broad_condition == "Cloudy":
            options = ["Tackle an analytical logic puzzle.", "Catch up on a good film.","Great weather to read a Murder Mystery book.","What about doing some puzzle?","Bake some cookies."]
        else: 
            options = ["Catch up on a good film.", "Stay warm and start for a new knitting project.","What about doing some puzzle?","Bake some cookies."]
            
    elif 41 <= temp < 54:
        if broad_condition == "Sunny":
            options = ["A good day for a brisk outdoor walk.", "Plan a daytrip to somewhere close by.","Catch up on a good film.","What about doing some puzzle?","Bake some cookies."]
        elif broad_condition == "Cloudy":
            options = ["Work on a knitting project", "Any planning to for the rest of the week.","Cleaning day!","Catch up on a good film.","What about doing some puzzle?","Bake some cookies."]
        else:
            options = ["Brew a carefully calibrated espresso at home.", "Watch a long movie.", "Laundry day!","Catch up on a good film.","What about doing some puzzle?","Bake some cookies."]
            
    elif 54 <= temp < 62:
        if broad_condition == "Sunny":
            options = ["Ideal for a neighborhood walk.", "Browse an outdoor market.","Catch up on a good film.","What about doing some puzzle?","Ride a bicycle"]
        elif broad_condition == "Cloudy":
            options = ["Try some Home Pilates.", "Work on some arts&crafts.","Catch up on a good film.","What about doing some puzzle?","Bake some cookies.","What about a movie theatre?"]
        else:
            options = ["Spend some time with your pet", "Curl up with a good puzzle.","Catch up on a good film.","Bake some cookie.s","What about a movie theatre?"]
            
    elif 62 <= temp < 73:
        if broad_condition == "Sunny":
            options = ["Unbeatable weather for a long outdoor walk.", "A fantastic day to travel around.", "Don't forget your groceries","Meet with some friends"]
        elif broad_condition == "Cloudy":
            options = ["Grab a light jacket and explore a hiking trail.", "Read outside.","Catch up on a good film.","What about doing some puzzle?","Bake some cookie.","What about a movie theatre?"]
        else:
            options = ["Stay dry inside.", "Watch a documentary.","Catch up on a good film.","What about doing some puzzle?","Bake some cookies.","What about a movie theatre?"]
            
    elif 73 <= temp < 85:
        if broad_condition == "Sunny":
            options = ["Perfect for an exercise.", "A fantastic day to travel around.", "Call your friends to meet!","Definitely an Ice-Cream", "Visit a museum."]
        elif broad_condition == "Cloudy":
            options = ["Comfortable enough for a walk.", "Visit a museum.", "Call your friends to meet!"]
        else:
            options = ["A summer shower! Coffee at home.", "Read a new book.", "Organize your wardrobe.", "Watch a documentary.","Catch up on a good film.","What about doing some puzzle?","Bake some cookies."]
            
    elif 85 <= temp < 97:
        if broad_condition == "Sunny":
            options = ["Do an early morning walk before the heat sets.", "Watch a documentary.","Catch up on a good film.","What about doing some puzzle?","Bake some cookies.","Try making home ice-cream."]
        elif broad_condition == "Cloudy":
            options = ["Catch a matinee film in an air-conditioned theater.", "Watch a documentary.","Catch up on a good film.","What about doing some puzzle?","Bake some cookies."]
        else:
            options = ["Enjoy the cool down from the rain.", "Organize your wardrobe.", "Watch a documentary.","Catch up on a good film.","What about doing some puzzle?","Bake some cookies."]
            
    else: # 97 and above
        if broad_condition == "Sunny":
            options = ["Too hot for prolonged outdoor time. Stay in the AC.", "Watch a documentary.","Catch up on a good film.","What about doing some puzzle?","Bake some cookie."]
        elif broad_condition == "Cloudy":
            options = ["Still excessively warm. Keep cool indoors with a good book.", "Sort out your wardrobe", "Watch a documentary.","Catch up on a good film.","What about doing some puzzle?","Bake some cookies."]
        else:
            options = ["Stay indoors during the heavy summer storms.", "Great time to catch up on chores", "Play a video game.", "Watch a documentary.","Catch up on a good film.","What about doing some puzzle?","Bake some cookies."]

    return options

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/get_weather", methods=["POST"])
def get_weather():
    zipcode = request.form.get("zipcode")
    # Fetching data from an external source such as a REST API.
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={zipcode}&days=1"
    response = requests.get(url)
    data = response.json()

    if "error" in data:
        return f"<h3>Error: {data['error']['message']}</h3><a href='/'>Try again</a>"
    
    location_name = data["location"]["name"]
    current_temp = data["current"]["temp_f"]
    current_condition = data["current"]["condition"]["text"]
    #Storing the data in a database.
    new_log = WeatherLog(location_name=location_name, current_temp=current_temp, condition_text=current_condition)
    db.session.add(new_log)
    db.session.commit()
    print(f"SAVED WEATHER LOG: {location_name} - {current_temp}°F - {current_condition}")
    
    daily_data = data["forecast"]["forecastday"][0]["day"]
    max_temp = daily_data["maxtemp_f"]
    min_temp = daily_data["mintemp_f"]
    avg_temp = daily_data["avgtemp_f"]
    
    options_list = get_activity_recommendation(current_temp, current_condition)
    initial_activity = random.choice(options_list)

    return render_template(
        "weather.html", 
        location_name=location_name,
        current_temp=current_temp,
        current_condition=current_condition,
        max_temp=max_temp,
        min_temp=min_temp,
        avg_temp=avg_temp,
        initial_activity=initial_activity,
        options_list=json.dumps(options_list)
    )


@app.route("/save_favorite", methods=["POST"])
def save_favorite():
    data = request.json
    liked_activity = data.get("activity")
    new_favorite = Favorite(activity_text=liked_activity)
    #Storing the data in a database.
    db.session.add(new_favorite)
    db.session.commit()
    print(f"SAVED TO DATABASE: {liked_activity}")
    
    return {"status": "success"}

@app.route("/remove_favorite", methods=["POST"])
def remove_favorite():
    data = request.json
    activity_to_remove = data.get("activity")
    
    favorite = Favorite.query.filter_by(activity_text=activity_to_remove).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        print(f"REMOVED FROM DATABASE: {activity_to_remove}")
        
    return {"status": "success"}

@app.route("/get_count/<path:activity>")
def get_count(activity):
    count = Favorite.query.filter_by(activity_text=activity).count()
    return {"count": count}

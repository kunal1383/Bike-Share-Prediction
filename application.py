from flask import Flask, request, render_template
from src.logger import logging
from src.exception import CustomException 
from src.pipeline.training_pipline import TrainingPipeline
from src.pipeline.prediction_pipeline import PredictionPipeline
import os
import sys
import pandas as pd
from src.utils import fetch_weather_details ,get_days
import pycountry
from datetime import datetime


application = Flask(__name__)
app = application




@app.route('/')
def home_page():
    countries = [{"code": country.alpha_2, "name": country.name} for country in pycountry.countries]
    return render_template('index.html', countries=countries)



@app.route('/training', methods=['GET', 'POST'])
def training():
    try:
        training_pipeline = TrainingPipeline()
        training_pipeline.initiate_training()
        return render_template("Training Completed")
    except Exception as e:
        raise CustomException(e, sys)
    
    
@app.route('/fetch_data', methods=['GET', 'POST'])
def fetch_data():
    countries = [{"code": country.alpha_2, "name": country.name} for country in pycountry.countries]
    try:
        if request.method == 'POST':
            date = request.form.get('date')
            fetch_data = request.form.get('fetch_data')
            city = request.form.get('city')
            country_code = request.form.get('country')
            place = f"{city}, {country_code}"
            logging.info(f"Place:{place}") 
            
            if fetch_data:
                humidity, temperature, wind_speed = fetch_weather_details(place=place)
                
                return render_template('index.html', temperature=temperature, humidity=humidity, wind_speed=wind_speed ,city = city ,date = date ,country_code = country_code ,countries =countries)             

    except Exception as e:
        return render_template('error.html' ,error_message = e)



@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    try:
        if request.method == 'POST':
            date = request.form.get('hidden_date')
            selected_date = datetime.strptime(date, '%Y-%m-%d')
            month = selected_date.month
            year = selected_date.year
            day = selected_date.day
            country_code = request.form.get('hidden_country')
            season = int(request.form.get('Season'))
            weather = int(request.form.get('Weather'))
            temperature = round(float(request.form.get('Temperature')) /100 ,4    )
            humidity = round(float(request.form['Humidity'])/ 100, 4)
            wind_speed = round(float(request.form['Wind_speed']) /10, 4)
            holiday ,weekday ,working_day = get_days(year= year ,month = month ,day = day ,country_code= country_code)
            
            features = {
                "season": season,
                "yr": year,
                "mnth": month,
                "holiday": holiday,
                "weekday": weekday,
                "workingday": working_day,
                "weathersit": weather, 
                "temp": temperature,
                "hum": humidity,
                "windspeed": wind_speed     
            }
            
            df = pd.DataFrame([features])
            
            logging.info(df)
            
            predict_pipeline = PredictionPipeline()
            pred = predict_pipeline.predict(df)
            
            return render_template('result.html', final_result=pred)                      
                
    except Exception as e:
        return render_template('error.html' ,error_message = e)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
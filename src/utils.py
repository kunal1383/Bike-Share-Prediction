from src.exception import CustomException
from src.logger import logging
from sklearn.metrics import mean_squared_error ,r2_score , mean_absolute_error , mean_squared_error
import numpy as np
import os
import sys
import pickle
import pyowm
from datetime import datetime ,date

import holidays



#openWeather api key
WEATHER_API_KEY = ""

def save_object(file_path,obj):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
    
    except Exception as e:

        raise CustomException(e, sys)
    
def load_object(file_path):
    try:
        with open(file_path,'rb') as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        logging.info('Exception Occured in load_object function utils')
        raise CustomException(e,sys)    

def evaluate_model(true, predicted):
    mae = mean_absolute_error(true, predicted)
    mse = mean_squared_error(true, predicted)
    rmse = np.sqrt(mean_squared_error(true, predicted))
    r2_square = r2_score(true, predicted)
    return mae, rmse, r2_square

def objective(trial, model_instance, model_name , X_train, y_train, X_test, y_test):
    try:
        params = {}

        if model_name == 'RandomForest':
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 200),
                'max_depth': trial.suggest_int('max_depth', 5, 15),
                'min_samples_split': trial.suggest_float('min_samples_split', 0.1, 1.0),
                'min_samples_leaf': trial.suggest_float('min_samples_leaf', 0.1, 0.5),
                'max_features': trial.suggest_categorical('max_features', ['log2', 'sqrt']),
            }
            model = model_instance.set_params(**params, random_state=42)
            
        elif model_name == 'XGBoost':    
            params = {
                'objective': 'reg:squarederror',
                'booster': 'gbtree',
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.1),
                'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            }
            model = model_instance.set_params(**params, random_state=42)
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        r2= r2_score(y_test, y_pred)
        return r2
        
    except Exception as e:
        logging.info('Exception occurred in objective function')
        raise CustomException(e, sys)
    

def get_days(year ,month ,day ,country_code):
    
    try:
        given_date = date(year, month, day)
        holiday = 0
        working_day = 1
        # Get the weekday value of the given date (0 for Sunday, 6 for Saturday)
        weekday_value = given_date.weekday()

        # Convert weekday value to match your feature encoding (0 for Sunday, 6 for Saturday)
        adjusted_weekday = (weekday_value + 1) % 7

        # Create the CountryHoliday object for the specified country
        country_holidays = holidays.CountryHoliday(country_code)

        # Check if the given date is a holiday
        if given_date in country_holidays:
            holiday = 1 
        if adjusted_weekday == 0 or adjusted_weekday == 1 or holiday  == 1:
            working_day =   0 
        
        return holiday , adjusted_weekday,working_day     
    except Exception as e:
        logging.info('Exception occurred in Getting days function')
        raise CustomException(e, sys)    
    
        
def fetch_weather_details(place):
    try:
        owm = pyowm.OWM(WEATHER_API_KEY) 
        weather_mgr = owm.weather_manager()
    
        observation = weather_mgr.weather_at_place(place)
        temperature = observation.weather.temperature("celsius")["temp"]
        humidity = observation.weather.humidity
        wind = observation.weather.wind()
        print(f'Temperature: {temperature}°C')
        print(f'Humidity: {humidity}%')
        print(f'Wind Speed: {wind["speed"]} m/s')
        return humidity ,temperature ,wind["speed"]
    except Exception as e:
        logging.info('Exception occurred in fetch_weather_details function')
        raise CustomException(e, sys)    
    
    # geo_mgr = owm.geocoding_manager()
    # location = geo_mgr.geocode(place)
    # name = location[0].name
    # latitude = location[0].lat
    # longitude = location[0].lon
    # print(f"Location: {name} ({latitude}, {longitude})")
    # # Convert the provided date string to a datetime object
    # provided_date = datetime.strptime(date_str, "%d-%m-%Y")

    # # Calculate the timestamp for the provided date
    # timestamp = int(provided_date.timestamp())

    # # Fetch historical weather data for the provided date
    # historical_weather = weather_mgr.one_call_history(lat=latitude, lon=longitude, dt=timestamp)
    # temperature = historical_weather.current.temperature("celsius")["temp"]
    # humidity = historical_weather.current.humidity
    # wind_speed = historical_weather.current.wind()["speed"]

    # print(f'Temperature on {provided_date.date()}: {temperature}°C')
    # print(f'Humidity on {provided_date.date()}: {humidity}%')
    # print(f'Wind Speed on {provided_date.date()}: {wind_speed} m/s')



if __name__ == "__main__":
    # holiday ,weekday  ,working_day = get_days(2023 ,8,30 ,"IN")
    # print(f"Holiday :{holiday} ,weekday: {weekday} ,workingday :{working_day} ")
    fetch_weather_details("Nasik ,IN")

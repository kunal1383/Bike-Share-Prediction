import sys
import os
from src.exception import CustomException
from src.logger import logging
from src.utils import load_object
import pandas as pd
import numpy as np
from src.components.connect_database import DatabaseHandler
from src.pipeline.training_pipline import TrainingPipeline
from sklearn.preprocessing import StandardScaler 



class PredictionPipeline:
    def __init__(self):
        self.training_pipeline = TrainingPipeline()
        
    def load_models_from_artifacts(self):
        preprocessor_path = os.path.join('artifacts', 'preprocessor.pkl')
        model_path = os.path.join('artifacts', 'model.pkl')

        preprocessor = None
        model = None  
        
        try:
            logging.info("Ckecking if models present in artifacts")
            model = load_object(model_path)
            preprocessor = load_object(preprocessor_path)
            logging.info("Model loaded successfully")
            return model ,preprocessor
        except FileNotFoundError:
            logging.info("model not  present in artifacts starting the training of model")
            self.training_pipeline.initiate_training()

        return self.load_models_from_artifacts()
    
    def predict(self, features):
        logging.info('Starting the prediction pipeline')
        try:
            model ,preprocessor = self.load_models_from_artifacts()
            data_scaled = preprocessor.transform(features)
            prediction = model.predict(data_scaled)
            logging.info('Finished the prediction')
            return int(prediction)
        except Exception as e:
            logging.info("Exception occurred in prediction") 
            return None  
        
        

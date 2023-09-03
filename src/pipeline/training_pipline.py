from src.logger import logging
from src.exception import CustomException
from src.components.data_ingestion import DataIngestion
from src.components.data_transformer import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.components.connect_database import DatabaseHandler
import sys
import os

class TrainingPipeline:
    def __init__(self):
        self.train_arr = None
        self.test_arr = None

    def initiate_training(self):
        logging.info("Starting Training Pipeline")
        data_ingestion = DataIngestion()
        train_data_path, test_data_path, run_id = data_ingestion.initiate_data_ingestion()

        try:
            logging.info("Trying data transformation")
            data_transformation = DataTransformation()
            self.train_arr, self.test_arr = data_transformation.initiate_data_transformation(train_data_path, test_data_path)
            
            if self.train_arr is None or self.test_arr is None:
                logging.info("Failed to fetch the data from data transformation, trying database")
                db_handler = DatabaseHandler()
                train_columns, self.train_arr = db_handler.retrieve_data_as_numpy(table_name='train_df')
                test_columns, self.test_arr = db_handler.retrieve_data_as_numpy(table_name='test_df')

            if self.train_arr is not None and self.test_arr is not None:
                model_trainer = ModelTrainer(run_id=run_id)
                model_trainer.initiate_model_training(self.train_arr, self.test_arr)
                logging.info("Training Pipeline completed successfully")
            else:
                logging.info("Failed to fetch data for training.")

        except Exception as e:
            logging.info("An error occurred during the training pipeline.")
            raise CustomException(e, sys)
            


if  __name__ == "__main__":
    training = TrainingPipeline()
    training.initiate_training()
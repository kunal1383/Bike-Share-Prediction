import os
import sys
import pandas as pd
import mlflow
from sklearn.model_selection import train_test_split
from mlflow.tracking import MlflowClient
from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass

# Initialize MLflow client
mlflow.set_tracking_uri("mlruns")
client = MlflowClient()


@dataclass
class DataIngestionconfig:
    train_data_path:str=os.path.join('artifacts','train.csv')
    test_data_path:str=os.path.join('artifacts','test.csv')
    raw_data_path:str=os.path.join('artifacts','raw.csv')
    
class DataIngestion:
    def __init__(self):
        self.ingestion_config=DataIngestionconfig()

    def initiate_data_ingestion(self):
        logging.info('Data Ingestion methods Started')
        try:
            # Read the dataset
            df = pd.read_csv(os.path.join('dataset', 'day.csv'))
            logging.info('Dataset read as pandas Dataframe')

            # Log raw data as artifact
            with mlflow.start_run() as run:
                os.makedirs(os.path.dirname(self.ingestion_config.raw_data_path),exist_ok=True)
                df.to_csv(self.ingestion_config.raw_data_path,index=False)              
                mlflow.log_artifact(self.ingestion_config.raw_data_path)

                logging.info('Train test split') 
                # Split data and log artifacts
                train_set, test_set = train_test_split(df, test_size=0.30, random_state=42)
                
                train_set.to_csv(self.ingestion_config.train_data_path, index=False, header=True)
                mlflow.log_artifact(self.ingestion_config.train_data_path)

                test_set.to_csv(self.ingestion_config.test_data_path, index=False, header=True)
                mlflow.log_artifact(self.ingestion_config.test_data_path)
                
                run_id = run.info.run_id
            
            # Get artifact URIs for all data artifacts
            raw_data_artifact_uri = f"{client.get_run(run.info.run_id).info.artifact_uri}/{self.ingestion_config.raw_data_path}"
            logging.info(f"Raw Data Artifact URI:{raw_data_artifact_uri}" )
            train_data_artifact_uri = f"{client.get_run(run.info.run_id).info.artifact_uri}/{self.ingestion_config.train_data_path}"
            logging.info(f"Train Data Artifact URI:{ train_data_artifact_uri}")
            test_data_artifact_uri = f"{client.get_run(run.info.run_id).info.artifact_uri}/{self.ingestion_config.test_data_path}"
            logging.info(f"Test Data Artifact URI:{test_data_artifact_uri}" )
            
            logging.info('Ingestion of Data is completed')
                
            return(
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path,
                run_id
            )

        except Exception as e:
            raise CustomException(e, sys)




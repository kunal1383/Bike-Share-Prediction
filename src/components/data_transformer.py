import os
import sys
import pandas as pd 
import numpy as np

from src.logger import logging
from src.exception import CustomException
#from src.mongodb import MongoDBHandler
from src.utils import save_object

from sklearn.preprocessing import StandardScaler 
from src.components.connect_database import DatabaseHandler
from dataclasses import dataclass
@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path=os.path.join('artifacts','preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()
    
    def initiate_data_transformation(self,train_path,test_path):
        try:
            
            logging.info('Data Transformation initiated')
            # Reading train and test data
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            
            logging.info('Read train and test data completed')
            
            logging.info("Separating the target and the features")
            
            # separating the features and target
            target_column_name = 'cnt'
            drop_columns=[target_column_name,'instant', 'dteday','atemp','casual' ,'registered']
            
            
            input_feature_train_df = train_df.drop(columns=drop_columns,axis=1)
            target_feature_train_df=train_df[target_column_name]


            input_feature_test_df = test_df.drop(columns=drop_columns,axis=1)
            target_feature_test_df=test_df[target_column_name]
            
            logging.info(f"input_feature_columns : {input_feature_train_df.columns}")
            
            logging.info(" Completed separating of target and the features")
            
            logging.info("Normalizing the features")
            
            # Normalizing the features
            scaler = StandardScaler()
            
            input_feature_train_scaled = scaler.fit_transform(input_feature_train_df)
            
            input_feature_test_scaled = scaler.transform(input_feature_test_df)
            
            
            train_arr = np.c_[input_feature_train_scaled, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_scaled, np.array(target_feature_test_df)]
            
            train_df = pd.DataFrame(train_arr, columns=[
                        'season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday',
                        'weathersit', 'temp', 'hum', 'windspeed', 'target'])
            test_df = pd.DataFrame(test_arr, columns=[
                        'season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday',
                        'weathersit', 'temp', 'hum', 'windspeed', 'target'
                    ])
            
            db_handler = DatabaseHandler()
            try:
                if db_handler.check_keyspace():
                    if not db_handler.check_table(table_name='train_df'):
                        db_handler.create_table(table_name='train_df')
                    else:
                        
                        db_handler.drop_table(table_name='train_df')
                        db_handler.create_table(table_name='train_df')

                    if not db_handler.check_table(table_name='test_df'):
                        db_handler.create_table(table_name='test_df')
                    else:
                        
                        db_handler.drop_table(table_name='test_df')
                        db_handler.create_table(table_name='test_df')

                    db_handler.insert_dataframe_data(train_df, table_name='train_df')
                    db_handler.insert_dataframe_data(test_df, table_name='test_df')
                    save_object(

                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=scaler

            )

            except Exception as e:
                logging.info("Exception occur in the data transformation ")
                raise CustomException(e,sys)        
                
            
            logging.info(f"the train _arr is: {train_arr[5]}")
            logging.info(f"the test _arr is {test_arr[5]}")
            
            return(
                train_arr,
                test_arr
            )
            
        except Exception as e:
            logging.info("Exception occur in the data transformation ")

            raise CustomException(e,sys)    
            
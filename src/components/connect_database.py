from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import json
import os
import uuid
import sys
import numpy as np
import pandas as pd 
from src.logger import logging
from src.exception import CustomException

from dataclasses import dataclass

@dataclass
class databaseConfig:
    connect_cassandra_path:str = os.path.join('cassandra','secure-connect-cassandra.zip')
    cassandra_token_path:str =  os.path.join('cassandra' ,'kunalb1383@gmail.com-token.json')


class DatabaseHandler:
    def __init__(self):
        self.db_config = databaseConfig()
        self.session = self.connect()
    
    def connect(self):
        logging.info("Connecting to database")
        try:
            cloud_config = {
                'secure_connect_bundle': self.db_config.connect_cassandra_path
            }
                    
            with open(self.db_config.cassandra_token_path) as f:
                secrets = json.load(f)

                CLIENT_ID = secrets["clientId"]
                CLIENT_SECRET = secrets["secret"]

                auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
                cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
                session = cluster.connect()

                row = session.execute("select release_version from system.local").one()
                if row:
                    logging.info(f"{row[0]} connection successful with cassandra")
                else:
                    logging.info("An error occurred.")
                    
                logging.info("connection successful with database")
                return session
        except Exception as e:
            logging.info("An error occurred while connecting with database.")
            raise CustomException(e, sys)
            
        
    def disconnect(self): 
        logging.info("Shutting the database down")
        try:
            if self.session:
                self.session.shutdown()
        except Exception as e:
            logging.info("An error occurred while shutting database.")
            raise CustomException(e, sys)
                
            
    def create_table(self, table_name):
        logging.info("Creating the table in database")
        try:
            create_table_query = (
                f"CREATE TABLE IF NOT EXISTS bike_prediction_keyspace.{table_name} ("
                "id UUID PRIMARY KEY,"
                "season DOUBLE,"
                "yr DOUBLE,"
                "mnth DOUBLE,"
                "holiday DOUBLE,"
                "weekday DOUBLE,"
                "workingday DOUBLE,"
                "weathersit DOUBLE,"
                "temp DOUBLE,"
                "hum DOUBLE,"
                "windspeed DOUBLE,"
                "target DOUBLE);"
            )
            self.session.execute(create_table_query)
        except Exception as e:
            logging.info("An error occurred while creating the table.")
            raise CustomException(e, sys)
        
    def check_keyspace(self):
        keyspace_name = 'bike_prediction_keyspace'
        query = f"SELECT keyspace_name FROM system_schema.keyspaces WHERE keyspace_name = '{keyspace_name}';"
        try:
            result = self.session.execute(query).one()
            if result:
                logging.info(f"Keyspace '{keyspace_name}' exists.")
                return True
            else:
                logging.info(f"Keyspace '{keyspace_name}' does not exist.")
                return False
        except Exception as e:
            logging.info("An error occurred while checking keyspace.")
            raise CustomException(e, sys)

    def check_table(self, table_name):
        keyspace_name = 'bike_prediction_keyspace'
        query = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{keyspace_name}' AND table_name = '{table_name}';"
        try:
            result = self.session.execute(query).one()
            if result:
                logging.info(f"Table '{keyspace_name}.{table_name}' exists.")
                return True
            else:
                logging.info(f"Table '{keyspace_name}.{table_name}' does not exist.")
                return False
        except Exception as e:
            logging.info("An error occurred while checking table.")
            raise CustomException(e, sys)
            
    def insert_data(self, data ,table_name):
        try:
            insert_query = (
                f"INSERT INTO bike_prediction_keyspace.{table_name} "
                "(id, season, yr, mnth, holiday, weekday, workingday, weathersit, temp, hum, windspeed, target) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
            )     
            prepared_query = self.session.prepare(insert_query)
            
            bound_statement = prepared_query.bind((
                data['id'],
                data['season'],
                data['yr'],
                data['mnth'],
                data['holiday'],
                data['weekday'],
                data['workingday'],
                data['weathersit'],
                data['temp'],
                data['hum'],
                data['windspeed'],
                data['target']
            ))
            
            self.session.execute(bound_statement)
        except Exception as e:
            logging.info("An error occurred while inserting data in table.")
            raise CustomException(e, sys)
            
    def drop_table(self ,table_name):
        logging.info(f"Deleting {table_name} table.")
        try:
            keyspace_name = 'bike_prediction_keyspace'
            delete_query = f"DROP TABLE IF EXISTS {keyspace_name}.{table_name}"
            self.session.execute(delete_query)
        except Exception as e:
            logging.info("An error occurred while deleting the table.")
            raise CustomException(e, sys)
            
                    
    def get_data_by_id(self, id):
        select_query = (
            "SELECT * FROM bike_prediction_keyspace.scaled_data "
            "WHERE id = ?;"
        )
        
        prepared_query = self.session.prepare(select_query)
        bound_statement = prepared_query.bind((id,))
        
        result = self.session.execute(bound_statement)
        
        if result:
            row = result.one()
            return row
        else:
            return None    
        
        
    def insert_dataframe_data(self, df ,table_name):
        
        try:
            for index, row in df.iterrows():
                data = {
                    'id': uuid.uuid4(),
                    'season': row['season'],
                    'yr':row['yr'],
                    'mnth': row['mnth'],
                    'holiday': row['holiday'],
                    'weekday': row['weekday'],
                    'workingday': row['workingday'],
                    'weathersit': row['weathersit'],
                    'temp': row['temp'],
                    'hum': row['hum'],
                    'windspeed': row['windspeed'],
                    'target': row['target']
                }
                
                self.insert_data(data ,table_name=table_name)
            logging.info("Data from dataframe has been inserted.")
        except Exception as e:
            logging.info("An error while inserting the dataframe into database.")
            raise CustomException(e, sys)
        
    def retrieve_data_as_numpy(self, table_name):
        logging.info("Retrieving the data from database")
        try:
            query = f"SELECT * FROM bike_prediction_keyspace.{table_name}"
            result = self.session.execute(query)
            print(type(result))
            new_columns_order = ['season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday',
                                'weathersit', 'temp', 'hum', 'windspeed',]
            # Convert the Cassandra result to a pandas DataFrame
            data_df = pd.DataFrame(list(result))
            
            # Drop the 'id' column as it's not needed for conversion
            logging.info("Dropping the id and target column from cassandra db")
            data_df.drop(columns=['id','target'], inplace=True)
            data_df = data_df[new_columns_order]
            print(type(data_df))
            
            if data_df.empty:
                logging.info(f"No data found in the table '{table_name}'.")
                return None
            
            # Extract column names
            columns = data_df.columns
            
            # Exclude 'id' column
            data_array = data_df.to_numpy()
            logging.info("Data retrieved successfully from database")
            return columns, data_array
        except Exception as e:
                logging.info("An error occurred while retrieving the data from database.")
                return None ,None
        
    def check_data_in_table(self, table_name):
        query = f"SELECT COUNT(*) FROM bike_prediction_keyspace.{table_name};"
        try:
            result = self.session.execute(query).one()
            row_count = result[0]
            if row_count > 0:
                logging.info(f"Table '{table_name}' contains {row_count} rows.")
                return True
            else:
                logging.info(f"Table '{table_name}' is empty.")
                return False
            
        except Exception as e:
            logging.info("An error occurred while checking data in table.")
            raise CustomException(e, sys)
        
    
if __name__ == "__main__":
    db_handler = DatabaseHandler()
    
    # db_handler.check_keyspace()
    # db_handler.create_tables()
    # db_handler.check_tables()

    # # Sample data for insertion
    # sample_data = {
    #     'id': uuid.uuid4(),
    #     'season': 1.35326200e+00,
    #     'mnth': 1.01732430e+00,
    #     'holiday': -1.67836272e-01,
    #     'weekday': 3.04025689e-02,
    #     'workingday': 7.34272856e-01,
    #     'weathersit': 1.09523459e+00,
    #     'atemp': 7.36157516e-01,
    #     'hum': 1.13743092e+00,
    #     'windspeed': -1.62387536e+00,
    #     'casual': -2.20337176e-01,
    #     'registered': 2.07395271e+00,
    #     'target': 7.57200000e+03
    # }

    # #db_handler.insert_data(sample_data)
    # inserted_data = db_handler.get_data_by_id(sample_data['id'])
    # if inserted_data:
    #     print("Inserted data:")
    #     print(inserted_data)
    # else:
    #     print("Data not found.")

    # db_handler.disconnect()
    
    db_handler = DatabaseHandler()
    print(db_handler.check_table(table_name='train_df'))
    db_handler.drop_table(table_name='train_df')
    db_handler.drop_table(table_name='test_df')
    

    # Assuming you have already inserted data into 'train_df' and 'test_df' tables
    # train_columns, train_data = db_handler.retrieve_data_as_numpy(table_name='train_df')
    # test_columns, test_data = db_handler.retrieve_data_as_numpy(table_name='test_df')

    # if train_data is not None:
    #     print("Train DataFrame:")
    #     print(type(train_data))
    #     print(train_data)
    #     train_df = pd.DataFrame(train_data, columns=train_columns)
    #     print("Train DataFrame:")
    #     print(train_df.head())

    # if test_data is not None:
    #     test_df = pd.DataFrame(test_data, columns=test_columns)
    #     print("Test DataFrame:")
    #     print(type(test_data))
    #     print(test_data)
    #     print("Test DataFrame:")
    #     print(test_df.head())
    
    # if db_handler.check_keyspace():
    #     if db_handler.check_table(table_name='train_df'):
    #         if db_handler.check_data_in_table(table_name='train_df'):
    #             logging.info("Data is present in the 'train_df' table.")
    #         else:
    #             logging.info("No data found in the 'train_df' table.")
        
    #     if db_handler.check_table(table_name='test_df'):
    #         if db_handler.check_data_in_table(table_name='test_df'):
    #             logging.info("Data is present in the 'test_df' table.")
    #         else:
    #             logging.info("No data found in the 'test_df' table.")


    db_handler.disconnect()
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import optuna
import sys
import os
import mlflow

from src.utils import evaluate_model ,objective ,save_object
from src.exception import CustomException
from src.logger import logging
from dataclasses import dataclass
#from src.mongodb import MongoDBHandler

@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts', 'model.pkl')

class ModelTrainer:
    def __init__(self ,run_id):
        self.model_trainer_config = ModelTrainerConfig()
        self.run_id = run_id

    def initiate_model_training(self, train_array, test_array):
        report = {}
        try:
            logging.info('Splitting dependent and independent variables from train and test data')
            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1]
            )

            # Define models dictionary
            models = {
                'RandomForest': RandomForestRegressor(),
                'XGBoost': xgb.XGBRegressor()
            }
            logging.info("looping through models")
            # Loop through models for optimization and evaluation
            for model_name, model_instance in models.items():
                # Create an Optuna study
                study = optuna.create_study(direction='maximize')  
                
                # Optimize the model
                study.optimize(lambda trial: objective(trial, model_instance, model_name , X_train, y_train, X_test, y_test), n_trials=100)
                
                # Get the best set of hyperparameters
                best_params = study.best_params
                
                # Train the final model with the best parameters
                final_model = model_instance.set_params(**best_params)
                final_model.fit(X_train, y_train)
                
                # Evaluate the final model on the test set
                y_pred_test = final_model.predict(X_test)
                mae, rmse, r2 = evaluate_model(y_test, y_pred_test)
                
                # Store the evaluation metrics and best parameters in the report
                report[model_name] = {
                    "model" : final_model,
                    "best_parameters": best_params,
                    "mae": mae,
                    "rmse": rmse,
                    "r2": r2
                }
                
                # Print evaluation results
                logging.info(f"{model_name} Model Evaluation:")
                logging.info(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}, R^2: {r2:.2f}")
                
            logging.info("Getting best model ")    
            # Find the model with the best R^2 score
            logging.info(f"Current Report: {report}")
            best_model_name = max(report, key=lambda model: report[model]['r2'])
            logging.info(f"Best Model:{best_model_name}")
            logging.info(f"Best Model's Evaluation Metrics{report[best_model_name]}:")
            best_model = report[best_model_name]['model']
            logging.info(f"Actual model : {best_model}")
            
            with mlflow.start_run(run_id=self.run_id):
                # Log the evaluation metrics and best parameters of the best model
                best_model_metrics = report[best_model_name]
                mlflow.log_metric("Best Model MAE", best_model_metrics['mae'])
                mlflow.log_metric("Best Model RMSE", best_model_metrics['rmse'])
                mlflow.log_metric("Best Model R2", best_model_metrics['r2'])
                
                best_model_params = best_model_metrics['best_parameters']
                for param_name, param_value in best_model_params.items():
                    mlflow.log_param(f"Best Model {param_name}", param_value)
                
                save_object(
                    
                    file_path=self.model_trainer_config.trained_model_file_path,
                    obj=best_model

                )
                
                best_model_path=self.model_trainer_config.trained_model_file_path
                
                mlflow.log_artifact(best_model_path)
            
        except Exception as e:
            logging.info('Exception occurred during model training')
            raise CustomException(e, sys)
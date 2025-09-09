import wandb
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error
import numpy as np
import pandas as pd
import os
import json
import csv
from dotenv import load_dotenv
load_dotenv()

# Set up your WandB API key
WANDB_API_KEY = os.getenv("WANDB_API_KEY")

class WanDB:
    def __init__(self, project_name="Dream11") -> None:
        wandb.login()
        self.project_name = project_name

        self.sweep_config = {
            "method": "random",
            "metric": {
                "name": "mae",
                "goal": "minimize"
            },
            "parameters": {
                "n_estimators": {"values": [50, 100, 200, 300]},
                "max_depth": {"values": [3, 6, 9, 12]},
                "learning_rate": {"distribution": "uniform", "min": 0.01, "max": 0.3},
                "subsample": {"distribution": "uniform", "min": 0.3, "max": 1.0},
                "reg_lambda": {"distribution": "log_uniform", "min": -3, "max": 1},
                "reg_alpha": {"distribution": "log_uniform", "min": -3, "max": 1},
            }
        }

        # Create sweep
        self.sweep_id = wandb.sweep(self.sweep_config, project=self.project_name)

    def preprocess_data(self, match_df):
        match_df = match_df.fillna(0)
        cols_drop = [
            'match_id', 'date_playing', 'League', 'team1', 'team2', 'stadium', 
            'team1.player_id', 'team2.player_id', 'Unnamed: 0', 'dream_points'
        ]
        X = match_df
        print(1)
        for col in cols_drop:
            if(col in X.columns):
                print(col)
                X = X.drop(columns= col)
        print(2)
        y = match_df['dream_points']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test

    def train(self, config=None):
        # Initialize WandB
        with wandb.init(config=config, project=self.project_name):
            config = wandb.config
            # print(config)
            current_config = {
            "learning_rate": config.learning_rate,
            "max_depth": config.max_depth,
            "n_estimators": config.n_estimators,
            "reg_alpha": config.reg_alpha,
            "reg_lambda": config.reg_lambda,
            "subsample": config.subsample
            }   

            # Train the model
            model = GradientBoostingRegressor(
                n_estimators=config.n_estimators, 
                max_depth=config.max_depth,
                learning_rate=config.learning_rate, 
                subsample=config.subsample
            )
            model.fit(self.X_train, self.y_train)
            # Predictions
            train_predictions = model.predict(self.X_train)
            test_predictions = model.predict(self.X_test)

            # Calculate metrics
            train_mae = mean_absolute_error(self.y_train, train_predictions)
            val_mae = mean_absolute_error(self.y_test, test_predictions)

            train_rmse = np.sqrt(mean_squared_error(self.y_train, train_predictions))
            val_rmse = np.sqrt(mean_squared_error(self.y_test, test_predictions))

            train_mape = mean_absolute_percentage_error(self.y_train, train_predictions)
            val_mape = mean_absolute_percentage_error(self.y_test, test_predictions)

            # Log metrics to WandB
            wandb.log({
                "train_mae": train_mae,
                "val_mae": val_mae,
                "train_rmse": train_rmse,
                "val_rmse": val_rmse,
                "train_mape": train_mape,
                "val_mape": val_mape
            })

            row_data={**current_config, 
                    "train_mae": train_mae, 
                    "val_mae": val_mae, 
                    "train_rmse": train_rmse, 
                    "val_rmse": val_rmse, 
                    "train_mape": train_mape, 
                    "val_mape": val_mape
            }
            file_exists = os.path.isfile("training_results.csv")
            with open(f"training_results.csv", mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=row_data.keys())
                if not file_exists:
                    writer.writeheader()  
                writer.writerow(row_data)

    def start_sweep(self, X_train, X_test, y_train, y_test, sweep_count=1):
        # Set train/test data as instance variables for use in `train`
        self.X_train, self.X_test = X_train, X_test
        self.y_train, self.y_test = y_train, y_test

        # Start the sweep
        wandb.agent(self.sweep_id, function=self.train, count=sweep_count)
        
        
    def fetch_results(self):
        print(self.sweep_id)
        api = wandb.Api()
        # sweep = api.sweep(f"{wandb.Api().default_entity}/{'lol'}/{'dxfw9suh'}")
        sweep = api.sweep(f"{wandb.Api().default_entity}/{self.project_name}/{self.sweep_id}")
        sweep_results = []
        print('initializing the data array')
        data = []
        mae = []
        print('entering loop')
        for i, run in enumerate(sweep.runs):
            if len(data) <= i:
                data.append([None] * 6)
            if len(mae) <= i:
                mae.append([None])
            mae[i] = run.summary.get("mae" , 0)
            # if(hasattr(run.summary , "mae")):
            #     mae[i] = run.summary.mae
            # else:
            #     mae[i] = 0
            print(1)
            data[i][0]=run.summary.get("train_mae")
            data[i][1]=run.summary.get("val_mae")
            data[i][2]=run.summary.get("train_rmse")
            data[i][3]=run.summary.get("val_rmse")
            data[i][4]=run.summary.get("train_mape")
            data[i][5]=run.summary.get("val_mape")
            run_data = {
                "url": run.url,
                "train_mae": run.summary.get("train_mae"),
                "val_mae": run.summary.get("val_mae"),
                "train_rmse": run.summary.get("train_rmse"),
                "val_rmse": run.summary.get("val_rmse"),
                "train_mape": run.summary.get("train_mape"),
                "val_mape": run.summary.get("val_mape"),
            }
            sweep_results.append(run_data)

        file_name = "training_results.csv" 
        df = pd.read_csv(file_name)
        df["mae"] = mae
        df.to_csv(file_name, index=False)
        print(mae)
        return data
        # return sweep.display(height=1080)

# Main execution
# wandb_project = WanDB()
# df = pd.read_csv("match.csv")
# X_train, X_test, y_train, y_test = wandb_project.preprocess_data(df)
# wandb_project.start_sweep(X_train, X_test, y_train, y_test)
# wandb_project.fetch_results()

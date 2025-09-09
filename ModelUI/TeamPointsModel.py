from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error , r2_score
import pandas as pd
import json
import numpy as np
import zipfile
import os
import re
from collections import deque, defaultdict
import datetime
from datetime import datetime
import pickle
import warnings
warnings.filterwarnings("ignore")
from sklearn.preprocessing import StandardScaler


class TeamPointsModel:
    def __init__(self, target_column="dream_points"):
        """
        Initialize the GradientBoostingModel with specified hyperparameters.
        """
        self.target_column = target_column

        # Initialize GradientBoostingRegressor with specified parameters
        self.model = GradientBoostingRegressor(
            n_estimators=84,
            learning_rate=0.1,
            max_depth=17,
            min_samples_split=15,
            min_samples_leaf=15,
            subsample=0.9,
            max_features=1.0,
            random_state=5,
            loss='absolute_error',
            tol=0.012770236105969923
        )

    def train(self, train_df, test_df, date, test_size=0.2, random_state=42):
        """
        Train the Gradient Boosting model on the given dataset and evaluate metrics.
        """
        # Split the data into features (X) and target (y)
        X_train = train_df.drop(columns=self.target_column)
        y_train = train_df[self.target_column]
        X_test = test_df.drop(columns=self.target_column)
        y_test = test_df[self.target_column]

        y_train = y_train ** 1.65

        # Train the model
        self.model.fit(X_train, y_train)

        # Save the model to a .pkl file
        with open(f'model_{date}.pkl', 'wb') as file:
            pickle.dump(self.model, file)

        # Make predictions on the testing set
        y_pred = self.model.predict(X_test)
        y_pred = y_pred ** (1/1.65)

        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        # Print metrics
        print("Model Evaluation Metrics:")
        print(f"Mean Absolute Error (MAE): {mae:.4f}")
        print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
        print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
        print(f"R-Squared (R²): {r2:.4f}")

    def predict(self, test_df):
        """
        Generate predictions for a given dataset.
        """
        # Generate predictions using the trained model
        y_pred = self.model.predict(test_df)
        y_pred = y_pred ** (1/1.65)

        # Convert predictions to a pandas DataFrame
        y_pred_df = pd.DataFrame(y_pred, columns=['Predicted'])
        return y_pred_df


# class TeamPointsModel:
#     def __init__(self, target_column = "dream_points", n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42):
#         """
#         Initialize the GradientBoostingModel with specified hyperparameters.

#         :param n_estimators: The number of boosting stages (default: 100).
#         :param learning_rate: Learning rate shrinks the contribution of each tree (default: 0.1).
#         :param max_depth: The maximum depth of the individual regression estimators (default: 3).
#         :param random_state: Controls the randomness of the estimator (default: 42).
#         """
#         self.target_column = target_column
#         self.model = GradientBoostingRegressor(
#             n_estimators=n_estimators,
#             learning_rate=learning_rate,
#             max_depth=max_depth,
#             random_state=random_state
#         )

#     def train(self, train_df, test_size=0.2, random_state=42):
#         """
#         Train the Gradient Boosting model on the given dataset.

#         :param X: The feature DataFrame.
#         :param y: The target variable.
#         :param test_size: The proportion of data to use for testing (default: 0.2).
#         :param random_state: Random seed for train-test split (default: 42).
#         :return: A tuple containing the Mean Absolute Error and predictions on the test set.
#         """

#         # Split the data into features (X) and target (y)
#         X = train_df.drop(columns=self.target_column)
#         y = train_df[self.target_column]

#         # Split the data into training and testing sets
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

#         # Train the model
#         self.model.fit(X_train, y_train)

#         # Make predictions on the testing set
#         y_pred = self.model.predict(X_test)

#         # Calculate Mean Absolute Error
#         mae = mean_absolute_error(y_test, y_pred)
#         print("Mean Absolute Error:", mae)

#     def predict(self, test_df):
#         """
#         Generate predictions for a given dataset.

#         :param X: The feature DataFrame.
#         :return: Predictions as a NumPy array.
#         """
#         # Generate predictions using the trained model
        
#         y_pred = self.model.predict(test_df)
#         # Convert predictions to a pandas DataFrame
#         y_pred_df = pd.DataFrame(y_pred, columns=['Predicted'])

#         return y_pred_df


# class TeamPointsModel:
#     def __init__(self, target_column="dream_points"):
#         """"
#         Initialize the GradientBoostingModel with specified hyperparameters.
#         """
#         self.target_column = target_column

#         # Initialize GradientBoostingRegressor with specified parameters
#         self.model = GradientBoostingRegressor(
#             n_estimators=84,
#             learning_rate=0.1,
#             max_depth=17,
#             min_samples_split=15,
#             min_samples_leaf=15,
#             subsample=0.9,
#             max_features=1.0,
#             random_state=5,
#             loss='absolute_error',
#             tol=0.012770236105969923
#         )

#     def train(self, train_df, test_size=0.2, random_state=42):
#         """
#         Train the Gradient Boosting model on the given dataset and evaluate metrics.
#         """
#         # Split the data into features (X) and target (y)
#         X = train_df.drop(columns=self.target_column)
#         y = train_df[self.target_column]

#         # scaler = StandardScaler()
#         # X = scaler.fit_transform(X)
#         # Split the data into training and testing sets
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

#         y_train = y_train ** 1.65

#         # Train the model
#         self.model.fit(X_train, y_train)

#         # Make predictions on the testing set
#         y_pred = self.model.predict(X_test)
#         y_pred = y_pred ** (1/1.65)

#         # Calculate metrics
#         mae = mean_absolute_error(y_test, y_pred)
#         mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
#         rmse = np.sqrt(mean_squared_error(y_test, y_pred))
#         r2 = r2_score(y_test, y_pred)

#         # Print metrics
#         print("Model Evaluation Metrics:")
#         print(f"Mean Absolute Error (MAE): {mae:.4f}")
#         print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
#         print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
#         print(f"R-Squared (R²): {r2:.4f}")

#     def predict(self, test_df):
#         """
#         Generate predictions for a given dataset.
#         """
#         # Generate predictions using the trained model
#         y_pred = self.model.predict(test_df)
#         y_pred = y_pred ** (1/1.65)

#         # Convert predictions to a pandas DataFrame
#         y_pred_df = pd.DataFrame(y_pred, columns=['Predicted'])
#         return y_pred_df
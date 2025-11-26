# Dream Team11 Prediction Platform

## Overview

The Dream Team11 Prediction Platform is a web application that leverages AI to assist users in predicting and creating their ideal Dream11 fantasy team for cricket matches. The platform uses a combination of **Next.js** for the frontend and **Flask** for the backend to integrate a Machine Learning (ML) model, providing personalized recommendations based on match data, player statistics, and real-time news. The platform is designed with a user-friendly interface to facilitate easy interaction and customization of fantasy teams.

This application has been developed to serve as a part of the **Inter IIT Mid Prep Problem Statement** by **Dream11**.

---
## DUEL UI MOCKUPS - https://drive.google.com/file/d/16qnIXz-vshcDSU74Gx_Tza1Jq-DOlPoE/view?usp=sharing

#  Dual-UI System for Dream11 Fantasy Analytics

This project delivers a **Dual-UI ecosystem** consisting of:

1. **Product UI** → Built for Dream11 fantasy users  
2. **Model UI** → Built for Dream11’s internal Data Science team  

Both UIs are powered by a common ML backend with SHAP explainability, enabling transparent, trustworthy, and data-driven decision-making.

---

##  1. Product UI (User-Facing Fantasy Sports Assistant)

The Product UI helps fantasy players make smarter team-building decisions using ML-driven insights.

### **Five Core Features**

---

### **1️⃣ Player Score Prediction Cards**
Each player card includes:
- Predicted fantasy score (ML output)  
- Confidence interval  
- Player role (BAT/BWL/AR/WK)  
- Risk indicator (Safe / Balanced / Risky)  
- Top contributing factors (simplified SHAP)  

Helps users instantly evaluate each player’s potential.

---

### **2️⃣ Context-Aware Filters & Sorting**
Filter players by:
- Form  
- Venue type  
- Player role  
- Opposition difficulty  
- Credits  

Sort options:
- Predicted score  
- Risk rating  
- Credit efficiency  

Enables personalized, strategy-driven team building.

---

### **3️⃣ Simplified Explainability (SHAP for Users)**
Human-readable “Why this prediction?” panel showing:
- Form impact  
- Venue advantage  
- Role influence  
- Opponent difficulty  

Each factor displayed as a +/– point contribution.  
Boosts user trust via transparent AI.

---

### **4️⃣ Captain & Vice-Captain Recommendation Engine**
Based on ML predictions + stability metrics:
- Suggests high-value C/VC picks  
- Shows confidence & risk  
- Explains the reasoning  

Improves the most critical decision in fantasy sports.

---

### **5️⃣ Interactive Team Builder Panel**
Features:
- Real-time player selection  
- Predicted total team score  
- Credit usage updates  
- Role distribution validation  
- Risk meter (based on variance)  

Streamlines the entire team creation experience.

---

---

##  2. Model UI (Internal ML Debugging & Model Comparison Tool)

The Model UI is designed for Dream11’s internal DS team to analyze, compare, and debug ML models.

### **Five Core Features**

---

### **1️⃣ Model Comparison Dashboard**
Side-by-side comparison of 5+ ML models:
- R²  
- MAE / RMSE  
- Training time  
- Inference latency  
- Stability score  
- Feature count  

Helps quickly identify the most reliable model.

---

### **2️⃣ Global & Local SHAP Explainability**
Includes:
- Global SHAP bar chart  
- Player-level waterfall plots  
- SHAP force plots  
- Model-to-model SHAP comparison  

Critical for understanding model behavior.

---

### **3️⃣ Error Analysis & Diagnostic Panel**
Provides:
- Under/over-prediction distribution  
- Player-wise error heatmaps  
- Match-level error trends  
- Outlier detection  
- Predicted vs Actual scatterplots  

Identifies edge cases and model weaknesses.

---

### **4️⃣ Player-Level Insight Explorer**
For any selected player:
- Raw features  
- Normalized values  
- Predictions from multiple models  
- SHAP contributions  
- Error patterns  

Supports granular debugging.

---

### **5️⃣ Hyperparameters & Training Configuration Viewer**
Shows:
- Max depth  
- Learning rate  
- Trees/estimators  
- Loss function  
- Regularization  
- Training logs  

Ensures reproducibility and quick re-training.

---

---

##  Unified ML Backend

Both UIs are powered by the same ML pipeline:

- Data extraction  
- Preprocessing  
- EDA  
- Feature engineering  
- 5+ regression models  
- Best model achieved **R² = 0.91**  
- SHAP explainability (global + local)  

---

##  Outcome

This dual-UI system provides:

- A **transparent AI assistant** for Dream11 users  
- A **technical, deep debugging interface** for Dream11’s ML team  
- A cohesive **product + ML + explainability** ecosystem  

---

## Folder Structure
```
├── README.md                   <- Project overview and usage instructions


├── docs                        <- Documentation and project demo
│   └── video_demo              <- Walk-through video, covering setup, UI, and functionality


├── src                         


├── data                        <- Data folder with all stages of data
│   ├── processed               <- Finalized datasets ready for modeling and generated training datasets
│   └── raw                     <- Original data as downloaded
│       ├── cricksheet          <- Raw data from Cricksheet
│       └── additional          <- GenAI Augmented data



├── data_processing             <- Scripts to process data
│   ├── data_download.py        <- Download all project data using this script. All raw data sources are processed here before further use.
│   └── feature_engineering.py  <- Handles all data manipulation and feature engineering for the project.
│   └── SHAP_controller.py      <- Runner code for SHAP explanations.
│   └── SHAP.py                 <- Contains the SHAP class.



├── model                       <- Modeling scripts for training and prediction
│   ├── teampointsmodel.py      <- Predicts Dream Team total points.
│   └── playerpointsmodel.py    <- Predicts individual points for each player (Product UI).
│   └── playerpointsmodel2.py   <- Predicts individual points for each player (Model UI).



├── model_artifacts             <- Storage for trained models
│                             (Includes pre-trained model for Product UI and generated model weight files from Model UI)



├── rest                        <- Contains functions for miscellaneous requirements for Product UI.

└── UI                          <- All files related to the user interface 
```


## Tech Stack

- **Frontend**: 
  - **Next.js**: A React framework used for building the interactive UI, handling routing, and server-side rendering.
  - **Tailwind CSS**: For responsive and clean UI design.
  - **React**: Core library for building the user interface components.

- **Backend**:
  - **Flask**: A lightweight Python web framework for handling API requests and integrating with the ML model.
  - **Python (ML model)**: The backend hosts the AI model, which is responsible for predicting the Dream11 team based on the data input from the frontend.

- **Database**:
 The platform uses **MongoDB** as its database to store:

  - **User Information**: User authentication details, preferences, and settings are securely stored for personalized experiences.
  - **Chat History**: Interaction logs with the AI chatbot ("Dream") are saved, enabling continuity in conversations and allowing users to revisit past suggestions and recommendations.
- **External APIs**:
  - **Cricket News API**: To fetch the latest cricket news.
---

## Installation & Setup
The product UI and ModelUI cannot be run at the same time on a SAME machine. Kindly use two different machines to run them at the same time. 

## Product UI:
### Prerequisites

Before you start, ensure that you have the following installed on your local machine:

- **Node.js** (>= 14.x)
- **Python** (>= 3.7)
- **pip** (Python package manager)
- **Flask**
- **Virtual Environment (for Python)**

### Frontend Setup (Next.js)

1. Clone the repository:
   ```bash
   git clone https://github.com/D11-MP/Dream11-prototype
   cd Dream11-prototype
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`.

### Backend Setup (Flask)

1. Navigate to the backend folder:
   ```bash
   cd ..
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask server:
   ```bash
   python runner.py
   ```

   The backend will be available at `http://localhost:5000`.

### Integration Between Frontend and Backend

- The Next.js frontend communicates with the Flask backend using RESTful APIs for fetching data and interacting with the machine learning model.
- The backend processes user input, runs predictions using the trained AI model, and returns the results to the frontend.


## Model UI:

The Model-UI is used to run the model between a start and end date for both- Training and Testing for the Dream-11 players and provide the downloadable csv along with the metric visualized using graphs

### Prerequisites
 1. NodeJS should be installed in your local system(Download from [here](https://nodejs.org/en/download/package-manager))
 2. You should have a Account in WanDB for visalizing the graphs and must get a API key. [Click here](https://wandb.ai)
 3. Python must be installed and it's path must be set up in your local system. Download it from [here](https://www.python.org/downloads/)
 4. Set up a .env folder in the same directory as __main__.py. Follow the .env.sample file there


### How to start the Flask Server(this where the model runs)
 1. Create and Start a virtual enviroment in inside the directory where __main__.py exists. follow the below in the terminal
```
python -m venv venv
```
```
venv/Scripts/activate
```
 2.  Set the requriements.txt file by this - 
```
python -m pip install requirements.txt
``` 
 3. Start the Flask server by running the below code in same directory as __main__.py where the virtual enviroment is running(make sure the port 5000 on your localhost is free) 
```
pip __main__.py
```
Now the server is running on localhost:5000


## How to Run the UI Locally

1. **Navigate to the Frontend Directory**  
   Open a terminal and navigate to the `frontend` directory.  

2. **Install Dependencies**  
   Run the following command to install all the necessary dependencies:  
   ```bash
   npm install
   ```

3. **Start the Development Server**  
   After the dependencies are installed, run:  
   ```bash
   npm run dev
   ```  

4. **Access the UI**  
   - The UI will start on `localhost:3000`.  
   - Ensure that port 3000 is free; otherwise, the application will start on a different port (e.g., 3001).  
   - Check the terminal output to confirm the port being used.  



### User Flow
 Enter the start and end date for the training and testing and click on generate. This will take you to the next page where it takes time to generate the response in the server. 

---

## Usage

1. **Login**: Users can log in or sign up using the NextAuth.js authentication system.
2. **Upload CSV**: The admin can upload a CSV file containing the match data. The file should follow the predefined format.
3. **Navigate to Matches**: After login, users can view available matches, along with player lineups, and interact with the platform’s features.
4. **Build Your Dream11 Team**: Users can create their team by following the beginner or advanced paths, using AI suggestions, or customizing based on their preferences.
5. **Generate Team**: When ready, click the "Generate Team" button to get the final playing 11, which includes AI-generated reasons for each player’s selection.

---

## Future Enhancements

- **User Profile**: Add the ability for users to save their Dream11 teams and preferences.
- **Real-time Match Updates**: Integrate real-time match data, such as live scores and player performance.
- **Social Sharing**: Allow users to share their Dream11 teams on social media platforms.
- **Mobile App**: Create a mobile application version of the platform for iOS and Android.

---

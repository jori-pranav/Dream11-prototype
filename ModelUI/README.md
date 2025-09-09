# Model-UI

### The Model-UI is used to run the model between a start and end date for both- Training and Testing for the Dream-11 players and provide the downloadable csv along with the metric visualized using graphs

## Prerequisites
### NodeJS should be installed in your local system(Download from [here](https://nodejs.org/en/download/package-manager))
### You should have a Account in WanDB for visalizing the graphs and must get a API key. [Click here](https://wandb.ai)
### Python must be installed and it's path must be set up in your local system. Download it from [here](https://www.python.org/downloads/)
### set up a .env folder in the same directory as __main__.py. Follow the .env.sample file there


## How to start the Flask Server(this where the model runs)
### Create and Start a virtual enviroment in inside the directory where __main__.py exists. follow the below in the terminal
```
python -m venv venv
```
```
venv/Scripts/activate
```
### Set the requriements.txt file by this - 
```
python -m pip install requirements.txt
``` 
### Start the Flask server by running the below code in same directory as __main__.py where the virtual enviroment is running(make sure the port 5000 on your localhost is free) 
```
pip __main__.py
```
### Now the server is running on localhost:5000



## How to Run the UI on local?
### enter the Frontend directory -> ``` npm install ``` in the terminal -> ``` npm run dev ``` in the terminal after all the node_modules are installed -> UI starts on localhost:3000(make sure to keep it free else it will start on some other Port instead of 3000 like 3001 etc.)


## User Flow
### Enter the start and end date for the training and testing and click on generate. This will take you to the next page where it takes time to generate the response in the server. 

from PlayerPointsModel import *
from TeamPointsModel import *
from Format_config import *
from Format_config_points import *
from converter import *
from common import *
from Graph import *
from datetime import date
import wandb
from constants import *

player_identifier_to_name = {}
player_name_to_identifier = {}

from flask import Flask , send_file, request, jsonify

app = Flask(__name__)
from flask_cors import CORS 
CORS(app)

def last_preprocess(match_df , player_df):
  # match_df['League'] = match_df['League'].fillna(match_df['team2'] + ' in ' + match_df['team1'] + ' T20I Series')

  match_df['team1_high'] = match_df['team1'].apply(lambda x: 1 if x in high_teams else 0  )
  match_df['team1_mid'] = match_df['team1'].apply(lambda x: 1 if x in mid_teams else 0  )
  match_df['team1_low'] = match_df['team1'].apply(lambda x: 1 if x in low_teams else 0  )

  match_df['team2_high'] = match_df['team2'].apply(lambda x: 1 if x in high_teams else 0  )
  match_df['team2_mid'] = match_df['team2'].apply(lambda x: 1 if x in mid_teams else 0  )
  match_df['team2_low'] = match_df['team2'].apply(lambda x: 1 if x in low_teams else 0  )

  cols = ['match_id' , 'match_type']
  # temp_df = player_df[cols].groupby('match_id')
  temp_df = player_df[cols].groupby('match_id', as_index=False).first()


  # Use suffixes to prevent renaming of columns
  match_df = pd.merge(match_df, temp_df, on='match_id', how='left', suffixes=('', '_duplicate'))

  ## adding gender to match_df
  # Extract the first player ID from 'team1.player_id'

  match_df['first_player_id'] = match_df['team1.player_id'].apply(lambda x: x.split(',')[0])

  # Ensure 'player_id' is unique in player_df before mapping
  player_df = player_df[~player_df.duplicated(subset=['player_id'], keep='first')]

  # Map the 'gender' column from player_df based on 'first_player_id'
  match_df['gender'] = match_df['first_player_id'].map(
    player_df.set_index('player_id')['gender']
  )
  # Drop the 'first_player_id' column if it's no longer needed
  match_df.drop(columns=['first_player_id'], inplace=True)
  # One hot en
  match_df = pd.get_dummies(match_df, columns=['gender'], prefix='gender', dtype=int)
  match_df = pd.get_dummies(match_df, columns=['match_type'], prefix='match_type', dtype=int)

  #chaning trget variable
  # match_df['total_points_transformed'] = match_df['dream_points'] ** 1.65
  # match_df.drop(columns=['dream_points'], inplace=True)
  return match_df

def model_ui(start_train_date, end_train_date, start_test_date, end_test_date , player_df , match_df ):

    '''
      match_df -> original match by match data
      match_df_1 -> match by match for training period
      match_df_2 -> match by match for testing period
      match_df_train -> match by match for training model
      match_df_test -> match by match for testing model

      player_df -> original player by player data
      player_df_1 -> player by player for training period
      player_df_2 -> player by player for testing period
      player_df_train -> player by player for training model
      player_df_test -> player by player for testing model

    '''
    if isinstance(start_train_date, str):
      start_train_date = datetime.strptime(start_train_date, "%Y-%m-%d")  # Adjust format as needed
    if isinstance(end_train_date, str):
      end_train_date = datetime.strptime(end_train_date, "%Y-%m-%d")
    if isinstance(start_test_date, str):
      start_test_date = datetime.strptime(start_test_date, "%Y-%m-%d")
    if isinstance(end_test_date, str):
      end_test_date = datetime.strptime(end_test_date, "%Y-%m-%d")



    # formats = ball_by_ball_df['Match_type'].unique()

    # ball_by_ball_df['date_playing'] = pd.to_datetime(ball_by_ball_df['date_playing'])

    # ball_by_ball_df = ball_by_ball_df[
    #     (ball_by_ball_df['date_playing'] <= max(end_train_date, end_test_date))
    # ].reset_index(drop=True)
    # print("Generated ball_by_ball_df")

    # match_dfs_list = []
    # player_df_list = []

    # for format in formats:
    #   if format == "MDM" or format == "Test":
    #     ball_by_ball_temp = ball_by_ball_df[
    #         (ball_by_ball_df['Match_type'] == "MDM") | (ball_by_ball_df['Match_type'] == "Test")
    #     ]

    #   if format == "ODM" or format == "ODI":
    #     ball_by_ball_temp = ball_by_ball_df[
    #         (ball_by_ball_df['Match_type'] == "ODM") | (ball_by_ball_df['Match_type'] == "ODI")
    #     ]

    #   if format == "IT20" or format == "T20":
    #     ball_by_ball_temp = ball_by_ball_df[
    #         (ball_by_ball_df['Match_type'] == "IT20") | (ball_by_ball_df['Match_type'] == "T20")
    #     ]

    #   if format == "MDM":
    #     format = "Test"
    #   if format == "ODM":
    #     format = "ODI"
    #   if format == "IT20":
    #     format = "T20"

    #   player_summary_dfs = convert_to_player_summary_df(ball_by_ball_df, format)
    #   print(f"Generated player_summary_dfs for {format} format")

    #   for id in player_summary_dfs.keys():
    #     player_summary_dfs[id] = player_summary_dfs[id].sort_values(by = ['date_playing', 'match_id'])

    #   player_df = convert_to_player_df(player_summary_dfs)
    #   print(f"Generated player_df for {format} format")
    #   player_df_list.append(player_df)

    #   ball_by_ball_m = ball_by_ball_temp[ball_by_ball_temp['Gender'] == 'male']
    #   ball_by_ball_f = ball_by_ball_temp[ball_by_ball_temp['Gender'] == 'female']

    #   if(len(ball_by_ball_m) > 0):
    #     match_df_m = convert_to_match_data(player_summary_dfs, ball_by_ball_m)
    #     print(f"Generated match_df for {format} format male")
    #     match_dfs_list.append(match_df_m)

    #   if(len(ball_by_ball_f) > 0):
    #     match_df_f = convert_to_match_data(player_summary_dfs, ball_by_ball_f)
    #     print(f"Generated match_df for {format} format female")
    #     match_dfs_list.append(match_df_f)


    # match_df = pd.concat(match_dfs_list, ignore_index=True)
    # print("Generated match_df")

    # player_df = pd.concat(player_df_list, ignore_index=True)
    # print("Generated player_df")

    match_df.fillna(0, inplace = True)
    player_df.fillna(0, inplace = True)

    if 'Unnamed: 0' in match_df.columns:
      match_df = match_df.drop(columns=['Unnamed: 0'])

    # match_df_org = match_df.copy()
    match_df['date_playing'] = pd.to_datetime(match_df['date_playing'])
    player_df['date_playing'] = pd.to_datetime(player_df['date_playing'])

    match_df = last_preprocess(match_df, player_df)

    # Columns to exclude from scaling
    exclude_columns = ['League', 'team1', 'team2', 'stadium', 'match_id',
                  'date_playing', 'team1.player_id', 'team2.player_id', 'dream_points',  'team1_high',
       'team1_mid', 'team1_low', 'team2_high', 'team2_mid', 'team2_low',
       'gender_female', 'gender_male', 'match_type_ODI', 'match_type_T20', 'match_type_Test']

    # Separate the columns to scale and those to exclude
    columns_to_scale = [col for col in match_df.columns if col not in exclude_columns]

    # Initialize the scaler
    scaler = StandardScaler()

    # Scale only the selected columns
    match_df[columns_to_scale] = scaler.fit_transform(match_df[columns_to_scale])

    match_df_1 = match_df[(match_df['date_playing'] >= start_train_date) & (match_df['date_playing'] <= end_train_date)].reset_index(drop=True)
    print("Generated match_df_1")

    match_df_2 = match_df[(match_df['date_playing'] >= start_test_date) & (match_df['date_playing'] <= end_test_date)].reset_index(drop=True)
    print("Generated match_df_2")

    player_df_1 = player_df[(player_df['date_playing'] >= start_train_date) & (player_df['date_playing'] <= end_train_date)].reset_index(drop=True)
    print("Generated player_df_1")

    player_df_2 = player_df[(player_df['date_playing'] >= start_test_date) & (player_df['date_playing'] <= end_test_date)].reset_index(drop=True)
    print("Generated player_df_2")

    # # sorting all data frames by date , match_id
    match_df_1.sort_values(by=['date_playing', 'match_id'], inplace=True)
    player_df_1.sort_values(by=['date_playing', 'match_id'], inplace=True)
    match_df_2.sort_values(by=['date_playing', 'match_id'], inplace=True)
    player_df_2.sort_values(by=['date_playing', 'match_id'], inplace=True)

    cols_to_drop = ['Unnamed: 0', 'player_id', 'match_id', 'team', 'total_runs_made',
       'total_balls_faced', 'total_runs_given', 'total_balls_bowled',
       'total_extras', 'total_wickets', 'lbw_wickets', 'bowled_wickets',
       'maidens', 'catches', 'runouts', 'stadium', 'dates', 'date_playing',
       'league', 'match_type', 'gender', 'total_runs_points', 'run_6_points',
       'run_bonus_points', 'strike_rate', 'strike_rate_points',
       'total_bat_points', 'economy_rate', 'total_wickets_points',
       'lbw_bowled_bonus_points', 'wicket_bonus_points', 'economy_rate_points',
       'maiden_overs_points', 'total_bowl_points', 'catch_points',
       'catch_bonus_points', 'run_outs_points', 'total_fielding_points']

    match_df_train = match_df_1.drop(columns = ['League', 'team1', 'team2', 'stadium', 'match_id' , 'date_playing', 'team1.player_id', 'team2.player_id'])

    player_df_train  = player_df_1.copy()
    for col in cols_to_drop:
      if col in player_df_train.columns:
        player_df_train = player_df_train.drop(columns=[col])

    match_df_test = match_df_2.drop(columns = ['League', 'team1', 'team2', 'stadium', 'match_id', 'date_playing', 'team1.player_id', 'team2.player_id'])

    player_df_test  = player_df_2.copy()
    for col in cols_to_drop:
      if col in player_df_test.columns:
        player_df_test = player_df_test.drop(columns=[col])
    player_df_test = player_df_test.drop(columns = ['total_points'])

    match_df_train.to_csv(f'training_data_{end_train_date.date()}.csv')
    player_df_train.to_csv(f'training_data_auxillary_{end_train_date.date()}.csv')

    #calling the models
    team_points_model = TeamPointsModel()
    team_points_model.train(match_df_train, match_df_test, end_train_date.date())
    match_df_test.drop(columns = ['dream_points'], inplace = True)
    team_point_predictions = team_points_model.predict(match_df_test)

    player_points_model = PlayerPointsModel()
    player_points_model.train(player_df_train, end_train_date.date())
    player_point_predictions = player_points_model.predict(player_df_test)

    #creating results df
    final_cols = [ 'Match Date',
    'Team 1',
    'Team 2',
    ]
    for i in range(1,12):
      final_cols.append(f"Predicted Player {i}")
      final_cols.append(f"Predicted Player {i} Points")
    for i in range(1,12):
      final_cols.append(f"Dream Team Player {i}")
      final_cols.append(f"Dream Team Player {i} Points")
    final_cols.extend(["Total Points Predicted","Total Dream Team Points","Total Points MAE"])
    # final_cols.extend(["Total_Points_Predicted_player","Total Points MAE Player"])

    results_df = pd.DataFrame(columns=final_cols)

    #populating the values
    new_row = {}
    j = 0
    curr_date = datetime(2020, 11, 20) #RANDOM
    for i in range(0, len(team_point_predictions), 2):
        new_row["Total Points Predicted"] = team_point_predictions.iloc[i].item()
        new_row["Total Dream Team Points"] = match_df_2.iloc[i]["dream_points"]
        new_row["Match Date"] = match_df_2.iloc[i]["date_playing"]
        curr_date = new_row["Match Date"]
        new_row["Match Date"] = match_df_2.iloc[i]["date_playing"].date()
        new_row["Team 1"] = match_df_2.iloc[i]["team1"]
        new_row["Team 2"] = match_df_2.iloc[i]["team2"]
        new_row["Total Points MAE"] = abs(team_point_predictions.iloc[i].item() - new_row["Total Dream Team Points"])
        all_player_actual = []
        all_player_predicted = []
        sum = 0.0000000001
        players = []
        for id in match_df_2.iloc[i]["team1.player_id"].split(','):
          players.append(id)
        for id in match_df_2.iloc[i]["team2.player_id"].split(','):
          players.append(id)

        curr_player = []
        while j < len(player_df_2) and player_df_2.iloc[j]['match_id'] == match_df_2.iloc[i]['match_id'] :
          all_player_predicted.append((player_point_predictions.iloc[j].item(), player_df_2.iloc[j]['player_id'] ))
          curr_player.append(player_df_2.iloc[j]["player_id"])
          all_player_actual.append((player_df_2.iloc[j]["total_points"], player_df_2.iloc[j]['player_id']) )
          j += 1

        for id in players:
          if id not in curr_player  :
              filtered_df = player_df_2 [(player_df_2['player_id'] == id) & (player_df_2['date_playing'] < curr_date)]
              if filtered_df.empty:
                zero_array = np.zeros((1, len(player_df_test.columns)))
                pred_row = pd.DataFrame(zero_array)
              else:
                most_recent_index = filtered_df['date_playing'].idxmax()
                pred_row = player_df_test.iloc[[most_recent_index]]
              temp_pred =  player_points_model.predict(pred_row)
              all_player_actual.append((0, id))
              all_player_predicted.append((temp_pred.iloc[0].item(), id))


        all_player_actual.sort(key=lambda x: x[0], reverse=True)  # Sort based on the first element of each tuple
        all_player_predicted.sort(key=lambda x: x[0], reverse=True)  # Sort based on the first element of each tuple
        for j1 in range(min(11, len(all_player_predicted))):
          sum += all_player_predicted[j1][0]
        for j1 in range(11):
          if j1 < len(all_player_predicted) :
            player_id = all_player_predicted[j1][1]
            new_row[f"Predicted Player {j1+1}"] = player_identifier_to_name.get(player_id, "NA")
          else :
            new_row[f"Predicted Player {j1+1}"] = "NA"

          if j1 < len(all_player_predicted) :
            new_row[f"Predicted Player {j1+1} Points"] = team_point_predictions.iloc[i].item()*(all_player_predicted[j1][0]/sum)
          else :
            new_row[f"Predicted Player {j1+1} Points"] = 0

          if j1 < len(all_player_actual) :
            player_id = all_player_actual[j1][1]
            new_row[f"Dream Team Player {j1+1}"] = player_identifier_to_name.get(player_id, "NA")
          else :
            new_row[f"Dream Team Player {j1+1}"] = "NA"

          if j1 < len(all_player_actual) :
            new_row[f"Dream Team Player {j1+1} Points"] = all_player_actual[j1][0]
          else :
            new_row[f"Dream Team Player {j1+1} Points"] = 0

        #adding new row
        results_df.loc[len(results_df)] = new_row


    #downloading model and weights
    #how to dump two weights ? (check PS )
    # results_df.to_csv(f"results_{end_train_date.date()}.csv")

    end_t = end_train_date.strftime("%d-%m-%Y %H:%M:%S")
    results_df.to_csv(f"results_e{datetime.strptime(end_t, "%d-%m-%Y %H:%M:%S").date()}.csv")
    return f"results_e{datetime.strptime(end_t, "%d-%m-%Y %H:%M:%S").date()}.csv"



def main(startTrainDate,endTrainDate,startTestDate,endTestDate):
# def main():
    # prompt: create hashmap and populate it with identifier as keys and unique name as values
    ppl = pd.read_csv("people (2).csv")
    # match_df = pd.read_csv("match.csv")
    with open("players_dfs.pkl" , "rb") as f:
      player_df = pickle.load(f)
    with open("match_df.pkl" , "rb") as f:
      match_df = pickle.load(f)
    player_df.fillna(0 , inplace =True)
    match_df.fillna(0, inplace = True)
    # Assuming 'ppl' DataFrame has columns 'identifier' and 'unique_name'
    for index, row in ppl.iterrows():
        identifier = row['identifier']
        unique_name = row['unique_name']
        player_identifier_to_name[identifier] = unique_name
        player_name_to_identifier[unique_name] = identifier
    start_train_date = datetime(int(startTrainDate[0:4]), int(startTrainDate[5:7]), int(startTrainDate[8:10]))
    end_train_date = datetime(int(endTrainDate[0:4]), int(endTrainDate[5:7]), int(endTrainDate[8:10]))
    start_test_date = datetime(int(startTestDate[0:4]), int(startTestDate[5:7]), int(startTestDate[8:10]))
    end_test_date = datetime(int(endTestDate[0:4]), int(endTestDate[5:7]), int(endTestDate[8:10]))
    # start_train_date = datetime(2024, 5, 8)
    # end_train_date = datetime(2024, 5, 19)
    # start_test_date = datetime(2024, 1, 1)
    # end_test_date = datetime(2024, 1, 10)
    # df_ball = pd.read_csv("sj1.csv")
    fileName=model_ui(start_train_date, end_train_date, start_test_date, end_test_date , player_df , match_df)
    return fileName


class WandBPlotter:
  def __init__(self):
    wandb.login()
  
  def runWandB(self):
    wandb_project = WanDB()
    # df = pd.read_csv("match.csv")
    with open('match_df.pkl' , 'rb') as f:
      df = pickle.load(f)
    X_train, X_test, y_train, y_test = wandb_project.preprocess_data(df)
    print("Proccessed Data")
    wandb_project.start_sweep(X_train, X_test, y_train, y_test)
    data = wandb_project.fetch_results()
    return data

  # def getGraphsUrl(self , run_id=None):
  #   api=wandb.Api()
  #   project = api.project('lol')
  #   print(project)
  #   runs = api.runs('lol')
  #   urls=[]
  #   for run in runs:
  #     if run_id and run.id != run_id:
  #       continue
  #     urls.append(run.url)
  #   return urls


@app.route("/graphs" , methods=["GET"])
def graphs():
  try:
    plotter = WandBPlotter()
    data = plotter.runWandB()
    print('WandB ran')
    # plotter.fetch_results()
    # urls = plotter.getGraphsUrl()
    # print(urls)
    data2=[]
    with open(f"training_results.csv", mode='r') as file:
      reader = csv.reader(file)
      next(reader)
      for row in reader:
        data2.append([float(value) for value in row])
      
    print(data2)
    return jsonify({"message":"success","data":data,"data2":data2})
  except Exception as e:
    return jsonify({"error": str(e)}) 




@app.route("/download", methods=["POST"])
def download():
  try:
    data = request.get_json()
    fileName = data.get("fileName","")
    if not fileName:
      return jsonify({'error':'No filename sent'})
    filePath = f"./{fileName}"
    return send_file(filePath, as_attachment=True, download_name=fileName)
  except FileNotFoundError:
    return jsonify({"error": f"File '{file_name}' not found in server"})
  except Exception as e:
    return jsonify({"error": str(e)}) 





@app.route("/predict" , methods=["POST"])
def predict():
  data = request.get_json()
  startTrainDate = data.get('start_train_date', '')
  endTrainDate = data.get('end_train_date', '')
  startTestDate = data.get('start_test_date', '')
  endTestDate = data.get('end_test_date', '')

  fileName = main(startTrainDate,endTrainDate,startTestDate,endTestDate)
  return jsonify({"message":"Success","fileName":fileName})

if __name__ == "__main__":
  app.run(debug=True)
  # main()

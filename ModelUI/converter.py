from PlayerPointsModel import *
from TeamPointsModel import *
from Format_config import *
from Format_config_points import *
import pandas as pd
import json
import pandas as pd
import numpy as np
import zipfile
import os
import re
from collections import deque, defaultdict
import datetime
from datetime import datetime
import pickle
import ast
import warnings
warnings.filterwarnings("ignore")



def convert_to_player_df(player_summary_dfs):

  for id in player_summary_dfs.keys():
      df2  =  player_summary_dfs[id]
      # dream11 = Dream11Points_t20(player_scorecard= df2, pointsconfig=t20_pointsconfig)
  # Calculate total points
      # dream11.get_batsmen_bowler_points()
      df3 = df2.select_dtypes(include='number')
      add_rolling_averages(df2, df3.columns, 1, 2,  5, 10, 15)



  final_df_new = pd.concat(
      [df.assign(player_id=player_id)[['player_id'] + df.columns.tolist()] for player_id, df in player_summary_dfs.items()],
      ignore_index=True
  )


  # ######## assigning date here ###################
  # final_df2 = final_df_new[final_df_new['date_playing'] >= start_date]
  # final_df2 = final_df2[final_df2['date_playing'] <= end_date]
  final_df2 = final_df_new

  cols_to_drop = [col for col in final_df2.columns if any(x in col for x in [ '3', '4'])]
  final_df2 = final_df2.drop(cols_to_drop,axis=1)
  train_df = final_df2

  train_df['matches_played'] = train_df.groupby('player_id').cumcount() + 1

  # Sort the DataFrame by 'player_id' and 'date_playing'
  train_df = train_df.sort_values(by=['player_id', 'date_playing'])

  # Calculate cumulative sums for the relevant columns and add them as new columns
  train_df['total_runs_made_cumulative'] = train_df.groupby('player_id')['total_runs_made'].cumsum().shift(1, fill_value=0)
  train_df['total_runs_given_cumulative'] = train_df.groupby('player_id')['total_runs_given'].cumsum().shift(1, fill_value=0)
  train_df['total_sixes_cumulative'] = train_df.groupby('player_id')['total_sixes'].cumsum().shift(1, fill_value=0)
  train_df['total_fours_cumulative'] = train_df.groupby('player_id')['total_fours'].cumsum().shift(1, fill_value=0)
  train_df['total_wickets_taken_cumulative'] = train_df.groupby('player_id')['total_wickets'].cumsum().shift(1, fill_value=0)
  train_df['total_balls_bowled_cumulative'] = train_df.groupby('player_id')['total_balls_bowled'].cumsum().shift(1, fill_value=0)
  train_df['total_catches_cumulative'] = train_df.groupby('player_id')['catches'].cumsum().shift(1, fill_value=0)

  train_df=train_df.fillna(0)

  ## BATTING FEATURES
  train_df['Consistency_batting'] = (
      0.4262 * train_df['avg_total_runs_made_last_5_matches'] +
      0.2566 * train_df['matches_played'] +
      0.1510 * train_df['avg_strike_rate_last_5_matches']
  )

  ## BOWLING FEATURES
  train_df['Consistency_bowling'] = (
      0.4174 * train_df['total_balls_bowled_cumulative']/6 +
      0.2634 * train_df['matches_played'] +
      0.1602 * train_df['total_balls_bowled_cumulative']/train_df['total_wickets_taken_cumulative']
  )

  # Data Cleaning and removing unnecessary Columns

  mean_target = train_df.groupby('stadium')['total_points'].mean()
  train_df['stadium'] = train_df['stadium'].map(mean_target)

  mean_target = train_df.groupby('team')['total_points'].mean()
  train_df['team'] = train_df['team'].map(mean_target)

  # train_df=train_df.drop(['match_id','gender','league','dates'],axis=1)

  columns_to_drop = [col for col in train_df.columns if col.startswith('avg_avg')]
  train_df = train_df.drop(columns=columns_to_drop)

  # columns_to_drop = [col for col in train_df.columns if 'points' in col and col!="total_points"]
  # train_df = train_df.drop(columns=columns_to_drop)
  train_df = train_df.drop("Consistency_bowling",axis=1)
  train_df = train_df.fillna(0)  # Replace nulls with 0

  train_df['match_type'] = train_df['match_type'].replace('IT20', 'T20')
  train_df['match_type'] = train_df['match_type'].replace('MDM', 'ODI')
  train_df['match_type'] = train_df['match_type'].replace('ODM', 'ODI')

  train_df = train_df.drop([col for col in train_df.columns if 'cumulative' in col],axis=1)

  T20_train_df = train_df[train_df['match_type']=="T20"]
  ODI_train_df = train_df[train_df['match_type']=="ODI"]
  Test_train_df = train_df[train_df['match_type']=="Test"]

  # Sort the DataFrame by 'player_id' and 'date_playing'
  T20_train_df = T20_train_df.sort_values(by=['player_id', 'date_playing'])

  # Calculate cumulative sums for the relevant columns and add them as new columns
  T20_train_df['total_runs_made_cumulative'] = T20_train_df.groupby('player_id')['total_runs_made'].cumsum().shift(1, fill_value=0)
  T20_train_df['total_runs_given_cumulative'] = T20_train_df.groupby('player_id')['total_runs_given'].cumsum().shift(1, fill_value=0)
  T20_train_df['total_sixes_cumulative'] = T20_train_df.groupby('player_id')['total_sixes'].cumsum().shift(1, fill_value=0)
  T20_train_df['total_fours_cumulative'] = T20_train_df.groupby('player_id')['total_fours'].cumsum().shift(1, fill_value=0)
  T20_train_df['total_wickets_taken_cumulative'] = T20_train_df.groupby('player_id')['total_wickets'].cumsum().shift(1, fill_value=0)
  T20_train_df['total_balls_bowled_cumulative'] = T20_train_df.groupby('player_id')['total_balls_bowled'].cumsum().shift(1, fill_value=0)
  T20_train_df['total_catches_cumulative'] = T20_train_df.groupby('player_id')['catches'].cumsum().shift(1, fill_value=0)


  # Sort the DataFrame by 'player_id' and 'date_playing'
  ODI_train_df = ODI_train_df.sort_values(by=['player_id', 'date_playing'])

  # Calculate cumulative sums for the relevant columns and add them as new columns
  ODI_train_df['total_runs_made_cumulative'] = ODI_train_df.groupby('player_id')['total_runs_made'].cumsum().shift(1, fill_value=0)
  ODI_train_df['total_runs_given_cumulative'] = ODI_train_df.groupby('player_id')['total_runs_given'].cumsum().shift(1, fill_value=0)
  ODI_train_df['total_sixes_cumulative'] = ODI_train_df.groupby('player_id')['total_sixes'].cumsum().shift(1, fill_value=0)
  ODI_train_df['total_fours_cumulative'] = ODI_train_df.groupby('player_id')['total_fours'].cumsum().shift(1, fill_value=0)
  ODI_train_df['total_wickets_taken_cumulative'] = ODI_train_df.groupby('player_id')['total_wickets'].cumsum().shift(1, fill_value=0)
  ODI_train_df['total_balls_bowled_cumulative'] = ODI_train_df.groupby('player_id')['total_balls_bowled'].cumsum().shift(1, fill_value=0)
  ODI_train_df['total_catches_cumulative'] = ODI_train_df.groupby('player_id')['catches'].cumsum().shift(1, fill_value=0)


  # Sort the DataFrame by 'player_id' and 'date_playing'
  Test_train_df = Test_train_df.sort_values(by=['player_id', 'date_playing'])

  # Calculate cumulative sums for the relevant columns and add them as new columns
  Test_train_df['total_runs_made_cumulative'] = Test_train_df.groupby('player_id')['total_runs_made'].cumsum().shift(1, fill_value=0)
  Test_train_df['total_runs_given_cumulative'] = Test_train_df.groupby('player_id')['total_runs_given'].cumsum().shift(1, fill_value=0)
  Test_train_df['total_sixes_cumulative'] = Test_train_df.groupby('player_id')['total_sixes'].cumsum().shift(1, fill_value=0)
  Test_train_df['total_fours_cumulative'] = Test_train_df.groupby('player_id')['total_fours'].cumsum().shift(1, fill_value=0)
  Test_train_df['total_wickets_taken_cumulative'] = Test_train_df.groupby('player_id')['total_wickets'].cumsum().shift(1, fill_value=0)
  Test_train_df['total_balls_bowled_cumulative'] = Test_train_df.groupby('player_id')['total_balls_bowled'].cumsum().shift(1, fill_value=0)
  Test_train_df['total_catches_cumulative'] = Test_train_df.groupby('player_id')['catches'].cumsum().shift(1, fill_value=0)


  T20_train_df=T20_train_df.drop(['total_sixes','total_fours'],axis=1)
  ODI_train_df=ODI_train_df.drop(['total_sixes','total_fours'],axis=1)
  Test_train_df=Test_train_df.drop(['total_sixes','total_fours'],axis=1)

  T20_train_df = T20_train_df[T20_train_df['player_id'] != 0]
  ODI_train_df = ODI_train_df[ODI_train_df['player_id'] != 0]
  Test_train_df = Test_train_df[Test_train_df['player_id'] != 0]

  training_df = pd.concat([T20_train_df,ODI_train_df,Test_train_df])
  return training_df


def add_rolling_averages(df, columns, *window_sizes):
    """
    Adds new columns to the dataframe for rolling averages of the given columns over specified window sizes,
    excluding the current match in the calculation.

    Parameters:
        df (pd.DataFrame): The dataframe to modify.
        columns (list): List of column names to compute rolling averages on.
        *window_sizes: Variable number of window sizes to compute rolling averages.

    Returns:
        pd.DataFrame: The dataframe with added rolling average columns.
    """
    for column in columns:
        for window in window_sizes:
            new_col_name = f"avg_{column}_last_{window}_matches"
            # Use shift(1) to exclude the current match and calculate rolling mean
            df[new_col_name] = (
                df[column].shift(1)  # Exclude the current match
                .rolling(window=window, min_periods=1)  # Rolling window
                .mean()  # Calculate mean
            )
    return df

def convert_to_match_data(player_summary_dfs, df) :
    match_df = df.groupby('filename').agg({
        'date_playing': 'first',
        'League': 'first',
        'team1': 'first',
        'team2': 'first',
        'stadium': 'first',
        'team1.player_id': 'first',
        'team2.player_id': 'first'
    }).reset_index()

    match_df['match_id'] = match_df['filename'].apply(lambda x: x[:-5])
    match_df['match_id'] = match_df['filename'].apply(lambda x: x[:-5]).str.rsplit('/', n=1).str[-1]
    match_df = match_df.drop(columns=['filename'])

    # Apply the function to calculate team1_total_points
    match_df['team1_total_points'] = match_df.apply(
        lambda row: calculate_team_total_points(row['team1.player_id'].split(','), row['match_id'], player_summary_dfs), axis=1)

    # Apply the function to calculate team2_total_points
    match_df['team2_total_points'] = match_df.apply(
        lambda row: calculate_team_total_points(row['team2.player_id'].split(','), row['match_id'], player_summary_dfs), axis=1)

    # Apply the function to calculate dream_points
    match_df['dream_points'] = match_df.apply(lambda row: calculate_dream_points(row, player_summary_dfs), axis=1)
    # match_df = match_df.drop(columns=['team1.player_id', 'team2.player_id'])

    match_df['date_playing'] = pd.to_datetime(match_df['date_playing'])

    # Add columns for last i matches for team1 and team2
    for i in [1, 2, 3, 4, 5, 10, 15]:
        match_df[f'avg_points_team1_last_{i}_matches'] = calculate_avg_points(
            match_df, 'team1', 'team1_total_points', i
        )
        match_df[f'avg_points_team2_last_{i}_matches'] = calculate_avg_points(
            match_df, 'team2', 'team2_total_points', i
        )

    # Add overall average points columns for team1 and team2
    match_df['avg_points_team1'] = calculate_avg_points(match_df, 'team1', 'team1_total_points', len(match_df))
    match_df['avg_points_team2'] = calculate_avg_points(match_df, 'team2', 'team2_total_points', len(match_df))
    match_df = match_df.drop(columns=['team1_total_points', 'team2_total_points'])

    # Add columns for last i matches at the venue
    for i in [1, 2, 3, 4, 5, 10, 15]:
        match_df[f'avg_points_venue_last_{i}_matches'] = calculate_avg_points_venue(
            match_df, 'stadium', 'dream_points', i
        )

    # Add overall average points at the venue
    match_df['avg_points_venue'] = calculate_avg_points_venue(
        match_df, 'stadium', 'dream_points', len(match_df)
    )

    # Add columns for last i matches at the League
    for i in [1, 2, 3, 4, 5, 10, 15]:
        match_df[f'avg_points_League_last_{i}_matches'] = calculate_avg_points_League(
            match_df, 'League', 'dream_points', i
        )

    # Add overall average points at the League
    match_df['avg_points_League'] = calculate_avg_points_League(
        match_df, 'League', 'dream_points', len(match_df)
    )

    # Duplicate the original DataFrame
    swapped_df = match_df.copy()

    # Identify columns to swap
    team1_columns = [col for col in match_df.columns if 'team1' in col and 'avg_points' in col]
    team2_columns = [col.replace('team1', 'team2') for col in team1_columns]


    # Swap the values of the team1 and team2 columns
    for col1, col2 in zip(team1_columns, team2_columns):
        swapped_df[col1], swapped_df[col2] = match_df[col2], match_df[col1]

    # Concatenate the original and swapped DataFrames
    match_df = pd.concat([match_df, swapped_df], ignore_index=True)
    match_df = match_df.sort_values(by="date_playing")

    return match_df


def calculate_team_total_points(player_ids, match_id, player_summary_dfs):
    total_points = 0
    for player_id in player_ids:
        if player_id in player_summary_dfs:
            player_df = player_summary_dfs[player_id]
            points = player_df[player_df['match_id'] == match_id]['total_points'].sum()
            total_points += points
    return total_points

def calculate_dream_points(row, player_summary_dfs):
    team1_players = row['team1.player_id'].split(',')
    team2_players = row['team2.player_id'].split(',')
    all_points = []

    # Collect points for team1 players
    for player_id in team1_players:
        if player_id in player_summary_dfs:
            player_df = player_summary_dfs[player_id]
            points = player_df[player_df['match_id'] == row['match_id']]['total_points'].sum()
            all_points.append(points)

    # Collect points for team2 players
    for player_id in team2_players:
        if player_id in player_summary_dfs:
            player_df = player_summary_dfs[player_id]
            points = player_df[player_df['match_id'] == row['match_id']]['total_points'].sum()
            all_points.append(points)

    # Get the top 11 points and sum them
    top_11_points = sorted(all_points, reverse=True)[:11]
    return sum(top_11_points)

# Function to calculate average points for the last i matches
def calculate_avg_points(df, team_col, points_col, i):
    avg_points = []
    for index, row in df.iterrows():
        team = row[team_col]
        current_date = row['date_playing']

        # Filter past matches for the team
        past_matches = df[
            (df['date_playing'] < current_date) &
            ((df['team1'] == team) | (df['team2'] == team))
        ].sort_values('date_playing', ascending=False)

        # Get the last i matches
        past_matches = past_matches.head(i)

        # Calculate the total points scored by the team
        total_points = 0
        for _, match in past_matches.iterrows():
            if match['team1'] == team:
                total_points += match['team1_total_points']
            elif match['team2'] == team:
                total_points += match['team2_total_points']

        # Calculate the average points
        avg_points.append(total_points / len(past_matches) if not past_matches.empty else 0)

    return avg_points

# Function to calculate average points at a specific venue for the last i matches
def calculate_avg_points_venue(df, stadium_col, points_col, i):
    avg_points = []
    for index, row in df.iterrows():
        venue = row[stadium_col]
        current_date = row['date_playing']

        # Filter past matches at the same venue
        past_matches = df[
            (df['date_playing'] < current_date) &
            (df['stadium'] == venue)
        ].sort_values('date_playing', ascending=False)

        # Get the last i matches
        past_matches = past_matches.head(i)

        # Calculate the total points in those matches
        total_points = past_matches[points_col].sum()

        # Calculate the average points
        avg_points.append(total_points / len(past_matches) if not past_matches.empty else 0)

    return avg_points

# Function to calculate average points at a specific League for the last i matches
def calculate_avg_points_League(df, League_col, points_col, i):
    avg_points = []
    for index, row in df.iterrows():
        League = row[League_col]
        current_date = row['date_playing']

        # Filter past matches at the same League
        past_matches = df[
            (df['date_playing'] < current_date) &
            (df['League'] == League)
        ].sort_values('date_playing', ascending=False)

        # Get the last i matches
        past_matches = past_matches.head(i)

        # Calculate the total points in those matches
        total_points = past_matches[points_col].sum()

        # Calculate the average points
        avg_points.append(total_points / len(past_matches) if not past_matches.empty else 0)

    return avg_points

def convert_to_player_summary_df(df, format):
    player_summary = defaultdict(lambda: defaultdict(lambda: {
        "match_id": None,
        "team": None,
        "total_runs_made": 0,
        "total_balls_faced": 0,
        "total_runs_given": 0,
        "total_balls_bowled": 0,
        "total_sixes": 0,
        "total_fours": 0,
        "total_extras": 0,
        "total_wickets": 0,
        "lbw_wickets": 0,
        "bowled_wickets": 0,
        "total_extras": 0,
        "maidens": 0,
        "catches": 0,
        "runouts": 0,
        "stadium": None,
        "dates": None,
        "date_playing": None,
        "league": None,
        "match_type": None,
        "gender": None
    }))

    i1 = 0
    s2 = {set}
    run_over = 0
    # Iterate through the DataFrame rows
    for _, row in df.iterrows():
        i1+=1
        if i1%100000 == 0 :
          print(i1)
        # Extract information
        match_id = row['filename'][:-5]
        match_id = match_id.rsplit('/', 1)[-1]
        batter = row['batsman_id']
        bowler = row['bowler_id']
        batting_team = row['inning_team']
        bowling_team = row['team2'] if row['team1'] == batting_team else row['team1']
        catch_fielders = row['catch_fielder'] if pd.notna(row['catch_fielder']) else []
        catch_fielders = ast.literal_eval(catch_fielders)
        # print(type(catch_fielders))
        runout_fielders = row['runout_fielder'] if pd.notna(row['runout_fielder']) else []
        runout_fielders = ast.literal_eval(runout_fielders)
        # runout_fielders = row['runout_fielder']
        run_over += row['runs.total']
        # if match_id == '1359524' and batter == 'ba607b88':
        #   print(f"{bowler} {row['wicket.kind']} {i1}")

        # Update batter stats
        player_summary[batter][match_id]["match_id"] = match_id
        player_summary[batter][match_id]["team"] = batting_team
        player_summary[batter][match_id]["total_runs_made"] += row['runs.batter']
        player_summary[batter][match_id]["total_sixes"] += row['boundary_6']
        player_summary[batter][match_id]["total_fours"] += row['boundary_4']
        player_summary[batter][match_id]["total_balls_faced"] += 1
        player_summary[batter][match_id]["stadium"] = row['stadium']
        player_summary[batter][match_id]["dates"] = row['dates']
        player_summary[batter][match_id]["date_playing"] = row['date_playing']
        player_summary[batter][match_id]["league"] = row['League']
        player_summary[batter][match_id]["match_type"] = row['Match_type']
        player_summary[batter][match_id]["gender"] = row['Gender']

        # Update bowler stats
        player_summary[bowler][match_id]["match_id"] = match_id
        player_summary[bowler][match_id]["team"] = bowling_team
        player_summary[bowler][match_id]["total_wickets"] += 1 if row['wicket.kind'] == "caught" or row['wicket.kind'] == "stumped" or row['wicket.kind'] == "bowled" or row['wicket.kind'] == "lbw" or row['wicket.kind'] == "caught and bowled" or row['wicket.kind'] == "hit wicket" else 0
        player_summary[bowler][match_id]["lbw_wickets"] += 1 if row['wicket.kind'] == "lbw" else 0
        player_summary[bowler][match_id]["bowled_wickets"] += 1 if row['wicket.kind'] == "bowled" else 0
        player_summary[bowler][match_id]["total_runs_given"] += row['runs.batter'] + row['extras.wides'] + row['extras.noballs']
        player_summary[bowler][match_id]["total_extras"] += row['extras.wides'] + row['extras.noballs']
        player_summary[bowler][match_id]["total_balls_bowled"] += 1
        player_summary[bowler][match_id]["stadium"] = row['stadium']
        player_summary[bowler][match_id]["dates"] = row['dates']
        player_summary[bowler][match_id]["date_playing"] = row['date_playing']
        player_summary[bowler][match_id]["league"] = row['League']
        player_summary[bowler][match_id]["match_type"] = row['Match_type']
        player_summary[bowler][match_id]["gender"] = row['Gender']
        if i1==len(df) :
          player_summary[bowler][match_id]["maidens"] += 1 if run_over == 0 else 0
        else :
          if df.iloc[i1]['bowl_number']==float('nan') and int(row['bowl_number']) != int(df.iloc[i1]['bowl_number']) :
            player_summary[bowler][match_id]["maidens"] += 1 if run_over == 0 else 0
            run_over = 0

        # Update fielder stats
        for fielder in catch_fielders :
            print(fielder)
            player_summary[fielder][match_id]["match_id"] = match_id
            player_summary[fielder][match_id]["team"] = bowling_team
            player_summary[fielder][match_id]["stadium"] = row['stadium']
            player_summary[fielder][match_id]["dates"] = row['dates']
            player_summary[fielder][match_id]["date_playing"] = row['date_playing']
            player_summary[fielder][match_id]["league"] = row['League']
            player_summary[fielder][match_id]["match_type"] = row['Match_type']
            player_summary[fielder][match_id]["gender"] = row['Gender']
            player_summary[fielder][match_id]["catches"] += 1

        for fielder in runout_fielders :
            print(fielder)
            player_summary[fielder][match_id]["match_id"] = match_id
            player_summary[fielder][match_id]["team"] = bowling_team
            player_summary[fielder][match_id]["stadium"] = row['stadium']
            player_summary[fielder][match_id]["dates"] = row['dates']
            player_summary[fielder][match_id]["date_playing"] = row['date_playing']
            player_summary[fielder][match_id]["league"] = row['League']
            player_summary[fielder][match_id]["match_type"] = row['Match_type']
            player_summary[fielder][match_id]["gender"] = row['Gender']
            if len(runout_fielders) == 1:
                player_summary[fielder][match_id]["runouts"] += 1
            else:
                player_summary[fielder][match_id]["runouts"] += 0.5

    player_summary_dfs = {
        player_id: pd.DataFrame.from_dict(stats, orient="index").reset_index(drop=True)
        for player_id, stats in player_summary.items()
    }

    for player_id, df_temp in player_summary_dfs.items():
        class_name = f"Dream11Points_{format}"
        config_file = globals()[f"{format}_pointsconfig"]
        dream11 = globals()[class_name](player_scorecard=df_temp, pointsconfig=config_file)
        dream11.get_batsmen_bowler_points()

    return player_summary_dfs

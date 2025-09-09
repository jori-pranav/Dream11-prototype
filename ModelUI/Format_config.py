from common import *


class Dream11Points_T20:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 10,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 50, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 60, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 70, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 170, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] >= 150, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] >= 130, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      self.player_scorecard['economy_rate'] = np.where(
            (self.player_scorecard['total_balls_bowled'] > 0),
            np.divide(
                self.player_scorecard['total_runs_given'],
                self.player_scorecard['total_balls_bowled']
            ) * 6,
            np.nan
      )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 5, self.pointsconfig['W1'],
          np.where(self.player_scorecard['total_wickets'] >= 4, self.pointsconfig['W2'],
                  np.where(self.player_scorecard['total_wickets'] >= 3, self.pointsconfig['W3'], 0))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 12,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 12, self.pointsconfig['E6'],
              np.where(self.player_scorecard['economy_rate'] > 11, self.pointsconfig['E5'],
                      np.where(self.player_scorecard['economy_rate'] >= 10, self.pointsconfig['E4'],
                                np.where(self.player_scorecard['economy_rate'] <= 5, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] <= 6, self.pointsconfig['E2'],
                                                  np.where(self.player_scorecard['economy_rate'] <= 7, self.pointsconfig['E3'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return
    
class Dream11Points_ODI:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 20,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 30, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 40, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 50, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 140, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] >= 120, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] >= 100, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      self.player_scorecard['economy_rate'] = np.where(
            (self.player_scorecard['total_balls_bowled'] > 0),
            np.divide(
                self.player_scorecard['total_runs_given'],
                self.player_scorecard['total_balls_bowled']
            ) * 6,
            np.nan
      )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 4, self.pointsconfig['W1'],
          np.where(self.player_scorecard['total_wickets'] >= 5, self.pointsconfig['W2'],
                  np.where(self.player_scorecard['total_wickets'] >= 3, self.pointsconfig['W3'], 0))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 30,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 9, self.pointsconfig['E7'],
              np.where(self.player_scorecard['economy_rate'] > 8, self.pointsconfig['E6'],
                      np.where(self.player_scorecard['economy_rate'] >= 7, self.pointsconfig['E5'],
                                np.where(self.player_scorecard['economy_rate'] <= 2.5, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] < 3.5, self.pointsconfig['E3'],
                                                  np.where(self.player_scorecard['economy_rate'] <= 4.5, self.pointsconfig['E4'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return
    
class Dream11Points_test:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 20,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 30, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 40, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 50, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 140, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] >= 120, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] >= 100, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      self.player_scorecard['economy_rate'] = np.where(
            (self.player_scorecard['total_balls_bowled'] > 0),
            np.divide(
                self.player_scorecard['total_runs_given'],
                self.player_scorecard['total_balls_bowled']
            ) * 6,
            np.nan
      )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 4, self.pointsconfig['W1'],
          np.where(self.player_scorecard['total_wickets'] >= 5, self.pointsconfig['W2'],
                  np.where(self.player_scorecard['total_wickets'] >= 3, self.pointsconfig['W3'], 0))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 30,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 9, self.pointsconfig['E7'],
              np.where(self.player_scorecard['economy_rate'] > 8, self.pointsconfig['E6'],
                      np.where(self.player_scorecard['economy_rate'] >= 7, self.pointsconfig['E5'],
                                np.where(self.player_scorecard['economy_rate'] <= 2.5, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] <= 3.5, self.pointsconfig['E3'],
                                                  np.where(self.player_scorecard['economy_rate'] <= 4.5, self.pointsconfig['E4'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return

class Dream11Points_test:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 20,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 30, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 40, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 50, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 140, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] >= 120, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] >= 100, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      self.player_scorecard['economy_rate'] = np.where(
            (self.player_scorecard['total_balls_bowled'] > 0),
            np.divide(
                self.player_scorecard['total_runs_given'],
                self.player_scorecard['total_balls_bowled']
            ) * 6,
            np.nan
      )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 4, self.pointsconfig['W1'],
          np.where(self.player_scorecard['total_wickets'] >= 5, self.pointsconfig['W2'],
                  np.where(self.player_scorecard['total_wickets'] >= 3, self.pointsconfig['W3'], 0))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 30,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 9, self.pointsconfig['E7'],
              np.where(self.player_scorecard['economy_rate'] > 8, self.pointsconfig['E6'],
                      np.where(self.player_scorecard['economy_rate'] >= 7, self.pointsconfig['E5'],
                                np.where(self.player_scorecard['economy_rate'] <= 2.5, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] <= 3.5, self.pointsconfig['E3'],
                                                  np.where(self.player_scorecard['economy_rate'] <= 4.5, self.pointsconfig['E4'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return
    
class Dream11Points_T10:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 5,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 60, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 70, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 80, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 190, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] > 170, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] > 150, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      self.player_scorecard['economy_rate'] = np.where(
            (self.player_scorecard['total_balls_bowled'] > 0),
            np.divide(
                self.player_scorecard['total_runs_given'],
                self.player_scorecard['total_balls_bowled']
            ) * 6,
            np.nan
      )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 2, self.pointsconfig['W1'],
          np.where(self.player_scorecard['total_wickets'] >=3, self.pointsconfig['W2'],
                  np.where(self.player_scorecard['total_wickets'] >= 3, self.pointsconfig['W3'], 0))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 6,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 16, self.pointsconfig['E7'],
              np.where(self.player_scorecard['economy_rate'] > 15, self.pointsconfig['E6'],
                      np.where(self.player_scorecard['economy_rate'] > 14, self.pointsconfig['E5'],
                                np.where(self.player_scorecard['economy_rate'] < 7, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] < 8, self.pointsconfig['E3'],
                                                  np.where(self.player_scorecard['economy_rate'] < 9, self.pointsconfig['E4'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return
    
class Dream11Points_Sixty:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 5,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 60, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 70, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 80, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 190, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] > 170, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] > 150, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      self.player_scorecard['economy_rate'] = np.where(
            (self.player_scorecard['total_balls_bowled'] > 0),
            np.divide(
                self.player_scorecard['total_runs_given'],
                self.player_scorecard['total_balls_bowled']
            ) * 6,
            np.nan
      )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 2, self.pointsconfig['W1'],
          np.where(self.player_scorecard['total_wickets'] >=3, self.pointsconfig['W2'],
                  np.where(self.player_scorecard['total_wickets'] >= 3, self.pointsconfig['W3'], 0))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 6,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 16, self.pointsconfig['E7'],
              np.where(self.player_scorecard['economy_rate'] > 15, self.pointsconfig['E6'],
                      np.where(self.player_scorecard['economy_rate'] > 14, self.pointsconfig['E5'],
                                np.where(self.player_scorecard['economy_rate'] < 7, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] < 8, self.pointsconfig['E3'],
                                                  np.where(self.player_scorecard['economy_rate'] < 9, self.pointsconfig['E4'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return
    
class Dream11Points_The_hundred:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 5,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 60, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 70, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 80, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 190, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] > 170, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] > 150, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      self.player_scorecard['economy_rate'] = np.where(
            (self.player_scorecard['total_balls_bowled'] > 0),
            np.divide(
                self.player_scorecard['total_runs_given'],
                self.player_scorecard['total_balls_bowled']
            ) * 6,
            np.nan
      )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 5, self.pointsconfig['W4'],
          np.where(self.player_scorecard['total_wickets'] >=4, self.pointsconfig['W3'],
                  np.where(self.player_scorecard['total_wickets'] >= 3, self.pointsconfig['W2'],
                           np.where(self.player_scorecard['total_wickets'] >= 2, self.pointsconfig['W1'],)))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 6,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 16, self.pointsconfig['E7'],
              np.where(self.player_scorecard['economy_rate'] > 15, self.pointsconfig['E6'],
                      np.where(self.player_scorecard['economy_rate'] > 14, self.pointsconfig['E5'],
                                np.where(self.player_scorecard['economy_rate'] < 7, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] < 8, self.pointsconfig['E3'],
                                                  np.where(self.player_scorecard['economy_rate'] < 9, self.pointsconfig['E4'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return

class Dream11Points_other_T20:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 10,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 50, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 60, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 70, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 170, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] > 150, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] > 130, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      self.player_scorecard['economy_rate'] = np.where(
            (self.player_scorecard['total_balls_bowled'] > 0),
            np.divide(
                self.player_scorecard['total_runs_given'],
                self.player_scorecard['total_balls_bowled']
            ) * 6,
            np.nan
      )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 3, self.pointsconfig['W1'],
          np.where(self.player_scorecard['total_wickets'] >=4, self.pointsconfig['W2'],
                  np.where(self.player_scorecard['total_wickets'] >= 5, self.pointsconfig['W3'], 0))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 12,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 12, self.pointsconfig['E7'],
              np.where(self.player_scorecard['economy_rate'] > 11, self.pointsconfig['E6'],
                      np.where(self.player_scorecard['economy_rate'] > 10, self.pointsconfig['E5'],
                                np.where(self.player_scorecard['economy_rate'] < 5, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] < 6, self.pointsconfig['E3'],
                                                  np.where(self.player_scorecard['economy_rate'] < 7, self.pointsconfig['E4'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return
    

class Dream11Points_other_OD:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 20,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 30, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 40, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 50, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 140, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] > 120, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] > 100, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      self.player_scorecard['economy_rate'] = np.where(
            (self.player_scorecard['total_balls_bowled'] > 0),
            np.divide(
                self.player_scorecard['total_runs_given'],
                self.player_scorecard['total_balls_bowled']
            ) * 6,
            np.nan
      )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 4, self.pointsconfig['W1'],
          np.where(self.player_scorecard['total_wickets'] >=5, self.pointsconfig['W2'],
                  np.where(self.player_scorecard['total_wickets'] >= 5, self.pointsconfig['W3'], 0))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 30,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 9, self.pointsconfig['E7'],
              np.where(self.player_scorecard['economy_rate'] > 8, self.pointsconfig['E6'],
                      np.where(self.player_scorecard['economy_rate'] > 7, self.pointsconfig['E5'],
                                np.where(self.player_scorecard['economy_rate'] < 2.5, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] < 3.5, self.pointsconfig['E3'],
                                                  np.where(self.player_scorecard['economy_rate'] < 4.5, self.pointsconfig['E4'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return
    
class Dream11Points_other_test:

    def __init__(self, player_scorecard, pointsconfig):
        self.player_scorecard = player_scorecard
        self.pointsconfig = pointsconfig

        return
    """
    Calculates batting points including strike rate-related fantasy points.
    pointsconfig: dictionary with points per score type as per Dream11.
    :return: None
    """
    def get_batting_points(self) -> None:
      self.player_scorecard['total_runs_points'] = self.player_scorecard['total_runs_made'] * self.pointsconfig['total_runs']
      self.player_scorecard['run_6_points'] = self.pointsconfig['run_6'] * self.player_scorecard['total_sixes']
      self.player_scorecard['run_4_points'] = self.pointsconfig['run_4'] * self.player_scorecard['total_fours']

      # Run bonuses
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] == 0, self.pointsconfig['duck'], 0)
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 30,
          self.pointsconfig['>=30'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 50,
          self.pointsconfig['>=50'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )
      self.player_scorecard['run_bonus_points'] = np.where(
          self.player_scorecard['total_runs_made'] >= 100,
          self.pointsconfig['>=100'] + self.player_scorecard['run_bonus_points'],
          self.player_scorecard['run_bonus_points']
      )

      # Strike rate calculation
      self.player_scorecard['strike_rate'] = np.where(
            (self.player_scorecard['total_balls_faced'] > 0),
            np.divide(
                self.player_scorecard['total_runs_made'],
                self.player_scorecard['total_balls_faced']
            ) * 6,
            np.nan
      )
      self.player_scorecard['strike_rate_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 20,  # Apply only if balls faced >= 10
          np.where(
              self.player_scorecard['strike_rate'] < 30, self.pointsconfig['S1'],
              np.where(
                  self.player_scorecard['strike_rate'] < 40, self.pointsconfig['S2'],
                  np.where(
                      self.player_scorecard['strike_rate'] < 50, self.pointsconfig['S3'],
                      np.where(
                          self.player_scorecard['strike_rate'] >= 140, self.pointsconfig['S6'],
                          np.where(
                              self.player_scorecard['strike_rate'] > 120, self.pointsconfig['S5'],
                              np.where(self.player_scorecard['strike_rate'] > 100, self.pointsconfig['S4'], 0)
                          )
                      )
                  )
              )
          ), 0
      )

      # Calculate total batting points
      self.player_scorecard['total_bat_points'] = (
          self.player_scorecard['total_runs_points']
          .add(self.player_scorecard['run_6_points'], fill_value=0)
          .add(self.player_scorecard['run_4_points'], fill_value=0)
          .add(self.player_scorecard['run_bonus_points'], fill_value=0)
          .add(self.player_scorecard['strike_rate_points'], fill_value=0)
      )
      self.player_scorecard['total_bat_points'] = np.where(
          self.player_scorecard['total_balls_faced'] >= 1,
          self.player_scorecard['total_bat_points'],
          np.nan
      )

      return

    def get_bowling_points(self) -> None:

      def get_bowling_points(self) -> None:

        self.player_scorecard['economy_rate'] = np.where(
                (self.player_scorecard['total_balls_bowled'] > 0),
                np.divide(
                    self.player_scorecard['total_runs_given'],
                    self.player_scorecard['total_balls_bowled']
                ) * 6,
                np.nan
        )

      # Points for total wickets
      self.player_scorecard['total_wickets_points'] = (
          self.pointsconfig['total_wickets'] * self.player_scorecard['total_wickets']
      )

      # Bonus for lbw or bowled dismissals
      self.player_scorecard['lbw_bowled_bonus_points'] = (
          self.pointsconfig['lbw/bowled_bonus'] * (self.player_scorecard['lbw_wickets'] + self.player_scorecard['bowled_wickets'] )
      )

      # Wicket bonus points
      self.player_scorecard['wicket_bonus_points'] = np.where(
          self.player_scorecard['total_wickets'] >= 4, self.pointsconfig['W1'],
          np.where(self.player_scorecard['total_wickets'] >=5, self.pointsconfig['W2'],
                  np.where(self.player_scorecard['total_wickets'] >= 5, self.pointsconfig['W3'], 0))
      )

      # Economy rate points (only for bowlers with at least 2 overs bowled)
      self.player_scorecard['economy_rate_points'] = np.where(
          self.player_scorecard['total_balls_bowled'] >= 30,  # Minimum 2 overs = 12 balls
          np.where(
              self.player_scorecard['economy_rate'] > 9, self.pointsconfig['E7'],
              np.where(self.player_scorecard['economy_rate'] > 8, self.pointsconfig['E6'],
                      np.where(self.player_scorecard['economy_rate'] > 7, self.pointsconfig['E5'],
                                np.where(self.player_scorecard['economy_rate'] < 2.5, self.pointsconfig['E1'],
                                        np.where(self.player_scorecard['economy_rate'] < 3.5, self.pointsconfig['E3'],
                                                  np.where(self.player_scorecard['economy_rate'] < 4.5, self.pointsconfig['E4'], 0))))))
          ,
          0  # No points if less than 2 overs bowled
      )

      # Points for maiden overs
      self.player_scorecard['maiden_overs_points'] = (
          self.pointsconfig['maiden_overs'] * self.player_scorecard['maidens']
      )

      # Total bowling points
      self.player_scorecard['total_bowl_points'] = (
          self.player_scorecard['total_wickets_points']
          + self.player_scorecard['lbw_bowled_bonus_points']
          + self.player_scorecard['wicket_bonus_points']
          + self.player_scorecard['economy_rate_points']
          # + self.player_scorecard['maiden_overs_points']
      )



      return
    def get_fielding_points(self) -> None:
      """
      Calculate fielding points based on the configured points system.
      """
      # Points for total catches
      self.player_scorecard['total_catches'] = (
          self.pointsconfig['total_catches'] * self.player_scorecard['catches']
      )

      # Bonus for 3 or more catches
      self.player_scorecard['catch_bonus_points'] = np.where(
          self.player_scorecard['catches'] >= 3,
          self.pointsconfig['C1'],
          0
      )

      # Points for run-outs (direct)
      self.player_scorecard['run_outs_points'] = (
          self.pointsconfig['run_out_bonus_direct'] * self.player_scorecard['runouts']
      )

    # Total fielding points
      self.player_scorecard['total_fielding_points'] = (
          self.player_scorecard['total_catches']
          + self.player_scorecard['catch_bonus_points']
          # + self.player_scorecard['stumping_points']
          + self.player_scorecard['run_outs_points']
          # + self.player_scorecard['run_out_indirect_points']
      )

      return



    def get_batsmen_bowler_points(self):
        self.get_batting_points()
        self.get_bowling_points()
        self.get_fielding_points()
        self.player_scorecard['total_points'] = self.player_scorecard['total_fielding_points'].add(self.player_scorecard['total_bat_points'].add(self.player_scorecard['total_bowl_points'], fill_value=0))
        return
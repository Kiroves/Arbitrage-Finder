import pandas as pd
from fuzzywuzzy import fuzz
from bisect import bisect_left

# create a new DataFrame to store arbitrage opportunities
arbitrage_df = pd.DataFrame(columns=['website1', 'website2', 'home','away','home_odds', 'draw_odds', 'away_odds', 'arbitrage_percentage'])

# build the arbitrage_df from the matched rows
def build_arbitrage_df(row):
    global arbitrage_df
    combinations = [1/row['home_odds1'] + 1/row['draw_odds1'] + 1/row['away_odds1'],
                    1/row['home_odds1'] + 1/row['draw_odds1'] + 1/row['away_odds2'],
                    1/row['home_odds1'] + 1/row['draw_odds2'] + 1/row['away_odds1'],
                    1/row['home_odds1'] + 1/row['draw_odds2'] + 1/row['away_odds2'],
                    1/row['home_odds2'] + 1/row['draw_odds1'] + 1/row['away_odds1'],
                    1/row['home_odds2'] + 1/row['draw_odds1'] + 1/row['away_odds2'],
                    1/row['home_odds2'] + 1/row['draw_odds2'] + 1/row['away_odds1'],
                    1/row['home_odds2'] + 1/row['draw_odds2'] + 1/row['away_odds2']]
    
    min_value = min(combinations)
    min_index = combinations.index(min_value)
    
    if min_value >= 1:
        return row
    
    if min_index < 4:
        home_odds = str(row['website1']) + '-' + str(row['home_odds1'])
    else:
        home_odds = str(row['website2']) + '-' + str(row['home_odds2'])
                
    match min_index:
        case 0 | 4:
            draw_odds = str(row['website1']) + '-' + str(row['draw_odds1'])
            away_odds = str(row['website1']) + '-' + str(row['away_odds1'])
        case 1 | 5:
            draw_odds = str(row['website1']) + '-' + str(row['draw_odds1'])
            away_odds = str(row['website2']) + '-' + str(row['away_odds2'])
        case 2 | 6:
            draw_odds = str(row['website2']) + '-' + str(row['draw_odds2'])
            away_odds = str(row['website1']) + '-' + str(row['away_odds1'])
        case _:
            draw_odds = str(row['website2']) + '-' + str(row['draw_odds2'])
            away_odds = str(row['website2']) + '-' + str(row['away_odds2'])
        
    arbitrage_percent = (1 - combinations[min_index]) * 100
    
    new_row = pd.Series({'website1': row['website1'], 'website2': row['website2'], 
                             'home': row['home'], 'away': row['away'], 
                             'home_odds': home_odds,
                             'draw_odds': draw_odds,
                             'away_odds': away_odds,
                             'arbitrage_percentage': arbitrage_percent})
    arbitrage_df = pd.concat([arbitrage_df, new_row.to_frame().T], ignore_index=True)
    return row

def find():
    # import pickle files
    df_ladbrokes = pd.read_pickle("./scrapers/ladbrokes.pickle")
    df_unibet = pd.read_pickle("./scrapers/unibet.pickle")
    df_tonybet = pd.read_pickle("./scrapers/tonybet.pickle")


    # array of DataFrames we have 
    dataframes = [df_ladbrokes, df_unibet, df_tonybet]

    # sort the DataFrames by the home column
    sorted_dataframes = [df.sort_values('home') for df in dataframes]

    # initialize matched games
    matched_games = []

    # iterate through each DataFrame
    for i, df in enumerate(sorted_dataframes):
        # iterate through each row in the DataFrame
        for index, row in df.iterrows():
            home_team = row['home']
            away_team = row['away']
            match_date = row['date']  

            # perform binary search in the other sorted DataFrames
            for other_df in sorted_dataframes[i + 1:]:
                home_team_values = other_df['home'].values
                away_team_values = other_df['away'].values
                other_date_values = other_df['date'].values

                # perform binary search on the 'home' column
                home_index = bisect_left(home_team_values, home_team)
                if (home_index < len(home_team_values)
                    and fuzz.ratio(home_team_values[home_index], home_team) > 60
                    and fuzz.ratio(away_team_values[home_index], away_team) > 60
                    and other_date_values[home_index] == match_date):
                    # get the matched game details from the other DataFrame
                    matched_game = other_df.iloc[home_index]

                    # extract the odds columns from both rows
                    home_odds1, draw_odds1, away_odds1, website1 = row['home_odds'], row['draw_odds'], row['away_odds'], row['website']
                    home_odds2, draw_odds2, away_odds2, website2 = matched_game['home_odds'], matched_game['draw_odds'], matched_game['away_odds'], matched_game['website']

                    # create a new row with the matched game details
                    matched_row = pd.Series([website1, website2, home_team, away_team, home_odds1, draw_odds1, away_odds1, home_odds2, draw_odds2, away_odds2],
                                                index=['website1', 'website2','home', 'away', 'home_odds1', 'draw_odds1', 'away_odds1', 'home_odds2', 'draw_odds2', 'away_odds2'])

                    # append the matched row to the matched games list
                    matched_games.append(matched_row)

    # concatenate all the matched game rows into a single DataFrame
    matched_games_df = pd.concat(matched_games, axis=1).T

    # reset the index of the matched games DataFrame
    matched_games_df.reset_index(drop=True, inplace=True)

    # convert relevant columns to numeric values
    cols_to_convert = ['home_odds1', 'draw_odds1', 'away_odds1', 'home_odds2', 'draw_odds2', 'away_odds2']
    matched_games_df[cols_to_convert] = matched_games_df[cols_to_convert].apply(pd.to_numeric)


    # build the arbitrage_df by filtering rows from matched games into it
    matched_games_df.apply(build_arbitrage_df, axis=1)
    arbitrage_df.reset_index(drop=True, inplace=True)
    
    return arbitrage_df
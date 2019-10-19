# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:51:38 2019

@author: sebas
"""
from urllib.request import urlopen
import re
import csv
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


COLUMN_NAMES = ['Game_id', 'Period', 'Time', 'Event_num', 'Event_Msg_Type',
                'Option1', 'Distance', 'Top', 'Left', 'Person1', 'Person2', 'Team_id',
                'Aw_Score', 'Hm_Score']

MONTHS = ["october",
          "november",
          "december",
          "january",
          "february",
          "march",
          "april",
          "may"]


def return_action(row, period, score, away, home):
    """
    Returns data that corresponds to the row input and return period and score

    Inputs:

    row - beautifulsoup tag to procees
    period - array-like period of the game
    score - array-like away and home score
    away - away team id
    home - home team id

    Outputs:
    event_msg_type - Type of event
    Team - team performing the action
    player1 - player performing the action
    player1 - secondary player on the play
    option1 - miscellanious information about the play
    """
    columns = row.findAll('td')
    time = columns[0].text

    event_msg_type = ""
    team = ""
    option1 = ""
    player1 = ""
    player2 = ""
    distance = np.nan
    
    #determine team id
    if columns[1].text != '\xa0':
        description = columns[1].text
        team = away
    elif columns[5].text != '\xa0':
        description = columns[5].text
        team = home
    if description == "":
        return time, event_msg_type, team, player1, player2, option1, distance, description
    #determine Event Type and update scores
    if description.split()[0] == 'Jump':
        event_msg_type = '10'
    elif 'free throw' in description or ' no shot' in description:
        event_msg_type = '3'
        if ' makes ' in description:
            option1 = 1
            if team == away:
                score[0] += 1
            else:
                score[1] += 1
        else:
            option1 = 0
    elif ' makes ' in description:
        event_msg_type = '1'
        option1 = re.search('\\d-pt', description).group()[0]
        if team == away:
            score[0] += int(option1)
        else:
            score[1] += int(option1)
        if "at rim" in description:
            distance = 0
        else:
            distance = int(re.search(' from (\d+) ft', description).group(1))
            
    elif ' misses ' in description:
        event_msg_type = '2'
        option1 = re.search('\\d-pt', description).group()[0]
        if "at rim" in description:
            distance = 0
        else:
            distance = int(re.search(' from (\d+) ft', description).group(1))
    elif ' rebound ' in description:
        event_msg_type = '4'
    elif ' turnover ' in description:
        event_msg_type = '5'
    elif ' foul ' in description:
        event_msg_type = '6'
    elif 'Violation' in description:
        event_msg_type = '7'
    elif ' enters ' in description:
        event_msg_type = '8'
    elif 'timeout' in description:
        event_msg_type = '9'
    elif 'ejected' in description:
        event_msg_type = '11'
    elif 'Start of ' in description:
        event_msg_type = '12'
        if description != "Start of 1st quarter":
            period[0] += 1
    else:
        event_msg_type = '13'

    #get player ids
    player1, player2 = get_player_ids(row.findAll('a'))

    #if event_msg_type in ['1','2'] and team == home:
        #print(description)

    return time, event_msg_type, team, player1, player2, option1, distance, description

def get_player_ids(player_tags):
    """Returns the player ids for an event"""
    try:
        tag1 = player_tags[0]
        player1 = str(tag1).split('.html')[0].split('/')[-1]
    except IndexError:
        player1 = ''

    try:
        tag2 = player_tags[1]
        player2 = str(tag2).split('.html')[0].split('/')[-1]
    except IndexError:
        player2 = ''

    return player1, player2


def pbp_to_df(away, home, date):
    """
    Returns the play by play data as a dataframe
    
    Inputs:
    
    away - away team id
    home - home team id
    date - date of the desired game (yyyymmdd)
    
    Output:
    
    df - dataframe containing the play by play data
    """
    #get pbp table
    pbp_quotepage = "https://www.basketball-reference.com/boxscores/pbp/{}0{}.html".format(date, home)
    pbp_page = urlopen(pbp_quotepage)
    pbp_soup = BeautifulSoup(pbp_page, 'html.parser')
    pbp = pbp_soup.find('table', id='pbp')
    pbp_rows = pbp.findAll('tr')

    #get shot chart
    shot_quotepage = "https://www.basketball-reference.com/boxscores/shot-chart/{}0{}.html".format(date, home)
    shot_page = urlopen(shot_quotepage)
    shot_soup = BeautifulSoup(shot_page, 'html.parser')
    away_chart = shot_soup.find('div', id='shots-{}'.format(away))
    home_chart = shot_soup.find('div', id='shots-{}'.format(home))
    away_shot_rows = away_chart.findAll('div')
    home_shot_rows = home_chart.findAll('div')
    
    game_id = "{}-{}-{}".format(away, home, date)
    
    df = pd.DataFrame(columns=COLUMN_NAMES)
    period = [1]
    event_num = 1
    score = [0, 0]
    away_shot_counter = 0
    home_shot_counter = 0

    #print(home_shot_rows)
    
    for row in pbp_rows:
        
        if row.findAll('th'):
            continue
        else:
            time, event_msg_type, team, player1, player2, option1, distance, description = (
                return_action(row, period, score, away, home))

        if (event_msg_type in ['1', '2']) and team == away and int(distance) < 40:
            style = away_shot_rows[away_shot_counter]['style']
            regex = re.search('top:(-?\d+)px;left:(-?\d+)px;', style)
            top, left = max(0, int(regex.group(1))), max(0, int(regex.group(2)))

            away_shot_counter += 1

        elif (event_msg_type in ['1', '2']) and team == home and int(distance) < 40:
            style = home_shot_rows[home_shot_counter]['style']
            regex = re.search('top:(-?\d+)px;left:(-?\d+)px;', style)
            top, left = max(0, int(regex.group(1))), max(0, int(regex.group(2)))

            home_shot_counter += 1

        else:
            top, left = np.nan, np.nan

        
        new_row = [game_id, period[0], time, event_num, event_msg_type,
                   option1, distance, top, left, player1, player2, team,
                   score[0], score[1]]
        
        df.loc[event_num] = new_row
        event_num += 1

    return df


def pbp_to_csv(away, home, date):
    """
    Writes play-by-play data to a comma-separaed values (csv) file
    
    Inputs:
    
    away - away team id
    home - home team id
    date - date of the desired game (yyyymmdd)
    """
    #get pbp table
    pbp_quotepage = "https://www.basketball-reference.com/boxscores/pbp/{}0{}.html".format(date, home)
    pbp_page = urlopen(pbp_quotepage)
    pbp_soup = BeautifulSoup(pbp_page, 'html.parser')
    pbp = pbp_soup.find('table', id='pbp')
    pbp_rows = pbp.findAll('tr')

    #get shot chart
    shot_quotepage = "https://www.basketball-reference.com/boxscores/shot-chart/{}0{}.html".format(date, home)
    shot_page = urlopen(shot_quotepage)
    shot_soup = BeautifulSoup(shot_page, 'html.parser')
    away_chart = shot_soup.find('div', id='shots-{}'.format(away))
    home_chart = shot_soup.find('div', id='shots-{}'.format(home))
    away_shot_rows = away_chart.findAll('div')
    home_shot_rows = home_chart.findAll('div')
    
    game_id = "{}_{}_{}".format(away, home, date)
    
    period = [1]
    event_num = 1
    score = [0, 0]
    away_shot_counter = 0
    home_shot_counter = 0
    
    
    with open('{}.csv'.format(game_id), mode='w', newline='') as game_file:
        game_writer = csv.writer(game_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        game_writer.writerow(COLUMN_NAMES)
    
        for row in pbp_rows:
        
            if row.findAll('th'):
                continue
            else:
                time, event_msg_type, team, player1, player2, option1, distance, description = (
                    return_action(row, period, score, away, home))

            if (event_msg_type in ['1', '2']) and team == away and int(distance) < 40:
                style = away_shot_rows[away_shot_counter]['style']
                regex = re.search('-?top:(\d+)px;left:(-?\d+)px;', style)
                top, left = max(0, int(regex.group(1))), max(0, int(regex.group(2)))

                away_shot_counter += 1

            elif (event_msg_type in ['1', '2']) and team == home and int(distance) < 40:
                style = home_shot_rows[home_shot_counter]['style']
                regex = re.search('top:(-?\d+)px;left:(-?\d+)px;', style)
                top, left = max(0, int(regex.group(1))), max(0, int(regex.group(2)))

                home_shot_counter += 1


            else:
                top, left = np.nan, np.nan
            
            new_row = [game_id, period[0], time, event_num, event_msg_type,
                       option1, distance, top, left, player1, player2, team,
                       score[0], score[1]]
            
            game_writer.writerow(new_row)
            event_num += 1
    
    game_file.close()

def get_season(season):
    """
    Writes an entire season of games to csv files in current directory

    Input:

    season - desired season as a string
    """
    for month in MONTHS:
        quotepage = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(season, month)
        page = urlopen(quotepage)
        soup = BeautifulSoup(page, 'html.parser')
        schedule = soup.find('table', id='schedule')
        rows = schedule.findAll('tr')

        for row in rows:
            if row.find('th').text == "Date":
                continue
            elif row.find('th').text == "Playoffs":
                break
            else:
                away = row.findAll('td')[1]['csk'][:3]
                home = row.find('th')['csk'][-3:]
                date = row.find('th')['csk'][:-4]

                pbp_to_csv(away, home, date)

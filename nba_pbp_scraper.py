# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:51:38 2019

@author: sebas
"""
from urllib.request import urlopen
import re
import csv
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup


COLUMN_NAMES = ['Game_id', 'Period', 'Time', 'Event_num', 'Event_Msg_Type',
                'Option1', 'Person1', 'Person2', 'Team_id', 'Aw_Score', 'Hm_Score']


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

    option1 = ""
    
    #determine team id
    if columns[1].text != '\xa0':
        description = columns[1].text
        team = away
    else:
        description = columns[5].text
        team = home

    #determine Event Type and update scores
    if description.split()[0] == 'Jump':
        event_msg_type = '10'
    elif 'free throw' in description:
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
    elif ' misses ' in description:
        event_msg_type = '2'
        option1 = re.search('\\d-pt', description).group()[0]
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
        period[0] += 1
    else:
        event_msg_type = '13'

    #get player ids
    player1, player2 = get_player_ids(row.findAll('a'))

    return time, event_msg_type, team, player1, player2, option1

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
    start = datetime.now()
    
    quotepage = "https://www.basketball-reference.com/boxscores/pbp/{}0{}.html".format(date, home)
    page = urlopen(quotepage)
    soup = BeautifulSoup(page)
    pbp = soup.find('table', id='pbp')
    rows = pbp.findAll('tr')
    
    game_id = "{}-{}-{}".format(away, home, date)
    
    df = pd.DataFrame(columns=COLUMN_NAMES)
    period = [0]
    event_num = 1
    score = [0, 0]
    
    for row in rows:
        
        if row.findAll('th'):
            continue
        else:
            time, event_msg_type, team, player1, player2, option1 = (
                return_action(row, period, score, home, away))
        
        new_row = [game_id, period[0], time, event_num, event_msg_type,
                   option1, player1, player2, team, score[0], score[1]]
        df.loc[event_num] = new_row
        event_num += 1
    
    print(datetime.now() - start)
    return df


def pbp_to_csv(away, home, date, path):
    """
    Writes play-by-play data to a comma-separaed values (csv) file
    
    Inputs:
    
    away - away team id
    home - home team id
    date - date of the desired game (yyyymmdd)
    path - File path
    """
    start = datetime.now()

    quotepage = "https://www.basketball-reference.com/boxscores/pbp/{}0{}.html".format(date, home)
    page = urlopen(quotepage)
    soup = BeautifulSoup(page)
    pbp = soup.find('table', id='pbp')
    rows = pbp.findAll('tr')
    
    game_id = "{}_{}_{}".format(away, home, date)
    
    period = [0]
    event_num = 1
    score = [0, 0]
    
    
    with open('{}\\{}.csv'.format(path, game_id), mode='w', newline='') as game_file:
        game_writer = csv.writer(game_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        game_writer.writerow(COLUMN_NAMES)
    
        for row in rows:
        
            if row.findAll('th'):
                continue
            else:
                time, event_msg_type, team, player1, player2, option1 = (
                    return_action(row, period, score, home, away))
            
            new_row = [game_id, period[0], time, event_num, event_msg_type,
                       option1, player1, player2, team, score[0], score[1]]
            game_writer.writerow(new_row)
            event_num += 1
    
    game_file.close()
    
    print(datetime.now() - start)

import ffconstants
import requests
import sqlite3
from bs4 import BeautifulSoup

#given a URL and description of the task, return a BeautifulSoup of the website
#e.g. get_soup('https://www.pro-football-reference.com/years/2017/games.htm','getting game list')
#url: URL of the website to return a BeautifulSoup of
#task_name: purpose of html request. Used for providing info in error messages, if there is an error
#return: BeautifulSoup of provided URL, or None if error occurs
def get_soup(url,task_name):
    try:
        html = requests.get(url)
        html.raise_for_status()
    except requests.exceptions.Timeout:
        print('Timeout error while ' + task_name)
        return None
    except requests.exceptions.ConnectionError:
        print('Connection error while ' + task_name)
        return None
    except requests.exceptions.RequestException as e:
        print(e + ' while ' + task_name)
        return None
    return BeautifulSoup(html.text,'lxml')


#given a week in the NFL season, return a list of URLS, each one corresponding
#to the box score of a game from that week
def get_game_urls(week):
    game_urls = []
    game_list_url = ffconstants.PFR_GAME_LIST_URL_FORMAT.format(ffconstants.CURRENT_SEASON_STRING)
    game_list_soup = get_soup(game_list_url,'getting game list')
    if game_list_soup is None:
        return game_urls
    tags_id_all_games = game_list_soup.find_all('div',attrs={'id':'all_games'})
    if len(tags_id_all_games)>0:
         table = tags_id_all_games[0]
    else:
        print('table not found')
        return game_urls
    #Add a row to rows[] if it contains a game, i.e. if it isn't a subheader row
    trs = table.find_all('tr')
    rows = []
    for tr in trs:
        if len(tr.find_all('td'))!=0:
            rows.append(tr)
    for row in rows:
        if row.find_all('th')[0].text==str(week): #the only tag with the 'th' attribute is the week
            tag = row.find_all('td',attrs={'data-stat':'boxscore_word'})[0]
            url = tag.find('a')['href']
            game_urls.append(url)
    return game_urls

def read_boxscores(url):
    box_soup = get_soup(url,"getting boxscore {}".format(url))
    if box_soup is None:
        print("ERROR")
        #return
    #The table's HTML is in a comment for some reason, so it needs to be extracted and turned into a BeautifulSoup object
    table_comment = box_soup.find_all('div',attrs={'id':'wrap'})[0].find_all('div',attrs={'id':'all_player_offense'})[0]
    start = '<!--'
    end = '-->'
    table_soup = BeautifulSoup(str(table_comment).split(start)[1].split(end)[0],'lxml')

    rows = [row for row in table_soup.find_all('tr') if len(row.find_all('th')) == 1]
    #WORK IN PROGRESS


#Initialize the SQLite database and create the necessary tables.
#Return 0 if there is no error; otherwise, print the error and return 1
def initialize_db():
    db = ffconstants.DB
    try:
        conn = sqlite3.connect(db)
        create_qb_allowed = """CREATE TABLE IF NOT EXISTS QBallowed(
            Week real,
            Team text,
            Opp text,
            Pts real,
            PRIMARY KEY(Week,Team)
        );"""
        create_qb_for = """CREATE TABLE IF NOT EXISTS QBfor(
            Week real,
            Team text,
            Opp text,
            Pts real,
            PRIMARY KEY(Week,Team)
        );"""
        create_wr_allowed = """CREATE TABLE IF NOT EXISTS WRallowed(
            Week real,
            Team text,
            Opp text,
            Pts_Std real,
            Pts_PPR real,
            Pts_HPPR real,
            PRIMARY KEY(Week,Team)
        );"""
        create_wr_for = """CREATE TABLE IF NOT EXISTS WRfor(
            Week real,
            Team text,
            Opp text,
            Pts_Std real,
            Pts_PPR real,
            Pts_HPPR real,
            PRIMARY KEY(Week,Team)
        );"""
        create_rb_allowed = """CREATE TABLE IF NOT EXISTS RBallowed(
            Week real,
            Team text,
            Opp text,
            Pts_Std real,
            Pts_PPR real,
            Pts_HPPR real,
            PRIMARY KEY(Week,Team)
        );"""
        create_rb_for = """CREATE TABLE IF NOT EXISTS RBfor(
            Week real,
            Team text,
            Opp text,
            Pts_Std real,
            Pts_PPR real,
            Pts_HPPR real,
            PRIMARY KEY(Week,Team)
        );"""
        create_te_allowed = """CREATE TABLE IF NOT EXISTS TEallowed(
            Week real,
            Team text,
            Opp text,
            Pts_Std real,
            Pts_PPR real,
            Pts_HPPR real,
            PRIMARY KEY(Week,Team)
        );"""
        create_te_for = """CREATE TABLE IF NOT EXISTS TEfor(
            Week real,
            Team text,
            Opp text,
            Pts_Std real,
            Pts_PPR real,
            Pts_HPPR real,
            PRIMARY KEY(Week,Team)
        );"""
        c = conn.cursor()
        c.execute(create_qb_allowed)
        c.execute(create_qb_for)
        c.execute(create_wr_allowed)
        c.execute(create_wr_for)
        c.execute(create_rb_allowed)
        c.execute(create_rb_for)
        c.execute(create_te_allowed)
        c.execute(create_te_for)
        create_cumulative_qb_for = """CREATE TABLE IF NOT EXISTS CumulativeQBfor(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real
        );"""
        create_cumulative_qb_allowed = """CREATE TABLE IF NOT EXISTS CumulativeQBallowed(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        create_cumulative_wr_for = """CREATE TABLE IF NOT EXISTS CumulativeWRfor(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        create_cumulative_wr_allowed = """CREATE TABLE IF NOT EXISTS CumulativeWRallowed(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        create_cumulative_rb_for = """CREATE TABLE IF NOT EXISTS CumulativeRBfor(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        create_cumulative_rb_allowed = """CREATE TABLE IF NOT EXISTS CumulativeRBallowed(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        create_cumulative_te_for = """CREATE TABLE IF NOT EXISTS CumulativeTEfor(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        create_cumulative_te_allowed = """CREATE TABLE IF NOT EXISTS CumulativeTEallowed(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        c.execute(create_cumulative_qb_allowed)
        c.execute(create_cumulative_qb_for)
        c.execute(create_cumulative_wr_allowed)
        c.execute(create_cumulative_wr_for)
        c.execute(create_cumulative_rb_allowed)
        c.execute(create_cumulative_rb_for)
        c.execute(create_cumulative_te_allowed)
        c.execute(create_cumulative_te_for)
        create_adj_cumulative_QBallowed = """CREATE TABLE IF NOT EXISTS AdjCumulativeQBallowed(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        create_adj_cumulative_WRallowed = """CREATE TABLE IF NOT EXISTS AdjCumulativeWRallowed(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        create_adj_cumulative_RBallowed = """CREATE TABLE IF NOT EXISTS AdjCumulativeRBallowed(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        create_adj_cumulative_TEallowed = """CREATE TABLE IF NOT EXISTS AdjCumulativeTEallowed(
            Pastweeks real,
            Team text,
            Mean_Pts real,
            Variance real,
            PRIMARY KEY(Pastweeks,Team)
        );"""
        c.execute(create_adj_cumulative_QBallowed)
        c.execute(create_adj_cumulative_WRallowed)
        c.execute(create_adj_cumulative_RBallowed)
        c.execute(create_adj_cumulative_TEallowed)
        create_players = """CREATE TABLE IF NOT EXISTS Players(
            URL text PRIMARY KEY,
            Position text
        );"""
        create_vars = """CREATE TABLE IF NOT EXISTS Vars(
            Var text PRIMARY KEY,
            Val text
        );"""
        c.execute(create_players)
        c.execute(create_vars)
        conn.close()
        return 0
    except sqlite3.Error as e:
        print(e)
        return 1

def lookup_position(profile_url):
    profile_soup = get_soup(ffconstants.BASE_URL+profile_url,"getting profile from {}".format(profile_url))
    position = 'not found'
    for paragraph in profile_soup.find('div',attrs={'id':'info'}).find_all('p'):
        if 'Position: ' in paragraph.text:
            split_paragraph = paragraph.text.split('\n')
            for token in split_paragraph:
              if 'Position: ' in token:
                  position = token.replace('Position: ','')
                  return position

def enter_player_into_DB(profile_url):
    db = ffconstants.DB
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('SELECT * FROM Players WHERE URL = ?',(profile_url,))
        if len(c.fetchall())>0:
            return 0
        else:
            position = lookup_position(profile_url)
            if position == 'QB' or position=='WR' or position=='RB' or position=='TE':
                c.execute('INSERT INTO Players (URL,Position) VALUES (?,?)',(profile_url,position))
                conn.commit()
                conn.close()
                return 1
            else:
                conn.close()
                return -1
    except sqlite3.Error as e:
        print(e)
        return -2

import ffconstants
import requests
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

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import urllib
import pandas as pd
from unidecode import unidecode
import plotly.graph_objects as go
from PIL import Image


class NBAPlayer():
    def __init__(self, player_slug, player_id, player_url, player_fullname, player_team, player_no, image, player_pos, stats=None):
        self.slug = player_slug
        self.id = player_id
        self.url = player_url
        self.fullname = player_fullname
        self.team = player_team
        self.pos = player_pos
        self.no = player_no
        self.image = image
        self.stats = stats


response = urlopen('https://www.nba.com/players')
html_doc = response.read().decode('utf-8')
player_slug = re.findall("\"PLAYER_SLUG\":\"([^\"]+)\"", html_doc)
player_id = re.findall("\"PERSON_ID\":(\d+)", html_doc)

# iteratively access all player's homepage and scrape their information
AllPlayers = []
import json
with open("player.json", 'r+') as f:
    try:
        data = json.loads(f.read())
    except json.decoder.JSONDecodeError:
        data = json.loads('{}')
    # use caching file directly
    if 'precious-achiuwa' in data:
        for i in data.keys():
            p = NBAPlayer(data[i]['slug'], data[i]['id'], data[i]['url'], data[i]['fullname'], data[i]['team'], data[i]['no'], data[i]['image'], data[i]['pos'])
            AllPlayers.append(p)
    else:
        for i in range(len(player_id)):
            player_url = f"https://www.nba.com/player/{player_id[i]}/{player_slug[i]}"
            response = urlopen(player_url)
            player_doc = response.read().decode('utf-8')
            soup = BeautifulSoup(player_doc)
            info = soup.find(class_="PlayerSummary_mainInnerInfo__jv3LO")
            if info is None:
                continue
            if len((info.text).split(' | ')) < 3:
                continue
            player_team = (info.text).split(' | ')[0]
            player_no = (info.text).split(' | ')[1].replace('#', '')
            player_pos = (info.text).split(' | ')[2]
            player_fullname = soup.find('title').text.split(' | ')[0]
            image = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id[i]}.png"
            p = NBAPlayer(player_slug[i], player_id[i], player_url, player_fullname, player_team, player_no, image, player_pos)
            AllPlayers.append(p)
        # store all players' information in caching file
        for i in range(len(AllPlayers)):
            data[AllPlayers[i].slug] = {}
            data[AllPlayers[i].slug]['slug'] = AllPlayers[i].slug
            data[AllPlayers[i].slug]['id'] = AllPlayers[i].id
            data[AllPlayers[i].slug]['url'] = AllPlayers[i].url
            data[AllPlayers[i].slug]['fullname'] = AllPlayers[i].fullname
            data[AllPlayers[i].slug]['team'] = AllPlayers[i].team
            data[AllPlayers[i].slug]['pos'] = AllPlayers[i].pos
            data[AllPlayers[i].slug]['no'] = AllPlayers[i].no
            data[AllPlayers[i].slug]['image'] = AllPlayers[i].image
        f.seek(0)
        json.dump(data, f)
        f.truncate()


# implementation of binary search tree
class NBAPlayerTree:
    def __init__(self, key=None, val=None):
        self.key = key
        self.val = val  # position in AllPlayers Array
        self.left = None
        self.right = None

    def getKey(self):
        return self.key

    def insert(self, key, val):
        if self.key is None:
            self.key = key
            return

        if key < self.getKey():
            if self.left:
                self.left.insert(key, val)
                return
            self.left = NBAPlayerTree(key, val)
            return
        if self.right:
            self.right.insert(key, val)
            return
        self.right = NBAPlayerTree(key, val)

    def inorder(self, keys):
        if self.left is not None:
            self.left.inorder(keys)
        if self.key is not None:
            keys.append(self.key)
        if self.right is not None:
            self.right.inorder(keys)
        return keys

    # implementation of search function
    def exists(self, key):
        if key == self.key:
            return self.val
        if key < self.key:
            return self.left.exists(key)
        else:
            return self.right.exists(key)


bst = NBAPlayerTree()
for i in range(len(AllPlayers)):
    bst.insert(int(AllPlayers[i].id), i)


# load stats, convert data type and do some data cleaning
url = "https://www.basketball-reference.com/leagues/NBA_2023_per_game.html"
response1 = urllib.request.urlopen(url)
soup = BeautifulSoup(response1, 'html.parser')
headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
headers = headers[1:]

rows = soup.findAll('tr')[1:]
player_stats = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]
stats = pd.DataFrame(player_stats, columns=headers)
stats = stats.dropna(how='all')
stats = stats.astype({'Age':'int','G':'int', 'GS':'int', 'MP':'float', 'FG':'float', 'FGA':'float',
       '3P':'float', '3PA':'float','2P':'float', '2PA':'float','FT':'float', 'FTA':'float',
       'ORB':'float', 'DRB':'float', 'TRB':'float', 'AST':'float', 'STL':'float',
       'BLK':'float', 'TOV':'float', 'PF':'float', 'PTS':'float'})

for i in range(len(stats)):
    stats.iloc[i, 0] = unidecode(stats.iloc[i, 0])

name_with_id = pd.DataFrame(columns=['Player', 'id'])
Player_name = []
Player_id = []
for i in range(len(AllPlayers)):
    Player_name.append(AllPlayers[i].fullname)
    Player_id.append(AllPlayers[i].id)
name_with_id.Player = Player_name
name_with_id.id = Player_id
stats = stats.merge(name_with_id, on='Player')

# Interaction Part
print("Welcome to NBA 2022-23 season player stats!")

while True:
    print(" Choose the field you want to explore:")
    print("1. Offensive Performance \n2. Defensive Performance \n3. Overall Performance \n4. quit")
    while True:
        number = input("Please choose from the above index (1, 2, 3 or quit):")
        if (number == '1') | (number == '2') | (number == '3') | (number == '4') | (number == 'quit'):
            break
    if (number == '4') | (number == 'quit'):
        print("Bye!")
        break

    if number == '1':
        print("Please choose the criteria you want to rate the player:")
        print("1. FG (Field Goals)\n2. FGA (Field Goal Attempt)\n3. 3P (3-Point Field Goals)\n"
              "4. 3PA (3-Point Field Goal Attempt\n5. 2P (2-Point Field Goals\n6. 2PA (2-Point Field Goal Attempt\n"
              "7. FT (Free Throws)\n8. FTA (Free Throw Attempt)\n9. AST (Assists)\n"
              "10. PTS (Points)")
        while True:
            ct1 = input("Please input the first field that you want to use as the criteria:")
            if (ct1 == 'FG')|(ct1 == 'FGA')|(ct1 == '3P')|(ct1 == '3PA')|(ct1 == '2P')|(ct1 == '2PA')|(ct1 == 'FT')\
                    |(ct1 == 'FTA')|(ct1 == 'AST')|(ct1 == 'PTS'):
                break
        while True:
            ct2 = input("Please input the second field that you want to use as the criteria:")
            if (ct2 == 'FG')|(ct2 == 'FGA')|(ct2 == '3P')|(ct2 == '3PA')|(ct2 == '2P')|(ct2 == '2PA')|(ct2 == 'FT')|\
                    (ct2 == 'FTA')|(ct2 == 'AST')|(ct2 == 'PTS'):
                break
        rank_start = int(input("Please input the start position of the ranks:"))
        rank_end = int(input("Please input the end position of the ranks:"))

        temp = stats.copy()
        temp['ranking'] = temp[[ct1, ct2]].apply(tuple, axis=1).rank(method='first', ascending=False).astype(int)
        temp = temp.set_index('ranking')
        df = pd.DataFrame(columns=['Player', ct1, ct2], index=range(rank_start, rank_end))
        for i in range(rank_start, rank_end):
            df.loc[i]['Player'] = temp.loc[i]['Player']
            df.loc[i][ct1] = temp.loc[i][ct1]
            df.loc[i][ct2] = temp.loc[i][ct2]
        print(df)

        # visualize using plotly
        scatter_data = go.Scatter(x=df[ct1], y=df[ct2], mode='markers+text', text=df['Player'], marker={'symbol': 'circle', 'size': 5})
        scatter_layout = go.Layout(title=f"{ct1} vs {ct2} ranked from {rank_start} to {rank_end}", \
                                   xaxis=dict(title=f"{ct1}", showgrid=True), yaxis=dict(title=f"{ct2}", showgrid=True))
        fig = go.Figure(data=scatter_data, layout=scatter_layout)
        fig.update_traces(textposition='top center')
        fig.write_html(f"{ct1} vs {ct2} ranked from {rank_start} to {rank_end}.html", auto_open=True)

        # explore more information of the player
        while True:
            exp = input("Please enter the rank of the player you want to further explore, or press 0 to return:")
            if not exp.isdigit():
                break
            if (int(exp) >= rank_start) & (int(exp) < rank_end):
                exp_id = int(temp.loc[int(exp)]['id'])
                exp_id = bst.exists(exp_id) # use binary search tree to find that player
                print(f"Player full name: {AllPlayers[exp_id].fullname}")
                print(f"Player team: {AllPlayers[exp_id].team}")
                print(f"Player position: {AllPlayers[exp_id].pos}")
                print(f"Player number: {AllPlayers[exp_id].no}")
                print(f"Player homepage: {AllPlayers[exp_id].url}")
                urllib.request.urlretrieve(AllPlayers[exp_id].image, f"{AllPlayers[exp_id].slug}.png") # display the image of that player
                img = Image.open(f"{AllPlayers[exp_id].slug}.png")
                img.show()
            else:
                break

    if number == '2':
        print("Please choose the criteria you want to rate the player:")
        print("1. DRB (Defensive Rebounds)\n2. TRB (Total Rebounds)\n3. STL (Steals)\n4. BLK (Blocks)")
        while True:
            ct1 = input("Please input the first field that you want to use as the criteria:")
            if (ct1 == 'DRB')|(ct1 == 'TRB')|(ct1 == 'STL')|(ct1 == 'BLK'):
                break
        while True:
            ct2 = input("Please input the second field that you want to use as the criteria:")
            if (ct2 == 'TRB')|(ct2 == 'DRB')|(ct2 == 'STL')|(ct2 == 'BLK'):
                break
        rank_start = int(input("Please input the start position of the ranks:"))
        rank_end = int(input("Please input the end position of the ranks:"))

        temp = stats.copy()
        temp['ranking'] = temp[[ct1, ct2]].apply(tuple, axis=1).rank(method='first', ascending=False).astype(int)
        temp = temp.set_index('ranking')
        df = pd.DataFrame(columns=['Player', ct1, ct2], index=range(rank_start, rank_end))
        for i in range(rank_start, rank_end):
            df.loc[i]['Player'] = temp.loc[i]['Player']
            df.loc[i][ct1] = temp.loc[i][ct1]
            df.loc[i][ct2] = temp.loc[i][ct2]
        print(df)
        scatter_data = go.Scatter(x=df[ct1], y=df[ct2], mode='markers+text', text=df['Player'], marker={'symbol': 'circle', 'size': 5})
        scatter_layout = go.Layout(title=f"{ct1} vs {ct2} ranked from {rank_start} to {rank_end}", \
                                   xaxis=dict(title=f"{ct1}", showgrid=True), yaxis=dict(title=f"{ct2}", showgrid=True))
        fig = go.Figure(data=scatter_data, layout=scatter_layout)
        fig.update_traces(textposition='top center')
        fig.write_html(f"{ct1} vs {ct2} ranked from {rank_start} to {rank_end}.html", auto_open=True)

        # explore more information of the player
        while True:
            exp = input("Please enter the rank of the player you want to further explore, or press 0 to return:")
            if not exp.isdigit():
                break
            if (int(exp) >= rank_start) & (int(exp) < rank_end):
                exp_id = int(temp.loc[int(exp)]['id'])
                exp_id = bst.exists(exp_id) # use binary search tree to find that player
                print(f"Player full name: {AllPlayers[exp_id].fullname}")
                print(f"Player team: {AllPlayers[exp_id].team}")
                print(f"Player position: {AllPlayers[exp_id].pos}")
                print(f"Player number: {AllPlayers[exp_id].no}")
                print(f"Player homepage: {AllPlayers[exp_id].url}")
                urllib.request.urlretrieve(AllPlayers[exp_id].image, f"{AllPlayers[exp_id].slug}.png") # display the image of that player
                img = Image.open(f"{AllPlayers[exp_id].slug}.png")
                img.show()
            else:
                break

    if number == '3':
        print("Please choose the criteria you want to rate the player:")
        print("1.  Age (Age)                  2. G (Games Played)\n"
              "3.  GS (Games Started)         4. MP (Minutes Played)\n"
              "5.  FG (Field Goals)           6. 3P (3-Point Field Goals)\n"
              "7.  FT (Free Throws            8. TRB (Total Rebounds)\n"
              "9.  ORB (Offensive Rebounds)   10. DRB (Defensive Rebounds)\n"
              "11. AST (Assists)              12. STL (Steals)\n"
              "13. BLK (Blocks)               14. TOV (Turnovers)\n"
              "15. PF (Personal Fouls)        16. PTS (Points)")
        while True:
            ct1 = input("Please input the first field that you want to use as the criteria:")
            if (ct1 == 'Age')|(ct1 == 'G')|(ct1 == 'GS')|(ct1 == '3P')|(ct1 == 'MP')|(ct1 == 'FG')|(ct1 == 'FT')|\
                    (ct1 == 'TRB')|(ct1 == 'ORB')|(ct1 == 'DRB')|(ct1 == 'AST')|(ct1 == 'STL')|(ct1 == 'BLK')\
                    |(ct1 == 'TOV')|(ct1 == 'PF')|(ct1 == 'PTS'):
                break
        while True:
            ct2 = input("Please input the second field that you want to use as the criteria:")
            if (ct2 == 'Age') | (ct2 == 'G') | (ct2 == 'GS') | (ct2 == '3P') | (ct2 == 'MP') | (ct2 == 'FG') | (
                    ct2 == 'FT') | (ct2 == 'TRB') | (ct2 == 'ORB') | (ct2 == 'DRB') | (ct2 == 'AST') | (ct2 == 'STL') |\
                    (ct2 == 'BLK') | (ct2 == 'TOV') | (ct2 == 'PF') | (ct2 == 'PTS'):
                break
        rank_start = int(input("Please input the start position of the ranks:"))
        rank_end = int(input("Please input the end position of the ranks:"))

        temp = stats.copy()
        temp['ranking'] = temp[[ct1, ct2]].apply(tuple, axis=1).rank(method='first', ascending=False).astype(int)
        temp = temp.set_index('ranking')
        df = pd.DataFrame(columns=['Player', ct1, ct2], index=range(rank_start, rank_end))
        for i in range(rank_start, rank_end):
            df.loc[i]['Player'] = temp.loc[i]['Player']
            df.loc[i][ct1] = temp.loc[i][ct1]
            df.loc[i][ct2] = temp.loc[i][ct2]
        print(df)
        scatter_data = go.Scatter(x=df[ct1], y=df[ct2], mode='markers+text', text=df['Player'], marker={'symbol': 'circle', 'size': 5})
        scatter_layout = go.Layout(title=f"{ct1} vs {ct2} ranked from {rank_start} to {rank_end}",\
                                   xaxis=dict(title=f"{ct1}", showgrid=True), yaxis=dict(title=f"{ct2}", showgrid=True))
        fig = go.Figure(data=scatter_data, layout=scatter_layout)
        fig.update_traces(textposition='top center')
        fig.write_html(f"{ct1} vs {ct2} ranked from {rank_start} to {rank_end}.html", auto_open=True)

        # explore more information of the player
        while True:
            exp = input("Please enter the rank of the player you want to further explore, or press 0 to return:")
            if not exp.isdigit():
                break
            if (int(exp) >= rank_start) & (int(exp) < rank_end):
                exp_id = int(temp.loc[int(exp)]['id'])
                exp_id = bst.exists(exp_id) # use binary search tree to find that player
                print(f"Player full name: {AllPlayers[exp_id].fullname}")
                print(f"Player team: {AllPlayers[exp_id].team}")
                print(f"Player position: {AllPlayers[exp_id].pos}")
                print(f"Player number: {AllPlayers[exp_id].no}")
                print(f"Player homepage: {AllPlayers[exp_id].url}")
                urllib.request.urlretrieve(AllPlayers[exp_id].image, f"{AllPlayers[exp_id].slug}.png") # display the image of that player
                img = Image.open(f"{AllPlayers[exp_id].slug}.png")
                img.show()
            else:
                break



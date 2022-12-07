from bs4 import BeautifulSoup
from urllib.request import urlopen
import re


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

AllPlayers = []
import json
with open("player.json", 'r+') as f:
    try:
        data = json.loads(f.read())
    except json.decoder.JSONDecodeError:
        data = json.loads('{}')
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

print(AllPlayers[480].fullname)


class NBAPlayerTree():
    def __int__(self, key, val):
        self.key = key
        self.val = val  # position in AllPlayers Array
        self.left = None
        self.right = None

    def getKey(self):
        return self.key

    def insert(self, key, val):
        if not self.key:
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
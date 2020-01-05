import requests
import pandas as pd
from datetime import datetime
import webbrowser


def convert_size(bytes):
    bytes = int(bytes)
    if bytes > 1*10**9:
        num = bytes/(1024**3)
        return f"{round(num,2)} GB"
    else:
        num = bytes*0.00000095367432
        return f"{round(num,2)} MB"


search = input("What show should I check? ")
selected_page = 1

with open("API_key.txt") as file:
    key = file.read()

imdb_full = requests.get("http://www.omdbapi.com",
                         headers={"Accept": "application/json"},
                         params={"t": search, "apikey": key}).json()["imdbID"]

imdb = imdb_full[2:]

response_json = requests.get("https://eztv.io/api/get-torrents",
                             headers={"Accept": "application/json"},
                             params={"page": selected_page, "limit": 100, "imdb_id": imdb}).json()

size = len(response_json["torrents"])

titles = []
seasons = []
episodes = []
dates = []
magnets = []
sizes = []

numbers = [i for i in range(1, size+1)]


for item in response_json["torrents"]:
    titles.append(item["title"])
    seasons.append(item["season"])
    episodes.append(item["episode"])
    dates.append(datetime.utcfromtimestamp(
        item["date_released_unix"]).strftime('%H:%M  %d/%m/%Y'))
    sizes.append(convert_size(item["size_bytes"]))
    magnets.append(item["magnet_url"])

d = {"Number": numbers, 'Titles': titles[0:size], 'Season': seasons[0:size],
     'Episode': episodes[0:size], 'Sizes': sizes[0:size], "Dates": dates[0:size], 'Links': magnets[0:size]}

df = pd.DataFrame(data=d)
df.set_index("Number")


def get_latest():

    count = 0
    new_sizes = []
    latest = max(episodes)
    for ep in episodes:
        if ep != latest:
            continue
        count += 1
    for s in sizes[0:count]:
        if "M" in s:
            y = s.replace(" MB", "")
            new_sizes.append(float(y))
        if "G" in s:
            y = s.replace(" GB", "")
            new_sizes.append(float(y)*1000)

    maxim = max(new_sizes)

    index = new_sizes.index(maxim)
    webbrowser.open(df.iloc[index, 6])


def get_ep_seas(y, x):

    indexes = []
    indexes_old = []
    temp_sizes = []
    temp_sizes_old = []

    new_sizes = []

    for index, season in enumerate(seasons):
        if int(season) == y:
            indexes_old.append(index)
            temp_sizes_old.append(sizes[index])

    episodes_new = []
    for i, j in zip(indexes_old, episodes):
        episodes_new.append(episodes[i])

    for index, ep in zip(indexes_old, episodes_new):
        if int(ep) == x:
            indexes.append(index)
            temp_sizes.append(sizes[index])

    for s in temp_sizes:
        if "M" in s:
            y = s.replace(" MB", "")
            new_sizes.append(float(y))
        if "G" in s:
            y = s.replace(" GB", "")
            new_sizes.append(float(y)*1000)

    maxim = max(new_sizes)

    if maxim > 1000:
        maxim = str((float(maxim)/1000))+" GB"
    else:
        maxim = str(maxim) + " MB"

    chosen = sizes.index(maxim)
    webbrowser.open(df.iloc[chosen, 6])


def download():
    x = ""
    y = ""

    while "stop" not in x or "stop" not in y:
        y = input("Which Season? ")
        x = input("Which Episode should I download? ")

        try:

            # new or latest for latest episode

            if "new" in x or "latest" in x:
                get_latest()
            elif "new" in x or "latest" in y:
                get_latest()
            else:
                get_ep_seas(int(y), int(x))
        except:
            print("An error has occured")


download()

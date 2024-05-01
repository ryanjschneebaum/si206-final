from bs4 import BeautifulSoup
import re
import os
import csv
import requests
import json
import sqlite3
import unittest
import matplotlib.pyplot as plt
import numpy as np

def retrieve_categories(html_file): 

    using_list = ["Song Of The Year", "Album Of The Year", "Record Of The Year", "Best Pop Vocal Album", "Best Dance/Electronic Recording", "Best Pop Dance Recording", "Best Dance/Electronic Music Album", "Best Rock Song", "Best Rock Album", "Best Alternative Music Album", "Best R&B Song", "Best Progressive R&B Album", "Best R&B Album", "Best Rap Song", "Best Rap Album", "Best Jazz Vocal Album", "Best Jazz Instrumental Album", "Best Large Jazz Ensemble Album", "Best Latin Jazz Album", "Best Alternative Jazz Album", "Best Traditional Pop Vocal Album", "Best Contemporary Instrumental Album", "Best Country Song", "Best Country Album", "Best American Roots Song", "Best Americana Album", "Best Bluegrass Album", "Best Traditional Blues Album", "Best Contemporary Blues Album", "Best Folk Album", "Best Regional Roots Music Album", "Best Gospel Performance/Song", "Best Contemporary Christian Music Performance/Song", "Best Gospel Album", "Best Contemporary Christian Music Album", "Best Roots Gospel Album", "Best Latin Pop Album", "Best Música Urbana Album", "Best Latin Rock or Alternative Album", "Best Música Mexicana Album (Including Tejano)", "Best Tropical Latin Album", "Best Global Music Album", "Best Reggae Album", "Best New Age, Ambient, or Chant Album", "Best Children's Music Album", "Best Comedy Album", "Best Compilation Soundtrack For Visual Media", "Best Score Soundtrack For Visual Media (Includes Film And Television)", "Best Score Soundtrack for Video Games and Other Interactive Media", "Best Song Written For Visual Media", "Best Historical Album", "Best Engineered Album, Non-Classical", "Best Engineered Album, Classical", "Best Remixed Recording", "Best Immersive Audio Album", "Best Instrumental Composition", "Best Opera Recording", "Best Classical Instrumental Solo", "Best Classical Solo Vocal Album"]
    #print("Using List:", len(using_list))


    file = open(html_file, "r", encoding="utf-8-sig")
    soup = BeautifulSoup(file, 'html.parser')
    file.close()

    blocks = {}

    categories = []
    winners = []
    nominees = []

    category_tags = soup.find_all(class_='w-full text-left md-xl:text-right mb-1 md-xl:mb-20px text-14 md-xl:text-22 font-polaris uppercase')
    for category in category_tags:
        cat_name = re.findall('<div[^>]*>(.*?)</div>', str(category))[0].replace("amp;", "")
        #if(not re.findall('Performance', cat_name)):
        categories.append(cat_name)
    
    winner_tags = soup.find_all(class_="w-full text-center md-xl:text-left text-17 md-xl:text-22 mr-10px md-xl:mr-30px font-polaris font-bold md-xl:leading-8 tracking-wider")
    for winner in winner_tags:
        win_name = re.findall('<div[^>]*>(.*?)</div>', str(winner))[0].strip("\"").replace("amp;", "").replace("\\", "")
        winners.append(win_name)

    nominee_try = soup.find_all(class_="flex-1 flex flex-row md-xl:max-w-710px")
    for nominee in nominee_try:
        nominee_list = re.findall('w-full text-left md-xl:text-22 text-17 mr-10px md-xl:mr-30px font-polaris font-bold md-xl:leading-8 tracking-wider flex flex-row justify-between"><span>(.*?)</span>', str(nominee))
        temp_list = []
        for nom in nominee_list:
            fin_nom = nom.strip("\"").replace("amp;", "").replace("\\", "")
            temp_list.append(fin_nom)
        nominees.append(temp_list)

    nominee_tags = soup.find_all(class_="w-full text-left md-xl:text-22 text-17 mr-10px md-xl:mr-30px font-polaris font-bold md-xl:leading-8 tracking-wider flex flex-row justify-between")
    for nominee in nominee_tags:
        nom_name = re.findall('<div[^>]*>(.*?)</div>', str(nominee))[0].strip("\"").replace("amp;", "").replace("\\", "")

    used_list = []
    # print("ALL CATEGORIES")
    for index in range(len(categories)):
        #print(categories[index])
        # if(categories[index] not in using_list): print(categories[index])
        # print(categories[index])
        if(categories[index] in using_list):
            used_list.append(categories[index])
            which_type = "UNDEF"
            if(re.findall('Album', categories[index]) or re.findall('Soundtrack', categories[index])): which_type = "album"
            elif(re.findall('Record', categories[index]) or re.findall('Song', categories[index]) or re.findall('Instrumental', categories[index])): which_type = "track"
            blocks[categories[index]] = { "search_type": which_type, "winner": winners[index], "nominees": nominees[index] }
    # print("IN OUR LIST BUT NOT FOUND")
    # for cat in using_list:
    #     if(cat not in used_list): print(cat)

    return blocks


def create_database(database_name):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS Categories')
    cur.execute('CREATE TABLE Categories (category TEXT, name TEXT, spotify_id TEXT, is_winner BOOLEAN)')
    cur.execute('DROP TABLE IF EXISTS Tracks')
    cur.execute('CREATE TABLE Tracks (id TEXT UNIQUE, name TEXT, popularity INTEGER)')
    cur.execute('DROP TABLE IF EXISTS Albums')
    cur.execute('CREATE TABLE Albums (id TEXT UNIQUE, name TEXT, popularity INTEGER)')
    conn.commit()
    conn.close()

def set_token(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        token_json = json.loads(file.read())
        # print(token_json['access_token'])
        return token_json['access_token']


def search(category_data, token, name, type):
    # if type == "track":
    url = f'https://api.spotify.com/v1/search?q={name}&type={type}&limit=1'
    response = requests.get(url, 
                            headers={'Authorization': f'Bearer {token}'})
    # print(response)
    if response.status_code != 200:
        # category_data_dict = {"name": name,
        #                     "id": "None"}
        category_data['winner_id'] = "None"
    else:
        response_dict = json.loads(response.text)
        # category_data_dict = {"name": name,
        #                     "id": response_dict[f"{type}s"]["items"][0]["id"]}
        # category_data['winner'] = category_data_dict
        category_data["winner_id"] = response_dict[f"{type}s"]["items"][0]["id"]
        # break
    nominee_ids = []
    for i in range(0, len(category_data['nominees'])):
        name = category_data['nominees'][i]
        url = f'https://api.spotify.com/v1/search?q={name}&type={type}&limit=1'
        response = requests.get(url, 
                                headers={'Authorization': f'Bearer {token}'})
        response_dict = json.loads(response.text)
        # category_data_dict = {"name": name,
        #                     "id": response_dict[f"{type}s"]["items"][0]["id"]}
        # category_data['nominees'][i] = category_data_dict
        nominee_ids.append(response_dict[f"{type}s"]["items"][0]["id"])
    category_data["nominee_ids"] = nominee_ids


def find_ids(data, token):
    """"""
    conn = sqlite3.connect("grammys.sqlite3")
    cur = conn.cursor()
    for category, category_data in data.items():
        name = category_data["winner"]
        type = category_data["search_type"]
        search(category_data, token, name, type)
        # cur.execute('INSERT INTO Categories (name, spotify_id) VALUES (?, ?)', (name, category_data["winner_id"]))
        for index in range(0, len(category_data["nominees"])):
            name = category_data["nominees"][index]
            id = category_data["nominee_ids"][index]
            # cur.execute('INSERT INTO Categories (name, spotify_id) VALUES (?, ?)', (name, id))


def make_database_categories(data):
    conn = sqlite3.connect("grammys.sqlite3")
    cur = conn.cursor()
    for category, category_data in data.items():
        name = category_data["winner"]
        cur.execute('INSERT INTO Categories (category, name, spotify_id, is_winner) VALUES (?, ?, ?, ?)', (category, name, category_data["winner_id"], True))
        for index in range(0, len(category_data["nominees"])):
            name = category_data["nominees"][index]
            id = category_data["nominee_ids"][index]
            cur.execute('INSERT INTO Categories (category, name, spotify_id, is_winner) VALUES (?, ?, ?, ?)', (category, name, id, False))
    conn.commit()
    conn.close()


def insert_data(type, id, name, popularity):
    # print(id, name, popularity)
    conn = sqlite3.connect("grammys.sqlite3")
    cur = conn.cursor()
    if type == "track":
        cur.execute('INSERT OR IGNORE INTO Tracks (id, name, popularity) VALUES (?, ?, ?)', (id, name, popularity))
    elif type == "album":
        cur.execute('INSERT OR IGNORE INTO Albums (id, name, popularity) VALUES (?, ?, ?)', (id, name, popularity))
    conn.commit()
    conn.close()

def query_api(data, token, type, ids):
    ""
    if isinstance(ids, str):
        url = f"https://api.spotify.com/v1/{type}s?ids={ids}"
        response = requests.get(url, 
                                headers={'Authorization': f'Bearer {token}'})
        if response.status_code != 200:
            print("error")
        else:
            # print(ids)
            response_dict = json.loads(response.text)
            # print(response_dict)
            data["winner_popularity"] = response_dict[f"{type}s"][0]["popularity"]
            insert_data(type, ids, data["winner_id"], data["winner_popularity"])
    else:
        url = f"https://api.spotify.com/v1/{type}s?ids={','.join(str(x) for x in ids)}"
        response = requests.get(url, 
                                headers={'Authorization': f'Bearer {token}'})
        if response.status_code != 200:
            print("error")
        else:
            response_dict = json.loads(response.text)
            # print(response_dict)
            data["nominee_popularity"] = []
            for i in range(0, len(response_dict[f"{type}s"])):
                popularity = response_dict[f"{type}s"][i]["popularity"]
                data["nominee_popularity"].append(popularity)
                insert_data(type, data["nominee_ids"][i], data["nominees"][i], popularity)
            print(data)
    

def calculate_popularity(data):
    """Calculate relative popularity based on the maximum popularity in each category."""
    popularity_data = {}
    for category, category_dict in data.items():
        max_popularity = max(category_dict["winner_popularity"], max(category_dict["nominee_popularity"]))
        #print(max_popularity)
        winner_score = category_dict["winner_popularity"] / max_popularity * 100
        nominees = []
        for nominee_popularity in category_dict["nominee_popularity"]:
            relative_popularity = nominee_popularity / max_popularity * 100
            nominees.append(relative_popularity)
        popularity_data[category] = {
            "winner_score": winner_score,
            "nominee_scores": nominees
        }
    return popularity_data

def make_charts():
    with open('data/popularity_data.json', 'r') as file:
        data = json.load(file)

    conn = sqlite3.connect("grammys.sqlite3")
    cur = conn.cursor()
    cur.execute("SELECT category, Categories.name, spotify_id, popularity FROM Categories INNER JOIN Tracks ON Categories.spotify_id = Tracks.id")
    for row in cur:
        print(row)
    cur.execute("SELECT category, Categories.name, spotify_id, popularity FROM Categories INNER JOIN Albums ON Categories.spotify_id = Albums.id")

    popularity_data = calculate_popularity(data)

    bar_chart('track', data, popularity_data)
    bar_chart('album', data, popularity_data)
    pie_chart(data)

def bar_chart(category_type, data, popularity_data):
    labels = []
    values = []
    colors = []
    winner_scores = []
    nominee_scores = []
    for category, details in data.items():
        if details['search_type'] == category_type:
            relative_popularity = popularity_data[category]
            winner_scores.append(relative_popularity['winner_score'])
            nominee_scores.extend(relative_popularity['nominee_scores'])
            labels.append(details['winner'])
            values.append(relative_popularity['winner_score'])
            colors.append('gold')
            for nominee, score in zip(details['nominees'], relative_popularity['nominee_scores']):
                labels.append(nominee)
                values.append(score)
                colors.append('gray')
    sorted_indices = np.argsort(values)
    sorted_labels = [f'{category_type} {i+1}' for i in range(len(labels))]
    sorted_values = [values[i] for i in sorted_indices]
    sorted_colors = [colors[i] for i in sorted_indices]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.bar(range(len(sorted_labels)), sorted_values, color=sorted_colors)
    ax.set_xticks([])
    ax.set_xlabel(category_type.capitalize() + 's')
    ax.set_ylabel('Relative Popularity')
    ax.set_title(f'Relative Popularity of {category_type.capitalize()}s')

    avg_winner_score = np.mean(winner_scores)
    avg_nominee_score = np.mean(nominee_scores)
    scores_box = f'Avg Winner: {avg_winner_score:.2f}%\nAvg Nominee: {avg_nominee_score:.2f}%'
    ax.text(0.02, 0.95, scores_box, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='gold', label='Winner'),
                       Patch(facecolor='gray', label='Nominee')]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.01, .85))

    plt.show()

def pie_chart(data):
    total_winners = 0
    total_nominees = 0
    most_popular_winners = 0
    most_popular_nominees = 0

    for category, details in data.items():
        total_winners += 1
        total_nominees += len(details['nominee_popularity'])
        max_popularity = max(details['winner_popularity'], max(details['nominee_popularity']))
        if details['winner_popularity'] == max_popularity:
            most_popular_winners += 1
        else:
            most_popular_nominees += 1

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    labels = ['Total Winners', 'Total Nominees']
    sizes = [total_winners, total_nominees]
    colors = ['gold', 'gray']
    ax[0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax[0].set_title('Total Winners vs. Total Nominees')

    labels = ['Most Popular Winners', 'Most Popular Nominees']
    sizes = [most_popular_winners, most_popular_nominees]
    colors = ['gold', 'gray']
    ax[1].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax[1].set_title('Most Popular Winners vs. Most Popular Nominees')

    plt.show()

def main():
    data = retrieve_categories("grammys.html")
    # # print(data)
    # # for datum in data:
    # #     print(datum)
    # #     print("\tWinner:")
    # #     print("\t\t", data[datum]["winner"])
    # #     print("\tNominees:")
    # #     for nom in data[datum]["nominees"]: print("\t\t", nom)
    # # print(data)
    token = set_token("access_token.txt")

    # Search for IDs
    # create_database("grammys.sqlite3")
    # find_ids(data, token)
    # make_database_categories(data)
    # with open('data.json', 'w') as file:
    #     json.dump(data, file)

    with open('data/data.json', 'r') as file:
        # print(file.read())
        data = json.load(file)
        # print(data)
    for category, category_dict in data.items():
        print(category)
        query_api(category_dict, token, category_dict["search_type"], category_dict["winner_id"])
        query_api(category_dict, token, category_dict["search_type"], category_dict["nominee_ids"])
    with open('popularity_data.json', 'w') as file:
        json.dump(data, file)

    # # Calculate relative popularity 
    # with open('data/popularity_data.json', 'r') as file:
    #     # print(file.read())
    #     data = json.load(file)
    # popularity_data = calculate_popularity(data)
    # print(popularity_data)
    # make_charts()


main()
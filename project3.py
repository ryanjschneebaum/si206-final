from bs4 import BeautifulSoup
import re
import os
import csv
import requests
import json
import unittest

def retrieve_categories(html_file): 

    using_list = ["Song Of The Year", "Album Of The Year", "Record Of The Year", "Best New Artist", "Best Pop Vocal Album", "Best Dance/Electronic Recording", "Best Pop Dance Recording", "Best Dance/Electronic Music Album", "Best Rock Song", "Best Rock Album", "Best Alternative Music Album", "Best R&B Song", "Best Progressive R&B Album", "Best R&B Album", "Best Rap Song", "Best Rap Album", "Best Jazz Vocal Album", "Best Jazz Instrumental Album", "Best Large Jazz Ensemble Album", "Best Latin Jazz Album", "Best Alternative Jazz Album", "Best Traditional Pop Vocal Album", "Best Contemporary Instrumental Album", "Best Country Song", "Best Country Album", "Best American Roots Song", "Best Americana Album", "Best Bluegrass Album", "Best Traditional Blues Album", "Best Contemporary Blues Album", "Best Folk Album", "Best Regional Roots Music Album", "Best Gospel Performance/Song", "Best Contemporary Christian Music Performance/Song", "Best Gospel Album", "Best Contemporary Christian Music Album", "Best Roots Gospel Album", "Best Latin Pop Album", "Best Música Urbana Album", "Best Latin Rock or Alternative Album", "Best Música Mexicana Album (Including Tejano)", "Best Tropical Latin Album", "Best Global Music Album", "Best Reggae Album", "Best New Age, Ambient, or Chant Album", "Best Children's Music Album", "Best Comedy Album", "Best Compilation Soundtrack For Visual Media", "Best Score Soundtrack For Visual Media (Includes Film And Television)", "Best Score Soundtrack for Video Games and Other Interactive Media", "Best Song Written For Visual Media", "Best Historical Album", "Best Engineered Album, Non-Classical", "Best Engineered Album, Classical", "Best Remixed Recording", "Best Immersive Audio Album", "Best Instrumental Composition", "Best Opera Recording", "Best Classical Instrumental Solo", "Best Classical Solo Vocal Album"]
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
            if(re.findall('Album', categories[index]) or re.findall('Soundtrack', categories[index])): which_type = "Album"
            elif(re.findall('Artist', categories[index])): which_type = "Artist"
            elif(re.findall('Record', categories[index]) or re.findall('Song', categories[index]) or re.findall('Instrumental', categories[index])): which_type = "Song"
            blocks[categories[index]] = { "search_type": which_type, "winner": winners[index], "nominees": nominees[index] }
    # print("IN OUR LIST BUT NOT FOUND")
    # for cat in using_list:
    #     if(cat not in used_list): print(cat)

    return blocks


def set_token(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        token_json = json.loads(file.read())
        # print(token_json['access_token'])
        return token_json['access_token']

def find_ids(data, token):
    ""
    for category, category_data in data.items():
        name = category_data["winner"]
        type = 'track'
        url = f'https://api.spotify.com/v1/search?q={name}&type={type}&limit=1'
        response = requests.get(url, 
                                headers={'Authorization': f'Bearer {token}'})
        # print(response)
        if response.status_code != 200:
            category_data_dict = {"name": name,
                                "id": "None"}
            category_data['winner'] = category_data_dict
        else:
            response_dict = json.loads(response.text)
            category_data_dict = {"name": name,
                                "id": response_dict["tracks"]["items"][0]["id"]}
            category_data['winner'] = category_data_dict
            # break
        for nominee in category_data['nominees']:
            name = nominee
            type = 'track'
            url = f'https://api.spotify.com/v1/search?q={name}&type={type}&limit=1'
            response = requests.get(url, 
                                    headers={'Authorization': f'Bearer {token}'})
            response_dict = json.loads(response.text)
            # print(response_dict)
            category_data_dict = {"name": name,
                                "id": response_dict["tracks"]["items"][0]["id"]}
            print(category_data_dict)
            nominee = category_data_dict
        
    
    # winner = data["Record Of The Year"]["winner"]
    # type = 'album'
    # url = f'https://api.spotify.com/v1/search?q={winner}&type={type}&limit=1'
    # print(response.text)


def query_api(data, token):
    ""
    response = requests.post('https://api.spotify.com/v1/albums', 
                            headers={'Authorization': f'Bearer {token}'})
    print(response)
    data = response.text
    # in_dict = json.loads(data)
    # print(in_dict.get("facts"))
    

    pass

def main():
    data = retrieve_categories("grammys.html")
    # print(data)
    # for datum in data:
    #     print(datum)
    #     print("\tWinner:")
    #     print("\t\t", data[datum]["winner"])
    #     print("\tNominees:")
    #     for nom in data[datum]["nominees"]: print("\t\t", nom)
    print(data)
    token = set_token("access_token.txt")
    # find_ids(data, token)
    # print(data)
    # query_api()

main()
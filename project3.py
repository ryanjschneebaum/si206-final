from bs4 import BeautifulSoup
import re
import os
import csv
import requests
import json
import unittest

def retrieve_categories(html_file): 

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

    for index in range(len(categories)):
        blocks[categories[index]] = { "winner": winners[index], "nominees": nominees[index] }
    
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
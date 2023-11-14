# coding: utf-8
import urllib.request, urllib.parse, urllib.error
import re
import json
import matplotlib.pyplot as plt
import math
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
#url for 原價屋(coolpc)
url = "http://www.coolpc.com.tw/evaluate.php"
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
# json file for google sheet API authorize
auth_json = "YOUR AUTHORIZE JSON FILE HERE" #TODO: set auth_json's path
scopes = ['https://spreadsheets.google.com/feeds']

#=========================this part is for the google sheet API=========================
credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json, scopes)
gss_client = gspread.authorize(credentials)
spreadsheet_key = "KEY FOR YOUR GOOGLE SPREADSHEETS" #TODO: add spreadsheet_key
sheet = gss_client.open_by_key(spreadsheet_key).sheet1

#====================this part for BeautifulSoup =========================
req = urllib.request.Request(url=url, headers=headers)
html = urllib.request.urlopen(req)
#BeautifulSoup auto-detect "windows-1252" as page's encoding, so it cause tons of glitch
#switch to 'big5', there are some error char '�', so we use 'CP950'
soup = BeautifulSoup(html.read(), 'html.parser', from_encoding= 'CP950', exclude_encodings=["windows-1252"])
#find the category of goods
category = soup.find_all('tr')
#find all goods
tags = soup.find_all('option')

#========================= variable initalize =========================
goods_shelf = {}
shelf_name = []
#key for google search API
engine_ID = '8494bc4843c0ec67a'
API_key = '' #TODO: add search API_key

shelf_name_count = -1

#========================= derive category =========================
for infor in category:
    title = re.search(r"<tr bgcolor=\"efefe0\"><td class=\"w\">[0-9]+<td class=\"t\">(.+)<td nowrap=\"\">", str(infor))
    if title:
        title = title.group(1).replace('</td>', '')

        if not title.find('<a') == -1:
            title = title[:title.find('<a')]
        title = title.strip()

        goods_shelf[title] = {}
        shelf_name.append(title)
shelf_name = shelf_name[2:]
#print(shelf_name)

#========================= derive classification and item from <tags> =========================
for line in tags:
    line = str(line).split('\n')
    if len(line) > 1:
        line = line[1:-2]
        shelf_name_count += 1
        for good in line:
            #print(good)
            type_define = re.search(r"<optgroup label=\"(.+)\">", good)
            if type_define:
                typ = type_define.group(1)
                goods_shelf[shelf_name[shelf_name_count]][typ] = []
            
            goods_search = re.search(r" value=\"[0-9]+\">(.+)<", good)
            if goods_search:
                #print(goods_search.group(1))
                try:
                    goods_shelf[shelf_name[shelf_name_count]][typ].append(goods_search.group(1))
                except KeyError:
                    pass
#print(goods_shelf)
html.close()

#========================= User interface =========================
layer = 1
row_count = 1
while True:
    #Layer for category
    if layer == 1:
        print('')
        for shelf_name in goods_shelf:
            print(shelf_name)
        print("\nNow in layer 1 - Category")
        print("Input 'Q' to quit, input name of item for more infor, and 'F' for favorite list")
        in_1 = input("Please input HERE:")
        #input loop inspire from homework-9
        while True:
            if in_1 == 'Q':
                break
            elif in_1 == 'F':
                layer += 4
                break
            elif in_1 in goods_shelf.keys():
                layer += 1
                break
            else:
                print("Unvaild input!!")
                in_1 = input("Please try again:")
        if in_1 == 'Q':
            break

    #Layer for sort
    elif layer == 2:
        print('')
        for typ in goods_shelf[in_1]:
            print(typ)
        print("\nNow in layer 2 - Sort")
        print("Input 'Q' to quit, 'B' to go back, item's name for more infor, and 'F' for favorite list")
        in_2 = input("Please input HERE:")
        while True:
            if in_2 == 'Q':
                break
            elif in_2 == 'B':
                layer -=1
                break
            elif in_2 == 'F':
                layer += 3
                break
            elif in_2 in goods_shelf[in_1].keys():
                layer += 1
                break
            else:
                print("\nUnvaild input!!")
                in_2 = input("Please try again:")
        if in_2 == 'Q':
            break
    
    #Layer for items
    elif layer == 3:
        price_interval = {}
        price_data = []
        chart = False

        print('')
        if len(goods_shelf[in_1][in_2]) == 0:
            print("--No item found--")
        else:
            for item in goods_shelf[in_1][in_2]:
                print(item)
                #derive price infor from item
                price = re.search(r"[↘]*(\$[0-9]+)\s", item)
                if price:
                    price_data.append(price.group(1))
            for i in range(len(price_data)):
                price_data[i] = int(price_data[i].replace('$', ''))
            #To devide all the item within 5 price interval, the size of each interaval need to > min_interval and < max_interval
            min_interval = math.ceil((max(price_data)- min(price_data))/5)
            max_interval = math.floor((max(price_data)- min(price_data))/4)
            #take the average of max and min, and make it a multiple of 10
            interval = math.floor((max_interval + min_interval)/20)*10
            if not interval == 0:
                #create the interval dict, count the number of price within this interval as the value 
                for i in range(5):
                    price_interval['$'+str(min(price_data) + interval*i) + '~' + str(min(price_data) + interval*(i+1) - 1)] =0
                #Only after the interval dict is created, we can present analysis chart
                chart = True
                print("\nYou can input 'C' for price analysis")
            #for interval == 0, all the price is the same
            else:
                print("\nFlat rate:$" + str(min(price_data)))

        print("\nNow in layer 3 - Item")
        print("Input 'Q' to quit, 'B' to go back, 'S' for item search, and 'F' for favorite list")
        in_3 = input("Please input HERE:")
        while True:
            if in_3 == 'Q':
                break
            elif in_3 == 'B':
                layer -=1
                break
            #Jump to search layer
            elif in_3 == 'S':
                layer +=1
                break
            #Jump to favorite list layer
            elif in_3 == 'F':
                layer +=2
                break
            #show chart when price is able to analyse 
            elif in_3 == 'C' and chart == True:
                for price in price_data:
                    #decide which interval to put the price in (By calculate the index of interval in price_interval.keys())
                    index = math.floor( (price - min(price_data)) /interval )
                    for i, key in enumerate(price_interval.keys()):
                        if index == i:
                            price_interval[key] += 1
                #show the result of analysis and the pie chart
                for key, value in price_interval.items():
                    print(key, 'has total', value, 'items')
                chart_show = input("\nShow chart? 'Y' / 'N' (unvaild input equals to 'N')")
                if chart_show == 'Y':
                    color = ['#ff0000', '#d200d2', '#66b3ff', '#28ff28', '#ffff37']
                    plt.figure(figsize=(12, 8))
                    separeted = (0, 0, 0, 0, 0)
                    pictures= plt.pie(
                            list(price_interval.values()),                 # 數值
                            colors = color,                                # 指定圓餅圖的顏色
                            labels = list(price_interval.keys()),          # 分類的標記
                            explode = separeted,                           # 設定分隔的區塊位置
                            pctdistance = 0.65,                            # 數值與圓餅圖的圓心距離
                            radius = 0.7,                                  # 圓餅圖的半徑，預設是1
                            center = (-10,0),                              # 圓餅圖的圓心座標
                            shadow=False)                                  # 是否使用陰影
                    plt.legend(loc = "center left")
                    plt.show()
                    print("\nChart showed")
                print("\nInput 'Q' to quit, 'B' to go back to layer 2, or 'C' to analysis again")
                print("For more feature: 'S' for search, and 'F' for favorite list")
                in_3 = input("Please input HERE:")
            else:
                print("\nUnvaild input!!")
                in_3 = input("Please try again:")
        if in_3 == 'Q':
            break
    #Layer for search
    elif layer == 4:
        print("\nWhich item do you want to search for review?")
        print("Or input 'Q' to quit, 'B' to go back to layer 3")
        in_4 = input("Please Ener HERE:")
        while True:
            if in_4 == 'Q':
                break
            elif in_4 == 'B':
                layer -=1
                break
            else:
                if len(in_4) == 0:
                    print("\nNo input detected!!")
                    in_4 = input("Please try again:")
                #communicate with google search api
                else:
                    in_4 = in_4.replace(' ', '+')
                    json_url = "https://www.googleapis.com/customsearch/v1?cx=" + engine_ID + "&key=" + API_key +"&q=" + in_4
                    print("\nsearching...")
                    json_data = urllib.request.urlopen(json_url)#this line of code sometimes is slow, for unknown reason
                    review_site = json.loads(json_data.read())
                    try:
                        for website in review_site["items"]:
                            print('\n' + website['title'])
                            print("    link:", website['link'])
                    #if no result were found, we will encounter KeyError
                    except KeyError:
                        print("\nNo result found")
                    break
        if in_4 == 'Q':
            break
    #Layer for favorite list
    elif layer == 5:
        print("\nNow in favorite list layer, row", row_count)
        print("Input 'F' to show favorite list")
        print("Or input 'Q' to quit, 'B' to go back to layer 1")
        in_5 = input("Which item in layer 3 do you want to add to favorite list?:")
        while True:
            if in_5 == 'Q':
                break
            elif in_5 == 'B':
                layer -=4
                break
            #in to favorite list edit section
            elif in_5 == 'F':
                print('')
                for fav in sheet.col_values(1):
                    if sheet.col_values(1).index(fav) == 0:
                        print(fav)
                    else:
                        print(sheet.col_values(1).index(fav), fav)
                print(' link: https://docs.google.com/spreadsheets/d/1oMUVfJkpnoMXWhfAuBFKqr78qw8snskTgNYY1M-yVbs/edit?usp=sharing')
                print("\nWant to delete any row or change the editing row?")
                print("Unvalid input will back to favorite list layer") 
                fav_edit = input("input integer to change editing row, input 'D' for delete:")
                #row delete
                if fav_edit == 'D':
                    delete_row = input("\nWhich row do you want delete:")
                    try:
                        delete_row = int(delete_row)
                    except ValueError:
                        print("\nUnvalid input")
                        print("back to favorite list layer")
                        break
                    sheet.update_cell(delete_row+1, 1, '')
                    sheet.update_cell(delete_row+1, 2, '')
                    print("Deleteing row", delete_row)
                    break
                #change the editing row
                else:
                    try:
                        fav_edit = int(fav_edit)
                        row_count = fav_edit
                        print("\nNow in row", fav_edit)
                    except ValueError:
                        print("\nUnvalid input")
                        print("back to favorite list layer")
                    break

            #add new item to favorite list
            elif in_5 in goods_shelf[in_1][in_2]:
                row_count += 1
                sheet.update_cell(row_count, 1, in_5)
                print("\nDone!")
                print("check list in https://docs.google.com/spreadsheets/d/1oMUVfJkpnoMXWhfAuBFKqr78qw8snskTgNYY1M-yVbs/edit?usp=sharing")
                index = goods_shelf[in_1][in_2].index(in_5)
                #if '↪' exist, mean there exist something to remark
                try:
                    if '↪' in goods_shelf[in_1][in_2][index +1]:
                        sheet.update_cell(row_count, 2, goods_shelf[in_1][in_2][index +1])
                    else:
                        sheet.update_cell(row_count, 2, '')
                    break
                except IndexError:
                    break
            else:
                print("\nUnvaild input!!")
                in_5 = input("Please try again:")
        if in_5 == 'Q':
            break

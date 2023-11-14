# coding: utf-8
import urllib.request, urllib.parse, urllib.error
import re
from bs4 import BeautifulSoup
url = "http://www.coolpc.com.tw/evaluate.php"
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser', from_encoding= 'CP950', exclude_encodings=["windows-1252"])
#detect what encoding did BeautifulSoup auto-detected
#it auto detect "windows-1252", so caause tons of glitch
#switch to 'big5', there are some error char '�', so we use 'CP950'
print(soup.original_encoding)
tags = soup.find_all('optgroup')
count = 0
times = 0
for line in tags:
    count +=1
    line = str(line)
    print(line)
    # for cha in line:
    #     try:
    #         #print(cha, end = '')
    #         cha = cha.encode('utf-8')
    #         cha = re.search(r"b\'(.+)\'", str(cha))
    #         #print(cha.group(1), end= '')
    #     except UnicodeEncodeError:
    #         continue
    times +=1
    if times == 10:
        break
print(count)
input()
# Coolpc-WebCrawler
### Overview
this is the final Project for course: \<Introduction to Computers and Programming\>(NCTU 2020 Fall). 
I made a web crawler to get information from coolpc's website(https://coolpc.com.tw/evaluate.php). which is a popular website for purchasing computer hardware.

### Features
the crawler has following feature:
* present infomation of commodities
* present price analysis graph
* able to add items to collection list (online googlesheet)
* provide further information about commodity via google search api

project screenshot
![螢幕擷取畫面 2023-11-16 002104](https://github.com/ChicoChen/Coolpc-WebCrawler/assets/107322822/706202dd-6e89-432c-ac03-bf966981b419)


### How To Use
1. install packages
   * Matplotlib:
      ```
      python -m pip install -U pip
      python -m pip install -U matplotlib
      ```
    * Gspread & oauth2clien:
      ```
      pip install gspread oauth2client
      ```
2. set authorization tokens&keys
     1. apply google credentials.json file
     2. assign it to *auth_json* variable (line 14 of *API_Project.py*)
     3. create a google spreadsheet, make it public, and assign its key to *spreadsheet_key* (line 20 of *API_Project.py*)
     4. choose a search engine, assign it to *engine_ID* and set your google search API key (line 38,39 of *API_Project.py*)
### Update
* 2023/05: setup inconvenience, further improvement await...
* 2023/11: coolpc had changed their website architecture, ~~further update await...~~
* 2023/11: confirm that web structure remain unchange, crawler still usable


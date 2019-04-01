# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 22:21:38 2019

@author: Kunal
"""

# Importing Libraries

import time
import tkinter
import tkinter.scrolledtext as tkst
import urllib.request
import json
from cachetools import TTLCache

#Global variables

cache_key = ''

#Caches (TTL)

query_cache = TTLCache(maxsize = 400, ttl = 60)
results_cache = TTLCache(maxsize = 1000, ttl = 60)


#Class for the API Search Query

class WebQuery:     
    
    def __init__(self, isbn, title, authors):
        self.isbn = isbn
        self.title = title
        self.authors = authors

    def performquery(self):     #Function to perform the API search query
        
        global cache_key,query_cache
        
        #Generating the query URL
        
        url = 'https://www.googleapis.com/books/v1/volumes?q='
        original_url = url
        if self.isbn != '':
            url = url + 'isbn:' + self.isbn
        if self.title != '':
            if url != original_url:
                url = url + '&'
            url = url + 'title:'
            for i in range(0, len(self.title)):
                if self.title[i] == ' ':
                    url = url + '%20'
                else:
                    url = url + self.title[i]
        if len(self.authors) != 0:
            if url != original_url:
                url = url + '&'
            for idx, name in enumerate(self.authors):
                for i in range(0, len(name)):
                    if name[i] == ' ':
                        url = url + '%20'
                    elif name[i] == ',':
                        url = url + '%27'
                    else:
                        url = url + name[i]
        
        relevant_information = []   #To store the ISBN, Title, Authors of each result
        cache_key = url
        
        #Checking if the query has already been cached
        
        if url in query_cache:
            
            start = time.time()
            relevant_information = query_cache[url]
            end = time.time()
            print('Query fetched via cache.Time taken = ' + str(end-start) + ' secs')
            query_cache[url] = relevant_information
            return relevant_information
        
        else:   
        
        #Executing the query via API and storing the JSON results
        
            start = time.time()
            json_obj = urllib.request.urlopen(url).read()
            end = time.time()
            print('Query fetched via API. Time taken = ' + str(end - start) + ' secs')
            data = json.loads(json_obj)
            
            #Reading the relevant results
            
            if 'items' not in data:
                relevant_dataset = []
                return relevant_dataset
            relevant_dataset = data['items']
            for item in relevant_dataset:
                volume_itemset = item['volumeInfo']
                new_item = {}
                if "industryIdentifiers" in volume_itemset:
                    new_item['isbn'] = volume_itemset['industryIdentifiers'][0]['identifier']
                if "title" in volume_itemset:
                    new_item['title'] = volume_itemset['title']
                if "authors" in volume_itemset:
                    new_item['authors'] = volume_itemset['authors']
                if len(new_item) > 0:
                    relevant_information.append(new_item)
            query_cache[url] = relevant_information
            return relevant_information
    


class SearchOutput:
    
    def __init__(self, queryItem):
        
        global query_cache,results_cache,cache_key
        self.output_text = ''
        if len(queryItem) != 0:        
            for item in queryItem:
                if 'title' in item:
                    self.output_text = self.output_text + ' Title: ' + item['title'] + '\n'
                if 'isbn' in item:
                    self.output_text = self.output_text + ' ISBN: ' + item['isbn'] + '\n'
                if 'authors' in item:
                    self.output_text = self.output_text + ' Authors: '
                    for j in item['authors']:
                        self.output_text = self.output_text + j +', '
                    self.output_text = self.output_text[:-2]
                self.output_text = self.output_text + '\n\n'
        else:
            self.output_text = 'No Results'
        
        #Initializing the Output Window
        
        self.output_window = tkinter.Tk()
        self.output_window.title('Result')
        self.output_window.geometry('640x480')
        
        #Adding Widgets
        
        self.output_box =  tkst.ScrolledText(self.output_window, wrap = tkinter.WORD, width = 540, height = 420)
        self.output_box.pack()
        self.output_box.insert(tkinter.INSERT, self.output_text)
        
        #Caching the output
        
        if len(queryItem) != 0:
            results_cache[cache_key] = self.output_text
        
        

#Search Window

class SearchWindow:
    
    def __init__(self):    
        #Create a new Search Window
        
        self.search_window = tkinter.Tk()
        self.search_window.title('Search')
        self.search_window.geometry('400x180')
        
        #Add the Widgets
        
        self.title_label = tkinter.Label(self.search_window, text = 'Title', font = ('Roboto',15)).grid(row = 0)  #Title Label
        self.title_entry = tkinter.Entry(self.search_window, text = '', font = ('Times New Roman', 15), width = 30)
        self.title_entry.grid(row = 0,column = 1)   #Title Entry
        self.isbn_label = tkinter.Label(self.search_window, text = 'ISBN', font = ('Roboto',15)).grid(row = 1)    #ISBN Label
        self.isbn_entry = tkinter.Entry(self.search_window, text = '', font = ('Times New Roman',15), width = 30)
        self.isbn_entry.grid(row = 1, column = 1)    #ISBN Entry
        self.authors_label = tkinter.Label(self.search_window, text = 'Authors', font = ('Roboto',15)).grid(row= 2)   #Author Label
        self.authors_entry = tkinter.Entry(self.search_window, text = '', font = ('Times New Roman',15), width = 30)
        self.authors_entry.grid(row = 2, column = 1)  #Author Entry
        self.author_warning = tkinter.Label(self.search_window, text = 'Seperate authors by commas. No Spaces', font = ('Roboto')).grid(row = 3, column = 1)
        self.submit_button = tkinter.Button(self.search_window, text = 'Submit', font = ('Roboto',15), command = self.execute_search).grid(row = 4,column = 1)   #Submit Button
        
    def execute_search(self):   #Event Listener for Search Button
        
        isbn_search = self.isbn_entry.get()
        title_search = self.title_entry.get()
        authors_search = self.authors_entry.get()
        if (isbn_search != '') or (title_search != '') or authors_search != '':
            queryItem = WebQuery(isbn_search,title_search,authors_search)
            results = queryItem.performquery()
            SearchOutput(results)

class HistoryWindow:
    
    def __init__(self):
        
        global results_cache
        
        #Initializing the History Window
        
        self.history = tkinter.Tk()
        self.history.title('History')
        self.history.geometry('640x480')
        
        #Adding Widgets to the History Window
        
        self.history_box =  tkst.ScrolledText(self.history, wrap = tkinter.WORD, width = 480, height = 420)
        self.history_box.pack()
        self.history_helpful_label = tkinter.Label(self.history, text = 'History from previous 10 minutes', font = ('Roboto', 15)).pack()
        
        self.history_text = ''
        list_of_keys = results_cache.keys()
        for i in list_of_keys:
            self.history_text = self.history_text + results_cache[i]
        self.history_box.insert(tkinter.INSERT, self.history_text)
        
#Home Window        
        
class HomeWindow:
    
    def __init__(self):
        # Initializing the Home Window

        self.home = tkinter.Tk()
        self.home.title("Home")
        self.home.geometry('640x480')
        
        
        # Adding Widgets To Home Window
        
        self.top_heading  =  tkinter.Label(self.home, text = 'Libra', font = ('Open Sans', 50)).pack()    #Header
        self.top_tagline  = tkinter.Label(self.home, text = 'A Simple Way to Search All Your Books', font = ('Roboto', 20)).pack()    #Tagline
        self.empty_label1 = tkinter.Label(self.home, text = '', height = 5).pack()    
        self.search_button = tkinter.Button(self.home, text = 'Search Books', font = ('Roboto', 20), command = self.search_clicked).pack() #Button to open Search Window
        self.empty_label2 = tkinter.Label(self.home, text = '', height = 2).pack()
        self.history_button = tkinter.Button(self.home, text = 'History', font = ('Roboto', 20), command = self.history_clicked).pack()    #Button to open History Window
        
    
    def search_clicked(self):   #Event listener for Search Button on Home Window
        
        SearchWindow()
        
    
    def history_clicked(self):  #Event Listener for History Button on Home Window
        
        HistoryWindow()


# Initializing the Home Window

home_window = HomeWindow()
home_window.home.mainloop()
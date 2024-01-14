#!/usr/bin/env python
# coding: utf-8

# In[99]:


import pandas as pd
import re
import json
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from nltk.sentiment import SentimentIntensityAnalyzer
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
import sqlite3
import spacy
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
#Chatbot Development


# In[ ]:





# In[100]:

app = Flask(__name__)
conn = sqlite3.connect('product_database.db',check_same_thread=False)
cursor = conn.cursor()
nlp = spacy.load("en_core_web_sm")
# In[101]:


# In[102]:

def findavg(column):
    query = f"SELECT AVG({column}) FROM {'products'};"
    cursor.execute(query)
    avg = cursor.fetchone()[0]
    return avg


# In[103]:


query = "SELECT DISTINCT Brand FROM products"
cursor.execute(query)
brands = cursor.fetchall()

# brands = list(brands)
for i in range(len(brands)):
    brands[i] = brands[i][0].lower()
brands.remove("original")
brands.remove("imported")
brands.remove("combo")
brands.remove("a57")


# In[214]:


def extract_integer_from_text(doc):
    for i in doc:
        if i.is_digit:
            return int(i.text)
    return None
def extract_integers_from_text(doc):
    numbers = []
    current_number = ''
    
    for token in doc:
        if token.is_digit:
            current_number += token.text
        elif current_number:
            numbers.append(int(current_number))
            current_number = ''

    if current_number:
        numbers.append(int(current_number))

    return numbers if numbers else None
def extract_numbers_from_text(doc):
    numbers = []
    current_number = ''

    for token in doc:
        if token.like_num or (token.is_punct and token.text == '.'):
            current_number += token.text
        elif current_number:
            numbers.append(float(current_number) if '.' in current_number else int(current_number))
            current_number = ''

    if current_number:
        numbers.append(float(current_number) if '.' in current_number else int(current_number))

    return numbers if numbers else None
def undervalue(value):
    query = f"SELECT Name, Price, URL, Score FROM products WHERE Price < {value} ORDER BY Score DESC, NumOfReviews DESC LIMIT 1"
    cursor.execute(query)
    returning = cursor.fetchone()
    if not returning:
        return f"No product available under {value}"
    final=""
    final+="Name : "
    final+= returning[0]
    final+="\n"
    final+="Price : "
    final+= str(returning[1])
    final+="\n"
    final+="Rating : "
    final+=str(returning[3])
    final+="\n"
    final+="URL : "
    final+=returning[2]
    final+="\n"
    return final
def overvalue(value):
    query = f"SELECT Name, Price, URL, Score FROM products WHERE Price > {value} ORDER BY Score DESC, NumOfReviews DESC LIMIT 1"
    cursor.execute(query)
    returning = cursor.fetchone()
    if not returning:
        return f"No product available under {value}"
    final=""
    final+="Name : "
    final+= returning[0]
    final+="\n"
    final+="Price : "
    final+= str(returning[1])
    final+="\n"
    final+="Rating : "
    final+=str(returning[3])
    final+="\n"
    final+="URL : "
    final+=returning[2]
    final+="\n"
    return final
def undervalues(value):
    query = f"SELECT Name, Price, URL,Score FROM products WHERE Price < {value}"
    cursor.execute(query)
    returning = cursor.fetchall()
    if not returning:
        return f"No products available under {value}"
    final=""
    for i in range(len(returning)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= returning[i][0]
        final+="\n"
        final+="Price : "
        final+= str(returning[i][1])
        final+="\n"
        final+="Rating : "
        final+=str(returning[i][3])
        final+="\n"
        final+="URL : "
        final+=returning[i][2]
        final+="\n"
    return final
def overvalues(value):
    query = f"SELECT Name, Price, URL,Score FROM products WHERE Price > {value}"
    cursor.execute(query)
    returning = cursor.fetchall()
    if not returning:
        return f"No products available under {value}"
    final=""
    for i in range(len(returning)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= str(returning[i][0])
        final+="\n"
        final+="Price : "
        final+= str(returning[i][1])
        final+="\n"
        final+="Rating : "
        final+=str(returning[i][3])
        final+="\n"
        final+="URL : "
        final+=str(returning[i][2])
        final+="\n"
    return final
def between(val1,val2):
    query = f"SELECT Name, Price, URL, Score FROM products WHERE Price BETWEEN {val1} AND {val2}"
    cursor.execute(query)
    returning = cursor.fetchall()
    if not returning:
        return f"No products available between {val1} and {val2}"
    final=""
    for i in range(len(returning)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= str(returning[i][0])
        final+="\n"
        final+="Price : "
        final+= str(returning[i][1])
        final+="\n"
        final+="Rating : "
        final+=str(returning[i][3])
        final+="\n"
        final+="URL : "
        final+=str(returning[i][2])
        final+="\n"
    return final
def undervaluesbrand(brand,value):
    brand = brand[0].upper() + brand[1:]
    query = f"SELECT Name, Price, URL, Score FROM products WHERE Price < {value} AND Brand = ?"
    cursor.execute(query, (brand,))
    returning = cursor.fetchall()
    if not returning:
        return f"No products available under {value} for brand {brand}"
    final=f"Brand : {brand}"
    final+="\n"
    for i in range(len(returning)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= returning[i][0]
        final+="\n"
        final+="Price : "
        final+= str(returning[i][1])
        final+="\n"
        final+="Rating : "
        final+=str(returning[i][3])
        final+="\n"
        final+="URL : "
        final+=returning[i][2]
        final+="\n"
    return final
def overvaluesbrand(brand,value):
    brand = brand[0].upper() + brand[1:]
    query = f"SELECT Name, Price, URL, Score FROM products WHERE Price > {value} AND Brand = ?"
    cursor.execute(query, (brand,))
    returning = cursor.fetchall()
    if not returning:
        return f"No products available under {value} for brand {brand}"
    final=f"Brand : {brand}"
    final+="\n"
    for i in range(len(returning)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= returning[i][0]
        final+="\n"
        final+="Price : "
        final+= str(returning[i][1])
        final+="\n"
        final+="Rating : "
        final+=str(returning[i][3])
        final+="\n"
        final+="URL : "
        final+=returning[i][2]
        final+="\n"
    return final

def betweenbrand(brand,val1,val2):
    brand = brand[0].upper() + brand[1:]
    query = f"SELECT Name, Price, URL, Score FROM products WHERE Price BETWEEN {val1} AND {val2} AND Brand = ?"
    cursor.execute(query, (brand,))
    returning = cursor.fetchall()
    if not returning:
        return f"No products available between {val1} and {val2} of Brand {brand}"
    final=""
    final=f"Brand : {brand}"
    final+="\n"
    for i in range(len(returning)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= str(returning[i][0])
        final+="\n"
        final+="Price : "
        final+= str(returning[i][1])
        final+="\n"
        final+="Rating : "
        final+=str(returning[i][3])
        final+="\n"
        final+="URL : "
        final+=str(returning[i][2])
        final+="\n"
    return final
def undervaluesbrandtop(brand,value,num):
    brand = brand[0].upper() + brand[1:]
    query = f"SELECT Name, Price, URL, Score FROM products WHERE Price < {value} AND Brand = ? ORDER BY Score DESC LIMIT {num}"
    cursor.execute(query, (brand,))
    returning = cursor.fetchall()
    if not returning:
        return f"No {num} products available under {value} for brand {brand}"
    final=f"Brand : {brand}"
    final+="\n"
    for i in range(len(returning)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= returning[i][0]
        final+="\n"
        final+="Price : "
        final+= str(returning[i][1])
        final+="\n"
        final+="Rating : "
        final+=str(returning[i][3])
        final+="\n"
        final+="URL : "
        final+=returning[i][2]
        final+="\n"
    return final
def overvaluesbrandtop(brand,value,num):
    brand = brand[0].upper() + brand[1:]
    query = f"SELECT Name, Price, URL, Score FROM products WHERE Price > {value} AND Brand = ? ORDER BY Score DESC LIMIT {num}"
    cursor.execute(query, (brand,))
    returning = cursor.fetchall()
    if not returning:
        return f"No {num} products available over {value} for brand {brand}"
    final=f"Brand : {brand}"
    final+="\n"
    for i in range(len(returning)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= returning[i][0]
        final+="\n"
        final+="Price : "
        final+= str(returning[i][1])
        final+="\n"
        final+="Rating : "
        final+=str(returning[i][3])
        final+="\n"
        final+="URL : "
        final+=returning[i][2]
        final+="\n"
    return final
def betweenvaluesbrandtop(brand,val1,num,val2):
    brand = brand[0].upper() + brand[1:]
    query = f"SELECT Name, Price, URL, Score FROM products WHERE Price BETWEEN {val1} AND {val2} AND Brand = ? ORDER BY Score DESC LIMIT {num}"
    cursor.execute(query, (brand,))
    returning = cursor.fetchall()
    if not returning:
        return f"No {num} products available between {val1} and {val2} for brand {brand}"
    final=f"Brand : {brand}"
    final+="\n"
    for i in range(len(returning)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= returning[i][0]
        final+="\n"
        final+="Price : "
        final+= str(returning[i][1])
        final+="\n"
        final+="Rating : "
        final+=str(returning[i][3])
        final+="\n"
        final+="URL : "
        final+=returning[i][2]
        final+="\n"
    return final
def words(token):
    dictionary = {
        "above": ["above", "more than", "higher than", "over"],
        "below": ["below", "under", "less than"],
        "between": ["range", "between", "from", "to"],
    }
    for keyword, syn in dictionary.items():
        if token.text.lower() in syn:
            return keyword
    return None

def flagcheck(doc):
    flag1 = False
    flag2 = False
    for word in doc:
        if word.text.lower() == "price":
            flag1 = True
        if word.text.lower() == "rating":
            flag2 = True
    return flag1 and flag2

def ello(doc):
#     conn = sqlite3.connect("product_database.db")
#     cursor = conn.cursor()
    signs = []
    seq = []
    temp = [token.text for token in doc]  # Extracting text from tokens

    for token in doc:
        if words(token):
            keyword = words(token)
            if keyword == "above":
                signs.append('>')
            elif keyword == "below":
                signs.append('<')
        if token.lower_ == "price" :
            seq.append(token.lower_)
        if token.lower_ == "rating":
            seq.append("Score")
    values = extract_numbers_from_text(doc)

    cursor.execute(f"""SELECT * FROM products
    WHERE {seq[0]} {signs[0]} {values[0]} AND {seq[1]} {signs[1]} {values[1]};
    """)
    results = cursor.fetchall()
    final=""
    for i in range(len(results)):
        final+="Product "
        final+=str(i+1)
        final+=" : "
        final+="\n"
        final+="Name : "
        final+= str(results[i][1])
        final+="\n"
        final+="Price : "
        final+= str(results[i][2])
        final+="\n"
        final+="Rating : "
        final+=str(results[i][6])
        final+="\n"
        final+="URL : "
        final+=str(results[i][5])
        final+="\n"
    return final

# In[223]:
greet = ["hi","hello","hey","hola"]
urdugreet = ["kesa","kese","kesi","kes"]
above = ["above", "more than", "higher than", "over"]
below = ["below", "under", "less than"]
def findresponse(query):
    if "fardeen" in query.text:
        return "OMG DID I JUST HEAR FARDEEN! I LOST YAAR ITNA CUTU BACHA HAI KASH MEI FARDEEN HOTA!"
    if "hi" in query.text:
        return "Hello!"
    if "hello" in query.text:
        return "Hello!"
    if flagcheck(query):
        return ello(query)
    if "top" in query.text:
        y = query.text.split()
        x = extract_integers_from_text(query)
        if any(word in query.text for word in below):
            tempbrand = []
            for i in y:
                if i in brands:
                    tempbrand.append(i)
            returningstring = ""
            if len(tempbrand)>1:
                for i in tempbrand:
                    returningstring+=undervaluesbrandtop(i,x[1],x[0])
                    returningstring+="\n"
            else:
                returningstring = undervaluesbrandtop(tempbrand[0],x[1],x[0])
            return returningstring
        if "between" in query.text:
            tempbrand = []
            for i in y:
                if i in brands:
                    tempbrand.append(i)
            returningstring = ""
            if len(tempbrand)>1:
                for i in tempbrand:
                    returningstring+=betweenvaluesbrandtop(i,x[1],x[0],x[2])
                    returningstring+="\n"
            else:
                returningstring = betweenvaluesbrandtop(tempbrand[0],x[1],x[0],x[2])
            return returningstring
        if any(word in query.text for word in above):
            tempbrand = []
            for i in y:
                if i in brands:
                    tempbrand.append(i)
            returningstring = ""
            if len(tempbrand)>1:
                for i in tempbrand:
                    returningstring+=overvaluesbrandtop(i,x[1],x[0])
                    returningstring+="\n"
            else:
                returningstring = overvaluesbrandtop(tempbrand[0],x[1],x[0])
            return returningstring
    if any(word in query.text for word in brands) and "between" in query.text:
        y = query.text.split()
        x = extract_integers_from_text(query)
        if x == None:
            return "I didn't quite get what you meant, can you please repeat yourself"
        tempbrand = []
        for i in y:
            if i in brands:
                tempbrand.append(i)
        returningstring = ""
        if len(tempbrand)>1:
            for i in tempbrand:
                returningstring+=betweenbrand(i,x[0],x[1])
                returningstring+="\n"
        else:
            returningstring = betweenbrand(tempbrand[0],x[0],x[1])
        return returningstring
    if any(word in query.text for word in brands) and "under" in query.text:
        y = query.text.split()
        x = extract_integer_from_text(query)
        if x == None:
            return "I didn't quite get what you meant, can you please repeat yourself"
        tempbrand = []
        for i in y:
            if i in brands:
                tempbrand.append(i)
        returningstring = ""
        if len(tempbrand)>1:
            for i in tempbrand:
                returningstring+=undervaluesbrand(i,x)
                returningstring+="\n"
        else:
            returningstring = undervaluesbrand(tempbrand[0],x)
        return returningstring
    if any(word in query.text for word in brands) and "over" in query.text:
        y = query.text.split()
        x = extract_integer_from_text(query)
        if x == None:
            return "I didn't quite get what you meant, can you please repeat yourself"
        tempbrand = []
        for i in y:
            if i in brands:
                tempbrand.append(i)
        returningstring = ""
        if len(tempbrand)>1:
            for i in tempbrand:
                returningstring+=overvaluesbrand(i,x)
                returningstring+="\n"
        else:
            returningstring = overvaluesbrand(tempbrand[0],x)
        return returningstring
    if any(word in query.text for word in greet):
        return "Hello!"
    if any(word in query.text for word in urdugreet):
        return "theek thaak Alhamdullilah"
    if any(word in query.text for word in below) and "phones" not in query.text:
        x = extract_integer_from_text(query)
        if x == None:
            return "I didn't quite get what you meant, can you please repeat yourself"
        return undervalue(x)
    if any(word in query.text for word in below):
        x = extract_integer_from_text(query)
        if x == None:
            return "I didn't quite get what you meant, can you please repeat yourself"
        return undervalues(x)
    if any(word in query.text for word in above) and "phones" not in query.text:
        x = extract_integer_from_text(query)
        if x == None:
            return "I didn't quite get what you meant, can you please repeat yourself"
        return overvalue(x)
    if any(word in query.text for word in above):
        x = extract_integer_from_text(query)
        if x == None:
            return "I didn't quite get what you meant, can you please repeat yourself"
        return overvalues(x)
    if "between" in query.text:
        x = extract_integers_from_text(query)
        if x == None:
            return "I didn't quite get what you meant, can you please repeat yourself"
        return between(x[0],x[1])
    if "bye" in query.text:
        return "Bye Bye! Hope I was useful! Bye Bye Ehteshaam Bhai"
    if any(word in query.text for word in brands):
        return "Exact names are not searchable yet. Soon I will update the chatbot to search for exact names. Instead of that you can search our database for exact name of a product. Thank you"
    return "I didn't quite get what you meant, can you please repeat yourself"

# In[224]:


def simple_chatbot(query):
    doc = nlp(query.lower())  # Convert the query to lowercase
    return findresponse(doc)


# In[237]:


# user_query = "top 2 samsung phones under 140000"
# response = simple_chatbot(user_query)
# print(response)


# In[158]:


#review based searching
#flask


# In[ ]:


#flask


# In[238]:
# In[239]:

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/new_page')
def new_page():
    return render_template('new_page.html')
@app.route('/new_page2')
def new_page2():
    return render_template('index3.html')
@app.route('/new_page3')
def new_page3():
    return render_template('index4.html')
@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    # Call your chatbot function with user input
    bot_response = simple_chatbot(user_input)
    # bot_response_html = bot_response.replace('\n', '<br>')
    print(f"Generated bot response: {bot_response}")
    return {'bot_response': bot_response}

if __name__ == '__main__':
    app.run(debug=True)


# In[ ]:





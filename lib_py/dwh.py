#!/usr/bin/env python
# coding: utf-8

# Data Warehouse

import os
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3
import requests

STORAGE_PATH = os.path.join("data-lake")
SQL_PATH = os.path.join("dwh.sqlite3")

# Current date as string
now = datetime.now()
now_str = now.strftime("%Y-%m-%d")

log_file_name = os.path.join(
    STORAGE_PATH,
    f"{now_str}.csv",
)
log_file = pd.read_csv(log_file_name)
log_file.head()

stopwords_url = "https://raw.githubusercontent.com/solariz/german_stopwords/master/german_stopwords_full.txt"
stopwords_list = requests.get(stopwords_url, allow_redirects=True).text.split("\n")[9:]

def read_html_file(filename, encoding="utf-8"):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()
    return text

def process_html(text):
    items = text.replace("\n", " ").lower().split(" ")
    items = [i for i in items if len(i) > 1 and i not in stopwords_list]
    return items

def process_newspaper(newspaper):
    filename = newspaper["file_name"]
    encoding = newspaper["encoding"].lower()
    text = read_html_file(filename, encoding)
    bstext = BeautifulSoup(text, "html.parser").text
    items = process_html(bstext)
    count = pd.Series(items).value_counts().to_frame()
    count.columns = ["count"]
    count["word"] = count.index
    count["paper"] = newspaper["name"]
    count["date"] = now_str
    return count

collection = []

def process_wrapper(newspaper):
    name = newspaper["name"]
    try:
        count = process_newspaper(newspaper)
        print(f"[INFO] Processing {name}")
        collection.append(count)
    except:
        print(f"[ERROR] Failt to process {name}")

log_file.apply(process_wrapper, axis=1)

data = pd.concat(collection, axis=0)
print("Data shape:", data.shape)

lockdown = data.loc[data["word"] == "lockdown"]
lockdown.head()

connection = sqlite3.connect(SQL_PATH)
data.to_sql("wordcount", connection, index=False, if_exists="append")
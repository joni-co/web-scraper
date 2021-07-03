#!/usr/bin/env python
# coding: utf-8

# Prepare scraping

import os
from datetime import datetime
import pandas as pd
import requests

SOURCES_PATH = os.path.join("input", "web-sources.csv")
STORAGE_PATH = os.path.join("data-lake")

# Read sources
web_sources = pd.read_csv(SOURCES_PATH)
web_sources.head()

# Current date as string
now = datetime.now()
now_str = now.strftime("%Y-%m-%d")
print("Date:", now_str)

content_dict = {}
text_dict = {}
log_list = []
failing_list = []

def scrape_website(name, url):

    # (1) Run request
    response = requests.get(url, allow_redirects=True)
    content = response.content
    text = response.text

    # (2) File name to store the raw HTML
    file_name = os.path.join(
        STORAGE_PATH,
        f"{now_str}-{name}.html",
    )

    # (3) Write raw HTML
    with open(file_name, "wb") as f:
        f.write(response.content)

    # (4) Fill content_dict and text_dict
    content_dict[name] = response.content
    text_dict[name] = response.text

    # (5) Fill log_list
    log_info = dict(
        name=name,
        date=now_str,
        file_name=file_name,
        status=response.status_code,
        original_url=url,
        final_url=response.url,
        encoding=response.encoding,
    )
    log_list.append(log_info)

def scrape_wrapper(newspaper):
    url = newspaper["url"]
    name = newspaper["id"]
    try:
        scrape_website(name, url)
        print(f"[INFO] Scraped {name} ({url})")
    except:
        failing_list.append((name, url))
        print(f"[ERROR] Failed to scrape: {name} ({url})")


web_sources.apply(scrape_wrapper, axis=1)

log_file_name = os.path.join(
    STORAGE_PATH,
    f"{now_str}.csv",
)
log_df = pd.DataFrame(log_list)
log_df.to_csv(log_file_name)
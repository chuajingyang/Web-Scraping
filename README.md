# Scraping statistics of NCAA Basketball Players
Data is scrapped from https://basketball.realgm.com/ and https://www.sports-reference.com/ using BeautifulSoup.

# Introduction
Each year, the National Basketball Associaton (NBA) holds an annual draft, where 60 players get selected and ther remaining 30-40 players are left undrafted. Majority of these players come from NCAA Basketball. In this project, I scraped data of NCAA Basketball players', such as their on-court statistics, amongst other things such as their age, height, weight, position, etc.

The next part of the project can be found in my other repository, where I tried to predict how players will fair in the draft based on the data scraped in this repository.

# Getting Started

## Prerequisites
Python 3.8, `conda` and `pip`.

## Installation
```
conda install jupyter
conda install -c anaconda numpy pandas
conda install -c conda-forge beautifulsoup4 requests
```

# Running the workflow

## Web Scraping
The web scraping of data between the years 2005 - 2019 can be executed simply with: ```python scraping.py```
To scrape other years, the script can be edited in ```scraping.py```. 
However, the code might not work properly due to the differences in HTML layout patterns in https://www.sports-reference.com/ for earlier years (before 2005).

# Author
Chua Jing Yang

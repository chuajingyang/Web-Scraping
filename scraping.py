import requests
from bs4 import BeautifulSoup, Comment
import re
import string
import numpy as np
import pandas as pd
import time

'''
Scraping for the statistics of the final NCAA college seasons of Drafted/Undrafted NBA players between 2005 and 2019.
These years were chosen as there more advanced statistics were recorded from 2005 onwards.
Draft records (Labels) were scraped from https://basketball.realgm.com/ 
Final season statistics were scraped from https://www.sports-reference.com/
'''

def getColNames(url):
    '''
    Given a basketball.realgm.com url (to scrape the statistics headers), returns the column names of our data
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    perGame = [x.text.strip() for x in soup.find(id='players_per_game').find('thead').find_all('th')][1:]
    perGame.pop(-2)
    
    for i, comment in enumerate(soup.find_all(text=lambda text: isinstance(text, Comment))):
        if comment.find('id="players_advanced"') > 0:
            table = BeautifulSoup(comment, 'html.parser').find("table")
            advanced = [x.text.strip() for x in table.find('thead').find_all('th')][6:25]
            advanced.pop(14)
            
    output = ['ID', 'Name', 'Age', 'Position', 'Height', 'Weight', 'Season']
    output.extend(perGame)
    output.extend(advanced)
    output.append('DraftCategory')
    output.append('DraftPick')
            
    return output


def scrapeRow(url):
    '''
    Given a basketball.realgm.com url, return the statistics and various player details
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    ID = url.split('/')[-1].replace('.html', '')
    name = soup.find('h1').text.strip()
    position = soup.find('p').text.strip().split('\n')[2].strip()
    height, weight = re.findall(r'\d+', soup.find('p').find('p').contents[-1].strip())
    season = soup.find(id='players_per_game').find('tbody').find_all('tr')[-1].find('th').text.strip()
    season = season[0:2] + season[-2:]
    

    row = soup.find(id='players_per_game').find('tbody').find_all('tr')[-1]
    perGame = [x.text.strip() for x in row.find_all('td')]
    perGame.pop(-2)

    for i, comment in enumerate(soup.find_all(text=lambda text: isinstance(text, Comment))):
        if comment.find('id="players_advanced"') > 0:
            table = BeautifulSoup(comment, 'html.parser').find("table")
            
            advanced = list()
            row = table.find('tbody').find_all('tr')[-1]
            advanced = [x.text.strip() for x in row.find_all('td')][5:24]
            if len(advanced) == 18:
                advanced = [''] + advanced 
            advanced.pop(14)
            
    return [ID, name, position, height, weight, season] + perGame + advanced


def getDraftRecords(draftYear):
    '''
    Given a year (between 2005 and 2019 in this case), return a list of players who
    declared their draft eligiblity, along with their age draft category and draft pick.
    '''
    url = f'https://basketball.realgm.com/nba/draft/past_drafts/{draftYear}'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    rows = []

    for player in soup.find_all('tr')[1:]:
        text = player.text.split('\n')

        if len(text) == 14:
            pick, name, age = text[1], text[2], text[8]
            if name == 'Player':
                continue
            else:
                pick = int(pick)
                age = int(age)
                if pick <= 15:
                    rows.append([name, age, 'Top15', pick])
                elif pick <= 30:
                    rows.append([name, age, 'Top30', pick])
                elif pick <= 45:
                    rows.append([name, age, 'Top45', pick])
                else:
                    rows.append([name, age, 'Top60', pick])
        else:
            name, age = text[1], text[5]
            if name == 'Player':
                continue
            else:
                age = int(age)
                rows.append([name, age, 'Undrafted', 80])
        
    return rows


def scrapAndSave(year):
    '''
    Given a year, scrape for all the players drafted/undrafted.
    Due to inconsistent formatting on sports-reference.com and names that
    are recorded differently between the sites, the errors will have to be further 
    cleaned afterwards.
    '''
    data = []
    nonStandardName = []
    duplicates = []
    notFound = []
    errors = []
    
    records = getDraftRecords(year)

    for player in records:
        name, age, labelCat, labelPick = player[0], player[1], player[2], player[3]
        split_name = name.replace('.', '').lower().split(' ')
        if len(split_name) != 2:
            nonStandardName.append([year] + player)
            continue
        else:
            first, last = split_name[0], split_name[1]

        counter = 1
        while True:
            url = f'https://www.sports-reference.com/cbb/players/{first}-{last}-{counter}.html'
            if requests.get(url).status_code == 404:
                counter -= 1
                break
            counter += 1

        if counter > 1:
            sameFinalSeason = []
            
            for i in range(1, counter + 1):
                url = f'https://www.sports-reference.com/cbb/players/{first}-{last}-{i}.html'
                try:
                    season = scrapeRow(url)[5]
                except:
                    continue
                if int(season) == year:
                    sameFinalSeason.append(url)
            if len(sameFinalSeason) == 1:
                url = sameFinalSeason[0]
                row = scrapeRow(url)
                data.append([row[0], name, age] + row[2:] + [labelCat, labelPick])
            else:
                duplicates.append([year] + player)
                
        elif counter == 0:
            notFound.append([year] + player)
        else:
            url = f'https://www.sports-reference.com/cbb/players/{first}-{last}-1.html'
            try:
                row = scrapeRow(url)
                data.append([row[0], name, age] + row[2:] + [labelCat, labelPick])
            except:
                errors.append([year] + player)
    
    return data, nonStandardName, duplicates, notFound, errors


def main():
    '''
    Scrape for the players between 2005-2019 and save each as npy files for further cleaning
    '''
    for year in range(2005, 2020):
        start = time.time()
        out = scrapAndSave(year)
        print(f'Year {year} done! It took {(time.time() - start) / 60} minutes.')
        np.save(f'data/{year}.npy', out) 

if __name__ == "__main__":
    main()
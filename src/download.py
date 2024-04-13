from bs4 import BeautifulSoup
import csv
from database.postgres import Database
import os
import requests

'''
Downloads the latest lotto game data and adds them to the database.
'''

LINK_TYPES = {
    'Saturday Lotto': 'SATURDAY',
    'Monday Lotto': 'MONDAY',
    'Wednesday Lotto': 'WEDNESDAY',
    'OZ Lotto': 'OZ',
    'Powerball': 'POWERBALL',
    'Set for Life': 'SET_FOR_LIFE'
}

DATABASE = Database()

def get_type(anchor: str) -> str:
    anchor_text = anchor.get_text()
    for (key, value) in LINK_TYPES.items():
        if anchor_text.startswith(f"Download {key}"):
            return (value, anchor.get('href'))
    return None

def parse(heading: str, value: str, accumulator: dict):
    if heading == "Draw number":
        accumulator["game"] = int(value)
    elif heading.startswith("Winning Number"):
        if len(value) > 0:
            accumulator["numbers"].append(int(value))
    elif heading.startswith("Supplementary Number") or heading.startswith("Powerball Number"):
        if len(value) > 0:
            accumulator["supplementaries"].append(int(value))

def process(type: str, address: str):
    last_stored = DATABASE.get_latest_game(game_type=type)
    response = requests.get(url=address)
    csv_lines = response.text.splitlines()
    content = csv.reader(csv_lines)
    headings = next(content)

    if last_stored is None:
        last_stored = -1

    try:
        while True:
            row = next(content)
            accumulator = dict()
            accumulator["numbers"] = []
            accumulator["supplementaries"] = []

            for index in range(0, min(len(headings), len(row))):
                parse(headings[index], row[index], accumulator)

            if (accumulator["game"] > last_stored):
                print(f"{type} #{accumulator['game']}: {accumulator['numbers']} &  {accumulator['supplementaries']}")
                DATABASE.add(type, accumulator['game'], accumulator['numbers'], accumulator['supplementaries'])
    except StopIteration:
        DATABASE.commit()
        pass

sourceUrl = os.getenv("LOTTO_SOURCE", "https://www.lotterywest.wa.gov.au/results/frequency-charts")
response = requests.get(url=sourceUrl)
soup = BeautifulSoup(response.text, 'html.parser')
entries = [x for x in [get_type(c) for c in soup.find_all('a')] if x]
for (type, url) in entries:
    game = DATABASE.get_latest_game(type)
    process(type=type, address=url)

DATABASE.close()

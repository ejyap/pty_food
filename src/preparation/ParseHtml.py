import pandas as pd
from bs4 import BeautifulSoup

with open('..\\..\\data\\raw\\RestList0000', 'r+', encoding="utf-8") as file:
    html = file.read()

soup = BeautifulSoup(html, 'lxml')

matches = soup.findall('main', {'class': 'dg-page-rest'})

print(len(matches))
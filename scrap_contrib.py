#!/usr/bin/env python3

import re
import csv

import requests
from bs4 import BeautifulSoup

with open('documents.csv', 'w') as csvfile:
    out = csv.writer(csvfile)
    out.writerow(['code_postal', 'ville', 'date', 'qui', 'url', 'doc'])
    r = requests.get('https://granddebat.fr/pages/comptes-rendus-des-reunions-locales')
    h = BeautifulSoup(r.text, 'html.parser')
    for l in h.find_all(class_='ligne'):
        c = l.find_all(class_='cellule')
        code_postal = c[0].string
        date = c[1].string
        ville = l.find(class_='cellule-uppercase').string
        qui = c[3].string
        for u in c[2].find_all('a'):
            out.writerow([code_postal, ville, date, qui, u.get('href').strip(), u.string])

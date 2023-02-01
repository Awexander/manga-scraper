from unidecode import unidecode
import string
import html
import re

def clean_title(title: str):
    title = convert_title_to_ascii(title)
    for a in title.split(' '):
        if len(a) <= 1:
            if a in string.punctuation:
                title = title.replace(a, '')
    
    return re.sub(' +', ' ', title).lower()

def convert_title_to_ascii(title: str):
    title = html.unescape(title)
    title = unidecode(title)

    return title

def percentage_match(num_title, num_url):
    return (num_title / num_url) * 100

title_string = 'I Became a Renowned Family’s Sword Prodigy'
title_string = 'Legend of Asura – The Venom Dragon'
title_string = 'Warrior High School – Dungeon Raid Department'
title_string = 'the S-classes hero i ranked'

url_string = 'the-s-classes-hero-i-ranked'
title_clean = clean_title(title_string)
match_list = [word in url_string.split('-') for word in title_clean.split(' ')]

percent = percentage_match(len([f for f in match_list if f is True]), len(url_string.split('-')))
print(percent)
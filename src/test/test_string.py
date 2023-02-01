

import string
from unidecode import unidecode
import html
import re

clean_str = ''
str_name ="Legend of Asura \u2013 The Venom Dragon!!!!!"
title = html.unescape(str_name)
title = unidecode(title)

for a in title.split(' '):
    if len(a) <= 1:
        if a in string.punctuation:
            title = title.replace(a, '')

clean_str = re.sub(' +', ' ', title).lower()
punctuation = r"""!"#$%&'()*+,./:;<=>?@[\]^_`{|}~"""
punctuation_table = str.maketrans("", "", punctuation)

for name in str_name.split("-"):
    name.translate(punctuation_table)
    print(name)

print([f.translate(punctuation_table) for f in clean_str.split(" ")])
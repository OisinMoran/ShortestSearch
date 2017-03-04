# NOTE: This does not search or use Google,
#       it only generates search suggestions

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from collections import Counter
import itertools
import re
import time

# Function to split a string into words
def getWords(text):
    return re.compile('\w+').findall(text)

# Function to check if a string can be a number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

## Get frequency of 20k most common English words
# File from https://github.com/first20hours/google-10000-english
with open('20k.txt', mode='r') as f:
    content = f.readlines()
# Remove whitespace
content = [x.strip() for x in content]
# Create a dict of of the form - word:rank_in_list
mydict = {word.upper():(index+1) for index,word in enumerate(content)}

MIN_FREQ = len(mydict)

## Read data from URL
given_url = "https://www.ted.com/talks/david_eagleman_can_we_create_new_senses_for_humans"
req = Request(given_url, headers={"User-Agent": "Mozilla/5.0"})
html = urlopen(req).read()
soup = BeautifulSoup(html)

## Extract words from site data
# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()

# get text
text = soup.get_text()
#print(text)

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
text = '\n'.join(chunk.upper() for chunk in chunks if chunk)
#print(text)

## Split into words
words = getWords(text)
# Get rid of numbers
words = [x for x in words if not is_number(x)]

# TF-IDF
word_scores = Counter(words)
for word in word_scores:
    if word in mydict:
        word_scores[word] = word_scores[word]*(mydict[word])
    else:
        word_scores[word] = word_scores[word]*MIN_FREQ

# Sort words based on score
sorted_words = sorted(word_scores, key=word_scores.get, reverse = True)
# print(sorted_words)
print("{} words found on page.".format(len(sorted_words)))

# Manual example of results that work
hits = ['TED VEST', 'TED EAGLEMAN', 'TED SENSES']
min_len = float('inf')
search_no = 1
MIN_WORDS_IN_PHRASE = 2
MAX_WORDS_IN_PHRASE = 2

print("Search Suggestions:")
## Generate search phrases
for L in range(MIN_WORDS_IN_PHRASE, MAX_WORDS_IN_PHRASE+1):
    for subset in itertools.combinations(sorted_words, L):
        phrase = "{} {}".format(subset[0], subset[1])
        if len(phrase) <= min_len:
            print("{}: {}".format(search_no, phrase))
            search_no += 1
            if phrase in hits:
                print('-AW NICE-')
                min_len = len(phrase)
            time.sleep(0.2)

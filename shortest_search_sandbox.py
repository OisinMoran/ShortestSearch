from urllib.request import Request, urlopen
from collections import Counter
from bs4 import BeautifulSoup, Comment, Doctype
import itertools
import time
import re

MIN_WORDS_IN_PHRASE = 2
MAX_WORDS_IN_PHRASE = 2
TITLE_FACTOR = 10
LINK_FACTOR = 0.1

# Function to split a string into words
def get_words(text):
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

min_freq = len(mydict)

## Read data from URL
given_url = "https://www.ted.com/talks/david_eagleman_can_we_create_new_senses_for_humans"
#given_url = "http://www.paulgraham.com/writing44.html"
req = Request(given_url, headers={"User-Agent": "Mozilla/5.0"})
html = urlopen(req).read()
soup = BeautifulSoup(html, "html.parser")

## Extract words from site data
# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()
# Delete comments and doctype
for element in soup(text=lambda text: isinstance(text, Comment) or isinstance(text, Doctype)):
    element.extract()
# Get text
text = " ".join(item.strip() for item in soup.find_all(text=True))
# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
text = '\n'.join(chunk.upper() for chunk in chunks if chunk)
## Split into words
words = get_words(text)
# Get rid of numbers
words = [x for x in words if not is_number(x)]


# Get words in title (these will score higher)
title = [word.upper() for word in get_words(soup.title.string)]
# Get words in links (these will score lower)
link_text = []
for link in soup.findAll('a'):
    if link.string:
        link_text += [word.upper() for word in get_words(link.string)]

# TF-IDF
word_scores = Counter(words)
for word in word_scores:
    if word in title:
        word_scores[word] = word_scores[word]*TITLE_FACTOR
    elif word in link_text:
        word_scores[word] = word_scores[word]*LINK_FACTOR
        
    if word in mydict:
        word_scores[word] = word_scores[word]*(mydict[word])
    else:
        word_scores[word] = word_scores[word]*min_freq

print("{} words found on page.".format(len(word_scores)))

## Generate search phrases
search_phrases = {}
for L in range(MIN_WORDS_IN_PHRASE, MAX_WORDS_IN_PHRASE+1):
    # Note searching 'x,y' is not same as 'y,x' so combinations may be suboptimal, but faster, here
    for subset in itertools.combinations(word_scores, L): 
        phrase = " ".join(subset)
        score = sum([word_scores[word] for word in subset])
        search_phrases[phrase] = score

sorted_phrases = sorted(search_phrases, key=search_phrases.get, reverse=True)
print(sorted_phrases[0:20])


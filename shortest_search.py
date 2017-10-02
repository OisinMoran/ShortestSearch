from googleapiclient.discovery import build
from urllib.request import Request, urlopen
from collections import Counter
from bs4 import BeautifulSoup, Comment, Doctype
import configparser
import itertools
import re

## Read configuration file for API access details
config = configparser.ConfigParser()
config.read('CSE_config.ini')
# Get custom search id and developer key from config file
# Get your own at:
# https://developers.google.com/custom-search/json-api/v1/overview
my_cse_id = config['CSE']['cse_id']
dev_key = config['CSE']['dev_key']

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

# Function to search Google using their CSE API
def google_search(search_term, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=dev_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

# Function to find the shortest phrase to Google to ensure given url is first result
# num_results is an optional parameter to get the n shortest results rather than just the shortest
# run_till_payment_error can be set to false if we wish to conserve free API calls
def shortest_search(given_url, num_results=1, run_till_payment_error=True):
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

    #print("{} words found on page.".format(len(word_scores)))

    ## Generate search phrases
    search_phrases = {}
    for L in range(MIN_WORDS_IN_PHRASE, MAX_WORDS_IN_PHRASE+1):
        # Note searching 'x,y' is not same as 'y,x' so combinations may be suboptimal, but faster, here
        for subset in itertools.combinations(word_scores, L): 
            phrase = " ".join(subset)
            score = sum([word_scores[word] for word in subset])
            search_phrases[phrase] = score
            
    # Sort search phrases based on their scores
    sorted_phrases = sorted(search_phrases, key=search_phrases.get, reverse=True)

    ## Perform Search
    #print("Search Hits:")
    min_len = float('inf')
    search_no = 0
    successful_searches = [];
    for search_phrase in sorted_phrases:
        # If we have enough search terms and don't want to keep trying for shorter ones
        if (len(successful_searches) == num_results) and not run_till_payment_error:
            return successful_searches
        elif len(search_phrase) <= min_len:
            try:
                result = google_search(search_phrase, my_cse_id, num=1)
            except:
                break
            first_url = result[0]['link']
            search_no += 1
            if first_url == given_url:
                #print("{}: {}".format(search_no, search_phrase))
                successful_searches.append(search_phrase)
                min_len = len(search_phrase)

    if run_till_payment_error:
        return successful_searches[-num_results:]
    else:
        # While we could return the same as above to give equal or better results
        # This approach ensures consistency and avoids unpredictable behaviour
        return successful_searches[:num_results]

print(shortest_search("http://www.paulgraham.com/writing44.html", 1, False))
print(shortest_search("https://www.ted.com/talks/david_eagleman_can_we_create_new_senses_for_humans"))

> **WARNING**: Automated querying is prohibited by the terms of service of Google and any other search engine. Programmatic searches must therefore be done through Google's Custom Search JSON/Atom API - https://developers.google.com/custom-search/json-api/v1/overview.

# ShortestSearch
Program to find the shortest phrase to Google to ensure a given URL is the first result

## Motivation
Standard URLs are hard to remember and take too long to type; URL-shorteners give links that are quicker to type but even harder to remember; and when instructing someone to Google something we often give them too much information.

This aims to perfect the art of *"It should be the first result if you Google 'x y z' "*.

## Usage
Example Input: "https://www.ted.com/talks/david_eagleman_can_we_create_new_senses_for_humans"

Example Output: "TED VEST"

---

**Note:** Google's search results are location dependent, therefore:
* For a given URL, the shortest phrase will not necessarily be the same for everyone
* A given phrase may not return the intended URL as the first search result for everyone

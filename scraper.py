import re
from urllib.parse import urlparse, urldefrag, urljoin
import urllib.robotparser
from bs4 import BeautifulSoup
from collections import defaultdict

freqWords = dict()
longestPageCnt, longestPage = 0, None
UniquePages = set()
subDomainFreq = defaultdict(set)

stopWords = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves"
}

"""
TRAPS FOUND:

url:  http://www.ics.uci.edu/~dvk/pub/SIGMOD09_dvk.html
2026-04-28 19:52:32,489 - Worker-0 - INFO - Downloaded http://www.ics.uci.edu/~dvk/pub/C16_SIGMOD14_Jeffrey.ppsx, status <200>, using cache ('styx.ics.uci.edu', 9004).
url:  http://www.ics.uci.edu/~dvk/pub/C16_SIGMOD14_Jeffrey.ppsx
Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.

026-04-28 21:21:20,594 - Worker-0 - INFO - Downloaded https://www.ics.uci.edu/~dsm/dyn/release/files/zImage_paapi, status <200>, using cache ('styx.ics.uci.edu', 9004).
Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.
Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.

2026-04-28 21:21:41,847 - Worker-0 - INFO - Downloaded http://dynamo.ics.uci.edu/changelog.txt, status <200>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:21:42,361 - Worker-0 - INFO - Downloaded http://dynamo.ics.uci.edu/files/zImage_paapi, status <200>, using cache ('styx.ics.uci.edu', 9004).
Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.
Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.

2026-04-28 21:23:01,393 - Worker-0 - INFO - Downloaded http://www.ics.uci.edu/~shantas/publications/20-secret-sharing-aggregation-TKDE-shantanu, status <200>, using cache ('styx.ics.uci.edu', 9004).
Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.

2026-04-28 21:29:16,647 - Worker-0 - INFO - Downloaded https://ics.uci.edu/~dechter/publications/r48a.html, stat

2026-04-28 21:30:39,038 - Worker-0 - INFO - Downloaded https://ics.uci.edu/~dechter/r47.html, status <404>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:30:39,548 - Worker-0 - INFO - Downloaded https://ics.uci.edu/~dechter/r48a.html, status <404>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:30:40,057 - Worker-0 - INFO - Downloaded https://ics.uci.edu/~dechter/r48.html, status <404>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:30:40,566 - Worker-0 - INFO - Downloaded https://ics.uci.edu/~dechter/r49a.html, status <404>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:30:41,074 - Worker-0 - INFO - Downloaded https://ics.uci.edu/~dechter/r49.html, status <404>,


2026-04-28 21:32:35,453 - Worker-0 - INFO - Downloaded https://www.ics.uci.edu/~dechter/acp_award.html, status <200>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:32:35,995 - Worker-0 - INFO - Downloaded https://www.ics.uci.edu/~dechter/talks.html, status <200>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:32:36,607 - Worker-0 - INFO - Downloaded https://www.ics.uci.edu/~dechter/talks/DeepLearn17-Outline, status <200>, using cache ('styx.ics.uci.edu', 9004).
Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.
Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.

2026-04-28 21:35:59,681 - Worker-0 - INFO - Downloaded http://www.ics.uci.edu/~darkhipo, status <200>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:36:00,203 - Worker-0 - INFO - Downloaded http://www.ics.uci.edu/~rasadi, status <500>, using cache ('styx.ics.uci.edu', 9004).

2026-04-28 21:36:15,418 - Worker-0 - INFO - Downloaded https://ics.uci.edu/people/shuang-zhao, status <608>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:36:15,927 - Worker-0 - INFO - Downloaded https://ics.uci.edu/people/erik-sudderth, status <608>, using cache ('styx.ics.uci.edu', 9004).
2026-04-28 21:36:16,435 - Worker-0 - INFO - Downloaded https://ics.uci.edu/people/gopi-meenakshisundaram, status <608>, using cache ('styx.ics.uci.edu', 9004).
"""

valid_domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]

MIN_CONTENT_BYTES = 500
MAX_CONTENT_BYTES = 10 * 1024 * 1024
MIN_WORD_COUNT = 50

def scraper(url, resp):

    global longestPage, longestPageCnt

    # TODO: Add other codes that are valid
    if not is_valid(url) or resp.status != 200 or not resp.raw_response:
        return []

    content = resp.raw_response.content
    if not content or len(content) < MIN_CONTENT_BYTES:
        return []
    
    if len(content) > MAX_CONTENT_BYTES:
        return []

    print("url: ", url)
    
    # open html file and lowercase the words and split in array
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    
    # MAYBE: Remove non-text HTML Tags
    for tag in soup(['script', 'noscript', 'style']):
        tag.decompose()

    # TODO: are we allowed to use regex or tokenizer?
    page_text = soup.get_text(separator=" ").lower()
    text = re.findall(r"\b[a-z0-9]+(?:'[a-z]+)?\b", page_text)
            
    if len(text) < MIN_WORD_COUNT:
        return []

    # getting frequency of words, exluding stop words
    for word in text:
        if word not in stopWords:
            freqWords[word] = freqWords.get(word,0) + 1
    
    # finding longest page
    if len(text) > longestPageCnt:
        longestPage = url
        longestPageCnt = len(text)

    # finding all unique pages
    clean_url, _ = urldefrag(url)
    UniquePages.add(clean_url)

    # finding subdomains
    parsed = urlparse(url)
    subdomain = parsed.netloc
    subDomainFreq[subdomain].add(clean_url)

    # extract links
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    valid_status_codes = set([200])

    # TODO: change to valid_status_codes
    if resp.status != 200 or not resp.raw_response:
        return []

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    links = []

    for tag in soup.find_all("a", href=True):
        href = tag.get("href")
        if not href or href.startswith(('javascript:', 'mailto:', '#', 'tel:')):
            continue
        absolute = urljoin(url, href)
        clean, _ = urldefrag(absolute)
        links.append(clean)

    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # doku.php is a trap
    # gitlab.ics.uci.edu
    # */events/*
    # grape.ics 

    #TODO: status code errors

    global valid_domains
    
    traps = {"calendar", "events", "doku.php"}

    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        
        netloc = parsed.netloc

        if not any(netloc == domain or netloc.endswith("." + domain) for domain in valid_domains):
            return False
        
        if "gitlab" in netloc or "grape" in netloc:
            return False
        
        if re.match(r"^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$", parsed.path):
            return False
        
        path_lower = parsed.path.lower()
        query_lower = parsed.query.lower() # its there
        for invalid in traps:
            if invalid in path_lower or invalid in query_lower:
                return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|pps|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

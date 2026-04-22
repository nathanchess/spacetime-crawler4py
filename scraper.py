import re
from urllib.parse import urlparse, RobotFileParser, urldefrag
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

def scraper(url, resp):
    if not is_valid(url):
        return []

    print("url: ", url)
    
    # open html file and lowercase the words and split in array
    resp = BeautifulSoup(resp.raw_response.content, 'html.parser')
    text = resp.get_text().lower().split(" ")
    
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
    subDomainFreq[subdomain].add(urldefrag(url))

    



    
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

    if resp.status not in valid_status_codes:
        return []

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    links = soup.find_all('a')


    valid_next_links = []

    for link in links:
        parsed = urlparse(link)
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt" )
        rp.read()
        if rp.can_fetch("*", link):
            valid_next_links.append(link.get('href'))
            
    return valid_next_links
    #return [link.get('href') for link in links]

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # doku.php is a trap
    # gitlab.ics.uci.edu
    # */events/*
    # grape.ics 

    traps = set()

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.netloc not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
            return False
        if url in traps:
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

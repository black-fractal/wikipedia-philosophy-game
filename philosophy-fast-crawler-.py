'''''''''''''''''''''''''''''''''
Getting to Philosophy Faster!
https://github.com/black-fractal/wikipedia-philosophy-game

@black-fractal
Vahid Khodabakhshi,
vkhodabakhshi@ce.sharif.edu
January 8, 2021
'''''''''''''''''''''''''''''''''

import json
import logging
import requests
from time import sleep
from datetime import datetime

from bs4 import BeautifulSoup

VERBOSE = True
CRAWL_STATE = 'NO-STATE'

'''---------------------------------------------------------
The function traverses Wikipedia links and stores the path
leading to the target from the initial link in the form of
a list of tuples named article_chain.
---------------------------------------------------------'''
def traverse_link( link, target, threshold ):

    article_chain = list( tuple() )                     # Create a list of tuples data structure to maintain visited links
    article_chain.append( (fetch_title(link), link) )   # Add the initial (title, link) into the article_chain data struture
    log( '*** Crawling is starting..' )
    log( '{:30s}-->\t\t{:50s}'.format( fetch_title(link), link ) )
    
    while continue_crawl( article_chain, target, threshold ):

        title, link = fetch_first_link( link )          # Fetching the first (title, link) from each article page
        log( '{:30s}-->\t\t{:50s}'.format( fetch_title(link), link ) )
        sleep( 1 )                                      # Pause for a second for avoiding flood Wikipedia with requests.
        article_chain.append( (title, link) )           # Add the new link and it's title into article_chain
        
    log( '*** Crawling is finished!' )
    return article_chain

'''-----------------------------------------------------
The function specifies how long the search will last.
-----------------------------------------------------'''
def continue_crawl( article_chain, target, threshold ):
    
    global CRAWL_STATE                                      # Make namespace of CRAWL_STATE global
    last_title = article_chain[-1][0]                       # Last visited article title
    last_link = article_chain[-1][1]                        # Last visited article link
    target_title = target.split('/')[-1]
    search_history = [ x[1] for x in article_chain ][:-1]   # All previous articles' link
    length = len( article_chain )

    if last_link in search_history:                         # If a duplicate link found! (The crawler has got stuck in a loop!)
        log( f'*** A loop was appeard! the article [{last_title}] is visited again!' )
        CRAWL_STATE = 'A loop was appeard! the article [{}] is visited again!'.format( last_title )
        return False

    if last_link.lower() == target.lower():                 # If the target link is found!
        log( f'*** The target artice [{target_title}] is visited after {length} articles!' )
        CRAWL_STATE = 'The target artice [{}] is visited after {} articles!'.format( target_title, length )
        return False
    
    if length >= threshold:                                 # If number of visited links was more than threshold
        log( f'*** Unfortunately, the target artice was not found after {length} links visited!' )
        CRAWL_STATE = 'Unfortunately, the target artice was not found after {} links visited!'.format( length )
        return False
    
    return True                                             # Going on..

'''----------------------------------------------------------------------
The function returns the title of an article based on the input link.
----------------------------------------------------------------------'''
def fetch_title( link ):
    res = requests.get( link )
    soup = BeautifulSoup( res.content, 'html.parser' )
    return soup.find( 'h1' ).text

'''----------------------------------------------------------------
The function fetches the first link on the page of the article
based on the input link. During the search for the first link,
links in parentheses or the form of references or out of the
main paragraphs are not considered.
----------------------------------------------------------------'''
def fetch_first_link( link ):
    
    base_url = 'https://en.wikipedia.org'
    res = requests.get( link )
    striped_brackets = strip_brackets( res.content )    # Remove all nested parentheses and their contents
    soup = BeautifulSoup( striped_brackets, 'html.parser' )

    for i in soup.find_all( 'p' ):
        for j in i.find_all( 'a', recursive=True ):
            if not j.find_parent('span'):
                if( is_correct_link( j.get( 'href' ) ) ):
                    return j.text, base_url + j.get( 'href' )

    # if a page with format [x may refer to:] as apeard:
    for i in soup.find_all( 'a', recursive=True ):
        if not i.find_parent('div', attrs={'class' : 'hatnote navigation-not-searchable'} ):
            if i.get( 'href' ):
                if( is_correct_link( i.get( 'href' ) ) ):
                    return i.text, base_url + i.get( 'href' )

'''-------------------------------------------------------------------
The function returns True if the input link does not contain ':' which
is using for Wikipedia Special links and contains 'wiki', because
all the correct links are in the form of /wiki/...
-------------------------------------------------------------------'''
def is_correct_link( link ):
    return link.find(':')==-1 and link.find('wiki')==1

'''--------------------------------------------------------------------------
The function removes all parentheses and all contents. the function
supports nested parentheses and ignores all parentheses in the html tags.
--------------------------------------------------------------------------'''
def strip_brackets( text ):
    paren_level = 0
    link_level = 0
    result = ''
    for letter in  str( text ):

        # Check html tags
        if paren_level < 1:
            if letter == '>':
                link_level -= 1
            if letter == "<":
                link_level += 1

		# Check for parentheses
        if link_level < 1:
            if letter == '(':
                paren_level += 1
            if paren_level > 0:
                result += ' '
            else:
                result += letter
            if letter == ')':
                paren_level -= 1
        else:
            result += letter

    return bytes( result, 'utf-8' ) # cast into the bytes format which is prepraed for BeautifulSoup method

'''-------------------------------------------------
The function set the initial config for logging
-------------------------------------------------'''
def set_log_config():
    logging.basicConfig( format='\033[95m[%(asctime)s] \033[93m%(message)s\033[0m', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO )

'''-----------------------------------------------------------
The function print log if global variable VERBOSE is True
-----------------------------------------------------------'''
def log( msg ):
    if VERBOSE:
        logging.info( msg )

'''-----------------------------------------------
The function writes all the (title, link) pairs
of data structure article_chain to a JSON file.
in addition to the final state of crawling.
-----------------------------------------------'''
def write_to_json_file( out_file, json_data ):
    with open( out_file, 'a', encoding='utf-8' ) as handler:
        handler.writelines( json_data )

'''----------------------------------------------------
The function returns a string contain date and time
example: article-chain-[2021-01-03]-[21-50-45].json.
----------------------------------------------------'''
def make_file_name( extension ):
    return '.\\json\\article-chain-{}.{}'.format( datetime.today().strftime('[%Y-%m-%d]-[%H-%M-%S]'), extension )

'''----------------------------------------------------
The function returns a json dump
----------------------------------------------------'''
def make_json( article_chain, target_link ):
    out = dict()
    out['search-history'] = dict( article_chain )
    out['target-link'] = target_link
    out['crawl-final-state'] = CRAWL_STATE
    return json.dumps( out, indent=4, ensure_ascii=False )

'''--------------
Main function.
--------------'''
def main():
    set_log_config()
    random_article_url = 'https://en.wikipedia.org/wiki/Special:Random'
    target_link = 'https://en.wikipedia.org/wiki/Philosophy'
    
    article_chain = traverse_link( random_article_url, target_link, 100 )
    write_to_json_file( make_file_name('json'), make_json(article_chain, target_link) )

if __name__ == "__main__":
    main()

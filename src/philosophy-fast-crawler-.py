'''''''''''''''''''''''''''''''''
Getting to Philosophy Faster!
https://github.com/black-fractal/wikipedia-philosophy-game

@black-fractal
Vahid Khodabakhshi,
vkhodabakhshi@ce.sharif.edu
Initiated Date: January 2, 2021
Last modified date: January 15, 2021

'''''''''''''''''''''''''''''''''

import glob, os
import json
import logging
from time import sleep
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
# from anytree import Node, RenderTree
# from anytree.exporter import DotExporter

REPETITIVE_TITLE_LINK       = dict()        # For when a link was seen again 
VERBOSE                     = True          # For logging
CRAWL_STATE                 = 'NO-STATE'    # Final state of the crawling
BAD_FILES_COUNTER           = 0             # The counter of bad files which have error in reading
IF_IS_REPITITIVE            = 0             # A boolean counter (0, 1) which will be 1 if a repititive article found
                                            # Colors codes for colorizing the output terminal
BLACK                       = '\u001b[30m'
RED                         = '\u001b[31m'
GREEN                       = '\u001b[32m'
YELLOW                      = '\u001b[33m'
BLUE                        = '\u001b[34m'
MAGENTA                     = '\u001b[35m'
CYAN                        = '\u001b[36m'
WHITE                       = '\u001b[37m'
RESET                       = '\u001b[0m'
BACKGROUND_BRIGHT_BLACK 	= '\u001b[40;1m'
BACKGROUND_BRIGHT_RED 		= '\u001b[41;1m'
BACKGROUND_BRIGHT_GREEN 	= '\u001b[42;1m'
BACKGROUND_BRIGHT_YELLOW 	= '\u001b[43;1m'
BACKGROUND_BRIGHT_BLUE 		= '\u001b[44;1m'
BACKGROUND_BRIGHT_MAGENTA 	= '\u001b[45;1m'
BACKGROUND_BRIGHT_CYAN		= '\u001b[46;1m'
BACKGROUND_BRIGHT_WHITE 	= '\u001b[47;1m'

'''---------------------------------------------------------
The function traverses Wikipedia links and stores the path
leading to the target from the initial link in the form of
a list of tuples named article_chain.
---------------------------------------------------------'''
def traverse_link( link, target, threshold = 40, sleep_time = 1, files_history=None ):

    article_chain = list( tuple() )                         # Create a `list of tuples` data structure to maintain visited links
    
    log()
    log( '*** Crawling is starting..' )
    title, link = fetch_title_and_link( link )              # Fetching the title and (redirected) link using the given link
    article_chain.append( (title, link) )                   # Add the initial (title, link) into the article_chain data structure
    log( '{:30s}-->\t\t{:50s}'.format( title, link ) )
    
    while continue_crawl( article_chain, target, threshold, files_history ):

        title, link = fetch_title_and_link( fetch_first_link( link ) )  # Fetching the first (title, link) from each article page
        article_chain.append( (title, link) )               # Add the new link and its title into article_chain
        log( '{:30s}-->\t\t{:50s}'.format( title, link ) )
        sleep( sleep_time )                                 # Pause for some moment for avoiding flood Wikipedia with requests.
        
    log( '*** Crawling is finished!' )
    log()
    return article_chain

'''-----------------------------------------------------
The function specifies how long the search will last.
-----------------------------------------------------'''
def continue_crawl( article_chain, target, threshold, files_history ):
    
    global REPETITIVE_TITLE_LINK                            # Make namespace of REPETITIVE_TITLE_LINK global
    global CRAWL_STATE                                      # Make namespace of CRAWL_STATE global
    global IF_IS_REPITITIVE                                 # Make namespace of IF_IS_REPITITIVE global
    last_title = article_chain[-1][0]                       # Last visited article title
    last_link = article_chain[-1][1]                        # Last visited article link
    target_title = target.split('/')[-1]
    search_history = [ x[1] for x in article_chain ][:-1]   # All previous articles' link
    length = len( article_chain )

    if last_link in search_history:                         # If a duplicate link found! (The crawler has got stuck in a loop!)
        log( f'*** A loop was appeard! the article [{last_title}] is visited again!' )
        REPETITIVE_TITLE_LINK[ last_title ] = last_link
        CRAWL_STATE = 'A loop appeared! the article [{}] is visited again!'.format( last_title )
        IF_IS_REPITITIVE = 1
        return False

    if last_link.lower() == target.lower():                 # If the target link is found!
        log( f'*** The target artice [{target_title}] is visited after {length} articles!' )
        CRAWL_STATE = 'The target artice [{}] is visited after {} articles!'.format( target_title, length )
        return False
    
    if length >= threshold:                                 # If the number of visited links was more than threshold
        log( f'*** Unfortunately, the target article was not found after {length} links visited!' )
        CRAWL_STATE = 'Unfortunately, the target article was not found after {} links visited!'.format( length )
        return False
    
    if search_in_files_history( last_link, files_history, article_chain ): # If the sequence found in files_history
        return False
    
    return True                                             # Going on..

'''----------------------------------------------------------------------
The function returns the title of an article based on the input link.
----------------------------------------------------------------------'''
def fetch_title_and_link( link ):
    link = requests.head( link, allow_redirects=True ).url
    res = requests.get( link )
    soup = BeautifulSoup( res.content, 'html.parser' )
    title = soup.find( 'h1' ).text.title()
    return title, link

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
                    return urljoin(base_url, j.get('href') )

    # if a page with format [x may refer to:] as apeard:
    for i in soup.find_all( 'a', recursive=True ):
        if not i.find_parent('div', attrs={'class' : 'hatnote navigation-not-searchable'} ):
            if i.get( 'href' ):
                if( is_correct_link( i.get( 'href' ) ) ):
                    return urljoin(base_url, i.get('href') )

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

'''----------------------------------------
The function follows the duplicate path
in the files_history data structure.
----------------------------------------'''
def search_in_files_history( link, files_history, article_chain ):
    
    global REPETITIVE_TITLE_LINK                            # Make namespace of REPETITIVE_TITLE_LINK global
    global CRAWL_STATE                                      # Make namespace of CRAWL_STATE global
    file_counter = 0
    for crawl in files_history['search-history']:
        titles = list( crawl.keys() )
        links = list( crawl.values() )
        if link in links:
            idx = links.index( link )
            for i, j in zip( titles[ idx+1: ], links[ idx+1: ] ):
                article_chain.append( (i, j) )
                log( '{:30s}-->\t\t{:50s}'.format( i, j ), logging.NOTSET )
            CRAWL_STATE = files_history[  'crawl-final-state' ][ file_counter-BAD_FILES_COUNTER ]
            REPETITIVE_TITLE_LINK = files_history[ 'repetitive-title-link' ][ file_counter-BAD_FILES_COUNTER ]
            log( f'*** {CRAWL_STATE}' )
            return True
        file_counter += 1
    return False

'''-------------------------------------------------
The function set the initial config for logging.
-------------------------------------------------'''
def set_log_config( level = logging.INFO ):
    if level == logging.WARNING:
        timestamp_color = BACKGROUND_BRIGHT_BLUE
        msg_color = BACKGROUND_BRIGHT_RED
    elif level == logging.NOTSET:
        timestamp_color = MAGENTA
        msg_color = BLUE
    else:
        timestamp_color = MAGENTA
        msg_color = YELLOW

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler( handler )
    out = '{} [{}] {} {} {} {}'.format( timestamp_color, '%(asctime)s', RESET, msg_color, '%(message)s', RESET )
    logging.basicConfig( format = out, datefmt='%Y-%m-%d %H:%M:%S', level = logging.INFO )

'''-----------------------------------------------------------
The function print log if global variable VERBOSE is True.
-----------------------------------------------------------'''
def log( msg = '', level = logging.INFO ):
    if VERBOSE:
        set_log_config( level )
        logging.info( msg )

'''----------------------------------------------------
The function returns a string contain date and time
example: article-chain-[2021-01-03]-[21-50-45].json.
----------------------------------------------------'''
def make_file_path( extension ):
    return '..\\json\\article-chain-{}.{}'.format( datetime.today().strftime('[%Y-%m-%d]-[%H-%M-%S]'), extension )

'''----------------------------------------------------
The function returns a json dump.
----------------------------------------------------'''
def make_json( article_chain, target_link ):
    out = dict()
    out['target-link']              = target_link
    out['search-history']           = dict( article_chain )
    out['repetitive-title-link']    = REPETITIVE_TITLE_LINK
    out['chain-length']             = len( article_chain ) - IF_IS_REPITITIVE
    out['crawl-final-state']        = CRAWL_STATE
    return json.dumps( out, indent=4, ensure_ascii=False )

'''-----------------------------------------------
The function writes all the (title, link) pairs
of data structure article_chain to a JSON file.
in addition to the final state of crawling.
-----------------------------------------------'''
def write_to_json_file( out_file, json_data ):
    with open( out_file, 'a', encoding='utf-8' ) as handler:
        handler.writelines( json_data )
    log( 'The output file [{}] has been created successfully!'.format( out_file ) )

'''-------------------------------------
The function read all JSON files and
store data in the history data structure
using analysis function.
-------------------------------------'''
def read_history_files( path, history ):
    
    global BAD_FILES_COUNTER
    os.chdir( path )
    total = len( glob.glob( '*.json' ) )
    c = 0
    for file in glob.glob( '*.json' ):
        c += 1
        with open( file, 'r', encoding='utf-8' ) as handler:
            data = json.load( handler )
            try:
                history['target-link'           ].append( data['target-link'            ] )
                history['search-history'        ].append( data['search-history'         ] )
                history['repetitive-title-link' ].append( data['repetitive-title-link'  ] )
                history['chain-length'          ].append( data['chain-length'           ] )
                history['crawl-final-state'     ].append( data['crawl-final-state'      ] )
            except KeyError:
                log( f'*** ERROR in reading file {c} of {total}', logging.WARNING )
                BAD_FILES_COUNTER += 1
            else:
                log(  f'file {c} of {total} was read successfully' )

'''--------------
Main function.
--------------'''
def main():
    
    # random_article_url  =   'https://en.wikipedia.org/wiki/Special:Random'        # random!
    # random_article_url  =   'https://en.wikipedia.org/wiki/Uncertainty'           # short chain!
    random_article_url  =   'https://en.wikipedia.org/wiki/Montagu%27s_harrier'   # repetitive chain!
    target_link         =   'https://en.wikipedia.org/wiki/Philosophy'
    threshold           =    100       # maximum crawling
    sleep_time          =    0.0       # second
    
    files_history = { 'target-link':[], 'search-history':[], 'repetitive-title-link':[], 'chain-length':[], 'crawl-final-state':[] }
    read_history_files( '.\\json\\', files_history )
    
    article_chain = traverse_link( random_article_url, target_link, threshold, sleep_time, files_history )
    out_file_path = make_file_path('json')
    out_json = make_json( article_chain, target_link )
    write_to_json_file( out_file_path, out_json )

if __name__ == "__main__":
    main()

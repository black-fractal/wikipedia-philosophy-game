'''''''''''''''''''''''''''''''''
Getting to Philosophy!
https://github.com/black-fractal/wikipedia-philosophy-game

@black-fractal
Vahid Khodabakhshi,
vkhodabakhshi@ce.sharif.edu
Initiated Date: January 2, 2021
Last modified date: January 9, 2021
TODO: it's incomplete!

'''''''''''''''''''''''''''''''''

import glob, os
import json
from time import sleep

'''----------------------------------
The function read all JSON files and
store data in results data structure
using analysis function.
----------------------------------'''
def read_files( path, results ):
    os.chdir( path )
    total = len( glob.glob( '*.json' ) )
    c = 1
    for file in glob.glob( '*.json' ):
        # print( f'file {c} of {total} is reading..' )
        c += 1
        with open( file, 'r', encoding='utf-8' ) as handler:
            data = json.load( handler )
            analysis( data, results )

'''----------------------------------
The function analyse raw data which
are fetched from all JSON files and
fills out results data structure.
----------------------------------'''
def analysis( data, results ):
    
    # filling out the number of each states (found, looped, exceed-threshold)
    state = data['crawl-final-state']
    if state.find( 'Unfortunately' )!=-1:
        results['exceed-threshold'] += 1
    elif state.find( 'loop' )!=-1:
        results['looped'] += 1
        looped_link = list( data['search-history'].keys() )[-1] # get the last element of the list which is repeated!
        results['looped-links'].append( looped_link )
    else:
        results['found'] += 1
    
    results['search-history'] += list( data['search-history'].keys() ) # get all search history including loops, unsuccessfull and successfull crawls!

'''--------------
Main function.
--------------'''
def main():
    
    results = { 'found':0, 'looped':0, 'exceed-threshold':0, 'looped-links':[], 'search-history':[], 'distance-to-ph':{} }
    
    read_files( '.\\json\\', results )
    
    results['looped-links'] = set( results['looped-links'] )
    # results['search-history'] = set( results['search-history'] )
    
    links_count = dict()
    for i in results['search-history']:
        links_count[ i ] = links_count.get( i, 0 ) + 1
    results['search-history'] = { k: v for k, v in sorted( links_count.items(), key=lambda item: -item[1] ) }
    
    print( results )
    
if __name__ == "__main__":
    main()
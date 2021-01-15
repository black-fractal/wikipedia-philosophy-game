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

from anytree import Node, RenderTree
from anytree.exporter import DotExporter

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
    
    state = data['crawl-final-state']
    
    if state.find( 'Unfortunately' )!=-1:
        # fill out `exceed-threshold`
        results['exceed-threshold'] += 1
        
    elif state.find( 'loop' )!=-1:
        # fill out `looped`
        results['looped'] += 1
        # fill out `looped-links`
        looped_link = list( data['search-history'].keys() )[-1] # get the last element of the list which is repeated!
        results['looped-links'].append( looped_link )
        
    else:
        # fill out `found`
        results['found'] += 1
        # fill out `distance-to-ph`
        i = int( state.split('after')[1].split(' ')[1] )
        results['distance-to-ph'][ i ] = results['distance-to-ph'].get( i, 0 ) + 1
    
    # fill out `search-history`
    results['search-history'] += list( data['search-history'].keys() ) # get all search history including loops, unsuccessfull and successfull crawls!
    
    # fill out `sorted_titles`
    links_count = dict()
    for i in results['search-history']:
        links_count[ i ] = links_count.get( i, 0 ) + 1
    results['sorted_titles'] = { k: v for k, v in sorted( links_count.items(), key=lambda item: -item[1] ) }

'''--------------
Main function.
--------------'''
def main():
    
    results = { 'found':0, 'looped':0, 'exceed-threshold':0, 'looped-links':[], 'sorted_titles':[], 'search-history':[], 'distance-to-ph':{} }
    
    read_files( '.\\json\\', results )
    
    results['looped-links'] = set( results['looped-links'] )
    
    print( results )
    # make_tree(  )
    
if __name__ == "__main__":
    main()
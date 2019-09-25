"""
ead2xml

Usage:
    ead2xml.py convert <xmlfile> <outfile> [--format=<saa>]
    ead2xml.py (-h | --help)
    ead2xml.py --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    --format=<saa>  Output rdf format [default: saa].
"""

import os
import xmltodict
from docopt import docopt

from pprint import pprint as print

def parseEAD(xmlfile):
    with open(xmlfile, 'rb') as xmlrbfile:
        parse = xmltodict.parse(xmlrbfile)

        ead = parse['ead']

    return ead

def convert(xmlfile, outfile, format='saa'):
    
    ead = parseEAD(xmlfile)    

    head = ead['eadheader']
    archdesc = ead['archdesc']

    # head

    collectionNumber = head['eadid']
    
    title = head['filedesc']['titlestmt']['titleproper']
    author = head['filedesc']['titlestmt']['author']
    publisher = head['filedesc']['publicationstmt']['publisher']
    date = head['filedesc']['publicationstmt']['date']

    # description

    ## meta

    collection_id = archdesc['did']['@id']
    collectionNumber = archdesc['did']['unitid']
    collectionName = archdesc['did']['unittitle']
    collectionDate = archdesc['did']['unitdate']
    collectionLanguage = archdesc['did']['langmaterial']
    collectionRepository = archdesc['did']['repository']['corpname']
    collectionOrigination = archdesc['did']['origination']['@label']
    collectionCorporation = archdesc['did']['origination']['corpname']

    print(archdesc.keys())
    print(archdesc['odd'].keys())

    ## odd

    ###

if __name__ == '__main__':
    arguments = docopt(__doc__)
    if arguments['convert'] and os.path.isfile(arguments['<xmlfile>']):
        convert(xmlfile=arguments['<xmlfile>'], outfile=arguments['<outfile>'], format=arguments['--format'])
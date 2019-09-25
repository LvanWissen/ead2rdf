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
        parse = xmltodict.parse(xmlrbfile, force_list={'note'})

        ead = parse['ead']

    return ead

def parseDID(c):

    did = c['did']

    id = did['@id']
    code = did['unitid']['#text']
    title = did['unittitle']

    print(code)

    if c['@level'] == 'file':
        if 'note' in did:
            for note in did['note']:
                if note['@label'] == "NB":
                    comments = note['p']
                elif note['@label'] == "ImageId":
                    scans = note['p'].split(' \n')
                    print(scans)
        else:
            scans = []

        return id, code, title, scans

    else:
        for k in c:
            if k not in ['head', '@level', 'did']:
                if type(c[k]) == list:
                    for subelement in c[k]:
                        parseDID(subelement)
                else:
                    parseDID(c[k])

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

    ## did

    collection_id = archdesc['did']['@id']
    collectionNumber = archdesc['did']['unitid']
    collectionName = archdesc['did']['unittitle']
    collectionDate = archdesc['did']['unitdate']
    collectionLanguage = archdesc['did']['langmaterial']
    collectionRepository = archdesc['did']['repository']['corpname']
    collectionOrigination = archdesc['did']['origination']['@label']
    collectionCorporation = archdesc['did']['origination']['corpname']

    ## odd

    # descriptive stuff in html

    ## dsc

    dsc = archdesc['dsc']

    # print(archdesc['dsc'].keys())

    for serie in dsc['c01']:

        print(parseDID(serie))

        # if serie =='head':
        #     continue

        # print(serie.keys())
        
        # serie_id = serie['did']['@id']
        # serieCode = serie['did']['unitid']
        # serieTitle = serie['did']['unittitle']

        # for subserie in serie['c02']:
        #     subserie_id = subserie['did']['@id']
        #     subserieCode = subserie['did']['unitid']
        #     subserieTitle = subserie['did']['unittitle']

        #     for subgroup in subserie['c03']:
        #         subgroup_id = subgroup['did']['@id']
        #         subgroupCode = subgroup['did']['unitid']
        #         subgroupTitle = subgroup['did']['unittitle']   

        #         print(subgroupTitle)

        #         for inventory in subgroup['c04']:
        #             file_id = inventory['did']['@id']
        #             fileCode = inventory['did']['unitid']
        #             fileTitle = inventory['did']['unittitle'] 

                    
                    # print(scans)    
    ###

if __name__ == '__main__':
    arguments = docopt(__doc__)
    if arguments['convert'] and os.path.isfile(arguments['<xmlfile>']):
        convert(xmlfile=arguments['<xmlfile>'], outfile=arguments['<outfile>'], format=arguments['--format'])
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

from dataclasses import dataclass


@dataclass
class Collection:
    title: str
    author: str
    publisher: str
    date: str

    collection_id: str
    collectionNumber: str
    collectionName: str
    collectionDate: str
    collectionLanguage: str
    collectionRepository: str
    collectionOrigination: str
    collectionCorporation: str

    children: list


@dataclass(order=True)
class C:
    id: str
    code: str
    date: str
    title: str
    comment: str
    scans: list

    children: list

    level: str


def parseEAD(xmlfile):
    with open(xmlfile, 'rb') as xmlrbfile:
        parse = xmltodict.parse(xmlrbfile,
                                force_list={'note', 'c02', 'c03', 'c04'},
                                dict_constructor=dict)
        ead = parse['ead']

    return ead


def parseDsc(serie, parentElement=None):

    did = serie['did']

    id = did['@id']
    code = did['unitid']['#text']
    date = did.get('unitdate')
    title = did['unittitle']
    comment = None
    scans = None

    if serie['@level'] == 'file':  # reached the end!
        if 'note' in did:
            for note in did['note']:
                if note['@label'] == "NB":
                    comment = note['p']
                elif note['@label'] == "ImageId":
                    scans = note['p'].split(' \n')
        else:
            scans = []

        return C(id,
                 code,
                 date,
                 title,
                 comment,
                 scans, [],
                 level=serie['@level'])

    else:
        children = []
        for k in serie:
            if k not in ['head', '@level', 'did']:
                for subelement in serie[k]:
                    children.append(parseDsc(subelement))

        return C(id, code, date, title, comment, scans, children,
                 serie['@level'])


def convert(xmlfile, outfile, format='saa'):

    ead = parseEAD(xmlfile)

    head = ead['eadheader']
    archdesc = ead['archdesc']

    collection = Collection(
        # collectionNumber=head['eadid'],
        title=head['filedesc']['titlestmt']['titleproper'],
        author=head['filedesc']['titlestmt'].get('author'),
        publisher=head['filedesc']['publicationstmt']['publisher'],
        date=head['filedesc']['publicationstmt'].get('date'),
        collection_id=archdesc['did']['@id'],
        collectionNumber=archdesc['did']['unitid'],
        collectionName=archdesc['did']['unittitle'],
        collectionDate=archdesc['did']['unitdate'],
        collectionLanguage=archdesc['did']['langmaterial'],
        collectionRepository=archdesc['did']['repository']['corpname'],
        collectionOrigination=archdesc['did']['origination']['@label'],
        collectionCorporation=archdesc['did']['origination']['corpname'],
        children=[parseDsc(serie) for serie in archdesc['dsc']['c01']])

    return collection


if __name__ == '__main__':
    arguments = docopt(__doc__)
    if arguments['convert'] and os.path.isfile(arguments['<xmlfile>']):
        print(
            convert(xmlfile=arguments['<xmlfile>'],
                    outfile=arguments['<outfile>'],
                    format=arguments['--format']))

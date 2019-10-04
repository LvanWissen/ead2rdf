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

from model import SAACollection, ga, Namespace


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
                    if type(subelement) != str:
                        children.append(parseDsc(subelement))

        return C(id, code, date, title, comment, scans, children,
                 serie['@level'])


def parseCollection(ead):

    head = ead['eadheader']
    archdesc = ead['archdesc']

    collection = Collection(
        # collectionNumber=head['eadid'],
        title=head['filedesc']['titlestmt']['titleproper'],
        author=head['filedesc']['titlestmt'].get('author'),
        publisher=head['filedesc']['publicationstmt']['publisher'],
        date=head['filedesc']['publicationstmt'].get('date'),
        collection_id=archdesc['did']['@id'],
        collectionNumber=archdesc['did']['unitid']['#text'],
        collectionName=archdesc['did']['unittitle']['#text'],
        collectionDate=archdesc['did']['unitdate']['#text'],
        collectionLanguage=archdesc['did']['langmaterial'],
        collectionRepository=archdesc['did']['repository']['corpname'],
        collectionOrigination=archdesc['did']['origination']['@label'],
        collectionCorporation=archdesc['did']['origination']['corpname'],
        children=[parseDsc(serie) for serie in archdesc['dsc']['c01']])

    return collection


def toRdf(collection, model='saa'):

    code = collection.collectionNumber.lower().replace('.', '')

    scanNamespace = Namespace(
        f"https://archief.amsterdam/inventarissen/inventaris/{code}.nl.html#")

    col = SAACollection(ga.term(collection.collection_id),
                        identifier=collection.collection_id,
                        code=collection.collectionNumber,
                        title=collection.title,
                        publisher=collection.publisher,
                        date=collection.collectionDate,
                        label=[collection.title])

    parts = [
        cToRdf(c, parent=col, scanNamespace=scanNamespace)
        for c in collection.children
    ]

    if parts != []:
        col.hasParts = parts

    return col.db


def cToRdf(c, parent=None, scanNamespace=None):

    if c.scans and scanNamespace:
        urlScans = [scanNamespace.term(i) for i in c.scans]
    else:
        urlScans = c.scans

    col = SAACollection(ga.term(c.id),
                        identifier=c.id,
                        code=c.code,
                        title=c.title,
                        date=c.date,
                        comment=[c.comment] if c.comment else None,
                        scans=urlScans,
                        partOf=parent,
                        label=[c.title])

    parts = [
        cToRdf(c, parent=col, scanNamespace=scanNamespace) for c in c.children
    ]

    if parts != []:
        col.hasParts = parts

    return col


def convert(xmlfile, outfile, model='saa'):

    ead = parseEAD(xmlfile)
    collection = parseCollection(ead)

    g = toRdf(collection)

    g.serialize(destination=outfile, format='turtle')


if __name__ == '__main__':
    arguments = docopt(__doc__)
    if arguments['convert'] and os.path.isfile(arguments['<xmlfile>']):

        convert(xmlfile=arguments['<xmlfile>'],
                outfile=arguments['<outfile>'],
                model=arguments['--format'])

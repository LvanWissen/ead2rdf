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

from datetime import datetime, timedelta
from dateutil import parser

from dataclasses import dataclass

from model import SAACollection, SAAInventoryBook, SAAScan, SAADoublePageSpread, ga, saa, Namespace, Literal, XSD, sem, foaf


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


def parseDate(date,
              circa=None,
              default=None,
              defaultBegin=datetime(2100, 1, 1),
              defaultEnd=datetime(2100, 12, 31)):

    if date is None or date == 's.d.':
        return {}

    date = date.strip()

    if '-' in date:
        begin, end = date.split('-')

        begin = parseDate(begin, default=defaultBegin)
        end = parseDate(end, default=defaultEnd)
    elif 'ca.' in date:
        date, _ = date.split('ca.')

        begin = parseDate(date, default=defaultBegin, circa=365)
        end = parseDate(date, default=defaultEnd, circa=365)

    else:  # exact date ?

        if circa:
            begin = parser.parse(date, default=defaultBegin) - timedelta(circa)
            end = parser.parse(date, default=defaultEnd) + timedelta(circa)
        else:
            begin = parser.parse(date, default=defaultBegin)
            end = parser.parse(date, default=defaultEnd)

    begin = begin
    end = end

    # And now some sem magic

    if begin == end:
        timeStamp = begin
    else:
        timeStamp = None

    if type(begin) == tuple:
        earliestBeginTimeStamp = begin[0]
        latestBeginTimeStamp = begin[1]
        beginTimeStamp = None
        timeStamp = None
    else:
        earliestBeginTimeStamp = begin
        latestBeginTimeStamp = begin
        beginTimeStamp = begin

    if type(end) == tuple:
        earliestEndTimeStamp = end[0]
        latestEndTimeStamp = end[1]
        endTimeStamp = None
    else:
        earliestEndTimeStamp = end
        latestEndTimeStamp = end
        endTimeStamp = end

    if default:
        if type(begin) == tuple:
            begin = min(begin)
        if type(end) == tuple:
            end = max(end)
        return begin, end

    dt = {
        "hasTimeStamp": timeStamp,
        "hasBeginTimeStamp": beginTimeStamp,
        "hasEarliestBeginTimeStamp": earliestBeginTimeStamp,
        "hasLatestBeginTimeStamp": latestBeginTimeStamp,
        "hasEndTimeStamp": endTimeStamp,
        "hasEarliestEndTimeStamp": earliestEndTimeStamp,
        "hasLatestEndTimeStamp": latestEndTimeStamp
    }

    return dt


def toRdf(collection, model='saa'):

    collectionNumber = collection.collectionNumber.lower().replace('.', '')
    scanNamespace = Namespace(
        f"https://archief.amsterdam/inventarissen/inventaris/{collectionNumber}.nl.html#"
    )

    col = SAACollection(ga.term(collectionNumber),
                        identifier=collection.collection_id,
                        code=collection.collectionNumber,
                        title=collection.title,
                        publisher=collection.publisher,
                        date=collection.collectionDate,
                        label=[collection.title])

    parts = [
        cToRdf(c,
               parent=col,
               collectionNumber=collectionNumber,
               scanNamespace=scanNamespace) for c in collection.children
    ]

    if parts != []:
        col.hasParts = parts

    return col.db


def cToRdf(c, parent=None, collectionNumber=None, scanNamespace=None):

    if collectionNumber:
        saaCollection = Namespace(
            f"https://data.goldenagents.org/datasets/saa/{collectionNumber}/")
    else:
        saaCollection = ga

    if (c.scans or not c.children) and collectionNumber:
        # Then this is a book --> InventoryBook

        inventoryId = c.id
        saaInventory = Namespace(
            f"https://data.goldenagents.org/datasets/saa/{collectionNumber}/{inventoryId}/"
        )

        if c.scans:

            saaScan = Namespace(
                f"https://data.goldenagents.org/datasets/SAA/Scan/")

            urlScans = [scanNamespace.term(i) for i in c.scans]
            scans = [saaInventory.term(i) for i in c.scans]

            parts = [
                SAADoublePageSpread(sUri,
                                    hasDigitalRepresentation=SAAScan(
                                        saaScan.term(img), depiction=imgUri),
                                    partOf=saaCollection.term(c.id))
                for img, sUri, imgUri in zip(c.scans, scans, urlScans)
            ]
        else:
            parts = []

        col = SAAInventoryBook(
            saaCollection.term(c.id),
            identifier=c.id,
            inventoryNumber=c.code,
            title=c.title,
            label=[Literal(f"Inventaris {c.code}", lang='nl')],
            date=c.date,
            hasParts=parts)

        try:
            parsedDate = parseDate(c.date)
        except:
            print(c.date)

        for k, v in parsedDate.items():
            if v:
                col.__setattr__(k, Literal(v.date(), datatype=XSD.date))

    else:
        # Not yet reached the end of the tree

        # collectionId = f"{collectionId}/{c.id}"

        col = SAACollection(saaCollection.term(c.id),
                            identifier=c.id,
                            code=c.code,
                            title=c.title,
                            date=c.date,
                            comment=[c.comment] if c.comment else [],
                            partOf=parent,
                            label=[c.title])

        parts = [
            cToRdf(c,
                   parent=col,
                   collectionNumber=collectionNumber,
                   scanNamespace=scanNamespace) for c in c.children
        ]

        if parts != []:
            col.hasParts = parts

    return col


def convert(xmlfile, outfile, model='saa'):

    ead = parseEAD(xmlfile)
    collection = parseCollection(ead)

    g = toRdf(collection)

    g.bind('saa', saa)
    g.bind('sem', sem)
    g.bind('foaf', foaf)

    g.serialize(destination=outfile, format='turtle')


if __name__ == '__main__':
    arguments = docopt(__doc__)
    if arguments['convert'] and os.path.isfile(arguments['<xmlfile>']):

        print(f"Parsing {arguments['<xmlfile>']}")
        convert(xmlfile=arguments['<xmlfile>'],
                outfile=arguments['<outfile>'],
                model=arguments['--format'])
        print(f"File written to {arguments['<outfile>']}")

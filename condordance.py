import collections
import json
import math
import time

import requests

from ead2xml import parseEAD, parseCollection

APIURL = "https://webservices.picturae.com/archives/scans/5001/"


def enumerateChildren(collection, path=None, n=0):
    """Retrieve paths for new SAA environment. 

    Args:
        collection (Collection): data collection class from EAD
        path (str, optional): starting path. Defaults to None.
        n (int, optional): index position. Defaults to 0.
    
    Returns:
        tuple: (inventoryNumber(int), path(str), nScans(int))
    """

    n += 1
    if path is None:
        path = ""
    elif path == "":
        path += f"{n}"
    else:
        path += f".{n}"

    if collection.children:
        return [
            enumerateChildren(c, path, i)
            for i, c in enumerate(collection.children)
        ]
    else:
        return collection.code, path, len(collection.scans)


def flatten(iterable):

    for obj in iterable:
        if isinstance(obj, collections.abc.Iterable) and not isinstance(
                obj, (str, bytes, tuple)):
            yield from flatten(obj)
        else:
            yield obj


def getScans(path, nscans, collectionNumber, start=0, limit=100,
             APIURL=APIURL):

    url = APIURL + path
    arguments = {
        'apiKey': 'eb37e65a-eb47-11e9-b95c-60f81db16c0e',
        'lang': 'nl_NL',
        'findingAid': collectionNumber,
        'path': path,
        'callback': 'callback_json8',
        'start': start,
        'limit': limit
    }

    scans = []
    for i in range(math.ceil(nscans / 100)):
        r = requests.get(url, arguments)

        data = r.text.replace('callback_json8(', '').replace(')', '')
        data = json.loads(data)

        arguments['start'] += limit
        time.sleep(1)  # be gentle

        scans += data['scans']['scans']

    return scans


if __name__ == "__main__":

    xmlfile = "/home/leon/Documents/Golden_Agents/ead2rdf/EAD_5001.xml"

    ead = parseEAD(xmlfile)
    collection = parseCollection(ead)
    collectionNumber = collection.collectionNumber

    paths = flatten(enumerateChildren(collection))

    data = collections.defaultdict(dict)  # store in dict
    for inventoryNumber, path, nscans in paths:
        scans = getScans(path, nscans, collectionNumber)

        data[collectionNumber][inventoryNumber] = scans

    # save to disc
    with open(f"{collectionNumber}.json", 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4)

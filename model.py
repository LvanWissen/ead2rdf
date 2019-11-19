from rdflib import Dataset, Graph, Namespace
from rdflib import XSD, RDF, RDFS, OWL
from rdflib import URIRef, BNode, Literal

from rdfalchemy.rdfSubject import rdfSubject
from rdfalchemy.rdfsSubject import rdfsSubject
from rdfalchemy import rdfSingle, rdfMultiple, rdfContainer, rdfList

schema = Namespace("https://schema.org/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
geos = Namespace("http://www.opengis.net/ont/geosparql#")

ga = Namespace("https://data.goldenagents.org/datasets/SAA/")
saa = Namespace("https://data.goldenagents.org/datasets/SAA/ontology/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")

AS = Namespace("http://www.w3.org/ns/activitystreams#")
oa = Namespace("http://www.w3.org/ns/oa#")
dcterms = Namespace("http://purl.org/dc/terms/")

prov = Namespace("http://www.w3.org/ns/prov#")

##########
# Schema #
##########


class Entity(rdfSubject):
    rdf_type = prov.Entity
    label = rdfMultiple(RDFS.label)
    comment = rdfMultiple(RDFS.comment)

    wasDerivedFrom = rdfMultiple(prov.wasDerivedFrom)
    qualifiedDerivation = rdfSingle(prov.qualifiedDerivation,
                                    range_type=prov.Derivation)

    partOf = rdfSingle(saa.partOf)
    hasParts = rdfMultiple(saa.hasParts)

    code = rdfSingle(saa.code)
    identifier = rdfSingle(saa.identifier)

    title = rdfSingle(saa.title)
    date = rdfSingle(saa.date)

    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)


class SAACollection(Entity):
    rdf_type = saa.Collection

    publisher = rdfSingle(saa.publisher)


class SAADocument(Entity):
    rdf_type = saa.Document


class SAAInventoryBook(SAADocument):
    rdf_type = saa.InventoryBook
    inventoryNumber = rdfSingle(saa.inventoryNumber)


class SAADoublePageSpread(SAADocument):
    rdf_type = saa.DoublePageSpread

    hasDigitalRepresentation = rdfSingle(saa.hasDigitalRepresentation,
                                         range_type=saa.Scan)


class SAAScan(Entity):
    rdf_type = saa.Scan

    url = rdfSingle(saa.url)
    depiction = rdfSingle(foaf.depiction)

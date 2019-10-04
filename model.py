from rdflib import Dataset, Graph, Namespace
from rdflib import XSD, RDF, RDFS, OWL
from rdflib import URIRef, BNode, Literal

from rdfalchemy.rdfSubject import rdfSubject
from rdfalchemy.rdfsSubject import rdfsSubject
from rdfalchemy import rdfSingle, rdfMultiple, rdfContainer, rdfList

schema = Namespace("https://schema.org/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
geos = Namespace("http://www.opengis.net/ont/geosparql#")

ga = Namespace("http://goldenagents.org/uva/SAA/datasets/")
saa = Namespace("http://goldenagents.org/uva/SAA/ontology/")
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


class SAACollection(Entity):
    rdf_type = saa.Collection

    code = rdfSingle(saa.code)
    identifier = rdfSingle(saa.identifier)

    title = rdfSingle(saa.title)
    publisher = rdfSingle(saa.publisher)
    date = rdfSingle(saa.date)

    partOf = rdfSingle(saa.partOf)
    hasParts = rdfMultiple(saa.hasParts)

    scans = rdfMultiple(saa.urlScan)


class SAAScan(Entity):
    rdf_type = saa.Scan

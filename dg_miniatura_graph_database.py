import sys
# sys.path.insert(1, 'D:\IBL\Documents\IBL-PAN-Python')
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import datetime
import regex as re
from my_functions import gsheet_to_df
from ast import literal_eval

#%%
# --- CONFIG ---
RECH = Namespace('https://example.org/rechtsextremismus/')
dcterms = Namespace("http://purl.org/dc/terms/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
FABIO = Namespace("http://purl.org/spar/fabio/")
BIRO = Namespace("http://purl.org/spar/biro/")
VIAF = Namespace("http://viaf.org/viaf/")
geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
bibo = Namespace("http://purl.org/ontology/bibo/")
schema = Namespace("http://schema.org/")
WDT = Namespace("http://www.wikidata.org/entity/")
OUTPUT_TTL = "rechtsextremismus.ttl"

#%% --- LOAD ---
df_novels     = gsheet_to_df('1iU-u4xjotqa3ZLijF5bMU7xWv-Hxgq1n8N3i-7UCdfU', 'novels')
df_people    = gsheet_to_df('1iU-u4xjotqa3ZLijF5bMU7xWv-Hxgq1n8N3i-7UCdfU', 'authors')
df_places     = gsheet_to_df('1iU-u4xjotqa3ZLijF5bMU7xWv-Hxgq1n8N3i-7UCdfU', 'places')
df_institutions = gsheet_to_df('1iU-u4xjotqa3ZLijF5bMU7xWv-Hxgq1n8N3i-7UCdfU', 'institutions')
df_prizes     = gsheet_to_df('1iU-u4xjotqa3ZLijF5bMU7xWv-Hxgq1n8N3i-7UCdfU', 'prizes')
#%% --- GRAPH ---
g = Graph()

g.bind("rechtsextremismus", RECH)
g.bind("dcterms", dcterms)
g.bind("fabio", FABIO)
g.bind("geo", geo)
g.bind("bibo", bibo)
g.bind("sch", schema)
g.bind("biro", BIRO)
g.bind("foaf", FOAF)
g.bind("wdt", WDT)
g.bind("owl", OWL)

# # new class
# def add_literary_prize_class(g: Graph):
#     RECH = Namespace('https://example.org/rechtsextremismus/')
#     schema = Namespace("http://schema.org/")
#     # URI klasy LiteraryPrize
#     cls = RECH.LiteraryPrize
#     # dodaj trójki:
#     # ex:LiteraryPrize a rdfs:Class .
#     g.add((cls, RDF.type, RDFS.Class))
#     # ex:LiteraryPrize rdfs:subClassOf bibo:Award .
#     g.add((cls, RDFS.subClassOf, schema.Award))
#     # ex:LiteraryPrize rdfs:label "Literary Prize" .
#     g.add((cls, RDFS.label, Literal("Literary Prize")))

# add_literary_prize_class(g)

# 1) Place nodes
def add_place(row):
    pid = str(row["place_id"])
    place = RECH[f"Place/{pid}"]
    g.add((place, RDF.type, schema.Place))
    g.add((place, schema.name, Literal(row["name"])))
    if pd.notnull(row["wikidata_id"]):
        g.add((place, OWL.sameAs, WDT[row["wikidata_id"]]))
    latitude = Literal(row['latitude'], datatype=XSD.float)
    g.add((place, geo.lat, latitude))
    longitude = Literal(row['longitude'], datatype=XSD.float)
    g.add((place, geo.long, longitude))

for _, r in df_places.iterrows():
    add_place(r)
    
# 2) Institution (publishers) nodes

def add_institution(row):
    #PAMIĘTAĆ -- info, że publisher to w relacji dopiero
    iid = str(row["institution_id"])
    institution = RECH[f"Organization/{iid}"]
    g.add((institution, RDF.type, schema.Organization))
    g.add((institution, schema.name, Literal(row["searchName"])))
    if pd.notnull(row["wikidataID"]):
        g.add((institution, OWL.sameAs, WDT[row["wikidataID"]]))
    if pd.notnull(row["viafid"]):
        g.add((institution, OWL.sameAs, VIAF[row["viafid"]]))
    if pd.notnull(row["location_id"]):
        # relation Institution->Place
        place_id = str(row["location_id"])
        g.add((institution, schema.location, RECH[f"Place/{place_id}"]))
    if pd.notnull(row.get("range")):
        g.add((institution, schema.areaServed, Literal(row["range"])))
    
for _, r in df_institutions.iterrows():
    add_institution(r)    
    
# 3) Prize nodes + Author->Prize relations
# create Prize nodes

def add_prize(row):
    pid = str(row["prize_id"]) 
    prize = RECH[f"Prize/{pid}"]
    g.add((prize, RDF.type, schema.Award))
    g.add((prize, schema.name, Literal(row["prize_name"])))
    g.add((prize, schema.temporalCoverage, Literal(row["prize_year"], datatype=XSD.gYear)))
    if pd.notnull(row["prize_wikidata"]):
        g.add((prize, OWL.sameAs, WDT[row["prize_wikidata"]]))

for _, r in df_prizes.iterrows():
    add_prize(r)       

# 4) Person (authors)
def add_person(row):
    pid = str(row["author_id"])
    person = RECH[f"Person/{pid}"]
    g.add((person, RDF.type, schema.Person))
    g.add((person, schema.name, Literal(row["searchName"])))
    if pd.notnull(row["wikidataID"]):
        g.add((person, OWL.sameAs, WDT[row["wikidataID"]]))
    if pd.notnull(row["viafid"]):
        g.add((person, OWL.sameAs, VIAF[row["viafid"]]))
    if pd.notnull(row['birthdate']):
        year = str(row['birthdate'])[:4]
        g.add((person, schema.birthDate, Literal(year, datatype=XSD.gYear)))
    if pd.notnull(row['deathdate']):
        year = str(row['deathdate'])[:4]
        g.add((person, schema.deathDate, Literal(year, datatype=XSD.gYear)))
    if pd.notnull(row["birthplace"]):
        # relation Person->Place
        place_id = str(row["birthplace"])
        g.add((person, schema.birthPlace, RECH[f"Place/{place_id}"]))
    if pd.notnull(row["deathplace"]):
        # relation Person->Place
        place_id = str(row["deathplace"])
        g.add((person, schema.deathPlace, RECH[f"Place/{place_id}"]))
    if pd.notnull(row['sex']):
        g.add((person, schema.gender, Literal(row["sex"])))
    if pd.notnull(row['occupation']):
        for o in row['occupation'].split('❦'):
            g.add((person, schema.hasOccupation, Literal(o.strip())))
    if pd.notnull(row['historical background']):
        for hb in row['historical background'].split(','):
            g.add((person, RECH.historicalBackground, Literal(hb.strip())))
    if pd.notnull(row['prize_id']):
        for pr in row['prize_id'].split('|'):
            g.add((person, schema.award, RECH[f"Prize/{pr}"]))

for _, r in df_people.iterrows():
    add_person(r)       

# 5) Text (novels)
def add_text(row):
# for _, row in df_novels.iterrows():
    tid = str(row["novel_id"])
    text = RECH[f"Text/{tid}"]
    g.add((text, RDF.type, schema.Text))
    g.add((text, schema.title, Literal(row["title"])))
    if pd.notnull(row["link"]):
        g.add((text, OWL.sameAs, URIRef(row["link"])))
    for a in row['author_id'].split(';'):
        g.add((text, schema.author, RECH[f"Person/{a.strip()}"]))
    g.add((text, dcterms.publisher, RECH[f"Organization/{row['institution_id']}"]))
    g.add((text, schema.datePublished, Literal(row['year'], datatype=XSD.gYear)))
    for a in row['genre'].split(','):
        g.add((text, schema.genre, Literal(a.strip())))
    g.add((text, schema.inLanguage, Literal(row['language'])))
    g.add((text, RECH.whichNovel, Literal(row['debut novel/further novel'])))
    g.add((text, schema.about, Literal(row['subject'])))
    if pd.notnull(row["place_id"]):
        for p in row['place_id'].split(';'):
            g.add((text, FABIO.hasPlaceOfPublication, RECH[f"Place/{p}"]))
    if pd.notnull(row['reason for violence']):
        for rfv in row['reason for violence'].split(','):
            g.add((text, RECH.reasonForViolence, Literal(rfv.strip())))
    if pd.notnull(row['art of violence']):
        for afv in row['art of violence'].split(','):
            g.add((text, RECH.reasonForViolence, Literal(afv.strip())))
    if pd.notnull(row['klappentext']):
        g.add((text, schema.description, Literal(row['klappentext'])))
    if pd.notnull(row['rezensionsnotiz']):
        try:
            rec = literal_eval(row['rezensionsnotiz'])
            for r in rec:
                g.add((text, schema.review, Literal(r)))
        except SyntaxError:
            g.add((text, schema.review, Literal(row['rezensionsnotiz'])))
    if pd.notnull(row['keywords']):
        for k in row['keywords'].split('|'):
            g.add((text, schema.keywords, Literal(k)))
        
for _, r in df_novels.iterrows():
    add_text(r)    

# --- EXPORT ---
g.serialize(destination=OUTPUT_TTL, format="turtle")
print(f"RDF triples written to {OUTPUT_TTL}")

# # testy
# for subj, pred, obj in g:
#     print(subj, pred, obj)

# turtle_str = g.serialize(format="turtle")
# # print(turtle_str)

#%% testy i sprawdzenia
# #places
# from rdflib import Namespace, RDF

# EX = Namespace("http://example.org/dg/")

# # otwieramy plik do zapisu (nadpisze istniejący)
# with open("data/places_info.txt", "w", encoding="utf-8") as f:
#     # iterujemy po wszystkich subject w grafie
#     for place in g.subjects():
#         # filtrujemy tylko te, które są typu Place
#         if (place, RDF.type, EX.Place) in g:
#             # zapisujemy linię nagłówkową
#             f.write(f"--- Place node: {place}\n")
#             # zapisujemy wszystkie predykaty i obiekty tego noda
#             for p, o in g.predicate_objects(subject=place):
#                 f.write(f"    {p} → {o}\n")
#             # dodatkowy pusty wiersz dla czytelności
#             f.write("\n")

# #novels
# from rdflib import Namespace, RDF

# EX = Namespace("http://example.org/dg/")

# # otwieramy plik do zapisu (nadpisze istniejący)
# with open("data/novels_info.txt", "w", encoding="utf-8") as f:
#     # iterujemy po wszystkich subject w grafie
#     for novel in g.subjects():
#         # filtrujemy tylko te, które są typu Text (powieści)
#         if (novel, RDF.type, EX.Text) in g:
#             # zapisujemy linię nagłówkową
#             f.write(f"--- Novel node: {novel}\n")
#             # zapisujemy wszystkie predykaty i obiekty tego noda
#             for p, o in g.predicate_objects(subject=novel):
#                 f.write(f"    {p} → {o}\n")
#             # dodatkowy pusty wiersz dla czytelności
#             f.write("\n")

# print("Zapisano informacje o węzłach Novel do data/novels_info.txt")























import sys
# sys.path.insert(1, 'D:\IBL\Documents\IBL-PAN-Python')
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import datetime
import regex as re
from my_functions import gsheet_to_df

#%%
def slugify(s: str) -> str:
    # zamienia wszystkie nie-alfanumeryczne na podkreślenie
    return re.sub(r'\W+', '_', s).strip('_')
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
    iid = str(r["institution_id"])
    institution = RECH[f"Organization/{iid}"]
    g.add((institution, RDF.type, schema.Organization))
    g.add((institution, schema.name, Literal(row["searchName"])))
    if pd.notnull(row["wikidataID"]):
        g.add((institution, OWL.sameAs, WDT[row["wikidataID"]]))
    if pd.notnull(row["viafid"]):
        g.add((institution, OWL.sameAs, VIAF[row["viafid"]]))
    if pd.notnull(r["location_id"]):
        # relation Institution->Place
        place_id = str(row["location_id"])
        g.add((institution, schema.location, RECH[f"Place/{place_id}"]))
    if pd.notnull(row.get("range")):
        g.add((institution, schema.areaServed, Literal(r["range"])))
    
for _, r in df_institutions.iterrows():
    add_institution(r)    
    
# 3) Prize nodes + Author->Prize relations
# create Prize nodes

def add_prize(row):
    pid = str(r["prize_id"]) 
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
    pid = str(r["author_id"])
    person = RECH[f"Person/{pid}"]
    g.add((person, RDF.type, schema.Person))
    g.add((person, schema.name, Literal(r["searchName"])))
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
    if pd.notnull(r["birthplace"]):
        # relation Person->Place
        place_id = str(row["birthplace"])
        g.add((person, schema.birthPlace, RECH[f"Place/{place_id}"]))
    if pd.notnull(r["deathplace"]):
        # relation Person->Place
        place_id = str(row["deathplace"])
        g.add((person, schema.deathPlace, RECH[f"Place/{place_id}"]))
    if pd.notnull(row['sex']):
        g.add((person, schema.gender, Literal(row["sex"])))
    if pd.notnull(row['occupation']):
        for o in row['occupation'].split('❦'):
            g.add((person, schema.hasOccupation, Literal(o.strip())))
    pv  = BNode()
    g.add((person, schema.additionalProperty, pv))
    if pd.notnull(row['historical background']):
        for hb in row['historical background'].split(','):
            g.add((pv, RDF.type, schema.PropertyValue))
            g.add((pv, schema.propertyID, Literal("historical background")))
            g.add((pv, schema.value, Literal(hb.strip())))
    if pd.notnull(row['prize_id']):
        for pr in row['prize_id'].split('|'):
            g.add((person, schema.award, RECH[f"Prize/{pr}"]))

for _, r in df_people.iterrows():
    add_person(r)       

# 5) Text (novels)
def add_text(row):
    tid = str(row["novel_id"])
    text = RECH[f"Text/{tid}"]
    g.add((text, RDF.type, schema.Text))
    g.add((text, schema.title, Literal(row["title"])))
    if pd.notnull(row["link"]):
        g.add((text, OWL.sameAs, URIRef(row["link"])))
    for a in row['author_id'].split(';'):
        g.add((text, schema.author, RECH[f"Person/{a.strip()}"]))
    
    URIRef("https://literarybibliography.eu/")
    
for _, r in df_novels.iterrows():
    nid = str(r["novel_id"])
    u = EX[f"Text/{nid}"]
    g.add((u, RDF.type, EX.Text))
    g.add((u, EX.title, Literal(r["title"])))
    # author
    g.add((u, EX.hasAuthor, EX[f"Person/{r['author_id']}"]))
    # publisher & place
    g.add((u, EX.publishedBy, EX[f"Institution/{r['publisher']}"]))
    g.add((u, EX.publishedIn, EX[f"Place/{r['place_id']}"]))
    # year, genre, language, type, debut/further
    for col,pred,dt in [
        ("year","year",XSD.gYear),
        ("genre","genre",None),
        ("language","language",None),
        ("type","textType",None),
        ("debut novel/further novel","debutStatus",None),
        ("subject","subject",None),
        ("reason for violence","violenceReason",None),
        ("art of violence","violenceArt",None),
    ]:
        if pd.notnull(r.get(col)):
            lit = Literal(r[col], datatype=dt) if dt else Literal(r[col])
            g.add((u, EX[pred], lit))
    # keywords: split on commas or pipes
    for keycol in ["keywords2","keywords","stichworter"]:
        if pd.notnull(r.get(keycol)):
            for kw in str(r[keycol]).split(";"):
                kw = kw.strip()
                if kw:
                    g.add((u, EX.hasKeyword, Literal(kw)))

# --- EXPORT ---
g.serialize(destination=OUTPUT_TTL, format="turtle")
print(f"RDF triples written to {OUTPUT_TTL}")

# testy
for subj, pred, obj in g:
    print(subj, pred, obj)

turtle_str = g.serialize(format="turtle")
# print(turtle_str)

#%%
#places
from rdflib import Namespace, RDF

EX = Namespace("http://example.org/dg/")

# otwieramy plik do zapisu (nadpisze istniejący)
with open("data/places_info.txt", "w", encoding="utf-8") as f:
    # iterujemy po wszystkich subject w grafie
    for place in g.subjects():
        # filtrujemy tylko te, które są typu Place
        if (place, RDF.type, EX.Place) in g:
            # zapisujemy linię nagłówkową
            f.write(f"--- Place node: {place}\n")
            # zapisujemy wszystkie predykaty i obiekty tego noda
            for p, o in g.predicate_objects(subject=place):
                f.write(f"    {p} → {o}\n")
            # dodatkowy pusty wiersz dla czytelności
            f.write("\n")

#novels
from rdflib import Namespace, RDF

EX = Namespace("http://example.org/dg/")

# otwieramy plik do zapisu (nadpisze istniejący)
with open("data/novels_info.txt", "w", encoding="utf-8") as f:
    # iterujemy po wszystkich subject w grafie
    for novel in g.subjects():
        # filtrujemy tylko te, które są typu Text (powieści)
        if (novel, RDF.type, EX.Text) in g:
            # zapisujemy linię nagłówkową
            f.write(f"--- Novel node: {novel}\n")
            # zapisujemy wszystkie predykaty i obiekty tego noda
            for p, o in g.predicate_objects(subject=novel):
                f.write(f"    {p} → {o}\n")
            # dodatkowy pusty wiersz dla czytelności
            f.write("\n")

print("Zapisano informacje o węzłach Novel do data/novels_info.txt")























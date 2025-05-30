import sys
# sys.path.insert(1, 'D:\IBL\Documents\IBL-PAN-Python')
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
import rdflib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from dateutil import parser
import regex as re
from my_functions import gsheet_to_df
import geopandas as gpd
from shapely.geometry import Point
import plotly.express as px
from plotly.offline import plot

#%% 1
# 1. Wczytaj graf RDF z pliku Turtle
g = rdflib.Graph()
g.parse('rechtsextremismus.ttl', format='ttl')

# 2. Zdefiniuj przestrzeń nazw Schema.org
SCH = rdflib.Namespace('http://schema.org/')

# 3. Ekstrakcja danych: rok publikacji oraz wartość sch:about
records = []
for text in g.subjects(rdflib.RDF.type, SCH.Text):
    year_lit = g.value(text, SCH.datePublished)
    about_lit = g.value(text, SCH.about)
    if year_lit and about_lit:
        year = int(str(year_lit))
        about = str(about_lit)
        # filtrujemy tylko trzy główne kategorie
        if about in [
            'rechte Gewalt in generationeller Perspektive',
            'rechte Gewalt in intersektionaler Perspektive',
            'andere'
        ]:
            records.append({'year': year, 'about': about})

# 4. Utwórz DataFrame i zlicz pozycje
df = pd.DataFrame(records)
df_counts = df.pivot_table(
    index='year',
    columns='about',
    aggfunc='size',
    fill_value=0
)

# 5. Dopilnuj, by były wszystkie lata w zakresie
all_years = range(df_counts.index.min(), df_counts.index.max() + 1)
df_counts = df_counts.reindex(all_years, fill_value=0)

# 6. Wygeneruj wykres słupkowy skumulowany
plt.figure(figsize=(12, 6))
df_counts.plot(
    kind='bar',
    stacked=True,
    legend=True,
    width=0.8,
    figsize=(12, 6)
)

plt.xlabel('Jahr der Ausgabe', fontsize=12)
plt.ylabel('Anzahl der Bücher', fontsize=12)
plt.title('Anzahl der Bücher pro Jahr nach Kategorie der rechten Gewalt', fontsize=14)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#%% 2
# 1. Wczytanie grafu RDF
g = rdflib.Graph()
g.parse('rechtsextremismus.ttl', format='ttl')

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')
# Automatycznie pobieramy URI dla prefixu "rechtsextremismus" z grafu
ns_map = dict(g.namespaces())
RE = rdflib.Namespace(ns_map.get('rechtsextremismus'))

# 3. Filtr: szukamy Text o sch:about = 'rechte Gewalt in intersektionaler Perspektive'
target_about = 'rechte Gewalt in intersektionaler Perspektive'
backgrounds = []

for text in g.subjects(rdflib.RDF.type, SCH.Text):
    about_val = g.value(text, SCH.about)
    if about_val and str(about_val) == target_about:
        # Dla każdego takiego Text pobierzemy autorów (sch:author)
        for author in g.objects(text, SCH.author):
            # Sprawdzamy, czy to Person
            if (author, rdflib.RDF.type, SCH.Person) in g:
                # Pobierz historicalBackground
                bg = g.value(author, RE.historicalBackground)
                if bg:
                    backgrounds.append(str(bg))

# 4. Przygotowanie danych do wykresu
df_bg = pd.Series(backgrounds, name='background')
counts = df_bg.value_counts()

# 5. Wykres kołowy
plt.figure(figsize=(8, 8))
counts.plot(kind='pie', autopct='%1.f%%', startangle=90)
plt.ylabel('')  # usuń etykietę osi Y
plt.title('Verteilung des historischen Hintergrunds von Autoren, \ndie über rechte Gewalt in intersektionaler Perspektive schreiben')
plt.tight_layout()
plt.show()

#%% 3

target_about = 'rechte Gewalt in generationeller Perspektive'
backgrounds = []

for text in g.subjects(rdflib.RDF.type, SCH.Text):
    about_val = g.value(text, SCH.about)
    if about_val and str(about_val) == target_about:
        # Dla każdego takiego Text pobierzemy autorów (sch:author)
        for author in g.objects(text, SCH.author):
            # Sprawdzamy, czy to Person
            if (author, rdflib.RDF.type, SCH.Person) in g:
                # Pobierz historicalBackground
                bg = g.value(author, RE.historicalBackground)
                if bg:
                    backgrounds.append(str(bg))

# 4. Przygotowanie danych do wykresu
df_bg = pd.Series(backgrounds, name='background')
counts = df_bg.value_counts()

# 5. Wykres kołowy
plt.figure(figsize=(8, 8))
counts.plot(kind='pie', autopct='%1.f%%', startangle=90)
plt.ylabel('')  # usuń etykietę osi Y
plt.title('Verteilung des historischen Hintergrunds von Autoren, \ndie über rechte Gewalt in generationeller Perspektive schreiben')
plt.tight_layout()
plt.show()

#%% 4

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')
ns_map = dict(g.namespaces())
RE = rdflib.Namespace(ns_map.get('rechtsextremismus'))

# 3. Filtr i zbieranie danych
target_about = 'rechte Gewalt in intersektionaler Perspektive'
rows = []

for text in g.subjects(rdflib.RDF.type, SCH.Text):
    if str(g.value(text, SCH.about)) == target_about:
        for author in g.objects(text, SCH.author):
            if (author, rdflib.RDF.type, SCH.Person) in g:
                uri = str(author)
                name = g.value(author, SCH.name)
                background = g.value(author, RE.historicalBackground)
                rows.append({
                    'Author_URI': uri,
                    'Name': str(name) if name else None,
                    'historicalBackground': str(background) if background else None
                })

# 4. Utworzenie DataFrame i pokazanie wyników
df = pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)

#%% 5

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')
ns_map = dict(g.namespaces())
RE = rdflib.Namespace(ns_map.get('rechtsextremismus'))

# 3. Filtr i zbieranie danych
target_about = 'rechte Gewalt in generationeller Perspektive'
rows = []

for text in g.subjects(rdflib.RDF.type, SCH.Text):
    if str(g.value(text, SCH.about)) == target_about:
        for author in g.objects(text, SCH.author):
            if (author, rdflib.RDF.type, SCH.Person) in g:
                uri = str(author)
                name = g.value(author, SCH.name)
                background = g.value(author, RE.historicalBackground)
                rows.append({
                    'Author_URI': uri,
                    'Name': str(name) if name else None,
                    'historicalBackground': str(background) if background else None
                })

# 4. Utworzenie DataFrame i pokazanie wyników
df = pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)

#%% 6

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')
ns_map = dict(g.namespaces())
RE = rdflib.Namespace(ns_map.get('rechtsextremismus'))

# 3. Określenie interesujących kategorii
about1 = 'rechte Gewalt in intersektionaler Perspektive'
about2 = 'rechte Gewalt in generationeller Perspektive'

# 4. Zbudowanie mapy autora -> zestaw kategorii jego tekstów
author_categories = {}
for text in g.subjects(rdflib.RDF.type, SCH.Text):
    about_val = g.value(text, SCH.about)
    if about_val and str(about_val) in {about1, about2}:
        for author in g.objects(text, SCH.author):
            if (author, rdflib.RDF.type, SCH.Person) in g:
                author_categories.setdefault(author, set()).add(str(about_val))

# 5. Filtrowanie autorów mających obie kategorie
qualified_authors = [a for a, cats in author_categories.items() if {about1, about2}.issubset(cats)]

# 6. Zbieranie danych o autorach
rows = []
for author in qualified_authors:
    uri = str(author)
    name = g.value(author, SCH.name)
    background = g.value(author, RE.historicalBackground)
    rows.append({
        'Author_URI': uri,
        'Name': str(name) if name else None,
        'historicalBackground': str(background) if background else None
    })

# 7. Utworzenie DataFrame i wyświetlenie
df = pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)

#%% 7

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')
ns_map = dict(g.namespaces())
RE = rdflib.Namespace(ns_map.get('rechtsextremismus'))

# 3. Mapa tytułów i wartości sch:about
categories = {
    'Generationelle Perspektive': 'rechte Gewalt in generationeller Perspektive',
    'Intersektionale Perspektive': 'rechte Gewalt in intersektionaler Perspektive'
}

def plot_donut_connectors(title, about_val):
    # Zbieranie wszystkich wartości reasonForViolence (wielokrotne dopuszczalne)
    reasons = []
    for text in g.subjects(rdflib.RDF.type, SCH.Text):
        if str(g.value(text, SCH.about)) == about_val:
            reasons.extend(str(r) for r in g.objects(text, RE.reasonForViolence))

    # Obliczenie udziału procentowego każdej kategorii
    series = pd.Series(reasons, name='reason')
    counts = series.value_counts()
    percentages = counts / counts.sum() * 100

    # Parametry wykresu
    radius = 1.0
    width = 0.3
    inner = radius - width

    # Rysowanie wykresu typu "donut"
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, _ = ax.pie(
        percentages,
        startangle=90,
        radius=radius,
        labels=None,
        wedgeprops=dict(width=width, edgecolor='white')
    )

    # Dla każdego wycinka rysujemy łamaną zaczynającą się w połowie grubości
    for wedge, (label, pct) in zip(wedges, percentages.items()):
        ang = (wedge.theta2 + wedge.theta1) / 2
        x, y = np.cos(np.deg2rad(ang)), np.sin(np.deg2rad(ang))

        # Punkt startowy łamanej: środek grubości wycinka
        start_r = inner + width / 2
        start = (x * start_r, y * start_r)

        # Punkt przy zewnętrznej krawędzi
        if label == 'sexuell':
            mid = (x * radius, y * radius + 0.3)
        elif label == 'andere' and title == 'Generationelle Perspektive':
            mid = (x * radius, y * radius + 0.55)
        else: mid = (x * radius, y * radius + 0.2)

        # Punkt końcowy łamanej (poziome przesunięcie)
        offset = 0.5
        end = (mid[0] + offset * np.sign(x), mid[1])

        # Rysujemy dwa odcinki łamanej
        ax.plot([start[0], mid[0]], [start[1], mid[1]], color='black', lw=0.8)
        ax.plot([mid[0], end[0]],   [mid[1], end[1]], color='black', lw=0.8)

        # Wyrównanie tekstu w zależności od strony
        ha = 'left' if x >= 0 else 'right'
        va = 'center'

        # Tekst nazwy i procentu, rozdzielony pionowo
        ax.text(end[0], end[1] + 0.03, label, ha=ha, va='bottom', fontsize=9, color='black')
        ax.text(end[0], end[1] - 0.03, f"{pct:.1f}%", ha=ha, va='top', fontsize=9, color='black')

    ax.set_title(f'Die Verteilung der Gründe für Gewalt in Büchern \nzum {about_val}', fontsize=12, pad=15)
    ax.axis('equal')
    plt.tight_layout()
    plt.show()

# Generujemy dwa wykresy
for title, val in categories.items():
    plot_donut_connectors(title, val)

#%% 8a

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')

# Pomocnicza funkcja do wydobywania roku z literału
def extract_year(literal):
    try:
        # Parsowanie daty ISO
        return parser.parse(str(literal)).year
    except:
        # Wyciągnięcie pierwszego czterocyfrowego ciągu
        m = re.search(r'(\d{4})', str(literal))
        return int(m.group(1)) if m else None

rows = []

# 3. Iteracja po wszystkich osobach
for person in g.subjects(rdflib.RDF.type, SCH.Person):
    person_name = g.value(person, SCH.name)
    person_uri  = str(person)
    
    # 4. Zbieranie wszystkich książek danej osoby z datą publikacji
    texts = []
    for text in g.subjects(SCH.author, person):
        date_lit = g.value(text, SCH.datePublished)
        year = extract_year(date_lit) if date_lit else None
        if year:
            texts.append((text, year))
    
    # Pomijamy osoby bez książek
    if not texts:
        continue
    
    # 5. Wybór najstarszej książki
    oldest_text, oldest_year = min(texts, key=lambda x: x[1])
    book_title = g.value(oldest_text, SCH.title)
    book_uri   = str(oldest_text)
    
    # 6. Iteracja po nagrodach danej osoby
    for award in g.objects(person, SCH.award):
        award_name = g.value(award, SCH.name)
        award_uri  = str(award)
        award_year = None
        
        # Przeszukanie wszystkich literałów nagrody w poszukiwaniu roku
        for _, lit in g.predicate_objects(award):
            if isinstance(lit, rdflib.Literal):
                y = extract_year(lit)
                if y:
                    award_year = y
                    break
        
        # 7. Dodanie wiersza do wyników
        rows.append({
            'Person Name':        str(person_name) if person_name else None,
            'Person URI':         person_uri,
            'Award Name':         str(award_name)  if award_name  else None,
            'Award URI':          award_uri,
            'Award Year':         award_year,
            'Oldest Book Title':  str(book_title)  if book_title  else None,
            'Oldest Book URI':    book_uri,
            'Oldest Book Year':   oldest_year
        })

# 8. Utworzenie i wyświetlenie DataFrame
df = pd.DataFrame(rows, columns=[
    'Person Name', 'Person URI',
    'Award Name', 'Award URI', 'Award Year',
    'Oldest Book Title', 'Oldest Book URI', 'Oldest Book Year'
])

print(df.to_markdown(index=False))

#%% 8b

oldest = gsheet_to_df('12GU4iIth0yL2cff1s2cUP6yrTmbCPZlNsGxQye84qE8', 'oldest book')
# oldest = oldest.loc[oldest['award after last book'] == 'True']
earliest = gsheet_to_df('12GU4iIth0yL2cff1s2cUP6yrTmbCPZlNsGxQye84qE8', 'earliest book')
# earliest = earliest.loc[earliest['award after first book'] == 'True']
# 1. Wczytanie pliku Excel ze wszystkimi arkuszami
sheets = {'Oldest': oldest,
          'Earliest': earliest}

# 2. Przetwarzanie każdego arkusza
for sheet_name, df in sheets.items():
    # Filtracja: ostatnia kolumna == True
    last_col = df.columns[-1]
    df_filtered = df[df[last_col] == 'True']
    
    # Grupowanie po nazwie osoby
    group_col = 'Person Name' if 'Person Name' in df_filtered.columns else df_filtered.columns[0]
    counts = df_filtered.groupby(group_col).size().sort_values(ascending=False).head(20)
    
    if counts.empty:
        print(f"Brak danych do wykresu w arkuszu {sheet_name}")
        continue

    # 3. Wykres słupkowy
    plt.figure(figsize=(10, 6))
    counts.plot(kind='bar')
    plt.xlabel('Osoba')
    plt.ylabel('Liczba nagród')
    plt.title(f'Top 20 osób z największą liczbą nagród (arkusz: {sheet_name})')
    plt.xticks(rotation=90, ha='center')
    plt.tight_layout()
    plt.show()

#%% 9

# 2. Przestrzeń nazw
SCH = rdflib.Namespace('http://schema.org/')

# 3. Zbieramy wszystkie wartości sch:genre
genres = []
for text in g.subjects(rdflib.RDF.type, SCH.Text):
    for genre in g.objects(text, SCH.genre):
        genres.append(str(genre))

# 4. Obliczamy udziały procentowe
series = pd.Series(genres, name='genre')
counts = series.value_counts()
percentages = counts / counts.sum() * 100

# 5. Rysujemy poziomy wykres słupkowy
plt.figure(figsize=(8, max(6, 0.3 * len(percentages))))
percentages.sort_values().plot(
    kind='barh'
)
plt.xlabel('Udział (%)')
plt.title('Anteil der Arten an der Basis')
plt.tight_layout()
plt.show()

#%% 10

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')

# 3. Lista trzech wartości sch:about
about_values = {
    'Generationelle Perspektive': 'rechte Gewalt in generationeller Perspektive',
    'Intersektionale Perspektive': 'rechte Gewalt in intersektionaler Perspektive',
    'Andere': 'andere'
}

# 4. Parametry wykresu typu "donut"
radius = 1.0
width = 0.3
inner = radius - width
offset = 0.4  # poziome przesunięcie etykiet

def plot_genre_donut(title, about_val):
    # Zbiór wszystkich gatunków dla tekstów o danym sch:about
    genres = []
    for text in g.subjects(rdflib.RDF.type, SCH.Text):
        if str(g.value(text, SCH.about)) == about_val:
            for genre in g.objects(text, SCH.genre):
                genres.append(str(genre))
    if not genres:
        print(f"Brak danych dla '{title}'")
        return

    # Obliczenie udziałów procentowych
    series = pd.Series(genres, name='genre')
    counts = series.value_counts()
    percentages = counts / counts.sum() * 100

    # Rysowanie donut
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, _ = ax.pie(
        percentages,
        startangle=90,
        radius=radius,
        labels=None,
        wedgeprops=dict(width=width, edgecolor='white')
    )

    # Łamane łączniki + etykiety
    for i, (wedge, (label, pct)) in enumerate(zip(wedges, percentages.items()),1):
        ang = (wedge.theta2 + wedge.theta1) / 2
        x, y = np.cos(np.deg2rad(ang)), np.sin(np.deg2rad(ang))

        # start: środek grubości wycinka
        start_r = inner + width/2
        start = (x * start_r, y * start_r)

        # mid: na zewnętrznej krawędzi
        if title == 'Andere' and label not in ['Autobiographischer Roman', 'Kriminalroman']:
            mid = (x * radius, y * radius + (i/4))
        elif title == 'Generationelle Perspektive' and label not in ['Autobiographischer Roman', 'Kriminalroman', 'Jugendbuch']:
            mid = (x * radius, y * radius + (i/8))
        else: mid = (x * radius, y * radius)

        # end: poziome przesunięcie
        end = (mid[0] + offset * np.sign(x), mid[1])

        # dwuczęściowa łamana
        ax.plot([start[0], mid[0]], [start[1], mid[1]], color='black', lw=0.8)
        ax.plot([mid[0], end[0]],   [mid[1], end[1]], color='black', lw=0.8)

        ha = 'left' if x >= 0 else 'right'
        # nazwa gatunku
        ax.text(end[0], end[1] + 0.02, label, ha=ha, va='bottom', fontsize=9, color='black')
        # procent
        ax.text(end[0], end[1] - 0.02, f"{pct:.1f}%", ha=ha, va='top', fontsize=9, color='black')

    ax.set_title(f'Beitrag von Büchern zum Thema: \n{about_val}', fontsize=12, pad=15)
    ax.axis('equal')
    plt.tight_layout()
    plt.show()

# 5. Generowanie trzech wykresów
for title, about_val in about_values.items():
    plot_genre_donut(title, about_val)

#%% 11

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')
DCT = rdflib.Namespace('http://purl.org/dc/terms/')

# 3. Trzy wartości sch:about i ich opisy
about_values = {
    'Generationelle Perspektive': 'rechte Gewalt in generationeller Perspektive',
    'Intersektionale Perspektive': 'rechte Gewalt in intersektionaler Perspektive',
    'Andere': 'andere'
}

def plot_area_served_distribution(title, about_val):
    # Zbiór areaServed dla wydawnictw tekstów o danym sch:about
    areas = []
    for text in g.subjects(rdflib.RDF.type, SCH.Text):
        if str(g.value(text, SCH.about)) == about_val:
            for pub in g.objects(text, DCT.publisher):
                # Sprawdzamy, czy to Organization
                if (pub, rdflib.RDF.type, SCH.Organization) in g:
                    for area in g.objects(pub, SCH.areaServed):
                        areas.append(str(area))
    if not areas:
        print(f"Brak danych dla '{title}'")
        return

    # Obliczenie udziału procentowego
    series = pd.Series(areas, name='areaServed')
    counts = series.value_counts()
    percentages = counts / counts.sum() * 100

    # Rysowanie wykresu kołowego
    plt.figure(figsize=(6,6))
    plt.pie(
        percentages,
        labels=[f"{a}\n{counts[a]} ({percentages[a]:.1f}%)" for a in counts.index],
        startangle=90,
        autopct=None,
        labeldistance=1.1,
        wedgeprops=dict(edgecolor='white')
    )
    plt.title(f'Beteiligung von Verlagsbereichen für das Thema: \n{about_val}', pad=10)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# 4. Generowanie trzech wykresów
for title, about_val in about_values.items():
    plot_area_served_distribution(title, about_val)

#%% 12

# 3. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')
FABIO = rdflib.Namespace('http://purl.org/spar/fabio/')
geo = rdflib.Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

# 4. Lista wartości sch:about
about_values = {
    'Generationelle Perspektive': 'rechte Gewalt in generationeller Perspektive',
    'Intersektionale Perspektive': 'rechte Gewalt in intersektionaler Perspektive',
    'Andere': 'andere'
}

# 6. Wczytanie mapy świata
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# 7. Generowanie map
for title, about_val in about_values.items():
    # title = 'Generationelle Perspektive'
    # about_val = 'rechte Gewalt in generationeller Perspektive'
    # Zbiór współrzędnych
    coords = []
    for text in g.subjects(rdflib.RDF.type, SCH.Text):
        if str(g.value(text, SCH.about)) == about_val:
            for place in g.objects(text, FABIO.hasPlaceOfPublication):
                if (place, rdflib.RDF.type, SCH.Place) in g:
                    lat = float(g.value(place, geo.lat))
                    lon = float(g.value(place, geo.long))
                    name = str(g.value(place, SCH.name))
                    coord = (lat, lon, name)
                    if coord:
                        coords.append(coord)

    # Przygotowanie GeoDataFrame
    df = pd.DataFrame(coords, columns=['latitude', 'longitude', 'name'])
    counts = df.groupby(['latitude', 'longitude', 'name']).size().reset_index(name='count')
    
    fig = px.scatter_mapbox(
            counts,
            lat="latitude",
            lon="longitude",
            size="count",
            hover_name="name",
            # hover_data=["title"],
            color_discrete_sequence=["red"],
            # animation_frame="year_fixed",
            # animation_group='name',
            zoom=3.75,
            center={'lat': 50.076301241046366,
                    'lon': 14.427848170989792}
            )
            
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    plot(fig, auto_open=False, filename=f'data/{title}.html')

#%% 13a

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')
ns_map = dict(g.namespaces())
RE = rdflib.Namespace(ns_map.get('rechtsextremismus'))

# 3. Zebranie wartości rechtsextremismus:whichNovel dla każdego Text
novels = []
for text in g.subjects(rdflib.RDF.type, SCH.Text):
    if pd.notnull(g.objects(text, SCH.about)):
        for novel in g.objects(text, RE.whichNovel):
            if str(novel) != 'nan':
                novels.append(str(novel))

# 4. Obliczenie udziałów procentowych
series = pd.Series(novels, name='whichNovel')
counts = series.value_counts()
percentages = counts / counts.sum() * 100

# 5. Rysowanie wykresu kołowego
plt.figure(figsize=(8, 8))
plt.pie(
    percentages,
    labels=[f"{label}\n{counts[label]} ({percentages[label]:.1f}%)" for label in counts.index],
    startangle=90,
    autopct=None,
    labeldistance=1.1,
    wedgeprops=dict(edgecolor='white')
)
plt.title('Aufschlüsselung von Debüt- und Folgeroman', size=20)
plt.axis('equal')
plt.tight_layout()
plt.show()

#%% 13 b i c

# 2. Definicja przestrzeni nazw
SCH = rdflib.Namespace('http://schema.org/')
ns_map = dict(g.namespaces())
RE = rdflib.Namespace(ns_map.get('rechtsextremismus'))

# 3. Definicja dwóch kategorii whichNovel
categories = {
    'Debütroman': 'Debütroman',  
    'weiterer Roman': 'weiterer Roman'
}

# 4. Funkcja rysująca wykres kołowy rozkładu gatunków dla danej kategorii whichNovel
def plot_genre_for_novel_type(title, which_val):
    # Zbiór gatunków dla tekstów spełniających warunek whichNovel
    genres = []
    for text in g.subjects(rdflib.RDF.type, SCH.Text):
        for wn in g.objects(text, RE.whichNovel):
            if str(wn).lower() == which_val:
                for genre in g.objects(text, SCH.genre):
                    genres.append(str(genre))
    if not genres:
        print(f"Brak danych dla kategorii: {title}")
        return

    # Obliczenie udziałów procentowych
    series = pd.Series(genres, name='genre')
    counts = series.value_counts()

    # Rysowanie poziomego wykresu słupkowego
    plt.figure(figsize=(10, 6))
    counts.sort_values().plot(kind='barh')
    plt.xlabel('Liczba wystąpień')
    plt.ylabel('Gatunek')
    plt.title(f'Artenverteilung für {title}')
    plt.tight_layout()
    plt.show()

# 5. Generowanie obu wykresów
for title, which_val in categories.items():
    plot_genre_for_novel_type(title, which_val.lower())




















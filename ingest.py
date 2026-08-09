from Bio import Entrez
import chromadb
import time

Entrez.email = "englich.felix@gmail.com"
Entrez.api_key = "91710f6a8f9917c17bb11e15aa63f7f55008"

suchbegriffe_mit_kategorie = [
    # Typ 3c / pankreatogener Diabetes
    ("pancreatogenic diabetes type 3c", "Typ 3c"),
    ("type 3c diabetes mellitus pancreatic", "Typ 3c"),
    ("exocrine pancreatic insufficiency diabetes", "Typ 3c"),
    ("chronic pancreatitis diabetes secondary", "Typ 3c"),
    ("pancreatic cancer diabetes glucose", "Typ 3c"),

    # Typ 1
    ("type 1 diabetes mellitus pathophysiology", "Typ 1"),
    ("type 1 diabetes autoimmune insulin", "Typ 1"),
    ("type 1 diabetes children diagnosis", "Typ 1"),
    ("type 1 diabetes management guidelines", "Typ 1"),

    # Typ 2
    ("type 2 diabetes mellitus management", "Typ 2"),
    ("type 2 diabetes insulin resistance", "Typ 2"),
    ("type 2 diabetes lifestyle treatment", "Typ 2"),
    ("type 2 diabetes prevention diet", "Typ 2"),
    ("type 2 diabetes medication metformin", "Typ 2"),

    # Blutzucker
    ("blood glucose monitoring management", "Blutzucker"),
    ("blood sugar control diet", "Blutzucker"),
    ("hyperglycemia causes treatment", "Blutzucker"),
    ("hypoglycemia symptoms management", "Blutzucker"),
    ("glucose variability diabetes", "Blutzucker"),
    ("HbA1c diabetes management target", "Blutzucker"),

    # Insulin
    ("insulin therapy diabetes types", "Insulin"),
    ("insulin dosing regimen diabetes", "Insulin"),
    ("insulin analog basal bolus", "Insulin"),
    ("insulin resistance mechanisms", "Insulin"),
    ("insulin injection technique guidelines", "Insulin"),

    # Insulinpumpen & Technologie
    ("insulin pump therapy diabetes", "Technologie"),
    ("automated insulin delivery system", "Technologie"),
    ("continuous glucose monitoring CGM", "Technologie"),
    ("closed loop insulin pump artificial pancreas", "Technologie"),
    ("insulin pump complications management", "Technologie"),
    ("diabetes technology review", "Technologie"),

    # Komplikationen
    ("diabetes mellitus complications review", "Komplikationen"),
    ("diabetic neuropathy treatment", "Komplikationen"),
    ("diabetic retinopathy screening", "Komplikationen"),
    ("diabetic nephropathy kidney disease", "Komplikationen"),
    ("diabetic foot ulcer care", "Komplikationen"),
    ("diabetes cardiovascular risk", "Komplikationen"),

    # Ernährung & Alltag
    ("diabetes nutrition dietary management", "Ernährung"),
    ("carbohydrate counting diabetes", "Ernährung"),
    ("diabetes meal planning guidelines", "Ernährung"),
    ("glycemic index food diabetes", "Ernährung"),
    ("exercise diabetes glucose control", "Ernährung"),
    ("diabetes diet patient education", "Ernährung"),

    # Weitere Formen
    ("gestational diabetes pregnancy management", "Andere Formen"),
    ("prediabetes diagnosis prevention", "Andere Formen"),
    ("MODY monogenic diabetes", "Andere Formen"),
]

id_zu_kategorie = {}

for begriff, kategorie in suchbegriffe_mit_kategorie:
    print(f"Suche: '{begriff}' ({kategorie})...")
    handle = Entrez.esearch(db="pubmed", term=begriff, retmax=50)
    ergebnis = Entrez.read(handle)
    handle.close()
    for pmid in ergebnis['IdList']:
        if pmid not in id_zu_kategorie:
            id_zu_kategorie[pmid] = kategorie
    time.sleep(0.11)

alle_ids = list(id_zu_kategorie.keys())
print(f"\nInsgesamt {len(alle_ids)} eindeutige Papers gefunden.\n")

dokumente = []
titel_liste = []
id_liste = []
kategorie_liste = []

haeppchen_groesse = 20
for i in range(0, len(alle_ids), haeppchen_groesse):
    haeppchen = alle_ids[i:i + haeppchen_groesse]
    print(f"Hole Details für Papers {i+1} bis {i+len(haeppchen)}...")

    handle = Entrez.efetch(db="pubmed", id=haeppchen, rettype="abstract", retmode="xml")
    papers = Entrez.read(handle)
    handle.close()

    for artikel in papers['PubmedArticle']:
        pmid = str(artikel['MedlineCitation']['PMID'])
        titel = str(artikel['MedlineCitation']['Article']['ArticleTitle'])

        try:
            abstract = str(artikel['MedlineCitation']['Article']['Abstract']['AbstractText'][0])
        except KeyError:
            abstract = None

        if abstract:
            dokumente.append(abstract)
            titel_liste.append(titel)
            id_liste.append(pmid)
            kategorie_liste.append(id_zu_kategorie.get(pmid, "Allgemein"))

    time.sleep(0.11)

print(f"\n{len(dokumente)} Papers mit Abstract werden gespeichert.\n")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="diabetes_papers")

for i in range(0, len(dokumente), 50):
    collection.upsert(
        documents=dokumente[i:i+50],
        metadatas=[{"titel": t, "kategorie": k} for t, k in zip(titel_liste[i:i+50], kategorie_liste[i:i+50])],
        ids=id_liste[i:i+50]
    )

print("Fertig!")
print(f"Anzahl Dokumente in der Collection: {collection.count()}")
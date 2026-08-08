from Bio import Entrez
import chromadb
import time

Entrez.email = "englich.felix@gmail.com"
Entrez.api_key = "91710f6a8f9917c17bb11e15aa63f7f55008"

# Mehrere Suchbegriffe, um breiter abzudecken
suchbegriffe = [
    "pancreatogenic diabetes type 3c",
    "type 3c diabetes mellitus pancreatic",
    "exocrine pancreatic insufficiency diabetes",
    "chronic pancreatitis diabetes secondary",
    "pancreatic cancer diabetes glucose",

    # Typ 1 Diabetes
    "type 1 diabetes mellitus pathophysiology",
    "type 1 diabetes autoimmune insulin",
    "type 1 diabetes children diagnosis",
    "type 1 diabetes management guidelines",

    # Typ 2 Diabetes
    "type 2 diabetes mellitus management",
    "type 2 diabetes insulin resistance",
    "type 2 diabetes lifestyle treatment",
    "type 2 diabetes prevention diet",
    "type 2 diabetes medication metformin",

    # Blutzucker allgemein
    "blood glucose monitoring management",
    "blood sugar control diet",
    "hyperglycemia causes treatment",
    "hypoglycemia symptoms management",
    "glucose variability diabetes",
    "HbA1c diabetes management target",

    # Insulin
    "insulin therapy diabetes types",
    "insulin dosing regimen diabetes",
    "insulin analog basal bolus",
    "insulin resistance mechanisms",
    "insulin injection technique guidelines",

    # Insulinpumpen & Technologie
    "insulin pump therapy diabetes",
    "automated insulin delivery system",
    "continuous glucose monitoring CGM",
    "closed loop insulin pump artificial pancreas",
    "insulin pump complications management",
    "diabetes technology review",

    # Komplikationen
    "diabetes mellitus complications review",
    "diabetic neuropathy treatment",
    "diabetic retinopathy screening",
    "diabetic nephropathy kidney disease",
    "diabetic foot ulcer care",
    "diabetes cardiovascular risk",

    # Ernährung & Lebensstil
    "diabetes nutrition dietary management",
    "carbohydrate counting diabetes",
    "exercise diabetes glucose control",

    # Weitere Formen
    "gestational diabetes pregnancy management",
    "prediabetes diagnosis prevention",
    "MODY monogenic diabetes",
]


alle_ids = set()  # set verhindert doppelte IDs

for begriff in suchbegriffe:
    print(f"Suche: '{begriff}'...")
    handle = Entrez.esearch(db="pubmed", term=begriff, retmax=50)
    ergebnis = Entrez.read(handle)
    handle.close()
    alle_ids.update(ergebnis['IdList'])
    time.sleep(0.11)  # NCBI bittet um max. 3 Anfragen/Sekunde

alle_ids = list(alle_ids)
print(f"\nInsgesamt {len(alle_ids)} eindeutige Papers gefunden.\n")

# Details in Häppchen abrufen (NCBI mag keine riesigen Anfragen auf einmal)
dokumente = []
titel_liste = []
id_liste = []

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

    time.sleep(0.11)

print(f"\n{len(dokumente)} Papers mit Abstract werden gespeichert.\n")

# In ChromaDB speichern
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="diabetes_papers")

# In Häppchen speichern (ChromaDB mag auch keine riesigen Batches)
for i in range(0, len(dokumente), 50):
    collection.upsert(
        documents=dokumente[i:i+50],
        metadatas=[{"titel": t} for t in titel_liste[i:i+50]],
        ids=id_liste[i:i+50]
    )

print("Fertig!")
print(f"Anzahl Dokumente in der Collection: {collection.count()}")
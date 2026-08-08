from Bio import Entrez
import chromadb
import ollama

Entrez.email = "englich.felix@gmail.com"

suchbegriff = "pancreatogenic diabetes type 3c"

# Schritt 1: Suche -> IDs holen
handle = Entrez.esearch(db="pubmed", term=suchbegriff, retmax=5)
ergebnis = Entrez.read(handle)
handle.close()

ids = ergebnis['IdList']
print(f"Gefundene Papers: {ergebnis['Count']}")
print(f"Hole Details zu {len(ids)} Papers...\n")

# Schritt 2: Details zu diesen IDs holen
handle = Entrez.efetch(db="pubmed", id=ids, rettype="abstract", retmode="xml")
papers = Entrez.read(handle)
handle.close()

# Schritt 3: Titel + Abstract sauber sammeln
dokumente = []
titel_liste = []
id_liste = []

for artikel in papers['PubmedArticle']:
    pmid = str(artikel['MedlineCitation']['PMID'])
    titel = str(artikel['MedlineCitation']['Article']['ArticleTitle'])

    try:
        abstract = str(artikel['MedlineCitation']['Article']['Abstract']['AbstractText'][0])
    except KeyError:
        abstract = None

    if abstract:  # nur Papers MIT Abstract speichern
        dokumente.append(abstract)
        titel_liste.append(titel)
        id_liste.append(pmid)

print(f"{len(dokumente)} Papers mit Abstract werden gespeichert.\n")

# Schritt 4: ChromaDB einrichten und Papers reinschreiben
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="diabetes_papers")

collection.add(
    documents=dokumente,
    metadatas=[{"titel": t} for t in titel_liste],
    ids=id_liste
)

print("Fertig! Papers sind jetzt in ChromaDB gespeichert.")
print(f"Anzahl Dokumente in der Collection: {collection.count()}")
# Test: eine Frage stellen und die passendsten Papers finden
frage = "What causes exocrine pancreatic insufficiency in diabetes?"

treffer = collection.query(
    query_texts=[frage],
    n_results=2
)

print(f"\n--- Suche: '{frage}' ---")
for i, doc in enumerate(treffer['documents'][0]):
    titel = treffer['metadatas'][0][i]['titel']
    print(f"\nTreffer {i+1}: {titel}")
    print(f"Auszug: {doc[:200]}...")
# Kontext aus den Treffern zusammenbauen
kontext = "\n\n".join(treffer['documents'][0])

prompt = f"""Beantworte die folgende Frage NUR basierend auf dem gegebenen Kontext.
Wenn die Antwort nicht im Kontext steht, sag das ehrlich.

Kontext:
{kontext}

Frage: {frage}

Antwort:"""

print("\n--- Antwort von phi3 ---")
antwort = ollama.chat(
    model="phi3",
    messages=[{"role": "user", "content": prompt}]
)

print(antwort['message']['content'])
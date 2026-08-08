import streamlit as st
import chromadb
import ollama

# Seite konfigurieren
st.set_page_config(page_title="Diabetes Typ 3c Assistent", page_icon="🩺")
st.title("🩺 Diabetes Typ 3c Wissensassistent")
st.caption("Basiert auf wissenschaftlichen PubMed-Artikeln · Läuft komplett lokal")

# ChromaDB verbinden (einmalig, wird gecacht)
@st.cache_resource
def lade_datenbank():
    client = chromadb.PersistentClient(path="./chroma_db")
    return client.get_or_create_collection(name="diabetes_papers")

collection = lade_datenbank()
@st.cache_resource
def lade_steckbrief():
    try:
        with open("steckbrief.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

steckbrief = lade_steckbrief()

st.info(f"📚 Wissensbasis: {collection.count()} wissenschaftliche Artikel")

# Eingabefeld für die Frage
frage = st.text_input("Stell deine Frage:", placeholder="z.B. Was verursacht Typ 3c Diabetes?")

anzahl_quellen = st.slider("Anzahl der Quellen zur Beantwortung", min_value=2, max_value=12, value=6)

if st.button("Frage stellen") and frage:
    with st.spinner("Suche relevante Studien..."):
        treffer = collection.query(query_texts=[frage], n_results=anzahl_quellen)

    kontext = "\n\n".join(treffer['documents'][0])

    prompt = f"""Du bist ein einfühlsamer medizinischer Assistent, der einem Patienten hilft, seine Erkrankung besser zu verstehen.

Sprich wie ein Arzt, der einem Patienten in einem persönlichen Gespräch etwas erklärt: warm, geduldig, in einfachen und klaren Worten. Vermeide unnötigen Fachjargon – wenn ein Fachbegriff nötig ist, erklär ihn kurz in Klammern. Keine trockene Aufzählung, sondern ein natürlicher, verständlicher Fließtext.

Antworte NUR basierend auf dem gegebenen Kontext. Wenn die Antwort nicht im Kontext steht, sag das ehrlich und ruhig, ohne den Patienten zu verunsichern.

Informationen zum Patienten:
{steckbrief if steckbrief else "(keine Angaben hinterlegt)"}

Wissenschaftlicher Kontext:
{kontext}

Frage des Patienten: {frage}

Antwort:"""
    with st.spinner("phi3 formuliert die Antwort..."):
        antwort = ollama.chat(
            model="phi3",
            messages=[{"role": "user", "content": prompt}]
        )

    st.subheader("Antwort")
    st.write(antwort['message']['content'])

    with st.expander(f"📄 Verwendete Quellen ({anzahl_quellen})"):
        for i, doc in enumerate(treffer['documents'][0]):
            titel = treffer['metadatas'][0][i]['titel']
            st.markdown(f"**{i+1}. {titel}**")
            st.caption(doc[:300] + "...")
            st.divider()
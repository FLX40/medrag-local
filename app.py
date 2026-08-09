import streamlit as st
import chromadb
import ollama
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PFAD = r"C:\poppler\poppler-24.08.0\Library\bin"

st.set_page_config(
    page_title="Diabetes Wissensassistent",
    layout="centered",
)

if "nachrichten" not in st.session_state:
    st.session_state.nachrichten = []

leerer_start = len(st.session_state.nachrichten) == 0

st.markdown("""
<style>
header[data-testid="stHeader"] {
height: 2rem;
background: transparent;
}
header[data-testid="stHeader"] button {
transform: scale(0.75);
}
div[data-testid="stToolbar"] {
transform: scale(0.75);
right: 0.4rem;
}
html, body, [class*="css"] {
font-size: 16px;
}
.stApp {
background-color: #fbfaf6;
}
.mono {
font-family: "Courier New", Courier, monospace;
}
.hero-zentral {
display: flex;
flex-direction: column;
align-items: center;
text-align: center;
padding: 0.6rem 0 0.3rem 0;
}
.hero-badge {
font-family: "Courier New", Courier, monospace;
font-size: 12.5px;
color: #0000f2;
border: 1px solid #0000f2;
border-radius: 3px;
padding: 3px 10px;
letter-spacing: 0.04em;
margin-top: 0.9rem;
background-color: #ffffff;
}
.hero-zentral h1 {
font-size: 2.9rem;
line-height: 1.02;
color: #0a0a1a;
margin: 1rem 0 0 0;
font-weight: 800;
letter-spacing: -0.03em;
}
.hero-zentral h1 .blau {
color: #0000f2;
}
.untertitel {
font-family: "Courier New", Courier, monospace;
color: #55557a;
font-size: 13.5px;
margin: 0.9rem 0 0 0;
letter-spacing: 0.02em;
}
.ascii-deko {
font-family: "Courier New", Courier, monospace;
color: #0000f2;
font-size: 13px;
margin-top: 0.8rem;
opacity: 0.75;
letter-spacing: 0.05em;
}
.basis-info {
font-family: "Courier New", Courier, monospace;
display: inline-block;
background-color: #ffffff;
border: 1px solid #ddd9cc;
color: #3a3a6a;
font-size: 12px;
padding: 4px 12px;
margin-top: 12px;
margin-bottom: 0.6rem;
}
.abschnitt-label {
font-family: "Courier New", Courier, monospace;
font-size: 12.5px;
color: #0000f2;
letter-spacing: 0.05em;
margin-bottom: 2px;
}
.stButton button {
background-color: #ffffff;
color: #0000f2;
border-radius: 4px;
padding: 0.45rem 1.2rem;
font-weight: 650;
font-size: 14.5px;
border: 1.5px solid #0000f2;
box-shadow: none;
}
.stButton button:hover {
background-color: #0000f2;
color: #ffffff;
}
div[data-testid="stChatInput"] {
border-radius: 6px;
border: 1.5px solid #0000f2;
background-color: #ffffff;
box-shadow: 4px 4px 0px #e3e0d4;
}
div[data-testid="stChatInput"]:focus-within {
box-shadow: 4px 4px 0px #c9c5b4;
}
div[data-testid="stChatMessage"] {
background-color: #ffffff;
border: 1px solid #e3e0d4;
border-radius: 6px;
padding: 1rem 1.2rem;
margin-bottom: 0.7rem;
}
div[data-testid="stExpander"] {
border: 1px solid #e3e0d4;
border-radius: 6px;
background-color: #f7f5ef;
}
.stTextInput input, .stTextArea textarea {
border-radius: 4px;
border: 1.5px solid #ddd9cc;
font-size: 15px;
background-color: #ffffff;
}
.stTextInput input:focus, .stTextArea textarea:focus {
border-color: #0000f2;
}
.footer-hinweis {
font-family: "Courier New", Courier, monospace;
font-size: 11.5px;
color: #a09c8c;
text-align: center;
padding-top: 1.4rem;
line-height: 1.7;
letter-spacing: 0.02em;
}
hr {
border-color: #e8e5da !important;
margin: 0.8rem 0 !important;
}
</style>
""", unsafe_allow_html=True)

CADUCEUS_SVG = "<svg width=\"104\" height=\"104\" viewBox=\"0 0 100 100\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><circle cx=\"50\" cy=\"9\" r=\"3.4\" fill=\"#0000f2\"/><line x1=\"50\" y1=\"14\" x2=\"50\" y2=\"93\" stroke=\"#0000f2\" stroke-width=\"3.6\" stroke-linecap=\"round\"/><path d=\"M 47 21 C 38 10, 22 8, 12 16 C 21 18, 27 21, 31 25 C 23 24, 16 27, 11 33 C 20 32, 28 32, 34 31 C 28 34, 24 38, 22 43 C 30 40, 38 35, 44 29 Z\" fill=\"#0000f2\"/><path d=\"M 53 21 C 62 10, 78 8, 88 16 C 79 18, 73 21, 69 25 C 77 24, 84 27, 89 33 C 80 32, 72 32, 66 31 C 72 34, 76 38, 78 43 C 70 40, 62 35, 56 29 Z\" fill=\"#0000f2\"/><path d=\"M 35 32 C 68 40, 32 50, 50 55 C 68 60, 32 70, 50 75 C 62 79, 66 84, 63 91\" stroke=\"#0000f2\" stroke-width=\"3.4\" fill=\"none\" stroke-linecap=\"round\"/><path d=\"M 65 32 C 32 40, 68 50, 50 55 C 32 60, 68 70, 50 75 C 38 79, 34 84, 37 91\" stroke=\"#0000f2\" stroke-width=\"3.4\" fill=\"none\" stroke-linecap=\"round\"/><circle cx=\"35\" cy=\"31\" r=\"3\" fill=\"#0000f2\"/><circle cx=\"65\" cy=\"31\" r=\"3\" fill=\"#0000f2\"/></svg>"

CADUCEUS_MINI = "<svg width=\"40\" height=\"40\" viewBox=\"0 0 100 100\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><circle cx=\"50\" cy=\"9\" r=\"4\" fill=\"#0000f2\"/><line x1=\"50\" y1=\"14\" x2=\"50\" y2=\"93\" stroke=\"#0000f2\" stroke-width=\"4.5\" stroke-linecap=\"round\"/><path d=\"M 47 21 C 38 10, 22 8, 12 16 C 21 18, 27 21, 31 25 C 23 24, 16 27, 11 33 C 20 32, 28 32, 34 31 C 28 34, 24 38, 22 43 C 30 40, 38 35, 44 29 Z\" fill=\"#0000f2\"/><path d=\"M 53 21 C 62 10, 78 8, 88 16 C 79 18, 73 21, 69 25 C 77 24, 84 27, 89 33 C 80 32, 72 32, 66 31 C 72 34, 76 38, 78 43 C 70 40, 62 35, 56 29 Z\" fill=\"#0000f2\"/><path d=\"M 35 32 C 68 40, 32 50, 50 55 C 68 60, 32 70, 50 75 C 62 79, 66 84, 63 91\" stroke=\"#0000f2\" stroke-width=\"4.2\" fill=\"none\" stroke-linecap=\"round\"/><path d=\"M 65 32 C 32 40, 68 50, 50 55 C 32 60, 68 70, 50 75 C 38 79, 34 84, 37 91\" stroke=\"#0000f2\" stroke-width=\"4.2\" fill=\"none\" stroke-linecap=\"round\"/></svg>"

@st.cache_resource
def lade_datenbank():
    client = chromadb.PersistentClient(path="./chroma_db")
    return client.get_or_create_collection(name="diabetes_papers")

collection = lade_datenbank()
KATEGORIE_STICHWORTE = {
    "Typ 3c": ["typ 3c", "typ-3c", "3c diabetes", "pankreatogen", "bauchspeicheldrüse", "pankreatitis", "pankreas"],
    "Typ 1": ["typ 1", "typ-1", "autoimmun"],
    "Typ 2": ["typ 2", "typ-2", "insulinresistenz"],
    "Blutzucker": ["blutzucker", "glukose", "hba1c", "unterzuckerung", "überzuckerung", "hypoglyk", "hyperglyk"],
    "Insulin": ["insulin", "spritzen", "injektion", "dosierung"],
    "Technologie": ["pumpe", "sensor", "cgm", "messgerät", "insulinpumpe"],
    "Komplikationen": ["nerven", "augen", "niere", "fuß", "herz", "netzhaut", "neuropathie", "retinopathie"],
    "Ernährung": ["essen", "ernährung", "kohlenhydrate", "mahlzeit", "diät", "lebensmittel", "sport", "bewegung"],
    "Andere Formen": ["schwangerschaft", "gestations", "mody"],
}

def kategorien_erkennen(frage_text):
    frage_klein = frage_text.lower()
    treffer_kategorien = []
    for kategorie, stichworte in KATEGORIE_STICHWORTE.items():
        for wort in stichworte:
            if wort in frage_klein:
                treffer_kategorien.append(kategorie)
                break
    return treffer_kategorien

@st.cache_resource
def lade_dokumenten_datenbank():
    client = chromadb.PersistentClient(path="./chroma_db")
    return client.get_or_create_collection(name="persoenliche_dokumente")

dokumente_collection = lade_dokumenten_datenbank()

@st.cache_resource
def lade_steckbrief():
    try:
        with open("steckbrief.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

steckbrief = lade_steckbrief()

def text_aus_datei_extrahieren(datei):
    text = ""
    dateiname = datei.name.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(dateiname)[1]) as tmp:
        tmp.write(datei.getvalue())
        tmp_pfad = tmp.name
    if dateiname.endswith(".pdf"):
        seiten = convert_from_path(tmp_pfad, poppler_path=POPPLER_PFAD)
        for seite in seiten:
            text += pytesseract.image_to_string(seite, lang="deu") + "\n"
    else:
        bild = Image.open(tmp_pfad)
        text = pytesseract.image_to_string(bild, lang="deu")
    os.remove(tmp_pfad)
    return text.strip()

def steckbrief_popover():
    with st.popover("Persönliche Angaben"):
        st.markdown("<span class=\"abschnitt-label\">#0 Profil</span>", unsafe_allow_html=True)
        st.caption("Wird bei jeder Frage automatisch berücksichtigt.")

        def wert_holen(feld_name, text):
            for zeile in text.split("\n"):
                if zeile.startswith(feld_name + ":"):
                    return zeile.split(":", 1)[1].strip()
            return ""

        eingabe_name = st.text_input("Name", value=wert_holen("Name", steckbrief))
        eingabe_diagnose = st.text_input("Diagnose", value=wert_holen("Diagnose", steckbrief))
        eingabe_seit = st.text_input("Diagnose seit", value=wert_holen("Diagnose seit", steckbrief))
        eingabe_vorerkrankung = st.text_input("Vorerkrankung", value=wert_holen("Vorerkrankung", steckbrief))
        eingabe_medikation = st.text_input("Aktuelle Medikation", value=wert_holen("Aktuelle Medikation", steckbrief))
        eingabe_besonderheiten = st.text_area("Besonderheiten", value=wert_holen("Besonderheiten", steckbrief))

        if st.button("Angaben speichern"):
            neuer_steckbrief = "Name: " + eingabe_name + "\nDiagnose: " + eingabe_diagnose + "\nDiagnose seit: " + eingabe_seit + "\nVorerkrankung: " + eingabe_vorerkrankung + "\nAktuelle Medikation: " + eingabe_medikation + "\nBesonderheiten: " + eingabe_besonderheiten
            with open("steckbrief.txt", "w", encoding="utf-8") as f:
                f.write(neuer_steckbrief)
            st.cache_resource.clear()
            st.rerun()

kopf_links, kopf_rechts = st.columns([5, 2])
with kopf_links:
    if not leerer_start:
        kopf_html = "<div style=\"display:flex;align-items:center;gap:12px;\">" + CADUCEUS_MINI + "<div><span style=\"font-size:1.1rem;font-weight:750;color:#0a0a1a;letter-spacing:-0.01em;\">Diabetes Wissensassistent</span><br><span class=\"mono\" style=\"font-size:11.5px;color:#a09c8c;\">" + str(collection.count()) + " Studien · " + str(dokumente_collection.count()) + " Dokumente · 100% lokal</span></div></div>"
        st.markdown(kopf_html, unsafe_allow_html=True)
with kopf_rechts:
    steckbrief_popover()

if leerer_start:
    hero_html = "<div class=\"hero-zentral\">" + CADUCEUS_SVG + "<div class=\"hero-badge\">Privat · 100% Lokal · Open Source</div><h1>Dein Wissen.<br>Deine Daten.<br><span class=\"blau\">Dein Assistent.</span></h1><p class=\"untertitel\">Wissenschaftlich fundiert · Persönlich erklärt · Läuft komplett offline</p><div class=\"ascii-deko\">/\\-_=+|&lt; medizin ~:*-/ wissen =+|&lt;-\\</div><span class=\"basis-info\">[" + str(collection.count()) + " Studien] · [" + str(dokumente_collection.count()) + " eigene Dokumente]</span></div>"
    st.markdown(hero_html, unsafe_allow_html=True)
else:
    st.divider()

for nachricht in st.session_state.nachrichten:
    with st.chat_message(nachricht["rolle"]):
        st.write(nachricht["inhalt"])
        if nachricht.get("quellen"):
            with st.expander("Verwendete Quellen"):
                for i, (titel, auszug) in enumerate(nachricht["quellen"]):
                    st.markdown(f"**{i+1}. {titel}**")
                    st.caption(auszug)

eingabe = st.chat_input(
    "Stell deine Frage – oder häng einen Befund an...",
    accept_file=True,
    file_type=["png", "jpg", "jpeg", "pdf"],
)

if eingabe:
    frage = eingabe.text if eingabe.text else ""
    dateien = eingabe.files if eingabe.files else []

    for datei in dateien:
        with st.spinner(f"Lese '{datei.name}' ein..."):
            try:
                erkannter_text = text_aus_datei_extrahieren(datei)
            except Exception:
                erkannter_text = ""

        if erkannter_text:
            doc_id = datei.name + "_" + str(dokumente_collection.count())
            dokumente_collection.add(
                documents=[erkannter_text],
                metadatas=[{"dateiname": datei.name}],
                ids=[doc_id]
            )
            bestaetigung = f"Der Befund '{datei.name}' wurde eingelesen und gespeichert ({len(erkannter_text)} Zeichen erkannt). Er wird ab jetzt bei deinen Fragen berücksichtigt."
        else:
            bestaetigung = f"Aus '{datei.name}' konnte leider kein Text erkannt werden. Ist das Bild scharf genug?"

        st.session_state.nachrichten.append({"rolle": "assistant", "inhalt": bestaetigung})

    if frage:
        st.session_state.nachrichten.append({"rolle": "user", "inhalt": frage})

        with st.spinner("Suche relevante Studien..."):
            erkannte_kategorien = kategorien_erkennen(frage)
            if erkannte_kategorien:
                treffer = collection.query(
                    query_texts=[frage],
                    n_results=8,
                    where={"kategorie": {"$in": erkannte_kategorien}}
                )
            else:
                treffer = collection.query(query_texts=[frage], n_results=8)

            eigene_treffer = None
            if dokumente_collection.count() > 0:
                eigene_treffer = dokumente_collection.query(query_texts=[frage], n_results=3)

        kontext = "\n\n".join(treffer['documents'][0])
        eigener_kontext = ""
        if eigene_treffer and eigene_treffer['documents'][0]:
            eigener_kontext = "\n\n".join(eigene_treffer['documents'][0])

        prompt = f"""Du bist ein einfühlsamer medizinischer Assistent, der einem Patienten hilft, seine Erkrankung besser zu verstehen.

Sprich wie ein Arzt, der einem Patienten etwas erklärt: warm, geduldig, in einfachen und klaren Worten. Vermeide unnötigen Fachjargon – wenn ein Fachbegriff nötig ist, erklär ihn kurz in Klammern. Antworte direkt auf die gestellte Frage. Stelle KEINE eigenen Rückfragen und erfinde KEINEN Dialogverlauf – antworte ausschließlich auf das, was tatsächlich gefragt wurde.

Falls der wissenschaftliche Kontext die Frage nicht direkt beantwortet (z. B. weil es sich um eine allgemeine Alltagsfrage statt um Forschungsinhalte handelt), sag das offen und gib nur die Informationen weiter, die tatsächlich im Kontext stehen – ohne zu improvisieren oder Allgemeinwissen als gesichert darzustellen.
Informationen zum Patienten:
{steckbrief if steckbrief else "(keine Angaben hinterlegt)"}

Wissenschaftlicher Kontext:
{kontext}

Persönliche Befunde des Patienten (falls vorhanden):
{eigener_kontext if eigener_kontext else "(keine eigenen Dokumente hochgeladen)"}

Frage des Patienten: {frage}

Antwort:"""

        with st.spinner("Antwort wird formuliert..."):
            try:
                antwort = ollama.chat(
                    model="llama3.1:8b",
                    messages=[{"role": "user", "content": prompt}]
                )
                antwort_text = antwort['message']['content']
                quellen = []
                for i, doc in enumerate(treffer['documents'][0]):
                    titel = treffer['metadatas'][0][i]['titel']
                    quellen.append((titel, doc[:250] + "..."))
            except Exception:
                antwort_text = "Die Verbindung zum Sprachmodell (Ollama) ist gerade nicht möglich. Bitte starte Ollama über das Startmenü und stell deine Frage danach einfach nochmal."
                quellen = []

        st.session_state.nachrichten.append({
            "rolle": "assistant",
            "inhalt": antwort_text,
            "quellen": quellen,
        })

    st.rerun()

st.markdown("""
<div class="footer-hinweis">
Dieses Tool dient dem besseren Verständnis deiner Erkrankung und ersetzt keine ärztliche Beratung.<br>
Bei medizinischen Entscheidungen wende dich bitte immer an deinen Arzt.<br>
MedRAG Local v1.0 · Privat & Lokal · 2026
</div>
""", unsafe_allow_html=True)
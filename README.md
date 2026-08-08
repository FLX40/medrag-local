# 🩺 MedRAG Local – Lokaler KI-Wissensassistent für Diabetes

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Ollama](https://img.shields.io/badge/LLM-Ollama%20%C2%B7%20phi3-green)
![ChromaDB](https://img.shields.io/badge/Vektordatenbank-ChromaDB-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![License](https://img.shields.io/badge/Lizenz-MIT-lightgrey)

Ein Retrieval-Augmented-Generation-System (RAG), das medizinische Fragen auf Basis von über **1.700 wissenschaftlichen PubMed-Studien** beantwortet – mit Schwerpunkt auf pankreatogenem Diabetes (Typ 3c). Der komplette Zyklus aus Suche, Kontext-Anreicherung und Antwortgenerierung läuft **vollständig lokal und offline**: keine Cloud-API, keine laufenden Kosten, volle Kontrolle über die Daten.

---

## 💡 Warum dieses Projekt

**Lernmotivation:** Ich habe dieses Projekt als Python-Einsteiger in strukturierten Lernsessions aufgebaut, um die Architektur moderner RAG-Systeme von Grund auf zu verstehen – nicht durch das Ansprechen einer fertigen API, sondern durch das eigenständige Zusammensetzen aller Bausteine: Datenbeschaffung, Embeddings, Vektorsuche, LLM-Anbindung und Benutzeroberfläche.

**Praktischer Nutzen:** Typ-3c-Diabetes (pankreatogener Diabetes) ist eine seltene, häufig fehldiagnostizierte Diabetesform, zu der verständliche Informationen schwer zu finden sind. Dieses Tool macht wissenschaftliche Fachliteratur zugänglich: Man stellt eine Frage in Alltagssprache und erhält eine verständliche, quellenbelegte Antwort – formuliert wie von einem Arzt, der sich Zeit nimmt, statt in Fachjargon.

---

## 🏗️ Architektur

### Das RAG-Prinzip in drei Schritten

```
Frage des Nutzers
      │
      ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  1. RETRIEVAL   │───▶│ 2. AUGMENTATION  │───▶│  3. GENERATION   │
│                 │    │                  │    │                  │
│ Semantische     │    │ Treffer werden   │    │ Lokales LLM      │
│ Suche findet    │    │ als Kontext mit  │    │ formuliert eine  │
│ relevante       │    │ der Frage        │    │ verständliche    │
│ Studien in      │    │ kombiniert       │    │ Antwort mit      │
│ ChromaDB        │    │                  │    │ Quellenbelegen   │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

1. **Retrieval:** Die Frage wird in einen Bedeutungsvektor umgewandelt (Embedding). ChromaDB findet die semantisch ähnlichsten Studien-Abstracts – auch wenn kein einziges Wort wörtlich übereinstimmt.
2. **Augmentation:** Die gefundenen Abstracts werden als Kontext in den Prompt eingebettet. Das LLM darf ausschließlich auf Basis dieses Kontexts antworten – das reduziert Halluzinationen deutlich.
3. **Generation:** Das lokale Sprachmodell (phi3 via Ollama) formuliert eine verständliche Antwort und die Oberfläche zeigt die verwendeten Quellen transparent an.

### Warum lokal statt Cloud?

| Aspekt | Lokale Architektur |
|---|---|
| **Datenschutz** | Keine Anfrage verlässt den Rechner – Voraussetzung für die geplante Erweiterung mit persönlichen medizinischen Dokumenten |
| **Kosten** | Keine API-Gebühren, unbegrenzte Nutzung |
| **Unabhängigkeit** | Kein Vendor-Lock-in, funktioniert offline |
| **Lernwert** | Jede Komponente der Pipeline ist selbst aufgebaut und verstanden |

---

## 🔧 Tech Stack

| Komponente | Technologie | Zweck |
|---|---|---|
| Sprache | **Python 3.14** | Gesamte Pipeline |
| LLM | **Ollama** (Modell: `phi3`) | Lokale Antwortgenerierung, komplett offline |
| Vektordatenbank | **ChromaDB** (persistent) | Speicherung & semantische Suche über 1.700+ Abstracts |
| Embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | Umwandlung von Text in durchsuchbare Vektoren |
| Datenbeschaffung | **Biopython** (NCBI Entrez API) | Rechtssicherer Abruf öffentlicher PubMed-Abstracts |
| Benutzeroberfläche | **Streamlit** | Web-App mit Quellen-Slider und Studienbelegen |

---

## ✨ Features

- 🔍 **Semantische Suche** über 1.700+ wissenschaftliche Artikel zu allen Diabetesformen (Typ 1, Typ 2, Typ 3c, Gestationsdiabetes, MODY), Insulintherapie, Insulinpumpen/CGM, Komplikationen und Ernährung
- 🎚️ **Einstellbare Quellenanzahl** per Slider – direkter Einblick, wie sich die Kontextmenge auf die Antwortqualität auswirkt
- 📄 **Transparente Quellenangaben:** Jede Antwort zeigt die verwendeten Studien aufklappbar mit Titel und Abstract-Auszug
- 🗣️ **Verständlicher Antwortstil:** Per Prompt Engineering antwortet das System wie ein Arzt im persönlichen Gespräch – Fachbegriffe werden erklärt statt vorausgesetzt
- 🔌 **100 % offline nach Einrichtung:** Nach dem initialen Daten- und Modell-Download läuft alles ohne Internetverbindung
- ♻️ **Deduplizierte Ingestion:** Der Daten-Import kann beliebig oft mit erweiterten Suchbegriffen laufen (Upsert-Logik verhindert Duplikate)

---

## 🚀 Setup / Installation

> **Voraussetzungen:** Python 3.10+, [Ollama](https://ollama.com/download), ca. 3 GB freier Speicherplatz

```bash
# 1. Repository klonen
git clone https://github.com/BENUTZERNAME/medrag-local.git
cd medrag-local

# 2. Virtuelle Umgebung erstellen und aktivieren
python -m venv venv
# Windows:
venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Lokales LLM herunterladen
ollama pull phi3

# 5. Wissensbasis aufbauen (einmalig, dauert einige Minuten)
#    Vorher in ingest.py die eigene E-Mail für die NCBI API eintragen
python ingest.py

# 6. App starten
streamlit run app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`.

---

## ⚕️ Verantwortungsvoller Einsatz

**Dieses Projekt ist ein Verständnis-Tool – kein medizinisches Entscheidungswerkzeug.**

- Die Antworten basieren ausschließlich auf dem gefundenen Studienkontext und werden mit Quellen belegt. Dennoch können lokale Sprachmodelle Inhalte falsch gewichten oder unvollständig wiedergeben.
- Das System ersetzt **keine ärztliche Beratung**. Alle medizinischen Entscheidungen – Diagnose, Medikation, Therapie – gehören in die Hände von Ärztinnen und Ärzten.
- Die geplante Erweiterung um persönliche medizinische Dokumente (siehe Ausblick) ist als **private Verständnishilfe für Angehörige** konzipiert. Persönliche Gesundheitsdaten verbleiben dabei ausschließlich lokal auf dem eigenen Rechner und sind **nicht Teil dieses Repositories** (via `.gitignore` ausgeschlossen).
- Die Datenbeschaffung nutzt die **offizielle NCBI Entrez API** und beschränkt sich auf öffentlich zugängliche Abstracts – rechtlich sauber und im Rahmen der Nutzungsbedingungen.

---

## 🔭 Ausblick

Geplante Erweiterungen, an denen ich aktuell arbeite:

- **OCR-Integration (Tesseract):** Gescannte Arztbriefe und Befunde als Bild/PDF einlesen und durchsuchbar machen
- **Zweite, private Wissensbasis:** Persönliche medizinische Dokumente als separate ChromaDB-Collection, die beim Retrieval mit der wissenschaftlichen Literatur kombiniert wird – vollständig lokal
- **Persönlicher Kontext-Steckbrief:** Feste Patienteninformationen (Diagnose, Medikation), die Antworten individueller machen
- **Metadaten-Filter:** Eingrenzung der Suche nach Diabetestyp für präzisere Treffer bei der breiten Wissensbasis
- **Code-Refactoring:** Aufteilen der linearen Skripte in wiederverwendbare Module mit Tests

---

## 📬 Kontakt

Fragen oder Feedback? Gerne über [GitHub Issues](https://github.com/BENUTZERNAME/medrag-local/issues).

---

*Eigenständig konzipiert und im KI-gestützten Pair-Programming umgesetzt – als praxisnahes Lernprojekt für moderne RAG-Architekturen.*

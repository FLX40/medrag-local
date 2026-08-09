# MedRAG Local – Lokaler KI-Wissensassistent für Diabetes

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Ollama](https://img.shields.io/badge/LLM-Ollama%20%C2%B7%20llama3.1:8b-green)
![ChromaDB](https://img.shields.io/badge/Vektordatenbank-ChromaDB-orange)
![OCR](https://img.shields.io/badge/OCR-Tesseract-yellow)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![License](https://img.shields.io/badge/Lizenz-MIT-lightgrey)

Ein Retrieval-Augmented-Generation-System (RAG), das medizinische Fragen auf Basis von über **1.900 wissenschaftlichen PubMed-Studien** beantwortet – mit Schwerpunkt auf pankreatogenem Diabetes (Typ 3c), aber Abdeckung aller Diabetesformen, Blutzucker, Insulintherapie, Insulinpumpen/CGM, Komplikationen und Ernährung. Bedienung über ein **Chat-Interface mit integriertem Befund-Upload (OCR)**. Der komplette Zyklus aus Suche, Kontext-Anreicherung und Antwortgenerierung läuft **vollständig lokal und offline**: keine Cloud-API, keine laufenden Kosten, volle Kontrolle über die Daten.

---

## Warum dieses Projekt

**Lernmotivation:** Ich habe dieses Projekt als Python-Einsteiger in strukturierten Lernsessions aufgebaut, um die Architektur moderner RAG-Systeme von Grund auf zu verstehen – nicht durch das Ansprechen einer fertigen API, sondern durch das eigenständige Zusammensetzen aller Bausteine: Datenbeschaffung, Embeddings, Vektorsuche, LLM-Anbindung, OCR-Pipeline und Benutzeroberfläche.

**Praktischer Nutzen:** Typ-3c-Diabetes (pankreatogener Diabetes) ist eine seltene, häufig fehldiagnostizierte Diabetesform, zu der verständliche Informationen schwer zu finden sind. Dieses Tool macht wissenschaftliche Fachliteratur zugänglich: Man stellt eine Frage in Alltagssprache und erhält eine verständliche, quellenbelegte Antwort – und kann eigene Arztbriefe als privaten Kontext einbinden.

---

## Architektur

### Das RAG-Prinzip in drei Schritten

```
Frage des Nutzers (+ optional: Befund als Foto/PDF)
      │
      ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  1. RETRIEVAL   │───▶│ 2. AUGMENTATION  │───▶│  3. GENERATION   │
│                 │    │                  │    │                  │
│ Automatische    │    │ Studien +        │    │ Lokales LLM      │
│ Themenerkennung │    │ eigene Befunde + │    │ (llama3.1:8b)    │
│ + semantische   │    │ Patientenprofil  │    │ formuliert eine  │
│ Suche in        │    │ als Kontext      │    │ verständliche    │
│ ChromaDB        │    │ kombiniert       │    │ Antwort + Quellen│
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

1. **Retrieval:** Eine Stichwortanalyse erkennt automatisch den Themenbereich der Frage (z. B. Ernährung, Technologie, Typ 3c) und grenzt die Suche gezielt ein. Die Frage wird in einen Bedeutungsvektor umgewandelt; ChromaDB findet die semantisch ähnlichsten Studien – auch ohne wörtliche Übereinstimmung.
2. **Augmentation:** Gefundene Studien, relevante eigene Befunde (aus der separaten, privaten Collection) und das Patientenprofil werden als Kontext in den Prompt eingebettet. Das LLM darf ausschließlich auf dieser Basis antworten.
3. **Generation:** Das lokale Sprachmodell formuliert eine verständliche Antwort im Arzt-Patient-Ton; die Oberfläche zeigt die verwendeten Quellen transparent an. Liegt eine Frage außerhalb der Wissensbasis, sagt das System das offen, statt zu improvisieren.

### Warum lokal statt Cloud?

| Aspekt | Lokale Architektur |
|---|---|
| **Datenschutz** | Keine Anfrage verlässt den Rechner – Voraussetzung für echte Gesundheitsdaten (Befunde, Patientenprofil) |
| **Kosten** | Keine API-Gebühren, unbegrenzte Nutzung |
| **Unabhängigkeit** | Kein Vendor-Lock-in, funktioniert offline |
| **Lernwert** | Jede Komponente der Pipeline ist selbst aufgebaut und verstanden |

---

## Tech Stack

| Komponente | Technologie | Zweck |
|---|---|---|
| Sprache | **Python 3.14** | Gesamte Pipeline |
| LLM | **Ollama** (`llama3.1:8b`) | Lokale Antwortgenerierung; Upgrade von `phi3` nach Qualitätsvergleich |
| Vektordatenbank | **ChromaDB** (2 Collections) | 1.935 Studien mit Kategorien-Metadaten + separate private Befund-Collection |
| Embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | Umwandlung von Text in durchsuchbare Vektoren |
| Datenbeschaffung | **Biopython** (NCBI Entrez API + API-Key) | 43 kategorisierte Suchprofile, Rate-Limiting, Upsert-Deduplizierung |
| Texterkennung | **Tesseract + Poppler** (pytesseract, pdf2image) | Befunde als Foto/PDF einlesen (deutsch) |
| Benutzeroberfläche | **Streamlit** + Custom CSS | Chat-Interface mit Datei-Upload, In-App-Patientenprofil |

---

## Features

- **Chat-Interface** mit Gesprächsverlauf – Fragen stellen wie bei ChatGPT, komplett lokal
- **Befund-Upload direkt im Eingabefeld:** Foto oder PDF anhängen, Text wird per OCR erkannt und in einer separaten, privaten Wissensbasis gespeichert
- **Automatische Themenerkennung:** Die Frage wird analysiert und die Suche gezielt auf passende Kategorien eingegrenzt (Typ 1/2/3c, Blutzucker, Insulin, Technologie, Komplikationen, Ernährung u. a.)
- **Patientenprofil in der App:** Diagnose, Medikation und Besonderheiten werden über ein Formular gepflegt und bei jeder Antwort berücksichtigt – ohne Dateibearbeitung
- **Transparente Quellenangaben:** Jede Antwort zeigt die verwendeten Studien aufklappbar mit Titel und Abstract-Auszug
- **Ehrliche Grenzen:** Per Prompt Engineering antwortet das System quellentreu und sagt offen, wenn eine Frage außerhalb der Wissensbasis liegt
- **1-Klick-Start:** Desktop-Verknüpfung startet Ollama und die App automatisch zusammen
- **100 % offline nach Einrichtung**, deduplizierte und beliebig erweiterbare Wissensbasis

---

## Setup / Installation

> **Voraussetzungen:** Python 3.10+, [Ollama](https://ollama.com/download), [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki), [Poppler](https://github.com/oschwartz10612/poppler-windows/releases), ca. 8 GB freier Speicherplatz

```bash
# 1. Repository klonen
git clone https://github.com/FLX40/medrag-local.git
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
ollama pull llama3.1:8b

# 5. Tesseract- und Poppler-Pfade in app.py an das eigene System anpassen
#    (Windows-Standardpfade sind vorkonfiguriert; macOS: Homebrew-Pfade)

# 6. Wissensbasis aufbauen (einmalig; eigene E-Mail + NCBI-API-Key in ingest.py eintragen)
python ingest.py

# 7. App starten
streamlit run app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`.

---

## Verantwortungsvoller Einsatz

**Dieses Projekt ist ein Verständnis-Tool – kein medizinisches Entscheidungswerkzeug.**

- Die Antworten basieren ausschließlich auf dem gefundenen Studienkontext und werden mit Quellen belegt. Dennoch können lokale Sprachmodelle Inhalte falsch gewichten oder unvollständig wiedergeben.
- Das System ersetzt **keine ärztliche Beratung**. Alle medizinischen Entscheidungen – Diagnose, Medikation, Therapie – gehören in die Hände von Ärztinnen und Ärzten. Ein entsprechender Hinweis ist dauerhaft in der Oberfläche verankert.
- Persönliche Gesundheitsdaten (Befunde, Patientenprofil) verbleiben ausschließlich lokal und sind **nicht Teil dieses Repositories** (via `.gitignore` ausgeschlossen).
- Die Datenbeschaffung nutzt die **offizielle NCBI Entrez API** und beschränkt sich auf öffentlich zugängliche Abstracts – rechtlich sauber und im Rahmen der Nutzungsbedingungen.

---

## Ausblick

- Deployment auf dem iMac (M1) des Endnutzers inkl. Befüllung von Patientenprofil und Befunden
- Gezielter Ausbau einzelner Wissenskategorien nach Praxistest
- Code-Refactoring der linearen Skripte in wiederverwendbare Module mit Tests

---

## Kontakt

Fragen oder Feedback? Gerne über [GitHub Issues](https://github.com/FLX40/medrag-local/issues)

---

*Eigenständig konzipiert und im KI-gestützten Pair-Programming umgesetzt – als praxisnahes Lernprojekt für moderne RAG-Architekturen.*

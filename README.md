# JSON Lister (Streamlit)

Ein lokales Tool mit ansprechender, IDE-ähnlicher UI zum Durchsehen von JSON-Datensätzen und Erstellen einer Whitelist/Blacklist von Variablennamen.

## Features

- JSON-Datei laden (Liste von Objekten oder einzelnes Objekt).
- Anzahl der Beispielelemente festlegen.
- IDE-ähnliche Strukturansicht des ausgewählten Elements (`"feld": wert`).
- Variablennamen auswählen und in Whitelist/Blacklist übernehmen.
- Felddetails anzeigen.
- White-/Blacklist als JSON exportieren.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit
```

## Start

```bash
streamlit run app.py
```

## Nutzung

1. JSON-Datei in der Sidebar laden.
2. Anzahl betrachteter Beispiele einstellen.
3. Oben ein Beispiel-Element auswählen.
4. Variablen markieren und in Whitelist/Blacklist verschieben.
5. Listen bei Bedarf bereinigen und exportieren.

## Hinweis

Der Fokus liegt auf den Variablennamen (Tags). Werte dienen primär zur Orientierung bei der Auswahl.

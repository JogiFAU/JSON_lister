# JSON Blacklist Builder (Streamlit)

Das Tool dient der Auswahl einer **Blacklist für finale Felder** (Leaf-Fields), um später eine Bereinigung durchzuführen.

## Kernverhalten

- Das JSON wird hierarchisch analysiert und als Feldstruktur dargestellt.
- **Nur finale Felder** (Felder ohne weitere Unterfelder) sind die eigentlichen Blacklist-Ziele.
- Für finale Felder wird der **erste gefundene Wert** im Datensatz angezeigt (zur Interpretation).
- Für nicht-finale Felder wird **kein Wert** angezeigt.

## Markierungslogik

- Wenn ein **finales Feld** markiert wird, landet genau dieses Feld in der Blacklist.
- Wenn ein **übergeordnetes Feld** markiert wird, werden automatisch **alle untergeordneten finalen Felder** markiert.
- Export enthält nur finale Felder in der Blacklist.

## Start

Voraussetzung: `streamlit` ist installiert.

```bash
streamlit run app.py
```

## Windows-Start (ohne venv)

```bat
start_json_lister.bat
```

## JSON anhand Blacklist bereinigen (CLI)

Zusätzlich gibt es ein Skript, das eine JSON-Datei mit der exportierten `blacklist.json` bereinigt.

```bash
python clean_json.py daten.json blacklist.json
```

Ergebnis: `daten_clean.json`

Optional kann ein Ausgabepfad gesetzt werden:

```bash
python clean_json.py daten.json blacklist.json -o mein_output.json
```

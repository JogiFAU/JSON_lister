# JSON Blacklist Builder (Streamlit)

Das Tool hilft dabei, aus einem JSON-Datensatz eine **Blacklist von Feldern** zu erstellen, die später für eine Bereinigung verwendet werden kann.

## Ziel

- Aus dem Datensatz jedes **einzigartige Field** genau einmal erkennen (inkl. Hierarchie/Pfad).
- Pro Field **X Beispielwerte** anzeigen, um die Bedeutung besser zu interpretieren.
- Der Nutzer markiert anschließend die gewünschten Felder für die **Blacklist**.
- Die Blacklist kann als JSON exportiert werden.

## Verhalten der Beispielwerte (X)

- X ist in den Einstellungen konfigurierbar.
- Standard: **3**, Minimum: **2**, Maximum: **10**.
- Die Beispiele werden möglichst gleichmäßig über alle Einträge verteilt.
  - Bei X=3 wird typischerweise angezeigt: erster, mittlerer (aufgerundet), letzter vorhandener Wert.

## Wichtige Hinweise

- Felder in Arrays werden als schemaartiger Pfad normalisiert, z. B. `Questions[].Text`.
- Dadurch ist jedes Feld nur einmal auswählbar, auch wenn es in vielen Einträgen vorkommt.
- In der Tabelle sind die Felder hierarchisch eingerückt dargestellt.

## Start

Voraussetzung: `streamlit` ist installiert.

```bash
streamlit run app.py
```

## Windows-Start (ohne venv)

```bat
start_json_lister.bat
```

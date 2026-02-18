# JSON Lister (Streamlit)

Ein lokales Tool mit IDE-ähnlicher Darstellung: links die Optionenleiste, rechts der komplette JSON-Inhalt. Variablennamen sind klickbar und werden je nach Modus farbig markiert.

## Features

- Gesamtes JSON wird wie in einem Editor dargestellt.
- **Klickbare Variablenpfade** im JSON.
- Drei Modi für Klicks auf Variablen:
  - **Whitelist** (grün)
  - **Blacklist** (rot)
  - **Zuordnung aufheben** (Markierung entfernen)
- Bereits geflaggte Variablen werden automatisch farbig erkannt und angezeigt.
- Option: Blacklist-Einträge in der Darstellung ausblenden.
- Export von Whitelist und Blacklist als JSON.

## Wichtige Logik bei Arrays

Felder werden **einzigartig als Schema-Pfad** behandelt (z. B. `Questions[].Text`).
Das bedeutet:

- Wenn du `Questions[].Text` markierst, gilt das automatisch für **alle** Einträge in `Questions`, die `Text` besitzen.
- Du musst nicht jedes Element einzeln auswählen.
- Trotzdem bleibt jedes einzigartige Feld separat auswählbar (z. B. `Questions[].Id`, `Questions[].Type`, `Questions[].Text`).

## Start

Voraussetzung: `streamlit` ist installiert.

```bash
streamlit run app.py
```

## Windows-Start (ohne venv)

```bat
start_json_lister.bat
```

## Nutzung

1. Links JSON-Datei laden.
2. Klickmodus auswählen.
3. Rechts auf Variablenpfade klicken.
4. Optional Blacklist-Ausblendung aktivieren.
5. Whitelist/Blacklist exportieren.

# JSON Lister (Streamlit)

Ein lokales Tool mit IDE-ähnlicher Ansicht, um JSON-Inhalte zu analysieren und Variablen (Fragen/Felder) in Whitelist oder Blacklist einzuordnen.

## Was ist neu

- Fokus auf den **Hauptkörper** des JSON (typische Metadatenfelder wie `metadata`, `meta`, `header` werden ignoriert).
- Darstellung des JSON als editorähnliche Struktur.
- **Anklickbare Variablennamen**: Klick fügt den Variablenpfad je nach Modus zur Whitelist (grün) oder Blacklist (rot) hinzu.
- Option: **Blacklist-Einträge ausblenden**, um das Endresultat des Blacklistings direkt zu sehen.
- Werte bleiben sichtbar (für Interpretation), sind aber nicht der primäre Interaktionspunkt.

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

1. JSON-Datei hochladen.
2. In der Sidebar den zu analysierenden Bereich auswählen (ohne Metadaten).
3. Klickmodus wählen: Whitelist oder Blacklist.
4. Im JSON-Editor Variablennamen anklicken.
5. Optional Blacklist ausblenden aktivieren.
6. Listen exportieren.

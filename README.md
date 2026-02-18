# JSON Lister

Ein einfaches lokales Desktop-Tool (Python + Tkinter), um JSON-Datensätze zu inspizieren und Variablennamen in eine Whitelist/Blacklist zu übernehmen.

## Features

- Öffnet eine JSON-Datei (Liste von Datensätzen oder einzelnes Objekt).
- Nutzer gibt an, wie viele Beispiel-Elemente betrachtet werden sollen.
- Für das aktuell gezeigte Element werden **Variablenname (Tag)** und **Wert** angezeigt.
- Ausgewählte Variablen können in eine **Whitelist** oder **Blacklist** übernommen werden.
- White-/Blacklist können als JSON exportiert werden.

## Start

Voraussetzungen: Python 3 (Tkinter ist in Standard-Python enthalten).

```bash
python3 app.py
```

## Bedienung

1. Auf **„JSON-Datei öffnen“** klicken.
2. **„Anzahl Beispiele“** eintragen und **„Anwenden“** drücken.
3. Mit **„Vorheriges“** / **„Nächstes“** durch die gewählte Anzahl Beispiel-Elemente navigieren.
4. Variablen in der Liste markieren und zu White-/Blacklist hinzufügen.
5. White-/Blacklist exportieren.

## Hinweise

- Wenn Elemente keine Objekte sind (z. B. Strings/Zahlen), werden sie als `value` angezeigt.
- Variablennamen sind die zentrale Entscheidungsgrundlage; Werte dienen nur zur Orientierung.

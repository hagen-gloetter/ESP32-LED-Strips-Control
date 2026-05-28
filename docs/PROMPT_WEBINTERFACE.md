# Prompt: Webinterface Modernisierung

Arbeite ausschließlich im Ordner `code/` dieses Projekts. Das Projekt steuert RGB-LED-Strips an einem ESP32 (MicroPython) für eine Sternwarte. Die Datei `web_html.py` enthält das gesamte Webinterface (HTML/CSS/JS als Python-Strings), das vom ESP32 auf Port 80 ausgeliefert wird.

**Aufgabe:** Überarbeite das Webinterface in `web_html.py` (Funktionen `web_page()` und `web_css()`) zu einem modernen, interaktiven Single-Page-UI:

- **Layout:** Ersetze die Tabellen-Struktur durch ein responsives CSS-Grid/Flexbox-Layout mit Cards/Panels für die Bereiche: Lichtsteuerung (On/Off), RGB-Farbwahl, Presets, Sensorwerte (Temperatur/Feuchtigkeit), Systeminformationen.
- **Farbwahl:** Füge einen interaktiven HTML5 Color-Picker (`<input type="color">`) hinzu, der die RGB-Werte in Echtzeit an den ESP32 sendet (via XHR/fetch an die bestehenden Endpunkte `/?r=X&g=X&b=X`). Behalte die numerischen RGB-Inputs als Alternative bei.
- **Visuelles Feedback:** Zeige eine Live-Farbvorschau (farbiges Div) der aktuell gesetzten RGB-Werte. Buttons sollen den aktuellen Zustand (ON/OFF) visuell hervorheben (aktiver State).
- **Styling:** Dunkles Theme (passend zur Sternwarte/Astronomie), abgerundete Buttons, sanfte Transitions, dezente Schatten. Moderne Typografie (system-font-stack).
- **Constraints:** Kein externes CSS-Framework (kein Bootstrap etc.) – alles muss inline oder über `web_css()` geliefert werden, da der ESP32 begrenzte Ressourcen hat. Kein jQuery – nutze Vanilla JS. Halte die Gesamtgröße des HTML/CSS/JS kompakt (ESP32-RAM ist limitiert). Die bestehende Polling-Logik (`data.json` alle 4s) und alle existierenden Endpunkte müssen weiterhin funktionieren.

# Changelog

All notable changes to this project will be documented in this file.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

---

## [Session 5] — 2026-05-26

### Changed

- **Webinterface komplett überarbeitet** — `web_html.py`: Tabellen-basiertes Layout durch modernes Card-basiertes Dark-Theme-UI ersetzt. Flexbox/Grid-Layout, responsive, mobiltauglich.
- **HTML5 Color-Picker** — Interaktiver `<input type="color">` mit Live-Farbvorschau-Div. RGB-Nummernfelder weiterhin als Alternative vorhanden.
- **Farb-Presets als visuelles Grid** — 8 Preset-Buttons mit farbigem Hintergrund statt Tabellen-Zeilen.
- **ON/OFF-State-Feedback** — Aktive Buttons erhalten Glow-Effekt via `classList.toggle('active')`.
- **Dark-Theme (Astronomie)** — Dunkler Hintergrund (#0d1117), GitHub-Dark-Farbpalette, abgerundete Cards, sanfte Transitions.
- **jQuery entfernt** — `debug_web_page()` und `logs_web_page()` nutzen nun Vanilla JS mit `fetch()` statt jQuery-CDN.
- **XHR durch fetch() ersetzt** — Alle HTTP-Aufrufe (Polling, Kommandos) nutzen nun die Fetch-API.
- **CSS modernisiert** — System-Font-Stack, CSS-Custom-Properties für Preset-Farben, kompaktes minifiziertes CSS (~2.8 KB).

---

## [Session 4] — 2026-03-28

### Added

- **IMP-03** — Separate Logs-Webseite: Neue Route `/logs.html` und `/logs.json` für Live-Debug-Logging. Pollt alle 5s für kontinuierliche Anzeige.
- **Konfigurationsdatei** — `config.json`: Konstanten (Brightness, Fade_speed, etc.) ausgelagert für einfache Anpassung ohne Code-Änderung.
- **Mehr Presets im Webinterface** — Zusätzliche Farb-Presets: Gelb, Lila, Cyan, Orange. Erweitert Benutzerfreundlichkeit.
- **Erweiterte Logging** — Mehr Debug-Nachrichten für Edge-Cases: DHT11-Fehler, Rotary-Encoder-Status, WiFi-Scan-Ergebnisse.

### Changed

- **WiFi-Check-Intervall** — Von 60s auf 30s reduziert für schnellere Reconnect-Erkennung.
- **RGB-Skalierung** — Web-Eingaben (0-255) werden auf interne PWM-Auflösung (0-1023) skaliert für volle Helligkeit.
- **Strip3-Integration** — Alle drei LED-Strips werden nun bei RGB-Web-Updates und Fading aktualisiert.
- **Code-Deduplikation** — Neue Funktion `update_all_strips()` für Strip-Updates. Reduziert Wiederholungen.
- **Button-Debounce** — `debounceTime` von 5 auf 10 Zyklen erhöht für robustere Fehleingabe-Verhinderung.
- **Webinterface-Layout** — Getrennte Eingabefelder für R, G, B mit Presets. Verbessert Usability.

---

### Fixed

- **BUG-01** — `class_wifi_connection.py` `connect()`: `ujson.load(open(fn_secrets))` leaked the file handle. Replaced with `with open(fn_secrets) as f: ujson.load(f)`.
- **BUG-02** — `class_wifi_connection.py` `connect()`: Bare `except:` swallowed all errors silently. Changed to `except Exception as e:` with the error included in the debug message.
- **BUG-03** — `main.py` `thread_webserver()`: `conn` was not initialised to `None` before the `try` block. If `websocket.accept()` raised an exception, the `except` block then called `conn.close()` which caused `NameError`. Added `conn = None` guard and `if conn is not None` check in `except`.
- **BUG-04** — `main.py` `get_websocket()`: Missing `SO_REUSEADDR` socket option. After a crash, port 80 remained busy for the TCP TIME_WAIT period. Added `websocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)`.
- **BUG-05** — `class_rotary_encoder.py` `get_rotary_encoder()`: Used `global isRotaryEncoder` which referred to a variable in the method's own module scope — never defined there — causing `NameError` at runtime. Replaced with an `is_enabled=True` parameter; callers pass their own flag.
- **BUG-06** — `main.py` `RotaryController()`: `rotary_val_old` was never updated after reading the encoder. The comparison always ran against the initial value (0), making the encoder fire on every timer tick once turned. Added `rotary_val_old = r_value` inside the change-detected branch.
- **BUG-07** — `main.py` `Button_R_switch()`: `txt = Button_R_switch` assigned the function object instead of a string. Changed to `txt = "Button_R_switch"`.
- **BUG-08** — `main.py`: `import gc` appeared twice (second occurrence with trailing comment). Removed the duplicate.
- **BUG-09** — `main.py` `RotaryController()`: `r_value != None` identity comparison used `==` instead of `is not`. Changed to `r_value is not None`.
- **BUG-10** — `main.py` `thread_webserver()`: All `conn.send()` calls passed `str` literals instead of `bytes`. MicroPython `usocket.send()` requires bytes-like objects. Changed all header sends to byte literals (`b"…"`) and added `.encode()` to `conn.sendall(response)`.
- **BUG-11** — `main.py` `thread_webserver()`: Bare `except:` silently discarded all exceptions. Changed to `except Exception as e:` with a debug log.
- **BUG-12** — `class_wifi_connection.py` `is_connected()`: Called `self.wifi.check_connection()` on a `network.WLAN` object which has no such method. Changed to `self.check_connection()`.
- **BUG-13** — `class_humidity_sensor.py` `get_humidity_and_temperature()`: Bare `except:` swallowed all errors. Changed to `except Exception:`.
- **BUG-14** — `class_debug.py` `debug()`: String concatenation `ctx + " " + message` raised `TypeError` when either argument was `None`. Changed to `str(ctx) + " " + str(message)`.

### Added

- **Hardware Watchdog (WDT)** — `main.py`: A 15-second WDT (`machine.WDT(timeout=15000)`) is started after WiFi connects. This is > the 10-second WiFi reconnect timeout so reconnect attempts complete before the WDT fires.
- **Loop-counter main loop** — `main.py`: The `while True` loop now runs at `LOOP_MS = 100 ms` and feeds the WDT on every iteration. A counter (`_loop_count % WIFI_CHECK_TICKS`) triggers the WiFi health check every 60 seconds, replacing the former `sleep_ms(60000)` which would have caused a WDT reset.
- **Loop constants** — `main.py`: Added `LOOP_MS = 100` and `WIFI_CHECK_TICKS = 600` with inline comments explaining their relationship.
- **Docstrings** — All modules, public classes and public methods now have docstrings: `main.py`, `class_pwm.py`, `class_debounce.py`, `class_debug.py`, `class_humidity_sensor.py`, `class_wifi_connection.py`, `class_rotary_encoder.py`, `web_html.py`, `boot.py`.

### Changed

- `main.py` `RotaryController()`: Comment corrected from "tranlate" to "translate".
- `class_rotary_encoder.py` `get_rotary_encoder()`: Signature changed from `(self, sw, val_old)` to `(self, sw, val_old, is_enabled=True)`. Call site in `main.py` updated accordingly. Backwards-compatible (default `True`).
- `class_wifi_connection.py` docstring: Replaced informal class docstring with structured Google-style docstring.

# WhatsApp2Html - Changelog

## Version 1.1 - 21.09.2023
- Update:  Erkennung des Timestamp-Formats verbessert
- Update:  Flags -ph & -pw aus Konsistenzgründen zu --ph & --pw gewechselt
- Update:  Flag -t aus Konsistenzgründen zu --odate gewechselt (neues Feature --idate)
- Feature: Möglichkeit zur Definition des vorliegenden Eingabeformats des Timestamps (--idate)

## Version 1.0.1 - 02.06.2023
- Bugfix: Problem bei der Erkennung einer zweiten Message-Zeile behoben
- Bugfix: Erkennung des Chat-Formats (Android vs. iOS) verbessert/korrigiert

## Version 1.0 - 16.03.2023
Umstellung auf CLI-Version und "UI" für Standardfälle
- Feature: Möglichkeit zur Definition der gewünschten Farben
- Feature: Möglichkeit zum Definition der maximalen Bildbreite und -Höhe
- Feature: Möglichkeit zum Definition der unterstützten Image-, Video- & Audio-Extensions
- Feature: Möglichkeit zur Definition des Ergebnispfads bzw. der Ergebnidatei
- Feature: Möglichkeit zur Definition des Ausgabeformats des Timestamps
- Feature: Möglichkeit zur Einschränkung der Umwandlung auf eine bestimmte Anzahl Messages
- Feature: Erkennung der Attachments ond Kommentarfelder via Regex ab patterns.json

## 23.02.2023
- Generiertes HTML von Table auf DIVs umgestellt... Word-Wrap kann nun bei langen Texten erzwungen werden.

## 09.02.2023
- Probleme mit der Zusammenstellung des Dateipfads behoben
- Probleme bei der Erkennung eines Attachments behoben
- Probleme bei der Erkennung einer mehrzeiligen Nachricht behoben
- Meldungen ohne Personenbeteiligung (z.B. "end-to-end encryption") werden anders dargestellt
- Bildergrössen nun mittels max-height & max-width definiert

## 15.09.2022
- Probleme mit 12h-Timestamps (AM/PM) behoben

## 25.04.2022
- Ergebnis-HTML um charset=UTF-8 erweitert, damit die Emojicons sicher richtig dargestellt werden
- Probleme mit Eingabepfaden behoben, welche Leerzeichen enthielten
- Probleme beim Schreiben des letzten Datensatzes, wenn dieser nach einem \n erfolgt, behoben

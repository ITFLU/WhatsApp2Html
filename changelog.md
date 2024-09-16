# WhatsApp2Html - Changelog

## Version 1.3 - 11.09.2024
- Feature: ...

## Version 1.2.1 - 13.08.2024
- Bugfix: Check auf das Vorhandensein von pattern.json eingefügt

## Version 1.2 - 27.11.2023
- Feature: Möglichkeit zur Einschränkung des zu verarbeitenden Zeitraums (--fdate & --tdate)
- Update:  Videos werden nun mit den video-Tag eingebunden

## Version 1.1.3 - 30.10.2023
- Bugfix: Fehler bei der Erkennung des Chat-Formats behoben (thx @txanetxarra)

## Version 1.1.2 - 26.10.2023
- Bugfix: Fehler bei der Erkennung von mehrzeiligen Mitteilungen bei Android-Chats behoben

## Version 1.1.1 - 28.09.2023
- Bugfix: Probleme bei der Umwandlung mehrzeiliger Messages aufgrund der neuen Timestamp-Erkennung behoben

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

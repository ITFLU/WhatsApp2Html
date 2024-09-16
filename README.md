# WhatsApp2Html

> For english version visit `README_en.md`

## Überblick

Generiert aus einem exportierten WhatsApp-Chat eine HTML-Ansicht (Chatview inkl. Attachments)


## Export aus WhatsApp

Besagte Chatdaten können aus WhatsApp vom entsprechenden Gerät exportiert werden.
- Chat öffnen
- Chatinformationen öffnen
- Funktion "Chat exportieren" wählen
- Funktion "Medien hinzufügen" wählen, wenn auch die Mediendateien (Audio, Video, Bilder, etc.) exportiert werden sollen


## Verwendung

### Ausführung Standardfall

1. *WhatsApp2Html.py* doppelklicken
2. Name der zu verarbeitenden Chat-Datei angeben oder via Drag-n-Drop hineinziehen
3. Das Ergebnis wird im Verzeichnis der angegebenen Chat-Datei mit demselben Namen als HTML erstellt

> Die generierte html-Datei muss im selben Verzeichnis wie die Attachments verbleiben, wenn diese in der HTML-Ansicht angezeigt werden sollen.

### Ausführung via CLI

In der Kommandozeile kann eine Chat-Datei folgendermassen verarbeitet werden:

`python wa2h-cli.py [optionen] chat-datei`

Dabei kann die Datei auch mittels Drag-n-Drop in die Kommandozeile gezogen werden. Mit Hilfe der Optionen können diverse Anpassungen bei der Verarbeitung vorgenommen werden.

Folgende Optionen stehen zur Verfügung (Hilfe mittels Option `-h` aufrufbar):

```
usage: wa2h-cli [options] file

Commandline version of 'WhatsApp2Html'
Generate an HTML chatview from a WhatsApp chatexport

positional arguments:
  file               export txt of WhatsApp

optional arguments:
  -h, --help          show this help message and exit
  -v, --version       show program's version number and exit
  -o output           defines the output path/filename
                      could be only a path or can include a filename too
                      (default: input directory and input filename with the extension .html)
  -l number           limitation of the output to this number of messages
                      (0 = no limit, default: 0)
  --pw width          max width of pictures in pixels (default: 700px)
  --ph height         max height of pictures in pixels (default: 200px)
  --month-first       in case of an ambiguous date format (day and month in whole chat both under 13) define the month as first value > ignored if detection is successful
  --day-first         like --month-first but define the day as first value
  --idate dateformat  format codes for the input timestamp (default: detected automatically) > see --odate for details
  --odate dateformat  format codes for the output timestamp > see python help for more details
                      %d  Day of the month (e.g. 01)
                      %m  Month (e.g. 12)
                      %y  Year without century (e.g. 23)
                      %Y  Year with century (e.g. 2023)
                      %H  Hour 24-hour clock (e.g. 13)
                      %I  Hour 12-hour clock (e.g. 01)
                      %p  Locale's AM or PM
                      %M  Minute (e.g. 30)
                      %S  Second (e.g. 01)
                      (default: '%d.%m.%Y, %H:%M:%S', if no seconds in input timestamp '%d.%m.%Y, %H:%M')
  --fdate date        start date from which messages should be read (until now or --tdate, dateformat: %d.%m.%Y)
  --tdate date        end date until messages should be read (from file start or --fdate, dateformat: %d.%m.%Y)
  --meta colorcode    hex color code for text of metadata (default: dark gray)
  --bg0 colorcode     hex color code for background of general messages (default: light gray)
  --bg1 colorcode     hex color code for background of user 1 (default: green)
  --text1 colorcode   hex color code for text of user 1 (default: black)
  --bg2 colorcode     hex color code for background of user 2 (default: blue)
  --text2 colorcode   hex color code for text of user 2 (default: black)
  --images list       list of file extension to be treated as image separated by comma
                      (default: jpg, jpeg, gif, png, webp)
  --videos list       list of file extension to be treated as video separated by comma
                      (default: mpg, mpeg, mp4, mov, m4v, wmv)
  --audios list       list of file extension to be treated as audio separated by comma
                      (default: mp3, opus, wav, m4a, wma)
```

**Beispiele:**

- Chat-Ansicht mit anderen Farben erstellen

  `python wa2h-cli.py chat.txt --bg1 FFAA00 --bg2 336699 --text2 FFFFFF`

- Chat-Ansicht mit US-Datenformat und Bilder in einer Maximal-Breite von 1000 Pixeln erstellen

  `python wa2h-cli.py chat.txt --odate "%m/%d/%y, %I:%M %p" --pw 1000`


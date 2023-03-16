# WhatsApp2Html

> Für die Version in Deutsch bitte `README.md` konsultieren

## Overview

Generates an HTML view from an exported WhatsApp chat (Chatview including attachments)


## Export from WhatsApp

Chats data can be exported from WhatsApp from the corresponding device.
- Open chat
- Open contact info view
- Choose function "Export Chat"
- Choose funtion "Attach Media" if the mediafiles (audio, video, pictures, etc.) should be exported too


## Usage

### Default case

1. Double click on *WhatsApp2Html.py*
2. Define the name of the chat file to analyze or drop it with drag-n-drop in the console
3. The result file will be created in the same location of the csv file with the same name in HTML format

> The generated html file must remain in the same directory as the attachments if they are to be displayed in HTML view.

### Usage in command line

A CSV file can be processed in the command line as follows:

`python wa2h-cli.py {chat-datei}`

The file can also be dropped with drag-n-drop in the console. Different configurations can be done via options.

The following options are available (help can be called with the `-h` option):

```
usage: wa2h-cli [options] file

Commandline version of 'WhatsApp2Html'
Generate an HTML chatview from a WhatsApp chatexport

positional arguments:
  file               export txt of WhatsApp

optional arguments:
  -h, --help         show this help message and exit
  -v, --version      show program's version number and exit
  -o output          defines the output path/filename
                     could be only a path or can include a filename too
                     (default: input directory and input filename with the extension .html)
  -l number          limitation of the output to this number of messages
                     (0 = no limit, default: 0)
  -pw width          max width of pictures in pixels (default: 700px)
  -ph height         max height of pictures in pixels (default: 200px)
  -t dateformat      format codes for the output timestamp > see python help for more details
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
  --meta colorcode   hex color code for text of metadata (default: dark gray)
  --bg0 colorcode    hex color code for background of general messages (default: light gray)
  --bg1 colorcode    hex color code for background of user 1 (default: green)
  --text1 colorcode  hex color code for text of user 1 (default: black)
  --bg2 colorcode    hex color code for background of user 2 (default: blue)
  --text2 colorcode  hex color code for text of user 2 (default: black)
  --images list      list of file extension to be treated as image separated by comma
                     (default: jpg, jpeg, gif, png, webp)
  --videos list      list of file extension to be treated as video separated by comma
                     (default: mpg, mpeg, mp4, mov, m4v, wmv)
  --audios list      list of file extension to be treated as audio separated by comma
                     (default: mp3, opus, wav, m4a, wma)
```

**Examples:**

- Generate a chatview with different new colors

  `python wa2h-cli.py chat.txt --bg1 FFAA00 --bg2 336699 --text2 FFFFFF`

- Generate a chatview with us date format and pictures with a maximum width of 1000px

  `python wa2h-cli.py chat.txt -t "%m/%d/%y, %I:%M %p" -pw 1000`


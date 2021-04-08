#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
WhatsApp2Html
-------------
Generates an HTML chatview from a WhatsApp chatexport (.txt) including possibly existing attachments

(c) 2021, Luzerner Polizei
Author:  Michael Wicki
Version: 08.04.2021
"""

# Ask for chatfile
defaultname = "_chat.txt"
chatname = input("Wie lautet die zu generierende Datei? [<Enter> = {}] ".format(defaultname)) or defaultname

try:
    # Open files
    file_input = open(chatname, "r", encoding="utf-8")
    file_output = open("_chat.html","w", encoding="utf-8")

    # Lists of extension
    images = ['jpg' , 'jpeg', 'gif', 'png', 'webp']
    audios = ['mp3' , 'opus', 'wav', 'm4a', 'wma']
    videos = ['mpg' , 'mpeg', 'mp4', 'mov', 'm4v', 'wmv']

    # Write start of html-file
    head = """
    <html>
    <head>
    <style>
    body,table { font-family: Arial, sans-serif; font-size: 14px; }
    .msg1 { background-color: #CEE5D5; }
    .msg2 { background-color: #CFDAE5; }
    .datetime { font-size: 12px; color: #888888; font-style: italic; }
    .sender { font-size: 12px; color: #888888; font-style: italic; font-weight: bold; }
    .comment { font-size: 12px; font-style: italic; }
    .divider { font-size: 11px; font-color: #888888; border-top: solid 1px #888888; padding: 0px 0px 0px 10px; margin-top: 15px; }
    </style>
    </head>
    <body>
    <table cellspacing="12px" cellpadding="10px" width="100%">
    """
    file_output.write(head)

    # Generate file
    i = 0
    day = ""
    firstPerson = "?"
    for line in file_input:
        i+=1
        line = line.replace('\u200e', '')
        line = line.replace('\u200f', '')
        result = "<tr>"
        if line.startswith('['):
            line = line.replace('[', '')
            line = line.replace(']', ':')

        date = line[:8]
        datetime = line[:18]
        line = line[20:]
        
        person = "?"
        posColon = line.find(':')
        if posColon > -1:
            person = line[:posColon]
            line = line[posColon+2:]
        else:
            i = 0
            continue

        if i==1:
            firstPerson = person

        if person == firstPerson:
            result += "<td colspan='2' class='msg1'>"
            result += "<span class='sender'>"+person+"</span> - "
            result += "<span class='datetime'>"+datetime+"</span><br>"
        else:
            result += "<td width='70px'></td>"
            result += "<td colspan='2' class='msg2'>"
            result += "<span class='sender'>"+person+"</span> - "
            result += "<span class='datetime'>"+datetime+"</span><br>"

        # message
        if line.startswith('<Anhang:'):
            filename = line[9:-2]
            ext = filename[filename.rfind('.')+1:]
            # image
            if ext in images:
                result += "<a href='"+filename+"' target='_blank'>"
                result += "<img src='"+filename+"' height='200px'></a>"
                result += "&nbsp;&nbsp;<span class='comment'>"+filename+"</span>"
            # video
            elif ext in videos:
                result += "VIDEO: <a href='"+filename+"' target='_blank'>"+filename+"</a>"
            # audio
            elif ext in audios:
                result += "AUDIO: <a href='"+filename+"' target='_blank'>"+filename+"</a>"
            # different files
            else:
                result += "DATEI: <a href='"+filename+"' target='_blank'>"+filename+"</a>"
        else:
            result += line

        if person == firstPerson:
            result += "<td width='70px'></td></tr>"
        else:
            result += "</tr>"

        if date != day:
            divider = "<tr><td colspan='3'><p class='divider'>"+date+"</p></td></tr>"
            file_output.write(divider)
            day = date
        # Write entry
        file_output.write(result)

    # Write end of html-file
    foot = """
    </table>
    <br><br>
    </body>
    </html>"""
    file_output.write(foot)

    # Close files
    file_input.close()
    file_output.close()

    print("Verarbeitung erfolgreich abgeschlossen! siehe _chat.html...")

except (FileNotFoundError):
    print("Die angegebene Datei ({}) wurde nicht gefunden!".format(chatname))

input("")
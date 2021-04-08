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


def isAndroid(filename):
    file_input = open(chatname, "r", encoding="utf-8")
    line = file_input.readline()
    file_input.close()
    return line[16] == "-"

def initializeHtml():
    file_html = open("_chat.html","w", encoding="utf-8")
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
    file_html.write(head)
    file_html.close()

def finishHtml():
    file_html = open("_chat.html","a", encoding="utf-8")
    # Write end of html-file
    foot = """
    </table>
    <br><br>
    </body>
    </html>"""
    file_html.write(foot)
    file_html.close()

def generateFromAndroid(chatname):
    # Open files
    file_input = open(chatname, "r", encoding="utf-8")
    file_html = open("_chat.html","a", encoding="utf-8")
    # init counters & flags
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

        # cut date
        date = line[:8]
        datetime = line[:15]
        line = line[18:]

        # person & date
        person = "?"
        posColon = line.find(':')
        if posColon > -1:
            person = line[:posColon]
            line = line[posColon+2:] # +1 = ':' / +1 = ' '
        else:
            i = 0
            continue
        # start of entry
        if i==1:
            firstPerson = person
        if person == firstPerson:
            # first person >> entry on left side
            result += "<td colspan='2' class='msg1'>"
            result += "<span class='sender'>"+person+"</span> - "
            result += "<span class='datetime'>"+datetime+"</span><br>"
        else:
            # second person >> entry on right side
            result += "<td width='70px'></td>"
            result += "<td colspan='2' class='msg2'>"
            result += "<span class='sender'>"+person+"</span> - "
            result += "<span class='datetime'>"+datetime+"</span><br>"
        # message
        if line.endswith(' angehängt)', 0, -1): # -1 = '\n'
            # attachment
            filename = line[:-19]
            ext = filename[filename.rfind('.')+1:]
            if ext in images:
                # image
                result += "<a href='"+filename+"' target='_blank'>"
                result += "<img src='"+filename+"' height='200px'></a>"
                result += "&nbsp;&nbsp;<span class='comment'>"+filename+"</span>"
            elif ext in videos:
                # video
                result += "VIDEO: <a href='"+filename+"' target='_blank'>"+filename+"</a>"
            elif ext in audios:
                # audio
                result += "AUDIO: <a href='"+filename+"' target='_blank'>"+filename+"</a>"
            else:
                # different files
                result += "DATEI: <a href='"+filename+"' target='_blank'>"+filename+"</a>"
        else:
            # text message
            result += line
        # end of message entry
        if person == firstPerson:
            # first person >> entry on left side
            result += "<td width='70px'></td></tr>"
        else:
            # second person >> entry on right side
            result += "</tr>"
        # new day >> date divider
        if date != day:
            divider = "<tr><td colspan='3'><p class='divider'>"+date+"</p></td></tr>"
            file_html.write(divider)
            day = date

        # Write entry
        file_html.write(result)

     # Close files
    file_input.close()
    file_html.close()

def generateFromIOS(chatname):
    # Open files
    file_input = open(chatname, "r", encoding="utf-8")
    file_html = open("_chat.html","a", encoding="utf-8")
    # init counters & flags
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

        # cut date
        date = line[:8]
        datetime = line[:18]
        line = line[20:]

        # person & date
        person = "?"
        posColon = line.find(':')
        if posColon > -1:
            person = line[:posColon]
            line = line[posColon+2:] # +1 = ':' / +1 = ' '
        else:
            i = 0
            continue
        # start of entry
        if i==1:
            firstPerson = person
        if person == firstPerson:
            # first person >> entry on left side
            result += "<td colspan='2' class='msg1'>"
            result += "<span class='sender'>"+person+"</span> - "
            result += "<span class='datetime'>"+datetime+"</span><br>"
        else:
            # second person >> entry on right side
            result += "<td width='70px'></td>"
            result += "<td colspan='2' class='msg2'>"
            result += "<span class='sender'>"+person+"</span> - "
            result += "<span class='datetime'>"+datetime+"</span><br>"
        # message
        if line.startswith('<Anhang:'):
            # attachment
            filename = line[9:-2]
            ext = filename[filename.rfind('.')+1:]
            if ext in images:
                # image
                result += "<a href='"+filename+"' target='_blank'>"
                result += "<img src='"+filename+"' height='200px'></a>"
                result += "&nbsp;&nbsp;<span class='comment'>"+filename+"</span>"
            elif ext in videos:
                # video
                result += "VIDEO: <a href='"+filename+"' target='_blank'>"+filename+"</a>"
            elif ext in audios:
                # audio
                result += "AUDIO: <a href='"+filename+"' target='_blank'>"+filename+"</a>"
            else:
                # different files
                result += "DATEI: <a href='"+filename+"' target='_blank'>"+filename+"</a>"
        else:
            # text message
            result += line
        # end of message entry
        if person == firstPerson:
            # first person >> entry on left side
            result += "<td width='70px'></td></tr>"
        else:
            # second person >> entry on right side
            result += "</tr>"
        # new day >> date divider
        if date != day:
            divider = "<tr><td colspan='3'><p class='divider'>"+date+"</p></td></tr>"
            file_html.write(divider)
            day = date

        # Write entry
        file_html.write(result)

     # Close files
    file_input.close()
    file_html.close()


# Lists of extension
images = ['jpg' , 'jpeg', 'gif', 'png', 'webp']
audios = ['mp3' , 'opus', 'wav', 'm4a', 'wma']
videos = ['mpg' , 'mpeg', 'mp4', 'mov', 'm4v', 'wmv']

# Ask for chatfile
defaultname = "_chat.txt"
chatname = input("Wie lautet die zu generierende Datei? [<Enter> = {}] ".format(defaultname)) or defaultname

try:
    # Start html-file
    initializeHtml()
    # Generate chat
    if isAndroid(chatname):
        generateFromAndroid(chatname)
    else:
        generateFromIOS(chatname)
    # Finish html-file
    finishHtml()

    print("Verarbeitung erfolgreich abgeschlossen! siehe _chat.html...")

except (FileNotFoundError):
    print("Die angegebene Datei ({}) wurde nicht gefunden!".format(chatname))

input("")
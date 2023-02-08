#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
WhatsApp2Html
-------------
Generates an HTML chatview from a WhatsApp chatexport (.txt) including possibly existing attachments

(c) 2023, Luzerner Polizei
Author:  Michael Wicki
Version: 08.02.2023
"""

from pathlib import Path


def getLinecount(filename):
    counter = 0
    file_input = open(filename, "r", encoding="utf-8")
    for line in file_input:
        counter += 1
    file_input.close()
    return counter

def isAndroid(chatname):
    file_input = open(chatname, "r", encoding="utf-8")
    line = file_input.readline()
    file_input.close()
    return line[16] == "-" or line[18] == "-"

def isSecondRow(line):
    try:
        return line[2] != "." or line[5] != "." or line[12] != ":"
    except:
        return True

def initializeHtml():
    file_html = open(outputfile,"w", encoding="utf-8")
    # Write start of html-file
    head = """
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
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
    file_html = open(outputfile,"a", encoding="utf-8")
    # Write end of html-file
    foot = """
    </table>
    <br><br>
    </body>
    </html>"""
    file_html.write(foot)
    file_html.close()

def generateFromAndroid(chatname):
    print("Android")
    # Open files
    file_input = open(chatname, "r", encoding="utf-8")
    file_html = open(outputfile,"a", encoding="utf-8")
    # init counters & flags
    i = 0
    day = ""
    firstPerson = "?"
    result = ""
    counter = 0
    linecount = getLinecount(chatname)
    for line in file_input:
        counter+=1
        i+=1
        line = line.replace('\u200e', '')
        line = line.replace('\u200f', '')
        original_line = line

        if isSecondRow(line) and i>1 and result != "":
            # Add line (= new line of previous message) to result & go to next line
            result += "<br>"+line
            if counter >= linecount:
                # close last entry & write it to the file
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
                file_html.write(result)
            continue
        elif i>1:
            # close previous entry & write it to the file
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
            file_html.write(result)

        # cut date
        posDash = line.find('-')
        dateBase = line[:posDash-1]
        date = dateBase[:8]
        datetime = dateBase[:posDash]
        line = line[posDash+2:]

        result = "<tr>"
        if original_line.startswith('['):
            line = line.replace('[', '')
            line = line.replace(']', ':')

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
            # ignored attachments
            if line.endswith(' weggelassen', 0, -1): # -1 = '\n'
                result += "<span class='comment'>"+line+"</span>"
            else:
                # deleted messages
                if line.endswith(' wurde gelöscht.', 0, -1): # -1 = '\n'
                    result += "<span class='comment'>"+line+"</span>"
                else:
                    # missed call
                    if line.endswith(' Videoanruf', 0, -1) or line.endswith(' Sprachanruf', 0, -1): # -1 = '\n'
                        result += "<span class='comment'>"+line+"</span>"
                    else:
                        # text message
                        result += line


        if counter >= linecount:
            # close last entry & write it to the file
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
            file_html.write(result)

     # Close files
    file_input.close()
    file_html.close()

def generateFromIOS(chatname):
    print("iOS")
    # Open files
    file_input = open(chatname, "r", encoding="utf-8")
    file_html = open(outputfile,"a", encoding="utf-8")
    # init counters & flags
    i = 0
    day = ""
    firstPerson = "?"
    result = ""
    counter = 0
    linecount = getLinecount(chatname)
    for line in file_input:
        counter+=1
        i+=1
        line = line.replace('\u200e', '')
        line = line.replace('\u200f', '')
        original_line = line

        if not line.startswith('[') and i>1 and result != "":
            # Add line (= new line of previous message) to result & go to next line
            result += "<br>"+line
            if counter >= linecount:
                # close last entry & write it to the file
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
                file_html.write(result)
            continue
        elif i>1:
            # close previous entry & write it to the file
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
            file_html.write(result)

        # cut date
        posDateStart = line.find('[')+1
        posDateEnd = line.find(']')
        dateBase = line[posDateStart:posDateEnd]
        date = dateBase[:8]
        datetime = dateBase[:posDateEnd]
        line = line[posDateEnd+2:]

        result = "<tr>"
        if original_line.startswith('['):
            line = line.replace('[', '')
            line = line.replace(']', ':')

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
        if line.lstrip().startswith('<Anhang:'):
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
            # ignored attachments
            if line.endswith(' weggelassen', 0, -1): # -1 = '\n'
                result += "<span class='comment'>"+line+"</span>"
            else:
                # deleted messages
                if line.endswith(' wurde gelöscht.', 0, -1): # -1 = '\n'
                    result += "<span class='comment'>"+line+"</span>"
                else:
                    # missed call
                    if line.endswith(' Videoanruf', 0, -1) or line.endswith(' Sprachanruf', 0, -1): # -1 = '\n'
                        result += "<span class='comment'>"+line+"</span>"
                    else:
                        # text message
                        result += line

        if counter >= linecount:
            # close last entry & write it to the file
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
# remove " from path (prevents error while reading the file)
chatname = chatname.replace("\"", "")
# generate path for output-file from given input-file
if ":" in chatname:
    basepath = Path(chatname).parent
    outputfile = Path(basepath, "_chat.html")
else:
    basepath = Path(chatname).parent.absolute() 
    outputfile = Path(basepath, "_chat.html").absolute()

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
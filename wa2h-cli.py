#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
WhatsApp2Html CLI
-----------------
Generates an HTML chatview from a WhatsApp chatexport (.txt) including possibly existing attachments

(c) 2023, Luzerner Polizei
Author:  Michael Wicki
Version: 1.0
"""
version = "1.0"

from pathlib import Path
from datetime import datetime
import os
import argparse


class Message:
	def __init__(self, timestamp: datetime, sender, message):
		self.timestamp = timestamp
		self.date_obj = None
		self.sender = sender
		self.message = message
		self.attachment = ""
		self.comment = ""
		self.gui_class = ""

	def add_to_message(self, text):
		self.message += text
	
	def set_attachment(self, attachment):
		self.attachment = attachment

	def set_comment(self, comment):
		self.comment = comment

	def set_gui_class(self, classname):
		self.gui_class = classname

	def get_date_string(self):
		return self.timestamp.strftime("%d.%m.%Y")

	def to_string(self):
		pass


class PathNotFoundException(Exception):
	"""
	error in case of a path not found
	"""
	def __init__(self, path):
		self.message = f"Path '{path}' not found"



def get_linecount(filename):
	counter = 0
	file_input = open(filename, "r", encoding="utf-8")
	for line in file_input:
		counter += 1
	file_input.close()
	return counter

def is_android(chatname):
	file_input = open(chatname, "r", encoding="utf-8")
	line = file_input.readline()
	file_input.close()
	# android separates date and sender by hyphen, ios not...
	return line[16] == "-" or line[18] == "-" or line[19] == "-"

def is_second_row_of_msg(line):
	try:
		# it is an additional row if no date is available
		return (line[2] != "." and line[2] != "/") or (line[5] != "." and line[5] != "/") or (line[12] != ":" and line[11] != ":")
	except:
		return True

def get_divider(date):
	return f"<div class='divider'>{date}</div>"

def get_deleted():
	return None

def get_calls():
	return None

def get_ignored():
	return None

def get_attachment():
	return None

def get_date_obj(date_string):
	length = len(date_string)
	format = ""
	if date_string[3]=="." or date_string[2]==".":
		if length == 15:
			format = "%d.%m.%y %H:%M"
		elif length == 18:
			if date_string.lower().endswith("m"):
				format = "%d.%m.%y %H:%M %p"
			else:
				format = "%d.%m.%y %H:%M:%S"
	if date_string[3]=="/" or date_string[2]=="/":
		if length == 15:
			format = "%m/%d/%y %H:%M"
		elif length == 18:
			if date_string.lower().endswith("m"):
				format = "%m/%d/%y %H:%M %p"
			else:   
				format = "%m/%d/%y %H:%M:%S"
	if format=="":
		return None
	return datetime.strptime(date_string, '%d.%m.%y %H:%M:%S')

def read_from_android(chatname):
	pass

def generate_from_android(chatname):
	print("[i] Chat seems to be from Android")
	# Open files
	file_input = open(chatname, "r", encoding="utf-8")
	file_html = open(htmlname,"a", encoding="utf-8")
	# init counters & flags
	i = 0
	day = ""
	firstPerson = "?"
	result = ""
	counter = 0
	linecount = get_linecount(chatname)
	for line in file_input:
		counter+=1
		i+=1
		line = line.replace('\u200e', '')
		line = line.replace('\u200f', '')
		original_line = line

		if is_second_row_of_msg(line) and i>1 and result != "":
			# Add line (= new line of previous message) to result & go to next line
			result += "<br>"+line
			if counter >= linecount:
				# close last entry & write it to the file
				result += "</div>"
				# new day >> date divider
				if date != day:
					file_html.write(get_divider(date))
					day = date
				file_html.write(result)
			continue
		elif i>1:
			# close previous entry & write it to the file
			result += "</div>"
			# new day >> date divider
			if date != day:
				file_html.write(get_divider(date))
				day = date
			file_html.write(result)

		# cut date
		posDash = line.find('-')
		dateBase = line[:posDash-1]
		date = dateBase[:8]
		datetime = dateBase[:posDash]
		line = line[posDash+2:]

		result = ""
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
			result += f"<div class='msg general'>{line}</div>"
			file_html.write(result)
			continue
		# start of entry
		if i==1:
			firstPerson = person
		if person == firstPerson:
			# first person >> entry on left side
			result += "<div class='msg msg1'>"
		else:
			# second person >> entry on right side
			result += "<div class='msg msg2'>"
		result += f"<span class='metadata sender'>{person}</span> - "
		result += f"<span class='metadata timestamp'>{datetime}</span><br>"
		# message
		if line.endswith(' angehängt)', 0, -1) or line.endswith(' attached)', 0, -1): # -1 = '\n'
			# attachment
			filename = line[:-19]
			if line.endswith(' attached)', 0, -1):
				filename = line[:-17]
			ext = filename[filename.rfind('.')+1:]
			if ext in images:
				# image
				result += f"<a href='{filename}' target='_blank'>"
				result += f"<img src='{filename}' height='200px'></a>"
				result += f"&nbsp;&nbsp;<span class='comment'>{filename}</span>"
			elif ext in videos:
				# video
				result += f"VIDEO: <a href='{filename}' target='_blank'>{filename}</a>"
			elif ext in audios:
				# audio
				result += f"AUDIO: <a href='{filename}' target='_blank'>{filename}</a>"
			else:
				# different files
				result += f"DATEI: <a href='{filename}' target='_blank'>{filename}</a>"
		else:
			# ignored attachments
			if line.endswith(' weggelassen', 0, -1): # -1 = '\n'
				result += f"<span class='comment'>{line}</span>"
			else:
				# deleted messages
				if line.endswith(' wurde gelöscht.', 0, -1): # -1 = '\n'
					result += f"<span class='comment'>{line}</span>"
				else:
					# missed call
					if line.endswith(' Videoanruf', 0, -1) or line.endswith(' Sprachanruf', 0, -1): # -1 = '\n'
						result += f"<span class='comment'>{line}</span>"
					else:
						# text message
						result += line


		if counter >= linecount:
			# close last entry & write it to the file
			result += "</div>"
			# new day >> date divider
			if date != day:
				file_html.write(get_divider(date))
				day = date
			file_html.write(result)

	# Close files
	file_input.close()
	file_html.close()
	return counter

def read_from_ios(chatname):
	pass

def generate_from_ios(chatname):
	print("[i] Chat seems to be from iOS")
	# Open files
	file_input = open(chatname, "r", encoding="utf-8")
	file_html = open(htmlname,"a", encoding="utf-8")
	# init counters & flags
	i = 0
	day = ""
	firstPerson = "?"
	result = ""
	counter = 0
	linecount = get_linecount(chatname)
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
				result += "</div>"
				# new day >> date divider
				if date != day:
					file_html.write(get_divider(date))
					day = date
				file_html.write(result)
			continue
		elif i>1:
			# close previous entry & write it to the file
			result += "</div>"
			# new day >> date divider
			if date != day:
				file_html.write(get_divider(date))
				day = date
			file_html.write(result)

		# cut date
		posDateStart = line.find('[')+1
		posDateEnd = line.find(']')
		dateBase = line[posDateStart:posDateEnd]
		date = dateBase[:8]
		datetime = dateBase[:posDateEnd]
		line = line[posDateEnd+2:]

		result = ""
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
			result += "<div class='msg msg1'>"
		else:
			# second person >> entry on right side
			result += "<div class='msg msg2'>"
		result += f"<span class='metadata sender'>{person}</span> - "
		result += f"<span class='metadata timestamp'>{datetime}</span><br>"
		# message
		if line.lstrip().startswith('<Anhang:'):
			# attachment
			filename = line[9:-2]
			ext = filename[filename.rfind('.')+1:]
			if ext in images:
				# image
				result += f"<a href='{filename}' target='_blank'>"
				result += f"<img src='{filename}' style='max-height:{pic_height}px;max-width:{pic_width}px;'></a>"
				result += f"&nbsp;&nbsp;<span class='comment'>{filename}</span>"
			elif ext in videos:
				# video
				result += f"VIDEO: <a href='{filename}' target='_blank'>{filename}</a>"
			elif ext in audios:
				# audio
				result += f"AUDIO: <a href='{filename}' target='_blank'>{filename}</a>"
			else:
				# different files
				result += f"DATEI: <a href='{filename}' target='_blank'>{filename}</a>"
		else:
			# ignored attachments
			if line.endswith(' weggelassen', 0, -1): # -1 = '\n'
				result += f"<span class='comment'>{line}</span>"
			else:
				# deleted messages
				if line.endswith(' wurde gelöscht.', 0, -1): # -1 = '\n'
					result += f"<span class='comment'>{line}</span>"
				else:
					# missed call
					if line.endswith(' Videoanruf', 0, -1) or line.endswith(' Sprachanruf', 0, -1): # -1 = '\n'
						result += f"<span class='comment'>{line}</span>"
					else:
						# text message
						result += line

		if counter >= linecount:
			# close last entry & write it to the file
			result += "</div>"
			# new day >> date divider
			if date != day:
				file_html.write(get_divider(date))
				day = date
			file_html.write(result)

	# Close files
	file_input.close()
	file_html.close()
	return counter

def generate_html(chatname):
	htmlname = os.path.join(get_output_path(chatname), get_output_name(chatname))
	# start of html
	head = f"""
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<style>
	* \u007B font-family: Arial, sans-serif; font-size: 14px; \u007D
	.msg \u007B display: block; overflow-wrap: break-word; word-wrap: break-word; hyphens: auto; padding: 8px; border-radius: 5px; margin-bottom: 5px; \u007D
	.general \u007B background-color: #CCCCCC; \u007D
	.msg1 \u007B background-color: #{bg1}; color: #{text1} margin-right: 70px; \u007D
	.msg2 \u007B background-color: #{bg2}; color: #{text2} margin-left: 70px; \u007D
	.metadata \u007B font-size: 12px; color: #888888; font-style: italic; \u007D
	.timestamp \u007B \u007D
	.sender \u007B font-weight: bold; \u007D
	.comment \u007B font-size: 12px; font-style: italic; \u007D
	.divider \u007B font-size: 11px; color: #888888; border-top: solid 1px #888888; padding: 0px 0px 15px 10px; margin-top: 20px; \u007D
	</style>
	</head>
	<body>

	"""
	# end of html
	foot = """
	<br><br>
	</body>
	</html>"""

	# write html file
	file_html = open(htmlname,"w", encoding="utf-8")
	file_html.write(head)
	for msg in message_list:
		file_html.write(msg.to_string())
	file_html.write(foot)
	file_html.close()

def has_file_extension(input):
	return os.path.splitext(input)[1]!=""

def get_file_basename(input):
	filename = os.path.basename(input)
	return os.path.splitext(filename)[0]

def get_output_name(inputname):
	if args.o and has_file_extension(args.o):
		return f"{get_file_basename(args.o)}.html"
	return f"{get_file_basename(inputname)}.html"

def get_output_path(inputname):
	path = ""
	if args.o:
		if not has_file_extension(args.o):
			path = args.o
		else:
			path = os.path.dirname(args.o)
	else:
		path = os.path.dirname(inputname)

	# check for existance
	if path != "" and not os.path.exists(path):
		raise PathNotFoundException(path)
	if path != "":
		path = path+os.sep
	return path

def configure_argparse():
	global args
	parser = argparse.ArgumentParser(prog="wa2h-cli", 
									description="Commandline version of 'WhatsApp2Html'\nGenerate an HTML chatview from a WhatsApp chatexport", 
									formatter_class=argparse.RawTextHelpFormatter,
									epilog='''\
Example of use
- Generate a chatview with different new colors
	python wa2h-cli.py chat.txt --bg1 FFAA00 --bg2 336699 --text2 FFFFFF''')
	parser.version=version
	parser.add_argument("file", type=str, help="export txt of WhatsApp")    
	parser.add_argument("-v", "--version", action="version")
	parser.add_argument("-o", metavar="output", action="store", type=str, 
						help='''\
defines the output path/filename
could be only a path or can include a filename too
(default: input directory and input filename with the extension .html)''')
	parser.add_argument("-l", metavar="number", action="store", type=int, help='''\
limitation of the output to this number of messages
(0 = no limit, default: 0)''')
	parser.add_argument("-pw", metavar="width", action="store", type=int, help=f"max width of pictures in pixels (default: {pic_width}px)")
	parser.add_argument("-ph", metavar="height", action="store", type=int, help=f"max height of pictures in pixels (default: {pic_height}px)")
	parser.add_argument("--bg1", metavar="colorcode", action="store", type=str, help="hex color code for background of user 1 (default: green)")
	parser.add_argument("--text1", metavar="colorcode", action="store", type=str, help="hex color code for text of user 1 (default: black)")
	parser.add_argument("--bg2", metavar="colorcode", action="store", type=str, help="hex color code for background of user 2 (default: blue)")
	parser.add_argument("--text2", metavar="colorcode", action="store", type=str, help="hex color code for text of user 2 (default: black)")
	parser.add_argument("--images", metavar="list", action="store", type=str, help=f'''\
list of allowed image formats separated by comma
(default: {", ".join(map(str,images))})''')
	parser.add_argument("--videos", metavar="list", action="store", type=str, help=f'''\
list of allowed video formats separated by comma
(default: {", ".join(map(str,videos))})''')
	parser.add_argument("--audios", metavar="list", action="store", type=str, help=f'''\
list of allowed audio formats separated by comma
(default: {", ".join(map(str,audios))})''')
	args = parser.parse_args()



# init
message_list = []

# init default values
bg1 = "CEE5D5"
text1 = "000000"
bg2 = "CFDAE5"
text2 = "000000"
limit = 0 # 0 = no limit
pic_width = 700
pic_height = 200
images = ['jpg' , 'jpeg', 'gif', 'png', 'webp']
audios = ['mp3' , 'opus', 'wav', 'm4a', 'wma']
videos = ['mpg' , 'mpeg', 'mp4', 'mov', 'm4v', 'wmv']

# init argparse
args = None
configure_argparse()

try:
	# get options input
	bg1 = args.bg1 if args.bg1 else bg1
	text1 = args.text1 if args.text1 else text1
	bg2 = args.bg2 if args.bg2 else bg2
	text2 = args.text2 if args.text2 else text2
	limit = args.l if args.l else limit
	pic_width = args.pw if args.pw else pic_width
	pic_height = args.ph if args.ph else pic_height
	if args.images:
		images = args.images.split(',')
	if args.videos:
		videos = args.videos.split(',')
	if args.audios:
		audios = args.audios.split(',')

	chatname = args.file
	# remove " & ' from path (prevents error while reading the file)
	chatname = chatname.replace("\"", "")
	chatname = chatname.replace("'", "")

	processed = 0
	if is_android(chatname):
		processed = read_from_android(chatname)
	else:
		processed = read_from_ios(chatname)
	htmlname = generate_html(chatname)
	print(f"DONE! {processed} messages processed (check result in '{htmlname}')")

except PathNotFoundException as exp:
	print()
	print("[!] Processing aborted!")
	print(">", exp.message)
except (FileNotFoundError):
	print("[!] Processing aborted!")
	print(f"> File '{chatname}' not found")

input("")
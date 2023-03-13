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
import re
import json
import argparse


FORMAT_ANDROID = "Android"
FORMAT_IOS = "iOS"


class Message:
	def __init__(self, timestamp: datetime, sender, message):
		self.user_number = 0 # general, no user
		self.timestamp = timestamp
		self.sender = sender
		self.message = message
		self.attachment_name = ""
		self.comment = ""

	def add_to_message(self, text):
		self.message += f"<br>{text}"

	def set_user_number(self, user_number):
		self.user_number = user_number
	
	def set_attachment_name(self, attachment_name):
		self.attachment_name = attachment_name

	def set_comment(self, comment):
		self.comment = comment

	def get_date_string(self):
		return self.timestamp.strftime("%d.%m.%Y")

	def to_html(self):
		msg_class = "general"
		if self.user_number > 0:
			msg_class = f"msg{self.user_number}"

		msg_text = self.message
		if self.attachment_name != "":
			msg_text = self.attachment_name
			ext = self.attachment_name[self.attachment_name.rfind('.')+1:]
			if ext in images:
				msg_text = f"<a href='{self.attachment_name}' target='_blank'><img src='{self.attachment_name}' height='200px'></a>&nbsp;&nbsp;<span class='comment'>{self.attachment_name}</span>"
			else:
				file_format = "DATEI"
				if ext in videos:
					file_format = "VIDEO"
				elif ext in audios:
					file_format = "AUDIO"
				msg_text = f"{file_format}: <a href='{self.attachment_name}' target='_blank'>{self.attachment_name}</a>"
		if self.comment != "":
			msg_text = f"<div class='comment'>{self.comment}</div>"

		sender_element = f"<span class='metadata sender'>{self.sender}</span> - " if self.sender != "" else ""
		html_element = f"""
		<div class='msg {msg_class}'>
			{sender_element}<span class='metadata timestamp'>{self.timestamp.strftime("%d.%m.%Y, %H:%M:%S")}</span><br>
			{msg_text}
		</div>
		"""
		return html_element


class PathNotFoundException(Exception):
	"""
	error in case of a path not found
	"""
	def __init__(self, path):
		self.message = f"Path '{path}' not found"
class PatternsNotFoundException(Exception):
	"""
	error in case of a patterns file not found
	"""
	def __init__(self):
		self.message = f"File with patterns (patterns.json) not found"



def get_linecount(filename):
	counter = 0
	file_input = open(filename, "r", encoding="utf-8")
	for line in file_input:
		counter += 1
	file_input.close()
	return counter

def get_divider(date):
	return f"<div class='divider'>{date}</div>"

def check_format(chatname):
	file_input = open(chatname, "r", encoding="utf-8")
	line = file_input.readline()
	file_input.close()
	# android separates date and sender by hyphen, ios not...
	if line[16] == "-" or line[18] == "-" or line[19] == "-":
		return FORMAT_ANDROID
	return FORMAT_IOS

def is_second_row_of_msg(line, format):
	try:
		if format == FORMAT_IOS:
			return not line.startswith('[')
		# android: it's an additional row if no date is available
		return (line[2] != "." and line[2] != "/") or (line[5] != "." and line[5] != "/") or (line[12] != ":" and line[11] != ":")
	except:
		return True
	
def get_date_format():
	pass

def get_date_obj(date_string):
	if date_string[1]=="." or date_string[2]==".":
		date_format = "%d.%m.%y"
	elif date_string[1]=="/" or date_string[2]=="/":
		date_format = "%m/%d/%y"
	else:
		return None

	format = f"{date_format}, %H:%M"
	if date_string.count(':') == 2:
		format = f"{format}:%S"
	if date_string.lower().endswith("m"):
		format = f"{format} %p"
	return datetime.strptime(date_string, format)

def extract_timestamp(line, format):
	if format==FORMAT_ANDROID:
		pos_dash = line.find('-')
		date_obj = get_date_obj(line[:pos_dash-1])
		line = line[pos_dash+2:] # +1 dash, +1 blank
		return (date_obj, line)
	
	# ios
	pos_date_start = line.find('[')+1
	pos_date_end = line.find(']')
	date_obj = get_date_obj(line[pos_date_start:pos_date_end])
	line = line[pos_date_end+2:] # +1 date end, +1 blank
	return (date_obj, line)

def extract_person(line, format):
	# android and ios use the same format
	pos_colon = line.find(':')
	person_str = ""
	if pos_colon > -1:
		person_str = line[:pos_colon]
		line = line[pos_colon+2:] # +1 colon, +1 blank
	return (person_str, line)

def extract_attachment(line):
	line = line.rstrip()
	for c in search_patterns["check_attachment"]:
		match = re.search(c, line, re.IGNORECASE)
		if match != None:
			if c.startswith("\\A"):
				result = line[len(c)-3:] # -3 pattern
			elif c.endswith("\\Z"):
				result = line[:-(len(c)-3)+1] # -3 pattern, +1 position start by 0
			return result
	return None

def is_pattern_match(line, check_type):
	line = line.rstrip()
	for c in search_patterns[check_type]:
		match = re.search(c, line, re.IGNORECASE)
		if match != None:
			return True
	return False

def check_for_message_comment(line):
	if is_pattern_match(line, "check_deleted"):
		return True
	if is_pattern_match(line, "check_ignored"):
		return True
	if is_pattern_match(line, "check_call"):
		return True
	return False

def read_chat(chatname, format):
	print(f"[i] Chat seems to be from {format}")
	# Open files
	file_input = open(chatname, "r", encoding="utf-8")
	counter_line = 0
	counter_msg = 0
	linecount = get_linecount(chatname)
	first_person = ""
	current_msg = None
	for line in file_input:
		counter_line+=1
		# remove problematic characters
		line = line.replace('\u200e', '')
		line = line.replace('\u200f', '')
		if not is_second_row_of_msg(line, format):
			if current_msg != None:
				# new message line found, add last message to message list
				message_list.append(current_msg)
			counter_msg+=1
			if message_limit > 0 and counter_msg > message_limit:
				# defined limit reached > cancel processing
				break
			# extract timestamp
			date_obj, line = extract_timestamp(line, format)
			# extract person
			person_str, line = extract_person(line, format)
			if person_str != "" and first_person == "":
				first_person = person_str
			# create message
			current_msg = Message(date_obj, person_str, line)
			if person_str != "":
				current_msg.set_user_number(1) if person_str == first_person else current_msg.set_user_number(2)
			attachment = extract_attachment(line)
			if attachment != None:
				current_msg.set_attachment_name(attachment)
			if check_for_message_comment(line):
				current_msg.set_comment(line)
		else:
			current_msg.add_to_message(line)

	file_input.close()
	return counter_msg

def generate_html(chatname):
	htmlname = os.path.join(get_output_path(chatname), get_output_name(chatname))
	# start of html
	html_start = f"""
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<style>
	* \u007B font-family: Arial, sans-serif; font-size: 14px; \u007D
	.msg \u007B display: block; overflow-wrap: break-word; word-wrap: break-word; hyphens: auto; padding: 8px; border-radius: 5px; margin-bottom: 5px; \u007D
	.general \u007B background-color: #CCCCCC; \u007D
	.msg1 \u007B background-color: #{bg1}; color: #{text1}; margin-right: 70px; \u007D
	.msg2 \u007B background-color: #{bg2}; color: #{text2}; margin-left: 70px; \u007D
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
	html_end = """
	<br><br>
	</body>
	</html>"""

	# write html file
	file_html = open(htmlname,"w", encoding="utf-8")
	file_html.write(html_start)
	current_date = ""
	for msg in message_list:
		if current_date == "" or msg.get_date_string() != current_date:
			file_html.write(get_divider(msg.get_date_string()))
			current_date = msg.get_date_string()
		file_html.write(msg.to_html())
	file_html.write(html_end)
	file_html.close()
	return htmlname

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

def read_search_patterns(format):
	result = {}
	with open('patterns.json', 'r', encoding='utf-8') as d:
		data = d.read()
	patterns = json.loads(data)
	for p in patterns["patterns"]:
		if p["format"] == format.lower():
			result["check_attachment"] = p["check_attachment"]
			result["check_deleted"] = p["check_deleted"]
			result["check_ignored"] = p["check_ignored"]
			result["check_call"] = p["check_call"]
			break
	return result

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
search_patterns = {}

# init default values
bg1 = "CEE5D5"
text1 = "000000"
bg2 = "CFDAE5"
text2 = "000000"
message_limit = 0 # 0 = no limit
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
	message_limit = args.l if args.l else message_limit
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

	used_format = check_format(chatname)
	search_patterns = read_search_patterns(used_format)
	processed = read_chat(chatname, used_format)
	htmlname = generate_html(chatname)
	print(f"DONE! {processed} messages processed (check result in '{htmlname}')")

except PathNotFoundException as exp:
	print()
	print("[!] Processing aborted!")
	print(">", exp.message)
except PatternsNotFoundException as exp:
	print()
	print("[!] Processing aborted!")
	print(">", exp.message)
except (FileNotFoundError):
	print("[!] Processing aborted!")
	print(f"> File '{chatname}' not found")

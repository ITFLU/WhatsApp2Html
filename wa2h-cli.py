#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
WhatsApp2Html CLI
-----------------
Generates an HTML chatview from a WhatsApp chatexport (.txt) including possibly existing attachments

(c) 2023, Luzerner Polizei
Author:  Michael Wicki
Version: 1.3.1
"""
version = "1.3.1"

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
		self.message = self.convert_text(message)
		self.attachment_name = ""
		self.comment = ""

	def add_to_message(self, text):
		self.message += f"<br>{self.convert_text(text)}"

	def set_user_number(self, user_number):
		self.user_number = user_number
	
	def set_attachment_name(self, attachment_name):
		self.attachment_name = attachment_name

	def set_comment(self, comment):
		self.comment = self.convert_text(comment)

	def get_date_string(self):
		return self.timestamp.strftime("%d.%m.%Y")

	def convert_text(self, text):
		sanitized = text.replace('<', '&lt;')
		sanitized = sanitized.replace('>', '&gt;')
		return sanitized
	
	def to_html(self, timestamp_format):
		msg_class = "general"
		if self.user_number > 0:
			msg_class = f"msg{self.user_number}"

		msg_text = self.message
		if self.attachment_name != "":
			msg_text = self.attachment_name
			ext = self.attachment_name[self.attachment_name.rfind('.')+1:]
			if ext in images:
				msg_text = f"<a href='{self.attachment_name}' target='_blank'><img src='{self.attachment_name}' style='max-height:{pic_height}px;max-width:{pic_width}px'></a>&nbsp;&nbsp;<span class='comment'>{self.attachment_name}</span>"
			elif ext in videos:
				msg_text = f"<a href='{self.attachment_name}' target='_blank'><video src='{self.attachment_name}' style='max-height:{pic_height}px;max-width:{pic_width}px'></a>&nbsp;&nbsp;<span class='comment'>VIDEO: {self.attachment_name}</span>"
			else:
				file_format = "DATEI"
				if ext in audios:
					file_format = "AUDIO"
				msg_text = f"{file_format}: <a href='{self.attachment_name}' target='_blank'>{self.attachment_name}</a>"
		if self.comment != "":
			msg_text = f"<div class='comment'>{self.comment}</div>"

		sender_element = f"<span class='metadata sender'>{self.sender}</span> - " if self.sender != "" else ""
		html_element = f"""
		<div class='msg {msg_class}'>
			{sender_element}<span class='metadata timestamp'>{self.timestamp.strftime(timestamp_format)}</span><br>
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
class UnknownDateFormatException(Exception):
	"""
	error in case of date format could not be identified
	"""
	def __init__(self, date_string):
		self.message = f"Date format could not be identified ('{date_string}')"
class UnknownChatFormatException(Exception):
	"""
	error in case of chat format could not be identified
	"""
	def __init__(self):
		self.message = f"Chat format could not be identified if iOS or Android (doesn't start with '[' and doesn't contain '-' between positions 13 to 20)"
class InvalidRangeDateException(Exception):
	"""
	error in case of date format of 'from' or 'to' range is not valid
	"""
	def __init__(self):
		self.message = f"Date format of chat range must correspond to %d.%m.%Y (e.g. 31.01.2023) and 'from' has to be earlier than 'to'"



def get_divider(date):
	return f"<div class='divider'>{date}</div>"

"""
is_second_row_... function for checks where the timestamp format is not available yet
"""
def is_second_row_without_timestampformat(line, format, delimiter):
	try:
		if format == FORMAT_IOS:
			return not line.startswith('[')
		# android: it's an additional row if no date is available
		pos_dash = line.find('-')
		if pos_dash < 0 or pos_dash > 40:
			return True
		return delimiter not in line[:pos_dash-1]
	except:
		return True

"""
usual check for second row of a message (timestamp format is available)
"""
def is_second_row_of_msg(line, format):
	try:
		if format == FORMAT_IOS:
			return not line.startswith('[')
		# android: it's an additional row if no date is available
		date_obj, ln = extract_timestamp(line, format)
		return date_obj == None
	except:
		return True
	
def get_timestamp_string(line, format):
	if format==FORMAT_ANDROID:
		pos_dash = line.find('-')
		return line[:pos_dash-1]
	# ios
	pos_date_start = line.find('[')+1
	pos_date_end = line.find(']')
	return line[pos_date_start:pos_date_end]

def extract_timestamp(line, format):
	# ios
	pos_timestamp_end = line.find(']')
	if format==FORMAT_ANDROID:
		pos_timestamp_end = line.find('-')
	
	date_obj = datetime.strptime(get_timestamp_string(line, format), timestamp_format)
	line = line[pos_timestamp_end+2:] # +1 date end, +1 blank
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
	line = line.strip()
	for c in search_patterns["check_attachment"]:
		match = re.search(c, line, re.IGNORECASE)
		if match != None:
			if c.startswith("\\A"):
				result = line[len(c)-2+1:] # -2 pattern (\\ counts as 1), +1 position starts by 0
			elif c.endswith("\\Z"):
				result = line[:-(len(c)-3)+1] # -3 pattern, +1 position starts by 0
			else:
				result = line[len(c)+1:] # +1 position starts by 0
			# remove brackets
			result = result.replace('<', '')
			result = result.replace('>', '')
			result = result.replace('(', '')
			result = result.replace(')', '')
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

def clean_line(line):
	# remove problematic characters
	line = line.replace('\u200e', '')
	line = line.replace('\u200f', '')
	line = line.replace('\u202f', ' ')
	return line

def read_chat(chatname, format):
	# range handling
	range_from = None
	text_from = "file start"
	range_to = None
	text_to = "now"
	try:
		if args.fdate:
			range_from = datetime.strptime(args.fdate, "%d.%m.%Y")
			text_from = args.fdate
		if args.tdate:
			range_to = datetime.strptime(f"{args.tdate} 23:59:59", "%d.%m.%Y %H:%M:%S")
			text_to = args.tdate
		if range_from != None and range_to!= None and range_from > range_to:
			raise InvalidRangeDateException() 
	except ValueError:
		raise InvalidRangeDateException()

	print(f"[i] Chat seems to be from {format}")
	if range_from != None or range_to != None:
		print(f"[i] Using date range '{text_from} - {text_to}'")
	# Open files
	file_input = open(chatname, "r", encoding="utf-8")
	counter_line = 0
	counter_msg = 0
	first_person = ""
	current_msg = None
	for line in file_input:
		counter_line+=1
		line = clean_line(line)
		if not is_second_row_of_msg(line, format):
			if current_msg != None:
				# new message line found, add last message to message list
				message_list.append(current_msg)
			# extract timestamp
			date_obj, line = extract_timestamp(line, format)
			# date range handling
			if range_from != None and date_obj < range_from:
				# defined 'from' date range not reached yet > process next message
				continue
			if range_to != None and date_obj > range_to:
				# defined 'to' date range reached > cancel processing
				break
			# check for message limit
			counter_msg+=1
			if message_limit > 0 and counter_msg > message_limit:
				# defined limit reached > cancel processing
				counter_msg -= 1
				break
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
			if current_msg != None:
				current_msg.add_to_message(line)

	if current_msg != None and range_to == None:
		# add last message to message list
		message_list.append(current_msg)

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
	.general \u007B background-color: #{bg0}; \u007D
	.msg1 \u007B background-color: #{bg1}; color: #{text1}; margin-right: 70px; \u007D
	.msg2 \u007B background-color: #{bg2}; color: #{text2}; margin-left: 70px; \u007D
	.metadata \u007B font-size: 12px; color: #{meta}; font-style: italic; \u007D
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
		if not args.odate:
			output_format = output_date_format_short if timestamp_format.count(':') == 1 else output_date_format
		else:
			output_format = args.odate
		file_html.write(msg.to_html(output_format))
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
	if not os.path.exists('patterns.json'): 
		raise PatternsNotFoundException()
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

def check_chat_format(chatname):
	file_input = open(chatname, "r", encoding="utf-8")
	line = file_input.readline()
	file_input.close()
	line = clean_line(line)
	if line.startswith('['):
		return FORMAT_IOS
	# android separates date and sender by hyphen, ios not...
	if line[13:20].find("-") != -1:
		return FORMAT_ANDROID
	raise UnknownChatFormatException()

def get_date_format(chatname, format, delimiter):
	with open(chatname, "r", encoding="utf-8") as file_input:
		year = "%y"
		for line in file_input:
			line = clean_line(line)
			# is_second_row_of_msg not possible because the timestamp format is not available yet
			if is_second_row_without_timestampformat(line, format, delimiter):
				continue
			timestamp = get_timestamp_string(line, format)
			first_pos = timestamp.find(delimiter)
			second_pos = timestamp.find(delimiter, first_pos+1)
			year_element = timestamp[second_pos+1:timestamp.find(" ")]
			if "," in year_element:
				year_element = year_element[:-1]
			if len(year_element) == 4:
				year = "%Y"
			# check for serbian year with point at the end
			if len(year_element) == 5 and year_element[4]=='.':
				year = "%Y."
			if len(year_element) == 3 and year_element[2]=='.':
				year = "%y."
			first_elem = timestamp[:first_pos]
			if int(first_elem) > 12:
				return f"%d{delimiter}%m{delimiter}{year}"
			second_elem = timestamp[first_pos+1:second_pos]
			if int(second_elem) > 12:
				return f"%m{delimiter}%d{delimiter}{year}"

			if args.month_first:
				return f"%m{delimiter}%d{delimiter}{year}"
			if args.day_first:
				return f"%d{delimiter}%m{delimiter}{year}"

		raise UnknownDateFormatException("day and month are not clear, use --month-first, --day-first or define the whole timestamp format with --idate")
	

def check_timestamp_format(chatname, format):
	delimiter = ""
	# read first line
	file_input = open(chatname, "r", encoding="utf-8")
	line = file_input.readline()
	file_input.close()
	line = clean_line(line)
	# detect day-month delimiter
	timestamp = get_timestamp_string(line, format)
	if timestamp[1]=="." or timestamp[2]==".":
		delimiter = "."
	elif timestamp[1]=="/" or timestamp[2]=="/":
		delimiter = "/"
	else:
		raise UnknownDateFormatException(timestamp)
	# check for day- and month-field
	date_format = get_date_format(chatname, format, delimiter)
	# detect existence of a comma between date and time
	comma = ""
	if "," in timestamp:
		comma = ","
	# detect existence of secons
	seconds = ""
	if timestamp.count(':') == 2:
		seconds = ":%S"
	# dectect existence of am/pm indicator
	time_format = f"%H:%M{seconds}"
	if timestamp.lower().endswith("m"):
		time_format = f"%I:%M{seconds} %p"
	return f"{date_format}{comma} {time_format}"

def configure_argparse():
	global args
	parser = argparse.ArgumentParser(prog="wa2h-cli", 
									description="Commandline version of 'WhatsApp2Html'\nGenerate an HTML chatview from a WhatsApp chatexport", 
									formatter_class=argparse.RawTextHelpFormatter,
									epilog='''\
Examples of use
- Generate a chatview with different new colors
	python wa2h-cli.py chat.txt --bg1 FFAA00 --bg2 336699 --text2 FFFFFF
- Generate a chatview with us date format and pictures with a maximum width of 1000px
	python wa2h-cli.py chat.txt --odate "%m/%d/%y, %I:%M %p" --pw 1000''')
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
	parser.add_argument("--pw", metavar="width", action="store", type=int, help=f"max width of pictures in pixels (default: {pic_width}px)")
	parser.add_argument("--ph", metavar="height", action="store", type=int, help=f"max height of pictures in pixels (default: {pic_height}px)")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--month-first", action="store_true", help="in case of an ambiguous date format (day and month in whole chat both under 13) define the month as first value > ignored if detection is successful")
	group.add_argument("--day-first", action="store_true", help="like --month-first but define the day as first value")
	parser.add_argument("--idate", metavar="dateformat", action="store", type=str, help=f"format codes for the input timestamp (default: detected automatically) > see --odate for details")
	parser.add_argument("--odate", metavar="dateformat", action="store", type=str, help=f'''\
format codes for the output timestamp > see python help for more details
%%d  Day of the month (e.g. 01)
%%m  Month (e.g. 12)
%%y  Year without century (e.g. 23)
%%Y  Year with century (e.g. 2023)
%%H  Hour 24-hour clock (e.g. 13)
%%I  Hour 12-hour clock (e.g. 01)
%%p  Locale's AM or PM
%%M  Minute (e.g. 30)
%%S  Second (e.g. 01)
(default: '{output_date_format.replace('%', '%%')}', if no seconds in input timestamp '{output_date_format_short.replace('%', '%%')}')''')
	parser.add_argument("--fdate", metavar="date", action="store", type=str, help=f"start date from which messages should be read (until now or --tdate, dateformat: %%d.%%m.%%Y)")
	parser.add_argument("--tdate", metavar="date", action="store", type=str, help=f"end date until messages should be read (from file start or --fdate, dateformat: %%d.%%m.%%Y)")
	parser.add_argument("--meta", metavar="colorcode", action="store", type=str, help="hex color code for text of metadata (default: dark gray)")
	parser.add_argument("--bg0", metavar="colorcode", action="store", type=str, help="hex color code for background of general messages (default: light gray)")
	parser.add_argument("--bg1", metavar="colorcode", action="store", type=str, help="hex color code for background of user 1 (default: green)")
	parser.add_argument("--text1", metavar="colorcode", action="store", type=str, help="hex color code for text of user 1 (default: black)")
	parser.add_argument("--bg2", metavar="colorcode", action="store", type=str, help="hex color code for background of user 2 (default: blue)")
	parser.add_argument("--text2", metavar="colorcode", action="store", type=str, help="hex color code for text of user 2 (default: black)")
	parser.add_argument("--images", metavar="list", action="store", type=str, help=f'''\
list of file extension to be treated as image separated by comma
(default: {", ".join(map(str,images))})''')
	parser.add_argument("--videos", metavar="list", action="store", type=str, help=f'''\
list of file extension to be treated as video separated by comma
(default: {", ".join(map(str,videos))})''')
	parser.add_argument("--audios", metavar="list", action="store", type=str, help=f'''\
list of file extension to be treated as audio separated by comma
(default: {", ".join(map(str,audios))})''')
	args = parser.parse_args()



# init
message_list = []
search_patterns = {}
timestamp_format = None

# init default values
bg1 = "CEE5D5"
text1 = "000000"
bg2 = "CFDAE5"
text2 = "000000"
meta = "888888"
bg0 = "CCCCCC"
message_limit = 0 # 0 = no limit
pic_width = 700
pic_height = 200
images = ['jpg' , 'jpeg', 'gif', 'png', 'webp']
audios = ['mp3' , 'opus', 'wav', 'm4a', 'wma']
videos = ['mpg' , 'mpeg', 'mp4', 'mov', 'm4v', 'wmv']
output_date_format = "%d.%m.%Y, %H:%M:%S"
output_date_format_short = "%d.%m.%Y, %H:%M"

# init argparse
args = None
configure_argparse()

try:
	# get options input
	bg1 = args.bg1 if args.bg1 else bg1
	text1 = args.text1 if args.text1 else text1
	bg2 = args.bg2 if args.bg2 else bg2
	text2 = args.text2 if args.text2 else text2
	meta = args.meta if args.meta else meta
	bg0 = args.bg0 if args.bg0 else bg0
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

	chat_format = check_chat_format(chatname)
	if not args.idate:
		timestamp_format = check_timestamp_format(chatname, chat_format)
	else:
		timestamp_format = args.idate
	search_patterns = read_search_patterns(chat_format)
	processed = read_chat(chatname, chat_format)
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
except UnknownDateFormatException as exp:
	print()
	print("[!] Processing aborted!")
	print(">", exp.message)
except InvalidRangeDateException as exp:
	print()
	print("[!] Processing aborted!")
	print(">", exp.message)
except UnknownChatFormatException as exp:
	print()
	print("[!] Processing aborted!")
	print(">", exp.message)
except (FileNotFoundError):
	print("[!] Processing aborted!")
	print(f"> File '{chatname}' not found")

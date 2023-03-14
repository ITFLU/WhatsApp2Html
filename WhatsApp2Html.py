#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
WhatsApp2Html DEFAULT
---------------------
Asks the user for the chat file and calls wa2h-cli.py with the default values so that the user doesn't have to use the command line for default cases

(c) 2023, Luzerner Polizei
Author:  Michael Wicki
Version: 1.0
"""
version = "v1.0"

import os


print("===== WhatsApp2Html {} =====".format(version))
# ask for informations
input_filename = input("Pfad/Name des Chat-TXT > ")
print()
# start whatsapp2html
os.system(f"python wa2h-cli.py {input_filename}")

print()
input()

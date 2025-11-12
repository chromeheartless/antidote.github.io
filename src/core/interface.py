import os
import time
import json
import hashlib

from encryption import generate_keypair, shape

ASCII = """

 ▄▄▄       ███▄    █ ▄▄▄█████▓ ██▓▓█████▄  ▒█████  ▄▄▄█████▓▓█████ 
▒████▄     ██ ▀█   █ ▓  ██▒ ▓▒▓██▒▒██▀ ██▌▒██▒  ██▒▓  ██▒ ▓▒▓█   ▀ 
▒██  ▀█▄  ▓██  ▀█ ██▒▒ ▓██░ ▒░▒██▒░██   █▌▒██░  ██▒▒ ▓██░ ▒░▒███   
░██▄▄▄▄██ ▓██▒  ▐▌██▒░ ▓██▓ ░ ░██░░▓█▄   ▌▒██   ██░░ ▓██▓ ░ ▒▓█  ▄ 
 ▓█   ▓██▒▒██░   ▓██░  ▒██▒ ░ ░██░░▒████▓ ░ ████▓▒░  ▒██▒ ░ ░▒████▒
 ▒▒   ▓▒█░░ ▒░   ▒ ▒   ▒ ░░   ░▓   ▒▒▓  ▒ ░ ▒░▒░▒░   ▒ ░░   ░░ ▒░ ░
  ▒   ▒▒ ░░ ░░   ░ ▒░    ░     ▒ ░ ░ ▒  ▒   ░ ▒ ▒░     ░     ░ ░  ░
  ░   ▒      ░   ░ ░   ░       ▒ ░ ░ ░  ░ ░ ░ ░ ▒    ░         ░   
      ░  ░         ░           ░     ░        ░ ░              ░  ░
"""

def main():
    print(ASCII)

def check_for_keys():

     folder_name = "releace"

     temp_dir = "~/Documents/release"

     keys_directory = "~/"
     contacts_directory = "~/"
     message_directory = "~/"

     CONFIGURATION_FILE = "~/"

     filename = "ANIKEYFILE.json"

     if not filename:
          prompt = input("Keyfile not found, ")

     # if the key file is found but no keys can be extracted say:

     if not keys:
          print´("Keyfile found; {file_location}, however keys seem to be corrupted.")
          prompt = input("Generate new keypair?")

main()

def config_parser():
     passz


def backup():
     pass
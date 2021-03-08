#!/usr/bin/env python

import os
import logging

import configparser
import argparse
from jinja2 import Environment, PackageLoader
from bs4 import BeautifulSoup

# Helper
def normalize(s):
  return '"%s"' % s.replace('"', '""')

# Setup logging
script_name = os.path.splitext(os.path.basename(__file__))[0]
logging.basicConfig()
logger = logging.getLogger(script_name)
logger.setLevel(logging.DEBUG)

# Parse command line options
parser = argparse.ArgumentParser(
    description='Converts KeePass XML file to 1Password CSV')
parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
args = parser.parse_args()

# Read config file
config = configparser.SafeConfigParser()
config.read(os.path.join('etc', script_name + '.conf'))

passwords_xml = BeautifulSoup(open(config.get('General', 'input')), features="lxml")
logger.info('KeePass XML file is opened')

passwords = []

for entry in passwords_xml.find_all('entry'):
  password = {}
  if entry.parent.name == 'history':
    continue

  # for el in entry.find_all('string'):
  for el in entry.findChildren("string", recursive=False):
    if not el.value.string:
      continue

    if el.key.string == 'Title':
      password['title'] = normalize(el.value.string)
    elif el.key.string == 'UserName':
      password['username'] = normalize(el.value.string)
    elif el.key.string == 'Password':
      password['password'] = normalize(el.value.string)
    elif el.key.string == 'URL':
      password['url'] = normalize(el.value.string.replace('http://', ''))
    elif el.key.string == 'Notes':
      # notes = '\n'.join(unicode(element) for element in entry.comment.contents if element.name != 'br')
      password['notes'] = normalize(el.value.string)

  passwords.append(password)

# Prepare output file
env = Environment(loader=PackageLoader('__main__', 'templates'))
template = env.get_template('passwords.tmpl')
output = open(config.get('General', 'output'), 'wb')
output.write(template.render(passwords = passwords).encode('utf-8'))
output.close()

logger.info('1Password CSV file is written')

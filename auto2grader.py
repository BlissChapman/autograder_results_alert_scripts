#################################################
# Required environment variables:               #
# A2G_USERNAME: username for SVN                #
# A2G_PASSWORD: password for SVN                #
# A2G_WEBHOOK: unique part of Slack webhook URL #
#################################################

import pickledb
import requests
import os
import sys
import xml.etree.ElementTree as ET
import hashlib

DB_HASH_DICT = 'hash_dict'
SVN_BASE_URL = 'https://subversion.ews.illinois.edu/svn/sp17-cs241/'
SLACK_BASE_URL = 'https://hooks.slack.com/services/'

def initialize():
    print "Initializing..."

def get_assignment_list():
    r = requests.get(SVN_BASE_URL + os.environ['A2G_USERNAME'] + '/', auth=(os.environ['A2G_USERNAME'], os.environ['A2G_PASSWORD']))
    htmlstr = r.text
    i = htmlstr.find('<ul>')
    j = htmlstr.find('</ul>') + 5
    if i > -1 and j > -1:
        htmlstr = htmlstr[i:j]
        xmlroot = ET.fromstring(htmlstr)
        assignments = []
        for i in range(1, len(xmlroot)):
            if xmlroot[i][0].text[-1:] == '/':
                assignments.append(xmlroot[i][0].text[:-1])
        return assignments
    return None

def get_result_hash(assignment):
    r = requests.get(SVN_BASE_URL + os.environ['A2G_USERNAME'] + '/' + assignment + '/results.json', auth=(os.environ['A2G_USERNAME'], os.environ['A2G_PASSWORD']))
    if r.status_code != 200:
        return ''
    return hashlib.md5(r.text).hexdigest()

# MAIN
db = pickledb.load('db0.db', False)

assignments = get_assignment_list()

if not (db.get('init')):
    print "First run; building database..."
    db.dcreate(DB_HASH_DICT)
    for assignment in assignments:
        db.dadd(DB_HASH_DICT, (assignment, get_result_hash(assignment)))
    db.set('init', True)
    db.dump()
    sys.exit(0)

for assignment in assignments:
    if db.dexists(DB_HASH_DICT, assignment):
        newhash = get_result_hash(assignment)
        if newhash != db.dget(DB_HASH_DICT, assignment):
            db.dadd(DB_HASH_DICT, (assignment, newhash))
            db.dump()
            # notify
            payload_value = '{"text": "<!channel> Autograder results have been updated for ' + assignment + '."}'
            r = requests.post(SLACK_BASE_URL + os.environ['A2G_WEBHOOK'], data={'payload': payload_value})
    else:
        db.dadd(DB_HASH_DICT, (assignment, get_result_hash(assignment)))
        db.dump()


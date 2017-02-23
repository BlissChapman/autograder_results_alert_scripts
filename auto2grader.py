import pickledb
import requests
import os
import sys
import time
import xml.etree.ElementTree as ET
import hashlib

DB_HASH_DICT = 'hash_dict'
SVN_BASE_URL = 'https://subversion.ews.illinois.edu/svn/sp17-cs241/'

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

print 'Updating assignment list...'
assignments = get_assignment_list()
print 'Assignments:'
for assignment in assignments:
    print '- ' + assignment + ": " + (db.dget(DB_HASH_DICT, assignment))

db.dump()

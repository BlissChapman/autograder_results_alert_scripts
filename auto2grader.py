import pickledb
import requests
import os
import xml.etree.ElementTree as ET

def initialize():
    print "Initializing..."

def update_assignment_list(pdb):
    r = requests.get('https://subversion.ews.illinois.edu/svn/sp17-cs241/srpatil2/', auth=(os.environ['A2G_USERNAME'], os.environ['A2G_PASSWORD']))
    htmlstr = r.text
    i = htmlstr.find('<ul>')
    j = htmlstr.find('</ul>') + 5
    if i > -1 and j > -1:
        htmlstr = htmlstr[i:j]
        xmlroot = ET.fromstring(htmlstr)
        pdb.lrem('assignments')
        pdb.lcreate('assignments')
        for i in range(1, len(xmlroot)):
            pdb.ladd('assignments', xmlroot[i][0].text[:-1])

db = pickledb.load('db0.db', False)

if (db.get('init')):
    initialize()
    db.set('init', True)
    db.lcreate('assignments')
    db.dcreate('last_updated')

print 'Updating assignment list...'
update_assignment_list(db)
print 'Assignments:'
for i in range(db.llen('assignments')):
    print '- ' + db.lget('assignments', i)

db.dump()

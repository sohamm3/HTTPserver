import uuid
import os
from csv import *
from glob import *
from time import *

header = ['E-Tag', 'resource', 'last modified']

f = open("etag.csv", "w")

write = DictWriter(f , fieldnames=header)
write.writeheader()

def modification_time(filename):
    t = os.path.getmtime(filename)

    time = strftime('%a, %d %b %Y %H:%M:%S %Z', localtime(t))
    return time

rows = []
files = glob('**', recursive = True)
for i in files:
    row = []
    id = uuid.uuid1()
    resource = i
    lmt = modification_time(i)
    row.append(id)
    row.append(resource)
    row.append(lmt)

    rows.append(row)

with open('etag.csv', 'w', encoding='UTF8', newline='') as f:
    writer = writer(f)
    writer.writerow(header)
    writer.writerows(rows)

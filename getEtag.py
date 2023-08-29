import pandas as pd
import os, uuid
from time import *
from csv import *

def modification_time(filename):
    t = os.path.getmtime(filename)
    time = strftime('%a, %d %b %Y %H:%M:%S %Z', localtime(t))
    return time

def get_etag(file):
    p = ''
    df = pd.read_csv('etag.csv')
    t = df['E-Tag'].loc[df['resource'] == file]
  
    p = str(t).split('\n')
    
    if(len(p) > 1):
        id = p[0].split('    ')[1]
    else:
        row = []
        id = uuid.uuid1()
        resource = file
        lmt = modification_time(file)
        row.append(id)
        row.append(resource)
        row.append(lmt)
        with open('etag.csv', 'a+', encoding='UTF8', newline='') as f:
            write = writer(f)
            write.writerow(row)

    #print(id)
    return id

def delete_etag(file):
    lines = []
    with open('etag.csv', 'r') as readFile:
            read = reader(readFile)
            for i, row in enumerate(read):
                    lines.append(row)
                    if row[1] == file:
                            lines.remove(row)
    with open('etag.csv', 'w') as writeFile:
            write = writer(writeFile)
            write.writerows(lines)

def modify_etag(file):
    lines = []
    with open('etag.csv', 'r') as readFile:
            read = reader(readFile)
            for i, row in enumerate(read):
                    lines.append(row)
                    if row[1] == file:
                            lines[i][2] = modification_time(file)
    with open('etag.csv', 'w') as writeFile:
            write = writer(writeFile)
            write.writerows(lines)

#get_etag(sys.argv[1])
#delete_etag(sys.argv[1])
#modify_csv(sys.argv[1])
import os
import sys
from time import *
import mimetypes
import re
from glob import *

print(strftime("%a, %d %b %Y %I:%M:%S %p %Z", gmtime()))
print(strftime("%a, %d %b %Y %I:%M:%S %p %Z\n"))

filename = sys.argv[1]

filename = filename.replace("/", "", 1)
print(filename)

length = str(os.path.getsize(filename))
print(length)

isFile = os.path.isfile(filename)
print(isFile)

path = os.path.abspath(filename)
print(path)

contentType,fileEncoding = mimetypes.guess_type(filename)
print(contentType)

# t has the time in seconds
t = os.path.getmtime(filename)
# Converting the time in seconds to a timestamp
time = ctime(t)

ti = time.split()

print(ti[0] + ", " + ti[2] + " " + ti[1] + " " + ti[4] + " " + ti[3] + " GMT")

f = open(filename, "rb")
file = f.read()
print(file)

matched = re.match(b"abhay", file)
is_match = bool(matched)
print(is_match)

if b"abhay" in file:
    print("yes")

a = set(glob('some*'))
b = set(glob('*.html'))

if(a&b):
    print(a&b)
else:
    print("no")

string = b"abhay"
print(isinstance(string, bytes))
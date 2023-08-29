import os
import random

# for authentication in delete request
USERNAME = "abhay"
PASSWORD = "abhaykoushal@2020"

# root directory
ROOT = os.getcwd()

# time after which log files should be compressed(12 hours)
EXPIRES = 43200

# max simultaneous connections
MAX_REQUESTS = 20

# max uri length
MAX_URI = 50

# max payload size (512 KB)
MAX_PAYLOAD = 512000    

# request URI which has been moved permanently
MOVED = ROOT + "/old.html"

# redirection to
NEW = ROOT + "/new.html"

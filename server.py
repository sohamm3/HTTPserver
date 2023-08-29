from socket import *
from time import *
from add import *
import sys
import os
import mimetypes
import base64
from glob import *
from config import *
import gzip
import shutil
import logging
import threading
import random
from getEtag import *
import uuid

ip = "127.0.0.1"
port = int(sys.argv[1])

def logs(n):
    if(n == 0):
        logging.basicConfig(filename = "user.log", format = '[%(asctime)s]: %(message)s', level = logging.INFO)
    elif(n == 1):
        logging.basicConfig(filename = "debug.log", format = '[%(asctime)s]: %(message)s', level = logging.DEBUG)
    elif(n == 2):
        logging.basicConfig(filename = "developer.log", format = '[%(asctime)s]: %(message)s', level = logging.WARNING)
    else:
        print("invalid logging level")
        sys.exit(0)

# log file compression 
def logs_compression(log_file):
    if(os.path.isfile(log_file)):
        mtime = os.stat(log_file).st_mtime    
        age = time() - mtime
        
        #EXPIRES = 60

        fname = log_file.split(".")[0]
        LOG_DIRECTORY = ROOT + "/" + fname + "logFiles"

        if(int(age) > EXPIRES):
            if(os.path.isdir(LOG_DIRECTORY)):
                with open(log_file, 'rb') as f_in:
                    number = len(os.listdir(LOG_DIRECTORY)) +1
                    logfile_compress = LOG_DIRECTORY + f"/{fname}logfile{number}.gz"
                    with gzip.open(logfile_compress, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(log_file)
            else:
                os.mkdir(LOG_DIRECTORY)
                with open(log_file, 'rb') as f_in:
                    logfile_compress = LOG_DIRECTORY + f"/{fname}logfile1.gz"
                    with gzip.open(logfile_compress, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(log_file)

logs_compression("user.log")
logs_compression("debug.log")
logs_compression("developer.log")

def date_time():
    dt = strftime("%a, %d %b %Y %H:%M:%S %Z")
    return dt

def file_length(filename):
    len = str(os.path.getsize(filename))
    return len

def file_type(filename):
    type,encoding = mimetypes.guess_type(filename)
    return type

def file_location(filename):
    path = os.path.abspath(filename)
    return path

def read_file(filename):
    ext = filename.split(".")[1]
    if ext in binary_extensions:
        f = open(filename, "rb")
        data = f.read()
        f.close()
        return data
    else:
        f = open(filename, "r")
        data = f.read().encode()
        f.close()
        return data


def write_file(filename, data):
    ext = filename.split(".")[1]
    if ext in binary_extensions:
        file = open(filename, "wb")
        file.write(data)
        file.close()
    else:
        f = open(filename, "w")
        f.write(data)
        f.close()
    return

flag = 1
def split_data(data):
    lines = data.split('\r\n')
    method = lines[0].split(' ')[0]
    version = lines[0].split(' ')[-1]
    filename = lines[0].split(' ')[1].replace('/','',1)
    user_agent = data.split('User-Agent: ')[1].split('\r\n')[0]

    if "Accept-Encoding: " in data:
        encoding = data.split('Accept-Encoding: ')[1].split('\r\n')[0]
    else:
        encoding = "-"

    if "Cookie: " in data:
        cookie = data.split('Cookie: ')[1].split('\r\n')[0]
    else:
        cookie = 0

    if "Content-Length: " in data:
        length = data.split('Content-Length: ')[1].split('\r\n')[0]
    else:
        length = 0
    
    return method, version, filename, user_agent, length, encoding, cookie

def error(version, filename, status_code, user_agent, error_file):
    err = f"{version} {status_code} {status_codes[status_code]}\r\n"
    err += "Date: " + date_time() + "\r\n"
    err += "Host: " + str(ip) + ":" + str(port) + "\r\n"
    err += "Server: Apache/2.4.46 (Ubuntu) \r\n"
    err += "User-Agent: " + user_agent + "\r\n"
    err += "Content-Length: " + file_length(error_file) + "\r\n"
    err += "Connection: Keep-Alive\r\n"
    err += "Content-Type: " + str(file_type(error_file)) + "\r\n\r\n"
    
    return err

def modification_time(filename):
    # t has the time in seconds
    t = os.path.getmtime(filename)
    
    """
    Converting the time in seconds to a timestamp
    ts = ctime(t)
    ti = ts.split()
    time = ti[0] + ", " + ti[2] + " " + ti[1] + " " + ti[4] + " " + ti[3] + " GMT" 
    """

    time = strftime('%a, %d %b %Y %H:%M:%S %Z', localtime(t))
    return time

def write_cookie():
    id = str(uuid.uuid1())
    with open ("cookies.txt", "a+") as cookiefile:
        cookiefile.write(id + "\n")

    return id

def get_headers(status_code, filename, version, user_agent, encoding, cookie):
    header = f"{version} {status_code} {status_codes[status_code]}\r\n"
    header += "Date: " + date_time() + "\r\n"
    header += "Host: " + str(ip) + ":" + str(port) + "\r\n"
    header += "Server: Apache/2.4.46 (Ubuntu) \r\n"
    header += "User-Agent: " + user_agent + "\r\n"
    header += "Accept: */* \r\n"
    header += "Last-Modified: " + modification_time(filename) + "\r\n"
    header += "Content-Length: " + file_length(filename) + "\r\n"
    header += "ETag: " + get_etag(filename) + "\r\n"
    header += "Accept-Encoding: " + encoding + "\r\n"
    header += "Accept-Charset : UTF-8\r\n"
    header += "Range: bytes=0-\r\n"
    header += "Accept-Ranges: bytes\r\n"

    if(cookie == 0):
        header += "Set-Cookie: id=" + write_cookie() + "; Max-Age=120\r\n"

    if(version == "HTTP/1.0"):
        conn = 'close'
    else:
        conn = 'keep-alive'
    
    header += "Connection: " + conn + "\r\n"
    header += "Content-Location: " + file_location(filename) + "\r\n"
    header += "Content-Type: " + str(file_type(filename)) + "\r\n\r\n"
    return header

def put_post(status_code, filename, version, user_agent, fname, cookie):
    header = f"{version} {status_code} {status_codes[status_code]}\r\n"
    header += "Date: " + date_time() + "\r\n"
    header += "Host: " + str(ip) + ":" + str(port) + "\r\n"
    header += "Server: Apache/2.4.46 (Ubuntu) \r\n"
    header += "User-Agent: " + user_agent + "\r\n"
    header += "Accept: */* \r\n"
    header += "Last-Modified: " + modification_time(filename) + "\r\n"
    header += "Content-Length: " + file_length(fname) + "\r\n"
    # header += "ETag: " + get_etag(filename) + "\r\n"

    if(cookie == 0):
        header += "Set-Cookie: id=" + write_cookie() + "; Max-Age=120\r\n"

    if(version == "HTTP/1.0"):
        conn = 'close'
    else:
        conn = 'keep-alive'
    
    header += "Connection: " + conn + "\r\n"
    header += "Location: " + file_location(filename) + "\r\n"
    header += "Content-Type: " + str(file_type(filename)) + "\r\n\r\n"
    
    return header

def ok(status_code, filename, version, user_agent, cookie):
    header = f"{version} {status_code} {status_codes[status_code]}\r\n"
    header += "Date: " + date_time() + "\r\n"
    header += "Host: " + str(ip) + ":" + str(port) + "\r\n"
    header += "Server: Apache/2.4.46 (Ubuntu) \r\n"
    header += "User-Agent: " + user_agent + "\r\n"
    header += "Accept: */* \r\n"
    header += "Last-Modified: " + modification_time(filename) + "\r\n"
    header += "Content-Length: " + file_length(filename) + "\r\n"

    if(cookie == 0):
        header += "Set-Cookie: id=" + write_cookie() + "; Max-Age=120\r\n"

    if(version == "HTTP/1.0"):
        conn = 'close'
    else:
        conn = 'keep-alive'

    header += "Connection: " + conn + "\r\n"
    header += "Content-Location: " + file_location(filename) + "\r\n"
    header += "Content-Type: " + str(file_type(filename)) + "\r\n\r\n"
    
    return header

def delete_header(status_code, filename, version, user_agent, cookie):
    header = f"{version} {status_code} {status_codes[status_code]}\r\n"
    header += "Date: " + date_time() + "\r\n"
    header += "Host: " + str(ip) + ":" + str(port) + "\r\n"
    header += "Server: Apache/2.4.46 (Ubuntu) \r\n"
    header += "User-Agent: " + user_agent + "\r\n"
    header += "Accept: */* \r\n"

    if(cookie == 0):
        header += "Set-Cookie: id=" + write_cookie() + "; Max-Age=120\r\n"

    if(version == "HTTP/1.0"):
        conn = 'close'
    else:
        conn = 'keep-alive'

    header += "Connection: " + conn + "\r\n"
    header += "Content-Type: " + str(file_type(filename)) + "\r\n\r\n"
    
    return header

def allow_header(status_code, filename, version, user_agent):
    header = f"{version} {status_code} {status_codes[status_code]}\r\n"
    header += "Date: " + date_time() + "\r\n"
    header += "Host: " + str(ip) + ":" + str(port) + "\r\n"
    header += "Server: Apache/2.4.46 (Ubuntu) \r\n"
    header += "User-Agent: " + user_agent + "\r\n"
    header += "Accept: */* \r\n"
    header += "Allow: GET, HEAD, DELETE, PUT, POST\r\n"

    if(version == "HTTP/1.0"):
        conn = 'close'
    else:
        conn = 'keep-alive'

    header += "Connection: " + conn + "\r\n"
    header += "Content-Length: " + file_length(filename) + "\r\n"
    header += "Content-Type: " + str(file_type(filename)) + "\r\n\r\n"
    
    return header

# authentication for delete method:
def auth(data):
    logging.debug("\"checking delete authentication\"")
    cred = data.split("Basic ")[1].split("\r\n")[0]
    cred = base64.decodebytes(cred.encode()).decode()
    user = cred.split(':')[0]
    password = cred.split(':')[1]
    if(user == USERNAME and password == PASSWORD):
        return True
    return False


no = ["", "favicon.ico"]

def post_name(filename):
    name, ext = filename.split(".")
    a = set(glob(name + "*"))
    b = set(glob("*." + ext))

    if(a & b):
        files = (a & b)
    
    new = name + "(" + str(len(files)) + ")" + "." + ext
    
    return new
    

def helper(data, body, socket):
    method, version, fname, user_agent, content_length, encoding, cookie = split_data(data)

    uri = data.split('\r\n')[0].split(' ')[1]

    if(fname == "old.html"):
        fname = "new.html"

    try:
        if(len(uri) > MAX_URI):
            status_code = 414
            file = "files/414_uriTooLong.html"
            msg = error(version, fname, status_code, user_agent, file)
            socket.sendall(msg.encode())
            socket.sendall(read_file(file))

            logging.debug(f"{status_code} \"uri length exceeded\"")
            logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
            logging.warning(f"{ip}:{port} \"URI is too long.\"")

        elif(method not in Allow):
            status_code = 405
            file = "files/405_notAllowed.html"
            msg = allow_header(status_code, file, version, user_agent)
            socket.sendall(msg.encode())
            socket.sendall(read_file(file))
            logging.debug(f"{status_code} \"method {method} not allowed.\"")
            logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
            logging.warning(f"{ip}:{port} \"method {method} not allowed.\"")

        elif(version not in http_versions):
            status_code = 505
            file = "files/505_version.html"
            msg = error(version, fname, status_code, user_agent, file)
            socket.sendall(msg.encode())
            socket.sendall(read_file(file))

            logging.debug(f"{status_code} \"version not found\"")
            logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
            logging.warning(f"{ip}:{port} \"{version} is not implemented.\"")

        elif(fname in no):
            msg = b"hello"
            socket.sendall(msg)

        else:
            if(method == 'GET' or method == 'HEAD' or method == 'DELETE'):
                try:
                    if(os.path.isfile(fname)):
                        if(os.access(fname, os.R_OK) and os.access(fname, os.W_OK)):
                            if(file_type(fname) in mime_types):
                                if(method == "GET"):
                                    status_code = 200
                                    if(fname == "new.html"):
                                        status_code = 301
                                    msg = get_headers(status_code, fname, version, user_agent, encoding, cookie)
                                    socket.sendall(msg.encode())
                                    socket.sendall(read_file(fname))
                                    logging.debug(f"{status_code} \"get successful\"")
                                    logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                    logging.warning(f"{ip}:{port} \"{fname} was accessed successfully.\"")
                                    return
                                elif(method == "HEAD"):
                                    status_code = 200
                                    file = "files/204_noContent.html"
                                    msg = get_headers(status_code, fname, version, user_agent, encoding, cookie)
                                    socket.sendall(msg.encode())
                                    socket.sendall(read_file(file))
                                    logging.debug(f"{status_code} \"head successful\"")
                                    logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                    logging.warning(f"{ip}:{port} \"only headers for {fname} were asked.\"")
                                    return
                                elif(method == "DELETE"):
                                    if(auth(data)):
                                        status_code = 200
                                        msg = delete_header(status_code, fname, version, user_agent, cookie)
                                        os.remove(fname)
                                        # delete_etag(fname)
                                        socket.sendall(msg.encode())
                                        logging.debug(f"{status_code} \"delete successful\"")
                                        logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                        logging.warning(f"{ip}:{port} \"{fname} deleted.\"")
                                        return
                                    else:
                                        status_code = 401
                                        file = "files/401_unauthorized.html"
                                        msg = error(version, fname, status_code, user_agent, file)
                                        socket.sendall(msg.encode())
                                        socket.sendall(read_file(file))
                                        logging.debug(f"{status_code} \"unauthorized\"")
                                        logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                        logging.warning(f"{ip}:{port} \"authorization failed for delete.\"")
                                        return
                            else:
                                status_code = 415
                                file = "files/415_unsupported.html"
                                msg = error(version, fname, status_code, user_agent, file)
                                socket.sendall(msg.encode())
                                socket.sendall(read_file(file))
                                logging.debug(f"{status_code} \"unsupported media type\"")
                                logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                logging.warning(f"{ip}:{port} \"{fname} is of an unsupported media type.\"")                    
                                return
                        else:
                            status_code = 403
                            file = "files/403_forbidden.html"
                            msg = error(version, fname, status_code, user_agent, file)
                            socket.sendall(msg.encode())
                            socket.sendall(read_file(file))
                            logging.debug(f"{status_code} \"forbidden\"")
                            logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                            logging.warning(f"{ip}:{port} \"{fname} does not have read/write permissions.\"")
                            return
                    else:
                        status_code = 404
                        file = "files/404_notfound.html"
                        msg = error(version, fname, status_code, user_agent, file)
                        socket.sendall(msg.encode())
                        socket.sendall(read_file(file))
                        logging.debug(f"{status_code} \"not found\"")
                        logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                        logging.warning(f"{ip}:{port} \"{fname} was not found.\"")
                        return
                        
                except:
                    status_code = 400
                    file = "files/400_badRequest.html"
                    msg = error(version, fname, status_code, user_agent, file)
                    socket.sendall(msg.encode())
                    socket.sendall(read_file(file))
                    logging.debug(f"{status_code} \"Bad Request in {method}.\"")
                    logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                    logging.warning(f"{ip}:{port} \"Bad Request in {method}.\"")
                    return

            elif(method == "PUT"):
                try:
                    if content_length:
                        if(len(body) < MAX_PAYLOAD):
                            if(os.path.isfile(fname)):
                                if(os.access(fname, os.R_OK) and os.access(fname, os.W_OK)):
                                    status_code = 200
                                    write_file(fname, body)
                                    # modify_etag(fname)
                                    msg = ok(status_code, fname, version, user_agent, cookie)
                                    socket.sendall(msg.encode())
                                    logging.debug(f"{status_code} \"created in put(existing file)\"")
                                    logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                    logging.warning(f"{ip}:{port} \"{fname} was modified successfully.\"")
                                    return
                                
                                else:
                                    status_code = 403
                                    file = "files/403_forbidden.html"
                                    msg = error(version, fname, status_code, user_agent, file)
                                    socket.sendall(msg.encode())
                                    socket.sendall(read_file(file))
                                    logging.debug(f"{status_code} \"forbidden in put\"")
                                    logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                    logging.warning(f"{ip}:{port} \"{fname} does not have write permissions.\"")
                                    return
                            else:
                                status_code = 201
                                write_file(fname, body)
                                file = "files/201_created.html"
                                msg = put_post(status_code, fname, version, user_agent, file, cookie)
                                socket.sendall(msg.encode())
                                socket.sendall(read_file(file))
                                logging.debug(f"{status_code} \"created in put(new file)\"")
                                logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                logging.warning(f"{ip}:{port} \"{fname} was created successfully.\"")
                                return
                        else:
                            status_code = 413
                            file = "files/413_payload.html"
                            msg = error(version, fname, status_code, user_agent, file)
                            socket.sendall(msg.encode())
                            socket.sendall(read_file(file))
                            logging.debug(f"{status_code} \"paylod size exceeded\"")
                            logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                            logging.warning(f"{ip}:{port} \"{fname} has size {len(body)} which exceeds max payload size({MAX_PAYLOAD}).\"")
                            return
                    else:
                        status_code = 411
                        file = "files/411_length.html"
                        msg = error(version, fname, status_code, user_agent, file)
                        socket.sendall(msg.encode())
                        socket.sendall(read_file(file))
                        logging.debug(f"{status_code} \"body length is 0\"")
                        logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                        logging.warning(f"{ip}:{port} \"{fname} is empty.\"")
                        return
                except:
                    status_code = 400
                    file = "files/400_badRequest.html"
                    msg = error(version, fname, status_code, user_agent, file)
                    socket.sendall(msg.encode())
                    socket.sendall(read_file(file))
                    logging.debug(f"{status_code} \"Bad Request in {method}.\"")
                    logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                    logging.warning(f"{ip}:{port} \"Bad Request in {method}.\"")
                    return

            elif(method == "POST"):
                try:
                    if content_length:
                        if(len(body) < MAX_PAYLOAD):
                            if(os.path.isfile(fname)):
                                if(os.access(fname, os.R_OK) and os.access(fname, os.W_OK)):
                                    status_code = 201
                                    
                                    new = post_name(fname)

                                    write_file(new, body)
                                    file = "files/201_created.html"
                                    msg = put_post(status_code, new, version, user_agent, file, cookie)
                                    socket.sendall(msg.encode())
                                    socket.sendall(read_file(file))
                                    logging.debug(f"{status_code} \"created in post\"")
                                    logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                    logging.warning(f"{ip}:{port} \"A new file named {new} was created.\"")
                                    return
                            else:
                                status_code = 201
                                write_file(fname, body)
                                file = "files/201_created.html"
                                msg = put_post(status_code, fname, version, user_agent, file, cookie)
                                socket.sendall(msg.encode())
                                socket.sendall(read_file(file))
                                logging.debug(f"{status_code} \"created in put\"")
                                logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                                logging.warning(f"{ip}:{port} \"A new file named {fname} was created.\"")
                                return
                        else:
                            status_code = 413
                            file = "files/413_payload.html"
                            msg = error(version, fname, status_code, user_agent, file)
                            socket.sendall(msg.encode())
                            socket.sendall(read_file(file))
                            logging.debug(f"{status_code} \"paylod size exceeded\"")
                            logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                            logging.warning(f"{ip}:{port} \"{fname} has size {len(body)} which exceeds max payload size({MAX_PAYLOAD}).\"")
                            return
                    else:
                        status_code = 411
                        file = "files/411_length.html"
                        msg = error(version, fname, status_code, user_agent, file)
                        socket.sendall(msg.encode())
                        socket.sendall(read_file(file))
                        logging.debug(f"{status_code} \"body length is 0\"")
                        logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                        logging.warning(f"{ip}:{port} \"{fname} is empty.\"")
                        return     
                except:
                    status_code = 400
                    file = "files/400_badRequest.html"
                    msg = error(version, fname, status_code, user_agent, file)
                    socket.sendall(msg.encode())
                    socket.sendall(read_file(file))
                    logging.debug(f"{status_code} \"Bad Request in {method}.\"")
                    logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                    logging.warning(f"{ip}:{port} \"Bad Request in {method}.\"")
                    return
            else:
                status_code = 501
                file = "files/501_notImplemented.html"
                msg = error(version, fname, status_code, user_agent, file)
                socket.sendall(msg.encode())
                socket.sendall(read_file(file))
                logging.debug(f"{status_code} \"method not implemented\"")
                logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
                logging.warning(f"{ip}:{port} \"{method} is not implemented.\"")
                return

        if(version == "HTTP/1.0"):
            socket.close()
            
    except:
        status_code = 500
        file = "files/500_internalServer.html"
        msg = error(version, fname, status_code, user_agent, file)
        socket.sendall(msg.encode())
        socket.sendall(read_file(file))
        logging.debug(f"{status_code} \"internal server error\"")
        logging.info(f"{ip}:{port} \"{method} {version} {fname}\" {status_code}")
        logging.warning(f"{ip}:{port} \"An internal server error occurred.\"")
        return

def mythread(connectionSocket):
    connectionSocket.setblocking(0)
    data = bytes("", 'utf-8')
    timeout = 2
    begin = time()
    while True:
        if data and time() - begin > timeout:
            break
        elif time() - begin > 2*timeout - 1:
            break
        try:
            t = connectionSocket.recv(8192)
            if t:
                data += t
                begin = time()
            else:
                sleep(0.1)
        except:
            pass
    #print(data)

    if not data:
        return
    try:
        data = data.decode()
        data, body = data.split('\r\n\r\n', 1)
    except UnicodeDecodeError:
        new = data.split(b'\r\n\r\n', 1)
        data = new[0].decode()
        body = new[1]

    helper(data, body, connectionSocket)
            

def main():
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('', port))
    server.listen(5)
    print(f'Address : http://{ip}:{port}')

    level = int(sys.argv[2])
    logs(level)
    
    while True: 
        try:
            conn, addr = server.accept()
            print(f'Connected by {addr}')

            if(threading.active_count() < MAX_REQUESTS):
                th = threading.Thread(target = mythread, args = (conn, ))
                th.start()
                
            else:
                status_code = 503
                t = random.randint(50, 200)

                file = "files/503_serviceUnavailable.html"
                msg = f"HTTP/1.1 {status_code} {status_codes[status_code]}\r\n"
                msg += "Date: " + date_time() + "\r\n"
                msg += "Retry-After: " + str(t) + "\r\n"
                msg += "Host: " + str(ip) + ":" + str(port) + "\r\n"
                msg += "Server: Apache/2.4.46 (Ubuntu) \r\n"
                msg += "Content-Length: " + file_length(file) + "\r\n"
                msg += "Connection: Close\r\n"
                msg += "Content-Type: " + str(file_type(file)) + "\r\n\r\n"

                conn.sendall(msg.encode())
                conn.sendall(read_file(file))
                
                conn.close()

        except KeyboardInterrupt:
            print("server stopped")
            sys.exit(0)
    
if __name__ == "__main__":
    main()

from socket import *
import sys
import threading
import os

ip = "127.0.0.1"
port = int(sys.argv[1])

def get():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "GET /test.txt HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    data = client.recv(8192)
    print("\nGet Request:\n")
    print(response.decode())
    print(data.decode())
    client.close()

def head():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "HEAD /sample.pdf HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nHead Request:\n")
    print(response.decode())
    client.close()

def delete():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "DELETE /fun.txt HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n"
    msg += "Authorization: Basic YWJoYXk6YWJoYXlrb3VzaGFsQDIwMjA=\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nDelete Request:\n")
    print(response.decode())
    client.close()

def unauthorized():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "DELETE /fun.txt HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n"
    msg += "Authorization: Basic YWJoYXk6YWJoYXlrb3VzaGFsQDIwMg==\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nDelete Request(unauthorized):\n")
    print(response.decode())
    client.close()

def put():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "PUT /fun.txt HTTP/1.1\r\n"
    msg += "Content-Length: 12\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    msg += "hello world!"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nPut Request:\n")
    print(response.decode())
    client.close()

def post():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "POST /fun.txt HTTP/1.1\r\n"
    msg += "Content-Length: 12\r\n"
    msg += "Content-Type: text/plain\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    msg += "hello world!"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nPost Request:\n")
    print(response.decode())
    client.close()

def method_not_implemented():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "COPY /fun.txt HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nGet Request(method not allowed):\n")
    print(response.decode())
    client.close()

def uri_too_long():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "GET /data/files/newfiles/oldfiles/myfiles/datafiles/allfiles/fun.txt HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nGet Request(uri too long):\n")
    print(response.decode())
    client.close()

def unsupported():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "GET /file.pp HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nGet Request(unsupported media type):\n")
    print(response.decode())
    client.close()

def length_required():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "PUT /fun.txt HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    msg += "hello world!"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nPut Request(length required):\n")
    print(response.decode())
    client.close()

def forbidden():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "GET /fun.txt HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nGet Request(forbidden):\n")
    print(response.decode())
    client.close()

def version_not_supported():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "GET /file.txt HTTP/2.1\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nGet Request(version not supported):\n")
    print(response.decode())
    client.close()

def non_persistent():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "HEAD /http.txt HTTP/1.0\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    print("\nHEAD Request(non persistent):\n")
    print(response.decode())
    client.close()

def moved_permanently():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((ip,port))
    msg = "GET /old.html HTTP/1.1\r\n"
    msg += "User-Agent: testing agent\r\n\r\n"
    client.send(msg.encode())
    response = client.recv(1024)
    data = client.recv(8192)
    print("\nGet Request(moved permanently):\n")
    print(response.decode())
    print(data.decode())
    client.close()

def main():
    get_thread = threading.Thread(target=get)
    get_thread.start()
    get_thread.join()

    head_thread = threading.Thread(target=head)
    head_thread.start()
    head_thread.join()

    put_thread = threading.Thread(target=put)
    put_thread.start()
    put_thread.join()

    delete_thread = threading.Thread(target=delete)
    delete_thread.start()
    delete_thread.join()

    post_thread = threading.Thread(target=post)
    post_thread.start()
    post_thread.join()

    unauthorized_thread = threading.Thread(target=unauthorized)
    unauthorized_thread.start()
    unauthorized_thread.join()

    method_thread = threading.Thread(target=method_not_implemented)
    method_thread.start()
    method_thread.join()

    uri_thread = threading.Thread(target=uri_too_long)
    uri_thread.start()
    uri_thread.join()
    
    unsupported_thread = threading.Thread(target=unsupported)
    unsupported_thread.start()
    unsupported_thread.join()

    length_required_thread = threading.Thread(target=length_required)
    length_required_thread.start()
    length_required_thread.join()

    put_thread = threading.Thread(target=put)
    put_thread.start()
    put_thread.join()

    os.chmod('fun.txt', 0o000)

    forbidden_thread = threading.Thread(target=forbidden)
    forbidden_thread.start()
    forbidden_thread.join()

    version_not_supported_thread = threading.Thread(target=version_not_supported)
    version_not_supported_thread.start()
    version_not_supported_thread.join()

    non_persistent_thread = threading.Thread(target=non_persistent)
    non_persistent_thread.start()
    non_persistent_thread.join()

    moved_permanently_thread = threading.Thread(target=moved_permanently)
    moved_permanently_thread.start()
    moved_permanently_thread.join()

if __name__ == "__main__":
    main()
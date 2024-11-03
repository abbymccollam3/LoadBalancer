# Author: Abby McCollam
# Title: Server
# Objectives: 
#   start-up then listen for incoming connections and forward to server
#   provide log message to verify incoming connection

''' 
LOG MESSAGE FORMAT:
    Received request from 127.0.0.1
    GET / HTTP/1.1
    Host: localhost
    User-Agent: curl/7.85.0
    Accept: */* 
'''

'''
HEADER FORMAT EXAMPLE:
    Host: localhost:8000
    Sec-Fetch-Site: none
    Connection: keep-alive
    Upgrade-Insecure-Requests: 1
    Sec-Fetch-Mode: navigate
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Safari/605.1.15
    Accept-Language: en-US,en;q=0.9
    Sec-Fetch-Dest: document
    Accept-Encoding: gzip, deflate
'''

# run python -m http.server 8000
# navigate http://localhost:8000 -> displays files/directories on port

import requests
import itertools
import threading

from http.server import SimpleHTTPRequestHandler, HTTPServer 
# HTTPServer (server_address, request handler class)

PORT = 8000
backend_ports = [8001, 8002, 8003]
backends = [f'http://localhost:{port}' for port in backend_ports]
backend_pool = itertools.cycle(backends)  # round robin

# this class defines how requests are handled
class Handler (SimpleHTTPRequestHandler): # inheriting Simple... (request, client_address, server, directory=None)
    # intercepts GET requests from client
    def do_GET(self): 
        
        address = self.client_address[0] # get client address
        path = self.path
        command = f"{self.command} {path} {self.request_version}" # get command, path, request_version

        headers = {key: value for key, value in self.headers.items()} # items iterates over the whole list

        # constructing log message and placing file in directory
        # log message only constructed once user navigates to page
        # messages added to the end of .msg
        log_message = f"""./msg
        HELLO
        Received request from {address} {command}
        Host: {headers.get("Host: ")}
        User-Agent: {headers.get("User-Agent: ")}
        Accept: {headers.get("Accept: ")}"""

        # Write log message to .msg file in append mode
        # with opens the file and automatically closes file
        with open('.msg', 'a') as log_file:
            log_file.write(log_message + '\n')

        backend_url = next(backend_pool) # selecting next backend server
        try:
            # response formed with backend url and header
            response = requests.get(backend_url + path, headers=headers)
            print(f"URL: {backend_url}")

            # send status code
            self.send_response(response.status_code) 

            # send_header(keyword, value); sending header information
            for key,value in response.headers.items():
                self.send_header(key, value)
            self.end_headers() # THIS IS REQUIRED
            self.wfile.write(response.content)
            self.wfile.write(b"Hello from: " + backend_url.encode() + b"!") # this will write to webpage

            print(f"Header: {self.headers}")
            print (f"Response from server: {self.request_version} {response.status_code} OK")
            print (f"Hello From Backend Server")
        except requests.RequestException:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(b"Bad Gateway: Could not connect to backend server.")
            print("Could not connect to backend server")

class BackEndHandler (SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

# Need to set up backend servers
def run_backendserver(port):   
    with HTTPServer(('localhost', port), BackEndHandler) as server:
        print(f"Server started at http://localhost:{port}")
        server.serve_forever() # starts and keeps running server

for port in backend_ports:
    thread = threading.Thread(target=run_backendserver, args=(port,))
    thread.daemon = True  # Allows the program to exit even if threads are running
    thread.start()

try:
    # HTTPServer (serverAddress, Request Handler Class)
    with HTTPServer(('localhost', PORT), Handler) as server:
        print(f"Server started at http://localhost:{PORT}")
        server.serve_forever() # starts and keeps running server
except KeyboardInterrupt:
    print("Shutting down servers...")

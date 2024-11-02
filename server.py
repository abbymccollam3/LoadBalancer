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

# run python -m http.server 8000
# navigate http://localhost:8000 -> displays files/directories on port

import requests
import itertools
import threading

from http.server import SimpleHTTPRequestHandler, HTTPServer 
# HTTPServer (server_address, request handler class)

PORT = 8000
backends = ['http://localhost:8001', 'http://localhost:8002']
backend_ports = [8001, 8002]
backend_pool = itertools.cycle(backends)  # Round-robin selection

class BackEndHandler (SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, "Hi")
        self.send_header("Content-type", "text/html")
        self.end_headers()

# this class defines how requests are handled
class Handler (SimpleHTTPRequestHandler): # inheriting Simple... (request, client_address, server, directory=None)
    # intercepts GET requests from client
    def do_GET(self): 
        # get client address
        address = self.client_address[0]
        
        # get command, path, request_version
        command = f"{self.command} {self.path} {self.request_version}"

        # retreives headers from request
        host = self.headers.get('Host')
        user_agent = self.headers.get('User-Agent')
        accept = self.headers.get('Accept')

        # constructing log message and placing file in directory
        # log message only constructed once user navigates to page
        log_message = f"""./msg
        Received request from {address}
        {command}
        Host: {host}
        User-Agent: {user_agent}
        Accept: {accept}"""

        # Write log message to .msg file in append mode
        # with opens the file and automatically closes file
        with open('.msg', 'a') as log_file:
            log_file.write(log_message + '\n')

        backend_url = next(backend_pool) + self.path #selecting next backend server in iteration
        try:
            # response formed with backend url and header
            response = requests.get(backend_url, headers=self.headers)

            # send status code
            self.send_response(response.status_code)

            # send_header(keyword, value); sending header information
            for key,value in response.headers.items():
                self.send_header(key, value)
            self.end_headers() # THIS IS REQUIRED

            print (f"Response from server: {self.request_version} {response.status_code} OK")
            print (f"Hello From Backend Server")
        except:
            self.send_response(502)
            self.end_headers
            print("Could not connect to backend server")

# Need to set up backend servers
def run_backendserver(port):   
    with HTTPServer(('localhost', port), BackEndHandler) as server:
        print(f"Server started at http://localhost:{port}")
        server.serve_forever() # starts and keeps running server

threads = []
for port in backend_ports:
    thread = threading.Thread(target=run_backendserver, args=(port,))
    thread.daemon = True  # Allows the program to exit even if threads are running
    threads.append(thread)
    thread.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Shutting down servers...")

# Server setup listening on localhost
# HTTPServer (serverAddress, Request Handler Class)
with HTTPServer(('localhost', PORT), Handler) as server:
    print(f"Server started at http://localhost:{PORT}")
    server.serve_forever() # starts and keeps running server
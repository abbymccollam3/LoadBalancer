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

from http.server import SimpleHTTPRequestHandler, HTTPServer 
# HTTPServer (server_address, request handler class)

PORT = 8000

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

        # send response -> 200 = OK
        self.send_response(200, "Hi")

        # send_header(keyword, value); sending header information
        self.send_header("Content-type", "text/html")
        self.end_headers() # THIS IS REQUIRED
        
        # if /hello is at end of URL
        if self.path == '/hello':
            self.wfile.write(b"Hello, World!") # actual message that prints

        # this is sending to back end
        elif self.path == ':8001':
            # The API endpoint
            url = "https://jsonplaceholder.typicode.com/posts/1"

            # A GET request to the API
            response = requests.get(url)

            print (f"Response from server: {self.request_version} {response.status_code} OK")
            print (f"Hello From Backend Server")
        
    
        else:
            super().do_GET()

# Server setup listening on localhost
# HTTPServer (serverAddress, Request Handler Class)
with HTTPServer(('localhost', PORT), Handler) as server:
    print(f"Server started at http://localhost:{PORT}")
    server.serve_forever() # starts and keeps running server

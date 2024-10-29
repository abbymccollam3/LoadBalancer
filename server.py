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

from http.server import SimpleHTTPRequestHandler, HTTPServer 
# HTTPServer (server_address, request handler class)

PORT = 8000

class Handler (SimpleHTTPRequestHandler): # inheriting Simple... (request, client_address, server, directory=None)
    # handle GET requests
    def do_GET(self):
        # get client address
        address = self.client_address[0]
        
        # get command, path, request_version
        command = f"{self.command} {self.path} {self.request_version}"

        host = self.headers.get('Host')
        user_agent = self.headers.get('User-Agent')
        accept = self.headers.get('Accept')

        # log message
        print(f"Received request from {address}") # (host, port)
        print(command)
        print(f"Host: {host}")
        print(f"User-Agent: {user_agent}")
        print(f"Accept: {accept}")

        if self.path == '/hello':
            # send response -> 200 = OK
            self.send_response(200, "Hi")

            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Hello, World!")

        else:
            super().do_GET()

# Server setup
with HTTPServer(('localhost', PORT), Handler) as server:
    print(f"Server started at http://localhost:{PORT}")
    server.serve_forever()

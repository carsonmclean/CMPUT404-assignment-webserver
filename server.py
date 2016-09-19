#  coding: utf-8
import SocketServer, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Carson McLean
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):

    def _check_resource_location(self, requested_resource):
        current_directory = os.path.abspath(os.curdir)
        data_directory = current_directory + "/www"
        return os.path.abspath(requested_resource).startswith(data_directory)

    def _adjust_resource(self, requested_resource):
        current_directory = os.path.abspath(os.curdir)
        requested_resource = current_directory + "/www" + requested_resource
        return requested_resource

    def _create_headers(self):
        return "HTTP/1.1 200 OK\r\n"

    def _send_404(self, requested_resource):
        headers = "HTTP/1.1 404 Not Found\r\n"

        close = "Connection: close\r\n\r\n"

        body = ("<html>\n<body>404 - Could not find resource at "
                + requested_resource
                + " </body>\n</html>")

        self.request.send(headers + close + body)

    def _get_mime(self, adjusted_resource):
        if (adjusted_resource[-4:] == ".css"):
            return "Content-Type: text/css\r\n"
        elif (adjusted_resource[-5:] == ".html"):
            return "Content-Type: text/html\r\n"
        else:
            return "Content Type: \r\n"

    def _send_302(self, requested_resource):
        headers = "HTTP/1.1 302 Found\r\n"
        location = "Location: http://127.0.0.1:8080" + requested_resource + "index.html\r\n"
        close = "Connection: close\r\n\r\n"

        self.request.send(headers + location + close)

    def _handle_directory_redirect(self, adjusted_resource):
        return os.path.isdir(adjusted_resource)

    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print("Got a request of: %s\n" % self.data)

        split_data = self.data.split(" ")
        requested_resource = split_data[1]
        adjusted_resource = self._adjust_resource(requested_resource)
        if (adjusted_resource.endswith("/")):
            self._send_302(requested_resource)

        elif (self._check_resource_location(adjusted_resource)):
            if (self._handle_directory_redirect(adjusted_resource)):
                self._send_302(requested_resource + "/")
            else:
                try:
                    resource = open(adjusted_resource).read()

                    headers = self._create_headers()

                    content_type = self._get_mime(adjusted_resource)

                    close = "Connection: close\r\n\r\n"

                    self.request.send(headers + content_type + close + resource)
                except:
                    self._send_404(requested_resource)
        else:
            self._send_404(requested_resource)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

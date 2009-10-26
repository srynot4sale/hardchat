#!/usr/bin/python

# Copyright 2009 Aaron Barnes <aaron.barnes@hbcosmo.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# Import python libs
import BaseHTTPServer

# Import hardchat libs
import file, messaging


class EchoHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''
    Handle incoming requests
    '''

    def do_GET(self):
        '''
        Handle GET requests (shouldn't get POST requests)
        '''

        # Respond 200 OK
        self.send_response(200)

        # Response is HTML
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Action type for logging
        action = ''

        # Handle root file request
        if self.path == '/':
            self.path = '/static/index.html'

        # File operations begin with /static/
        if self.path.startswith('/static/'):

            # Load and send file to the client
            file.handleRequest(self.wfile, self.path[8:])

        # Otherwise, must be a messaging request
        else:

            # Handle request and send response to the client
            handler = messaging.handler()
            handler.handleRequest(self.wfile, self.path[1:])


        # Create log message
        action = self.path

        # Print action to console for logging/debugging
        print "Action: %r" % action


# If file called directly, run server
if __name__ == '__main__':

    # Create forking server
    server = BaseHTTPServer.HTTPServer(('localhost', 8000), EchoHandler)
    print "Server listening on localhost:8000..."
    try:
        server.serve_forever()

    except KeyboardInterrupt:
        # On ctrl-c, bail
        print "\nbailing..."

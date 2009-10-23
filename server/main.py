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

import os
import BaseHTTPServer


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

        # If not a posted message
        if not self.path.startswith('/msg?'):

            # Handle root file request
            if self.path == '/':
                self.path = '/index.html'

            # Create log message
            action = self.path

            # Open requested file and send to client
            f = open('/home/aaronb/code/personal/hardchat/client'+self.path)
            self.wfile.write(f.read())
            f.close()

        # Must want some HTML
        else:

            # Remove prefix portion ( /msg? )
            message = self.path[5:]

            # Generate HTML
            html  = '<div class="message">'
            html += '<span class="author">Unknown</span>'
            html += '<span class="message">%s</span>' % message
            html += '</div>'

            # Send to client
            self.wfile.write(html)
            self.wfile.flush()

            # Create log message
            action = 'message - '+message

        # Print action to console for logging/debugging
        print "Action: %r" % action


# If file called directly, run server
if __name__ == '__main__':

    # Create forking server
    server = BaseHTTPServer.SocketServer.ForkingTCPServer(('localhost', 8000), EchoHandler)
    print "Server listening on localhost:8000..."
    try:
        server.serve_forever()

    except KeyboardInterrupt:
        # On ctrl-c, bail
        print "\nbailing..."

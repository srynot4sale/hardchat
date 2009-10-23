# This file is based on
# 
# http://gist.github.com/204027
#
# Simple forking echo server built with Python's SocketServer library. A more
# Pythonic version of http://gist.github.com/203520, which itself was inspired
# by http://tomayko.com/writings/unicorn-is-unix.
#

import os
import BaseHTTPServer

class EchoHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        action = ''

        if not self.path.startswith('/msg?'):

            if self.path == '/':
                self.path = '/index.html'

            action = self.path

            f = open('/home/aaronb/code/personal/hardchat/client'+self.path)
            self.wfile.write(f.read())
            f.close()

        else:

            message = self.path[5:]

            html  = '<div class="message">'
            html += '<span class="author">Unknown</span>'
            html += '<span class="message">%s</span>' % message
            html += '</div>'

            self.wfile.write(html)
            self.wfile.flush()

            action = 'message - '+message

        print "Action: %r" % action


if __name__ == '__main__':

    server = BaseHTTPServer.SocketServer.ForkingTCPServer(('localhost', 8000), EchoHandler)
    print "Server listening on localhost:8000..."
    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print "\nbailing..."

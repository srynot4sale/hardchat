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

        if self.path == '/':
            f = open('/home/aaronb/code/personal/hardchat/client/index.html')
            self.wfile.write(f.read())
            f.close()

        elif self.path == '/libs/jquery-1.3.2.min.js':
            f = open('/home/aaronb/code/personal/hardchat/client/libs/jquery-1.3.2.min.js')
            self.wfile.write(f.read())
            f.close()

        else:
            self.wfile.write('Child %s echo>' % os.getpid())
            self.wfile.flush()

            message = self.path
            self.wfile.write(message)

        print "Child %s echo'd: %r" % (os.getpid(), self.path)


if __name__ == '__main__':

    server = BaseHTTPServer.SocketServer.ForkingTCPServer(('localhost', 8000), EchoHandler)
    print "Server listening on localhost:8000..."
    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print "\nbailing..."

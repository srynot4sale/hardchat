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

class handler:

    public = ['msg']

    def handleRequest(self, connection, request):
        '''
        Handle messaging requests
        '''

        # Find action type
        action, data = request.split('?', 1)

        # Check method is usable
        if action not in self.public:
            raise Exception, 'Attempting to access private method'

        # Use appropriate method
        response = getattr(self, action)(data)

        # Send response back to client
        connection.write(response)
        connection.flush()


    def msg(self, data):
        '''
        Add message from user
        '''

        # Generate HTML
        html  = '<div class="message">'
        html += '<span class="author">Unknown</span>'
        html += '<span class="message">%s</span>' % data
        html += '</div>'

        return html

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
import hashlib, json, urlparse

# List of users active in the chat
users = {}

# List of message id's in order
messages = []

# Message data
message_data = {}


class handler:
    '''
    Handle messaging operations
    '''

    # Publically available methods
    public = ['post', 'nick']


    def handleRequest(self, request, path_data):
        '''
        Handle messaging requests
        '''
        # Find action type (string before first ?)
        action, data = path_data.split('?', 1)

        # Parse data into a dictionary
        data = urlparse.parse_qs(data)

        # Check action is public
        if action not in self.public:
            raise Exception, 'Attempting to access private method %s' % action

        # Run action and save response
        response = getattr(self, action)(request, data)

        # Add action type to response
        response['action'] = action

        # Send response back to client
        self._respond(request, response)


    def _respond(self, request, response):
        '''
        Send response back to client
        '''
        # Encode response as json and send
        json.dump(response, request.wfile)


    def nick(self, request, data):
        '''
        Change user's nick
        '''
        # Get supplied data
        nick = data['new_nick'][0]
        hash = data['user_hash'][0]

        # See if we are adding a new user
        while hash not in users:
            # Repeat until we create a unique hash
            # Create unique hash
            m = hashlib.md5()
            m.update(str(request.client_address[0]) + nick)
            hash = m.hexdigest()

            # If already used, try again
            if hash in users:
                continue

            # Save new hash
            users[hash] = {}

        # Update/save nick
        users[hash]['nick'] = nick
        return {'user_hash': hash, 'new_nick': nick, 'html': hash}


    def post(self, request, data):
        '''
        Post message from user
        '''

        # Generate HTML
        html  = '<div class="message">'
        html += '<span class="author">%s</span>' % users[data['user_hash'][0]]['nick']
        html += '<span class="message">%s</span>' % data['message'][0]
        html += '</div>'

        return {'html': html}

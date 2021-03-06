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
import hashlib, json, time, urlparse

# List of users active in the chat
users = {}

# List of message id's in order
messages = []


class handler:
    '''
    Handle messaging operations
    '''

    # Publically available methods
    public = [
        'nick',
        'poll',
        'post',
    ]


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


    def _authenticate(self, request, data):
        '''
        Authenticate users
        '''
        # Delete expired users
        expire = time.time() - 15
        for user in users.keys():
            if users[user]['keepalive'] < expire:
                self._serverMessage('<i>%s</i> left the chat' % users[user]['nick'])
                del users[user]

        # Authenticate current user
        if data['user_hash'][0] in users:
            # Update keepalive time
            users[data['user_hash'][0]]['keepalive'] = time.time()

            return True
        else:
            return False


    def _getMessages(self, request, data):
        '''
        Send new messages back to client
        '''
        # Grab all messages since the last one the user has seen
        last_message = int(data['last_message'][0])
        unread = messages[last_message:]

        # Loop through unread messages
        html = ''
        message_id = last_message
        for message in unread:

            # Generate HTML
            html += '<div id="message_%s" title="Message %s (%s)" ' % (message_id, message_id, time.strftime('%a, %d %b %Y %H:%M:%S', message['time']))

            if 'server' in message:
                html += 'class="message server">'
            else:
                html += 'class="message">'

            # If not a server message, display author
            if 'server' not in message:
                html += '<span class="author">%s</span>' % message['nick']

            html += '<span class="message">%s</span>' % message['message']
            html += '</div>'

            message_id += 1

        if unread:
            # Get new last message
            last_message = message_id

        return {'html': html, 'last_message': last_message}


    def _respond(self, request, response):
        '''
        Send response back to client
        '''
        # Encode response as json and send
        json.dump(response, request.wfile)


    def _saveMessage(self, message):
        '''
        Save a message to the queue, and limit the queues size
        '''
        message['time'] = time.localtime()

        messages.append(message)

        # Limit message archive length to 100
        while len(messages) > 100:
            messages.pop(0)


    def _serverMessage(self, text):
        '''
        Post a server generated message
        '''
        message = {
            'server': True,
            'message': text,
        }

        self._saveMessage(message)


    ##############################
    # Public methods

    def nick(self, request, data):
        '''
        Change user's nick
        '''
        # Make sure we timeout any old nicks before trying to login
        self._authenticate(request, data)

        # Get supplied data
        nick = data['new_nick'][0]
        hash = data['user_hash'][0]
        new_user = False

        # Check if nick already used
        for user in users.keys():
            if users[user]['nick'] == nick:
                return {
                    'html': '<div class="message server"><span class="message">Nick already in use. Choose another or if you have logged out and are returning - wait a few seconds and try again</span></div>',
                }

        # Create new user
        while hash not in users:
            new_user = True

            # Repeat until we create a unique hash
            # Create unique string - client ip, nick, current time
            unique = str(request.client_address[0]) + nick + str(time.time())

            # Create hash from unique string
            m = hashlib.md5()
            m.update(unique)
            hash = m.hexdigest()

            # If already used, try again
            if hash in users:
                hash = None
                continue

            # Save new hash
            users[hash] = {}

        # Get old nick
        if not new_user:
            old_nick = users[hash]['nick']

        # Update/save nick
        users[hash]['nick'] = nick
        users[hash]['keepalive'] = time.time()

        # Post message
        if new_user:
            self._serverMessage('<i>%s</i> joined the chat' % nick)
        else:
            self._serverMessage('<i>%s</i> changed nick to <i>%s</i>' % (old_nick, nick))

        # Get any new messages
        ret = self._getMessages(request, data)
        ret['user_hash'] = hash
        ret['new_nick'] = nick
        return ret


    def poll(self, request, data):
        '''
        Get any new messages from server
        '''
        # Check the user is logged in
        if not self._authenticate(request, data):
            return {
                'html': '<div class="message server"><span class="message">An error has occured, please refresh page</span></div>',
                'user_hash': '0',
            }

        return self._getMessages(request, data)


    def post(self, request, data):
        '''
        Post message from user
        '''
        # Check the user is logged in
        if not self._authenticate(request, data):
            return {
                'html': '<div class="message server"><span class="message">An error has occured, please refresh page</span></div>',
                'user_hash': '0',
            }

        # Add new message
        message = {
            'user': data['user_hash'][0],
            'nick': users[data['user_hash'][0]]['nick'],
            'message': data['message'][0],
        }

        self._saveMessage(message)

        return self._getMessages(request, data)

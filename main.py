import webapp2
import json
import datetime
import logging
from utils.jsondataencoder import JSONDateEncoder
from model.conveyordata import ConveyorData
from model.conveyorreset import ConveyorReset
from google.appengine.api import channel
from google.appengine.ext import deferred
from google.appengine.api import memcache
from utils.templateloader import JinjaTemplate, JinjaTemplateNotFoundException

class DialogHandler(webapp2.RequestHandler):
    """
    Class for keeping the clients updated and listening to the reset button
    message
    """

    @staticmethod
    def _get_latest_data():
        return {
                'last_data': ConveyorData.get_most_recent() or {},
                'last_reset': ConveyorReset.get_most_recent() or {},
                'now': datetime.datetime.utcnow()
                }

    def get(self):
        """
        Method called on HTTP GET /opened
        Writes {"last_data": ..., "last_reset": ...}
        """
        self.response.out.write(json.dumps(self._get_latest_data(),
                    cls=JSONDateEncoder))

    def post(self):
        """
        Method called on HTTP POST /opened
        If 'reset' is passed it will add a reset mark.
        If 'status' is passed then:
        - It expects also 'timestamp' with the Conveyor Machine data.
        - Expects 'current_total_weight'.
        - The new data is scheduled to be sent via channel to all clients.
        If 'new' is passed is a request for the old data (via channel).
        """
        to = memcache.get('clients') or []
        if self.request.get('reset'):
            current_total_weight = 0.0
            current_data = ConveyorData.get_most_recent()
            if current_data:
                current_total_weight = current_data.current_total_weight
            reset = ConveyorReset(current_total_weight = current_total_weight)
            reset.put()
            #Exit the function not to send messages back to the clients
            return
        elif self.request.get('status'):
            timestamp = datetime.datetime.strptime(
                    self.request.get('timestamp'),
                    '%Y-%m-%d %H:%M:%S.%f'
                    ) if self.request.get('timestamp') else None
            current_total_weight = \
                float(self.request.get('current_total_weight'))
            status = self.request.get('status')
            if None in (timestamp, current_total_weight, status):
                #TODO: Raise error!
                pass
            conveyor_data = ConveyorData(timestamp=timestamp,
                    current_total_weight=current_total_weight,
                    status=status)
            conveyor_data.put()
        message = self._get_latest_data()
        if self.request.get('new'):
            to = [{'user_token':self.request.get('user_token')}]
            message['previous'] = ConveyorData.get_most_recent(30, 1)
        # The response via channel to clients in the 'to' array
        deferred.defer(notify_clients, message, to)

def notify_clients(message, clients):
    """
    Function (usually deferred) to send the message to the clients via
    Google App Engine's Channel API
    Channels only last open for two hours so, here, all clients subscribed
    more than two hours ago are deleted from the array.
    """
    now = datetime.datetime.now()
    to_remove = []
    for i in clients:
        if 'created' in i:
            elapsed = now - i['created']
            if elapsed.total_seconds() > 2 * 60 * 60:
                to_remove.append(i)
                continue
        #Let every client know the server's datetime for syncing.
        #Since this job can be deferred the time needs to be updated.
        message['now'] = datetime.datetime.utcnow()
        channel.send_message(i['user_token'], json.dumps(message,
                                                cls=JSONDateEncoder))
    c = memcache.get('clients')
    for i in to_remove:
        c.remove(i)
    memcache.set('clients', c)

class MainPage(webapp2.RequestHandler):
    """
    Handler from the main page
    """

    def get(self):
        """
        Handler for HTTP GET /
        Creates the user token and writes back the templated data
        with the information needed for the client to connect to the
        Channel API.
        """

        user_token = self.request.get('user_token')

        if not user_token:
            import uuid
            user_token = uuid.uuid4().get_hex()

        token = channel.create_channel(user_token)


        template_values = {
                'token': token,
                'user_token': user_token,
                'created': datetime.datetime.now()
                }

        ret = None
        try:
            ret = JinjaTemplate('main.html').render(template_values)
        except JinjaTemplateNotFoundException as ex:
            ret = '<h1>Error: {}</h1>'.format(ex.message)
        except Exception as ex:
            ret = '<h1>Generic error: {}</h1>'.format(repr(ex))

        clients = memcache.get('clients') or []
        clients.append(template_values)
        memcache.set('clients', clients)

        self.response.out.write(ret)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/opened', DialogHandler),
])

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

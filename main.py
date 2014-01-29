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
        self.response.out.write(json.dumps(self._get_latest_data(),
                    cls=JSONDateEncoder))

    def post(self):
        to = memcache.get('clients') or []
        user_token = self.request.get('user_token')
        if user_token:
            #TODO: Refresh client on table
            #to = [{'user_token' : user_token}]
            pass
        if self.request.get('reset'):
            current_total_weight = 0.0
            current_data = ConveyorData.get_most_recent()
            if current_data:
                current_total_weight = current_data.current_total_weight
            reset = ConveyorReset(current_total_weight = current_total_weight)
            reset.put()
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
        deferred.defer(notify_clients, message, to)

def notify_clients(message, clients):
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

    def get(self):

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

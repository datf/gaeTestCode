import webapp2
import json
import datetime
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
    def date_handler(obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    def get(self):
        last_data = ConveyorData\
                .query()\
                .order(-ConveyorData.timestamp)\
                .fetch(1)\
                or\
                (ConveyorData(timestamp=datetime.datetime.now(),
                    current_total_weight=0,
                    status=''),)
        last_reset = ConveyorReset\
                .query()\
                .order(-ConveyorReset.timestamp)\
                .fetch(1)\
                or\
                (ConveyorReset(current_total_weight=0),)
        ret = {'last_data': last_data[0].to_dict(),
                'last_reset': last_reset[0].to_dict()
                }
        self.response.out.write(json.dumps(ret,
                    default=self.date_handler))

    def post(self):
        if self.request.get('user_token'):
            #TODO: Refresh client on table
            pass
        elif self.request.get('reset'):
            current_total_weight = 0
            current_reset = ConveyorData\
                    .query()\
                    .order(-ConveyorData.current_total_weight)\
                    .fetch(1)
            if len(current_reset) > 0:
                current_total_weight = current_reset[0].current_total_weight
            reset = ConveyorReset(current_total_weight = current_total_weight)
            reset.put()
            memcache.set('last_reset', reset)
        else:
            timestamp = datetime.datetime.strptime(
                    self.request.get('timestamp'),
                    '%Y-%m-%d %H:%M:%S.%f'
                    )
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
            memcache.set('last_data', conveyor_data)
        message = {
                'last_data': memcache.get('last_data') or {},
                'last_reset': memcache.get('last_reset') or {},
                }
        notify_clients(message)
        #deferred.defer(notify_clients, message)

def notify_clients(message):
    clients = memcache.get('clients') or []
    for i in clients:
        channel.send_message(i['user_token'], message)


class MainPage(webapp2.RequestHandler):

    def get(self):

        user_token = self.request.get('user_token')

        if not user_token:
            import uuid
            user_token = uuid.uuid4().get_hex()

        token = channel.create_channel(user_token)


        template_values = {
                'token': token,
                'user_token': user_token
                }

        ret = None
        try:
            ret = JinjaTemplate('main.html').render(template_values)
        except JinjaTemplateNotFoundException as ex:
            ret = '<h1>Error: {}</h1>'.format(ex.message)
        except Exception as ex:
            ret = '<h1>Generic error: {}</h1>'.format(repr(ex))

        clients = memcache.get('clients') or []
        memcache.set('clients', clients.append(template_values))

        self.response.out.write(ret)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/opened', DialogHandler),
])

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

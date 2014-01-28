import json
from google.appengine.ext import ndb

class JSONDateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ndb.Model):
            return obj.to_dict()
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat(' ') + ' +0000'
        else:
            return json.JSONEncoder.default(self, obj)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

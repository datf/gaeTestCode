from model.baseconveyor import BaseConveyor
from google.appengine.ext import ndb

class ConveyorData(BaseConveyor):
    """
    ORM for the data received from the Conveyor machine
    """
    timestamp = ndb.DateTimeProperty(indexed=True, required=True,
                                    auto_now_add=True)
    current_total_weight = ndb.FloatProperty(indexed=False, required=True)
    status = ndb.StringProperty(indexed=False)

    cached_name = 'last_data'

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

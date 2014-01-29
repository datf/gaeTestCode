from model.baseconveyor import BaseConveyor
from google.appengine.ext import ndb

class ConveyorReset(BaseConveyor):
    """
    ORM for the reset commands.
    When the reset button is pressed, we save the timestamp of the event
    and the weight the conveyor had at that time.
    """
    timestamp = ndb.DateTimeProperty(indexed=True, required=True,
                                    auto_now_add=True)
    current_total_weight = ndb.FloatProperty(indexed=False, required=True)

    cached_name = 'last_reset'


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

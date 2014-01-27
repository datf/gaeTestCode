from google.appengine.ext import ndb

class ConveyorData(ndb.Model):
    """
    ORM for the data received from the Conveyor machine
    """
    timestamp = ndb.DateTimeProperty(indexed=True, required=True,
                                    auto_now_add=True)
    current_total_weight = ndb.FloatProperty(indexed=False, required=True)
    status = ndb.StringProperty(indexed=False)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

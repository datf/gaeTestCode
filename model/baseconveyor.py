from google.appengine.ext import ndb
from google.appengine.api import memcache

class BaseConveyor(ndb.Model):
    """
    Base class for caching last inserted record and get_most_recent query.
    """
    cached_name = ''

    def _post_put_hook(self, future):
        memcache.set(self.cached_name, future.get_result().get())

    @classmethod
    def get_most_recent(cls, num=1, offset=0):
        if num == 1:
            from_memcache = memcache.get(cls.cached_name)
            if from_memcache:
                return from_memcache
        result = cls.query().order(-cls.timestamp).fetch(num, offset=offset)
        if len(result) == 1:
            memcache.set(cls.cached_name, result[0])
            return result[0]
        elif len(result) > 1:
            return result
        return None

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


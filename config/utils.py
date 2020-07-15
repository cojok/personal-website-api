import time
from config.extensions import get_redis_client
from custom_exceptions import RateLimitExceeded

def rate_per_second(count):
    def _rate_per_second(function):
        def __rate_per_second(*args, **kwargs):
            period_in_seconds = int(period.total_seconds())
            t = r.time()[0]
            separation = round(period_in_seconds / limit)
            r.setnx(key, 0)
            tat = max(int(r.get(key)), t)
            if tat - t <= period_in_seconds - separation:
                new_tat = max(tat, t) + separation
                r.set(key, new_tat)
                return False
            return True
            return function(*args, *kwargs)
        return __rate_per_second
    return _rate_per_second


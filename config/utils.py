from datetime import timedelta
from config.extensions import get_redis_client
from redis.exceptions import LockError
from flask import Response, make_response

def request_limit(limit: int, period: timedelta):
    def _request_limit(function):
        def __request_limit(*args, **kwargs):
            key: str = 'limit'
            period_in_seconds = int(period.total_seconds())
            r = get_redis_client()
            t = r.time()[0]
            separation = round(period_in_seconds / limit)
            r.setnx(key, 0)
            try:
                with r.lock('lock:' + key, blocking_timeout=1) as lock:
                    tat = max(int(r.get(key)), t)
                    if tat - t <= period_in_seconds - separation:
                        new_tat = max(tat, t) + separation
                        r.set(key, new_tat)
                        return function(*args, **kwargs)
                    return Response('Too many requests. Timeout', status=429)
            except LockError:
                print('lock');
                return Response('Too many requests. Timeout', status=429)
        return __request_limit
    return _request_limit

def allowed_contact_today(email, name) -> bool:
    r = get_redis_client()
    key: str = email
    if r.exists(key):
        return False
    else:
        r.setex(
            key,
            timedelta(days=1),
            value = name
        )
        return True

def build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
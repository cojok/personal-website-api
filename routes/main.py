from config.settings import SG_KEY
from config.extensions import get_redis_client

from flask import Blueprint, request, escape
from datetime import timedelta
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

test_schema = {
  'type': 'object',
  'properties': {
    'name': { 
      'type': 'string',
      'minLength': 3,
      'pattern': '^[\w\'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}$',
      'message': 'Not a valid name'
    },
    'email': { 
      'type': 'string',
      'minLength': 4,
      'pattern': '^[^\s@]+@[^\s@]+\.[^\s@]+$',
      'message': 'Not a valid email',
    },
    'message': { 
      'type': 'string',
      'minLength': 10,
      'message': 'Not a valid message'
    }
  },
  'required': ['name', 'email', 'message']
}

main = Blueprint('main', __name__)

def request_is_limited(key: str, limit: int, period: timedelta):
    period_in_seconds = int(period.total_seconds())
    print(period_in_seconds)
    r = get_redis_client()
    t = r.time()[0]
    separation = round(period_in_seconds / limit)
    r.setnx(key, 0)
    try:
      with r.lock('lock:' + key, blocking_timeout=5) as lock:
        tat = max(int(r.get(key)), t)
        if tat - t <= period_in_seconds - separation:
          new_tat = max(tat, t) + separation
          r.set(key, new_tat)
          return False
        return True
    except LockError:
        return True

@main.route('/testing', methods=['POST'])
def testing():
  limit: bool = request_is_limited('testing', 1, timedelta(seconds=1))
  return { 'hasLimit' : limit };
  r_data = request.data
  if len(r_data) == 0:
    return 'Not a valid body', 400
  
  r_data = request.json
  try:
    validate(instance=r_data, schema=test_schema)
    name: str = escape(r_data['name'])
    email: str = escape(r_data['email'])
    message_body: str = escape(r_data['message'])
    return '''
    <p>A message from the personal website.</p>
    <p>Name: {}</p>
    <p>Email: {}</p>
    <p>Message: {}</p>
    '''.format(name, email, message_body), 201
  except ValidationError as e:
    return { 'message': e.schema['message'], 'data': list(e.path) }, 400

@main.route('/contact', methods=['POST'])
def contact():
  name = escape(request.json['name'])
  email = escape(request.json['email'])
  message_body = escape(request.json['message'])
  message = Mail(
    from_email= 'cojokka@gmail.com',
    to_emails='cojokka@gmail.com',
    subject='Contact from Personal-Website <flaviuscojocariu.com>',
    html_content='''
    <p>A message from the personal website.</p>
    <p>Name: {}</p>
    <p>Email: {}</p>
    <p>Message: {}</p>
    '''.format(name, email, message_body))
  
  sg = SendGridAPIClient(SG_KEY)
  response = sg.send(message)
  print(response.status_code, response.body, response.headers)
  return 'hey'
  
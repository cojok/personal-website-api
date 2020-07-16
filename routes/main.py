from config.settings import SG_KEY
from config.utils import request_limit
from config.utils import allowed_contact_today

from flask import Blueprint, request, escape, abort
from datetime import timedelta
from jsonschema import validate
from jsonschema.exceptions import ValidationError
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

@main.route('/contact', methods=['POST'])
@request_limit(10, timedelta(minutes=1))
def contact():
  r_data = request.data
  if len(r_data) == 0:
    return 'Not a valid body', 400
  r_data = request.json
  try:
    validate(instance=r_data, schema=test_schema)
    name: str = escape(r_data['name'])
    email: str = escape(r_data['email'])
    if not allowed_contact_today(email, name):
      return abort(429)
    message_body: str = escape(r_data['message'])
    message = Mail(
      from_email= 'cojokka@gmail.com',
      to_emails='cojokka@gmail.com',
      subject='Contact from Personal-Website <flaviuscojocariu.com>',
      html_content= '''
        <p>A message from the personal website.</p>
        <p>Name: {}</p>
        <p>Email: {}</p>
        <p>Message: {}</p>
      '''.format(name, email, message_body))
  except ValidationError as e:
    return { 'message': e.schema['message'], 'data': list(e.path) }, 400
  sg = SendGridAPIClient(SG_KEY)
  response = sg.send(message)
  # print(response.status_code, response.body, response.headers)
  return 'hey', response.status_code
  

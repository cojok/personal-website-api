import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.utils import request_limit, allowed_contact_today, build_cors_prelight_response

from flask import Blueprint, request, escape, abort
from flask_cors import cross_origin
from datetime import timedelta
from jsonschema import validate
from jsonschema.exceptions import ValidationError

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

@main.route('/', methods=['GET'])
def main_route():
  return 'Welcome to my api'

@main.route('/contact', methods=['POST', 'OPTIONS'])
@cross_origin(allow_headers=['Content-Type'])
@request_limit(10, timedelta(minutes=1))
def contact():
  if request.method == "OPTIONS": # CORS preflight
    return build_cors_prelight_response()
  port = 25
  r_data = request.data
  if len(r_data) == 0:
    return 'Not a valid body', 400
  r_data = request.json

  try:
    validate(instance=r_data, schema=test_schema)
    name: str = escape(r_data['name'])
    sender: str = escape(r_data['email'])
    # if not allowed_contact_today(email, name):
      # return abort(429)
    message_body: str = escape(r_data['message'])
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = 'contact@api.flaviuscojocariu.com'
    message['Subject'] = 'Personal-Website-Contact'
    body = MIMEText(message_body, 'html')
    message.attach(body)

    with smtplib.SMTP('localhost', port) as server:
      server.sendmail('test@api.flaviuscojocariu.com', 'cojokka@gmail.com', message.as_string())
    return 'email sent', 200  
  except ValidationError as e:
    return { 'message': e.schema['message'], 'data': list(e.path) }, 400


from flask import Flask, make_response
from flask_cors import CORS, cross_origin

from routes.main import main

cors = CORS()

def create_app(config_file='config/settings.py'):
  # app init
  app = Flask(__name__)
  
  #CORS settings
  cors.init_app(app, resources={r"/v1/": {"origins": "*"}})
  
  # app get config from settings file 
  app.config.from_pyfile(config_file)
  
  # app register route blueprint
  app.register_blueprint(main, url_prefix='/v1/')
  
  return app
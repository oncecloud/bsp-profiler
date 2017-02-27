#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2017/01/06

import logging
from logging import Formatter

from flask import Flask
from flask_restful import Api
from flask_restful.representations.json import output_json

app = Flask(__name__)

class Service(Api):
    def handle_error(self, e):
        # Attach the exception to itself so Flask-Restful's error handler
        # tries to render it.
        if not hasattr(e, 'data'):
            e.data = e

        return super(Service, self).handle_error(e)

restful_api = Service(app)

@restful_api.representation('application/json')
def output_json_exception(data, code, *args, **kwargs):
    """Render exceptions as JSON documents with the exception's message."""
    if isinstance(data, Exception):
        data = {'status': code, 'message': str(data)}

    return output_json(data, code, *args, **kwargs)

# Logging
handler = logging.FileHandler('/var/log/optimizer.log')
handler.setLevel(logging.DEBUG)
handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)

# from api import dispatcher
from optimizer.restful import dispatcher

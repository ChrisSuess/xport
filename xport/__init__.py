from flask import Flask
from xport.config import Config

app = Flask(__name__)
app.config.from_object(Config)

import xport.routes

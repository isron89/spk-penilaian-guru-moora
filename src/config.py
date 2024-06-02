import os
import configparser
from sqlalchemy import create_engine

DEV = False

config = configparser.ConfigParser()
config.read(os.path.join('config','config.txt'))

engine = create_engine(config.get('database', 'con'))
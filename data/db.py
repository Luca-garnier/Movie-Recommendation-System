"""
MONGODB Connection
Create the connection to mongodb
"""
import configparser
import pathlib

from mongoengine import connect


def get_connection():
    config = configparser.ConfigParser()
    config.read(pathlib.Path(__file__).parent.parent / "config" / 'config.ini')

    # Open connection to mongoDB
    try:
        connect(
            host=config['mongoDB']['host'],
            db=config['mongoDB']['db'],
            alias='bd'
        )
        print("Connected to: ", config['mongoDB']['host'])
    except Exception as e:
        print("Error in connection to mongoDB: \n %s" % e)
        raise
